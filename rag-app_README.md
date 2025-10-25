# RAG App — Upload documents & ask questions (FastAPI + Chroma + OpenAI)

Overview:
This repository implements a Retrieval-Augmented Generation (RAG) pipeline:
- Upload documents (PDF / DOCX / TXT)
- Chunk & embed text
- Store embeddings in Chroma (local vector store)
- Retrieve top-k chunks for queries
- Call LLM (OpenAI or any REST model) to generate answers using the retrieved context

Quickstart:
1. Copy `.env.example` -> `.env` and set keys.
2. Run: `docker compose up --build`
3. API:
  - POST /api/upload (multipart form file)
  - POST /api/query (JSON {"query":"...","top_k":5})

See `.env.example` for configuration.
