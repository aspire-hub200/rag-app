import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def fake_embedding(text):
    return [0.01] * 8

def fake_llm(system_prompt, user_prompt, model=None, max_tokens=512):
    return "TEST ANSWER: use documents as source."

@pytest.fixture(autouse=True)
def patch_embeddings_and_llm(monkeypatch):
    monkeypatch.setattr("app.core.embeddings.get_embedding", fake_embedding)
    monkeypatch.setattr("app.core.llm_client.call_llm", fake_llm)
    yield

def test_upload_txt():
    data = {"file": ("test.txt", io.BytesIO(b"hello world " * 2000), "text/plain")}
    r = client.post("/api/upload", files=data)
    assert r.status_code == 201
    j = r.json()
    assert "document_id" in j
