from fastapi.testclient import TestClient

from app.main import app
from app.rag.search import InMemoryHybridIndex, SearchDocument


def test_register_and_search_document(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    client = TestClient(app)

    created = client.post(
        "/api/documents",
        json={
            "title": "Escalation guide",
            "text": "Priority support tickets should be escalated to tier two within one hour.",
            "metadata": {"team": "support"},
        },
    )
    assert created.status_code == 200
    document = created.json()
    assert document["metadata"]["team"] == "support"

    listed = client.get("/api/documents")
    assert listed.status_code == 200
    assert listed.json()["documents"][0]["id"] == document["id"]

    searched = client.post("/api/documents/search", json={"query": "tier two escalation", "k": 3})
    assert searched.status_code == 200
    results = searched.json()["results"]
    assert results
    assert results[0]["document_id"] == document["id"]


def test_identifier_query_prioritizes_exact_code_match():
    index = InMemoryHybridIndex(
        [
            SearchDocument(
                id="faq",
                title="Import Export FAQ",
                text="Answer: Markdown, plain text, CSV, JSON, PDF, and DOCX are accepted.",
                metadata={},
            ),
            SearchDocument(
                id="errors",
                title="Errors Reference",
                text=(
                    "AUTH_401 means the API key is missing, expired, or invalid. "
                    "Ask the customer admin to verify or rotate the API key."
                ),
                metadata={},
            ),
        ]
    )

    results = index.search(
        "AUTH_401 token expired errors should be handled how? Answer in Japanese.",
        k=2,
    )

    assert results[0].document.id == "errors"
