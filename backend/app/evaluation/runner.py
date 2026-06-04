from __future__ import annotations

import json
from pathlib import Path

from app.core.settings import Settings
from app.db.sqlite import SQLiteStore
from app.evaluation.metrics import (
    EvaluationCase,
    EvaluationPrediction,
    evaluate_predictions,
)
from app.rag.search import ChromaReadyHybridIndex, build_documents


def find_dataset(settings: Settings) -> Path | None:
    candidates = [
        Path("evaluation") / "qa_dataset.json",
        settings.data_dir / "evaluation" / "qa_dataset.json",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def load_cases(path: Path) -> list[EvaluationCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("cases", raw) if isinstance(raw, dict) else raw
    cases: list[EvaluationCase] = []
    for item in items:
        sources = item.get("relevant_document_ids") or item.get("expected_sources", [])
        relevant_ids = [
            str(source).replace("\\", "/").removeprefix("sample_docs/")
            for source in sources
        ]
        cases.append(
            EvaluationCase(
                question=item["question"],
                relevant_document_ids=relevant_ids,
                should_abstain=bool(item.get("should_abstain", False))
                or item.get("category") == "unanswerable"
                or not relevant_ids,
                expected_keywords=list(item.get("expected_keywords", [])),
            )
        )
    return cases


def run_evaluation(settings: Settings, store: SQLiteStore, k: int = 4) -> dict:
    dataset = find_dataset(settings)
    if dataset is None:
        metrics = {
            f"recall_at_{k}": 0.0,
            "mrr": 0.0,
            "citation_rate": 0.0,
            "abstention_accuracy": 0.0,
        }
        return {
            "available": False,
            "dataset_path": None,
            "case_count": 0,
            "metrics": metrics,
            "message": "No evaluation/qa_dataset.json file found.",
        }

    cases = load_cases(dataset)
    documents = build_documents(store.list_documents())
    index = ChromaReadyHybridIndex(documents)
    predictions: list[EvaluationPrediction] = []
    keyword_scores: list[float] = []
    for case in cases:
        results = index.search(case.question, k=k)
        retrieved_ids = [result.document.id for result in results]
        abstained = not results
        cited_ids = [] if abstained else [results[0].document.id]
        predictions.append(EvaluationPrediction(retrieved_ids, cited_ids, abstained))
        keyword_scores.append(_keyword_match(case.expected_keywords or [], results))

    metrics = evaluate_predictions(cases, predictions, k=k)
    metrics["expected_keyword_match_rate"] = (
        sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0
    )
    return {
        "available": True,
        "dataset_path": str(dataset),
        "case_count": len(cases),
        "metrics": metrics,
    }


def _keyword_match(keywords: list[str], results) -> float:
    if not keywords:
        return 1.0
    text = " ".join(result.document.text for result in results).lower()
    matched = sum(1 for keyword in keywords if str(keyword).lower() in text)
    return matched / len(keywords)
