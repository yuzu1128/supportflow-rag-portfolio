from fastapi.testclient import TestClient

from app.main import app
from app.rag.search import InMemoryHybridIndex, SearchDocument, chunk_count, chunk_text


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


def test_chunk_text_splits_long_documents_by_paragraph():
    text = "\n\n".join(
        [
            "First policy section explains routing ownership and default queues.",
            "Second policy section explains SLA breach escalation for VIP customers.",
            "Third policy section explains post-incident review ownership.",
        ]
    )

    chunks = chunk_text(text, chunk_size=90, overlap=20)

    assert len(chunks) == 3
    assert chunk_count(text) == 1


def test_search_returns_matching_chunk_metadata():
    long_intro = " ".join(
        [
            "General support queue ownership belongs to the operations lead.",
            "Default assignment rules are reviewed during weekly operations governance.",
        ]
        * 5
    )
    document = SearchDocument(
        id="policy",
        title="Support Policy",
        text="\n\n".join(
            [
                long_intro,
                "Webhook delivery incidents should be escalated when retry backoff is exhausted.",
                "Monthly reporting is reviewed by the customer success manager.",
            ]
        ),
        metadata={},
    )
    index = InMemoryHybridIndex([document])

    results = index.search("retry backoff exhausted webhook incident", k=1)

    assert results[0].document.id == "policy"
    assert results[0].chunk_id is not None
    assert results[0].chunk_index is not None
    assert results[0].chunk_index > 1
    assert "retry backoff" in results[0].snippet.lower()
