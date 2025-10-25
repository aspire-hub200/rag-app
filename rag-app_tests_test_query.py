import pytest
from fastapi.testclient import TestClient
from app.main import app
import io
import time

client = TestClient(app)

def fake_embedding(text):
    return [0.01] * 8

def fake_llm(system_prompt, user_prompt, model=None, max_tokens=512):
    return "TEST ANSWER: Paris."

@pytest.fixture(autouse=True)
def patch_all(monkeypatch):
    monkeypatch.setattr("app.core.embeddings.get_embedding", fake_embedding)
    monkeypatch.setattr("app.core.llm_client.call_llm", fake_llm)
    yield

def test_query_after_ingest():
    data = {"file": ("test.txt", io.BytesIO(b"The capital of France is Paris. " * 400), "text/plain")}
    r = client.post("/api/upload", files=data)
    assert r.status_code == 201
    time.sleep(0.5)
    q = {"query":"What is the capital of France?", "top_k":3}
    r2 = client.post("/api/query", json=q)
    assert r2.status_code == 200
    j = r2.json()
    assert "answer" in j
    assert "TEST ANSWER" in j["answer"] or "Paris" in j["answer"]
