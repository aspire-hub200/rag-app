from pydantic import BaseModel
from typing import Optional, List

class UploadResponse(BaseModel):
    document_id: int
    filename: str
    pages: int

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
