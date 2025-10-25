from fastapi import FastAPI
from app.api import upload, query
from app.db.session import init_db
from app.config import settings

app = FastAPI(title="RAG Service")

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")

@app.on_event("startup")
def startup():
    init_db()
    from app.core.vectorstore import ensure_collection
    try:
        ensure_collection()
    except Exception:
        # if vector provider doesn't support ensure_collection, ignore on startup
        pass

@app.get("/")
def health():
    return {"status":"ok", "version":"0.1"}
