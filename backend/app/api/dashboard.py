from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_store
from app.core.settings import get_settings
from app.db.sqlite import SQLiteStore
from app.llm.providers import provider_status
from app.rag.search import chunk_count


router = APIRouter()


def _doc_type(document: dict) -> str:
    metadata = document.get("metadata") or {}
    if metadata.get("document_type"):
        return str(metadata["document_type"]).upper()
    content_type = document.get("content_type", "")
    if "markdown" in content_type:
        return "MD"
    if "json" in content_type:
        return "JSON"
    if "csv" in content_type:
        return "CSV"
    if "pdf" in content_type:
        return "PDF"
    if "wordprocessing" in content_type:
        return "DOCX"
    return "TXT"


@router.get("/dashboard")
def dashboard(store: SQLiteStore = Depends(get_store)) -> dict:
    settings = get_settings()
    documents = store.list_documents()
    logs = store.list_query_logs(limit=25)
    providers = provider_status(settings)
    evaluation_runs = store.list_evaluation_runs(limit=1)
    latest_eval = evaluation_runs[0]["metrics"] if evaluation_runs else {}

    return {
        "mode": "backend",
        "documents": [
            {
                "id": document["id"],
                "name": document["title"],
                "type": _doc_type(document),
                "owner": document.get("metadata", {}).get("owner", "Northstar Systems"),
                "version": document.get("metadata", {}).get("version", "local-demo"),
                "status": "Indexed",
                "chunks": chunk_count(document["text"]),
                "updatedAt": document["created_at"][:10],
                "metadata": {
                    "region": document.get("metadata", {}).get("category", "supportflow"),
                    "tier": document.get("metadata", {}).get("document_type", _doc_type(document).lower()),
                },
            }
            for document in documents
        ],
        "providerStatus": [
            {
                "id": provider["name"],
                "label": provider["name"].title(),
                "detail": provider.get("model", "configured by runtime"),
                "health": "Available" if provider.get("configured") else "Not configured",
                "latency": "runtime",
                "role": "Remote answer generation"
                if provider["name"] == "openrouter"
                else "Local fallback"
                if provider["name"] == "ollama"
                else "Test fallback",
            }
            for provider in providers
        ],
        "recentQuestions": [log["question"] for log in logs[:5]]
        or [
            "How should a VIP SLA breach be escalated?",
            "Which API errors should be retried?",
            "When should webhook delivery incidents be escalated?",
        ],
        "evaluation": {
            "metrics": [
                {"label": "Recall@3", "value": f"{latest_eval.get('recall_at_3', 0):.2f}", "trend": "local run"},
                {"label": "Recall@5", "value": f"{latest_eval.get('recall_at_5', latest_eval.get('recall_at_4', 0)):.2f}", "trend": "local run"},
                {"label": "MRR", "value": f"{latest_eval.get('mrr', 0):.2f}", "trend": "local run"},
                {"label": "Abstention accuracy", "value": f"{latest_eval.get('abstention_accuracy', 0):.2f}", "trend": "local run"},
                {"label": "Citation rate", "value": f"{latest_eval.get('citation_rate', 0):.2f}", "trend": "local run"},
                {
                    "label": "Expected keyword match",
                    "value": f"{latest_eval.get('expected_keyword_match_rate', 0):.2f}",
                    "trend": "local run",
                },
            ],
            "failedQuestions": [
                {
                    "question": "Evaluation run required",
                    "issue": "Run /api/evaluation/run after indexing documents to populate failed cases.",
                    "severity": "Medium",
                }
            ],
            "suggestions": [
                "Tune keyword/vector weighting after reviewing Recall@5.",
                "Add missing SupportFlow runbooks when failed questions lack sources.",
                "Adjust abstention threshold for low-confidence answers.",
            ],
        },
        "logs": [
            {
                "id": f"log-{log['id']}",
                "time": log["created_at"],
                "provider": log["provider"],
                "method": "hybrid search",
                "responseTime": "logged locally",
                "status": "Abstained" if log["abstained"] else "Complete",
                "citations": len(log["citations"]),
                "warning": "Low confidence" if log["abstained"] else "None",
            }
            for log in logs
        ],
    }
