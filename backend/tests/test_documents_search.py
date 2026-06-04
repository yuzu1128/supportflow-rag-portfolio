from fastapi.testclient import TestClient

from app.main import app


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
