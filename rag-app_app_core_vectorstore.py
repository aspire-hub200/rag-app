from app.config import settings
from typing import List, Dict
import os

PROVIDER = os.getenv("VECTOR_PROVIDER", "CHROMA").upper()

if PROVIDER == "CHROMA":
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    client = chromadb.Client(ChromaSettings(chroma_db_impl="duckdb+parquet",
                                            persist_directory=settings.chroma_dir))
    COLLECTION_NAME = "rag_doc_chunks"

    def ensure_collection():
        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME in existing:
            return client.get_collection(COLLECTION_NAME)
        return client.create_collection(COLLECTION_NAME)

    def add_documents(doc_id: int, chunks: List[Dict]):
        col = ensure_collection()
        ids = [c["id"] for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]
        documents = [c["text"] for c in chunks]
        embeddings = [c["embedding"] for c in chunks]
        col.add(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
        client.persist()

    def query(query_embedding, top_k=5):
        col = ensure_collection()
        results = col.query(query_embeddings=[query_embedding], n_results=top_k)
        return results

elif PROVIDER == "PINECONE":
    import pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENV")
    INDEX_NAME = os.getenv("PINECONE_INDEX") or "rag-index"

    if not PINECONE_API_KEY or not PINECONE_ENV:
        raise RuntimeError("Pinecone selected but PINECONE_API_KEY / PINECONE_ENV not set")

    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    if INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(INDEX_NAME, dimension=1536)
    index = pinecone.Index(INDEX_NAME)

    def add_documents(doc_id: int, chunks: List[Dict]):
        to_upsert = []
        for c in chunks:
            to_upsert.append((c["id"], c["embedding"], c.get("metadata", {})))
        index.upsert(vectors=to_upsert)

    def query(query_embedding, top_k=5):
        res = index.query(vector=query_embedding, top_k=top_k, include_metadata=True, include_values=False)
        ids = [m["id"] for m in res["matches"]]
        docs = [m["metadata"].get("text", "") for m in res["matches"]]
        metadatas = [m["metadata"] for m in res["matches"]]
        return {"ids": [ids], "documents": [docs], "metadatas": [metadatas]}

elif PROVIDER == "WEAVIATE":
    import weaviate
    WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
    INDEX_NAME = os.getenv("WEAVIATE_INDEX") or "rag_chunk"

    if not WEAVIATE_URL:
        raise RuntimeError("Weaviate selected but WEAVIATE_URL not set")

    auth = None
    client = None
    if WEAVIATE_API_KEY:
        from weaviate.auth import AuthApiKey
        auth = AuthApiKey(api_key=WEAVIATE_API_KEY)
        client = weaviate.Client(url=WEAVIATE_URL, auth_client_secret=auth)
    else:
        client = weaviate.Client(url=WEAVIATE_URL)

    def ensure_class():
        schema = client.schema.get()
        classes = [c["class"] for c in schema.get("classes", [])]
        if INDEX_NAME not in classes:
            class_obj = {
                "class": INDEX_NAME,
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "doc_id", "dataType": ["int"]},
                    {"name": "chunk_index", "dataType": ["int"]},
                    {"name": "filename", "dataType": ["text"]}
                ],
                "vectorizer": "none"
            }
            client.schema.create_class(class_obj)

    ensure_class()

    def add_documents(doc_id: int, chunks: List[Dict]):
        with client.batch as batch:
            batch.batch_size = 50
            for c in chunks:
                meta = c.get("metadata", {})
                properties = {
                    "text": c["text"],
                    "doc_id": meta.get("doc_id"),
                    "chunk_index": meta.get("chunk_index"),
                    "filename": meta.get("filename")
                }
                batch.add_data_object(properties, INDEX_NAME, uuid=c["id"], vector=c["embedding"])

    def query(query_embedding, top_k=5):
        near_vector = {"vector": query_embedding}
        res = client.query.get(INDEX_NAME, ["text", "doc_id", "chunk_index", "filename"]).with_near_vector(near_vector).with_limit(top_k).do()
        matches = res.get("data", {}).get("Get", {}).get(INDEX_NAME, [])
        ids = []
        docs = []
        metadatas = []
        for m in matches:
            ids.append(m.get("_additional", {}).get("id"))
            docs.append(m.get("text"))
            meta = {
                "doc_id": m.get("doc_id"),
                "chunk_index": m.get("chunk_index"),
                "filename": m.get("filename")
            }
            metadatas.append(meta)
        return {"ids": [ids], "documents": [docs], "metadatas": [metadatas]}

else:
    raise RuntimeError(f"Unsupported VECTOR_PROVIDER: {PROVIDER}")
