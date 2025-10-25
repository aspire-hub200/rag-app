from fastapi import APIRouter
from app.schemas import QueryRequest, QueryResponse
from app.core.embeddings import get_embedding
from app.core.vectorstore import query as vs_query
from app.core.llm_client import call_llm

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_system(req: QueryRequest):
    q_emb = get_embedding(req.query)
    results = vs_query(q_emb, top_k=req.top_k or 5)
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    context_parts = []
    sources = []
    for i, d in enumerate(docs):
        src_meta = metadatas[i] if metadatas else {}
        sources.append(f"{src_meta.get('filename','unknown')}#chunk:{ids[i]}")
        context_parts.append(f"Source ({i+1}):\n{d}")

    context = "\n\n".join(context_parts)

    system_prompt = "You are an assistant that answers user queries using the provided context. Answer concisely and cite sources."
    user_prompt = f"Context:\n{context}\n\nQuestion: {req.query}\n\nProvide a concise answer and list the sources."

    answer = call_llm(system_prompt, user_prompt)
    return {"answer": answer, "sources": sources}
