from fastapi.testclient import TestClient

from app.main import app


def test_answer_flow_uses_mock_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = TestClient(app)

    created = client.post(
        "/api/documents",
        json={
            "title": "Refund policy",
            "text": "Refunds are available within 30 days for paid accounts.",
        },
    )
    assert created.status_code == 200

    response = client.post("/api/ask", json={"question": "When are refunds available?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "mock"
    assert payload["abstained"] is False
    assert "Refunds are available within 30 days" in payload["answer"]
    assert len(payload["citations"]) == 1


def test_answer_abstains_without_documents(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    client = TestClient(app)

    response = client.post("/api/ask", json={"question": "What is the SLA?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["abstained"] is True
    assert payload["citations"] == []
