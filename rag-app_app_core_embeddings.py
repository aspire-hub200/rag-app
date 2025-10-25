from app.config import settings
import openai

openai.api_key = settings.openai_api_key

def get_embedding(text: str) -> list:
    resp = openai.Embedding.create(model=settings.embedding_model, input=text)
    return resp["data"][0]["embedding"]
