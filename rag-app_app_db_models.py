from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filesize = Column(Integer)
    pages = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    description = Column(Text, nullable=True)

class ChunkMeta(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, index=True)
    chunk_id = Column(String, index=True)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
