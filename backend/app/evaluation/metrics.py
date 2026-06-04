from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    relevant_document_ids: list[str]
    should_abstain: bool = False
    expected_keywords: list[str] | None = None


@dataclass(frozen=True)
class EvaluationPrediction:
    retrieved_document_ids: list[str]
    cited_document_ids: list[str]
    abstained: bool


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    retrieved = set(retrieved_ids[:k])
    relevant = set(relevant_ids)
    return len(retrieved & relevant) / len(relevant)


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    relevant = set(relevant_ids)
    if not relevant:
        return 1.0
    for index, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant:
            return 1.0 / index
    return 0.0


def citation_rate(predictions: list[EvaluationPrediction]) -> float:
    if not predictions:
        return 0.0
    cited = sum(1 for prediction in predictions if prediction.cited_document_ids)
    return cited / len(predictions)


def abstention_accuracy(
    cases: list[EvaluationCase], predictions: list[EvaluationPrediction]
) -> float:
    if not cases:
        return 0.0
    correct = sum(
        1
        for case, prediction in zip(cases, predictions)
        if case.should_abstain == prediction.abstained
    )
    return correct / len(cases)


def evaluate_predictions(
    cases: list[EvaluationCase], predictions: list[EvaluationPrediction], k: int = 4
) -> dict[str, float]:
    if not cases:
        return {
            f"recall_at_{k}": 0.0,
            "recall_at_3": 0.0,
            "recall_at_5": 0.0,
            "mrr": 0.0,
            "citation_rate": 0.0,
            "abstention_accuracy": 0.0,
        }

    recalls = [
        recall_at_k(prediction.retrieved_document_ids, case.relevant_document_ids, k)
        for case, prediction in zip(cases, predictions)
    ]
    reciprocal_ranks = [
        mrr(prediction.retrieved_document_ids, case.relevant_document_ids)
        for case, prediction in zip(cases, predictions)
    ]
    return {
        f"recall_at_{k}": sum(recalls) / len(cases),
        "recall_at_3": sum(
            recall_at_k(prediction.retrieved_document_ids, case.relevant_document_ids, 3)
            for case, prediction in zip(cases, predictions)
        )
        / len(cases),
        "recall_at_5": sum(
            recall_at_k(prediction.retrieved_document_ids, case.relevant_document_ids, 5)
            for case, prediction in zip(cases, predictions)
        )
        / len(cases),
        "mrr": sum(reciprocal_ranks) / len(cases),
        "citation_rate": citation_rate(predictions),
        "abstention_accuracy": abstention_accuracy(cases, predictions),
    }
