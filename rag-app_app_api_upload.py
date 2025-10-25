from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi import status
from sqlalchemy.orm import Session
from app.db import session as db_session
from app.db.models import Document, ChunkMeta
from app.utils.docs import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.utils.chunker import naive_split_text
from app.core.embeddings import get_embedding
from app.core.vectorstore import add_documents
from app.config import settings
import uuid

router = APIRouter()

def get_db():
    db = db_session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()

    if file.content_type == "application/pdf":
        text, pages = extract_text_from_pdf(content, max_pages=settings.max_pages_per_doc)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text, pages = extract_text_from_docx(content)
    else:
        text, pages = extract_text_from_txt(content)

    doc = Document(filename=file.filename, filesize=len(content), pages=pages)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunks_text = naive_split_text(text, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
    prepared = []
    for idx, ctext in enumerate(chunks_text):
        chunk_id = f"{doc.id}_{idx}_{uuid.uuid4().hex[:8]}"
        embedding = get_embedding(ctext)
        prepared.append({
            "id": chunk_id,
            "text": ctext,
            "embedding": embedding,
            "metadata": {"doc_id": doc.id, "chunk_index": idx, "filename": file.filename}
        })
        cm = ChunkMeta(doc_id=doc.id, chunk_id=chunk_id, text=ctext)
        db.add(cm)
    db.commit()

    add_documents(doc.id, prepared)

    return {"document_id": doc.id, "filename": doc.filename, "pages": doc.pages}
