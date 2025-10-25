import pdfplumber
from docx import Document as DocxDocument
import io

def extract_text_from_pdf(file_bytes: bytes, max_pages: int = 1000) -> str:
    text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = min(len(pdf.pages), max_pages)
        for i in range(pages):
            page = pdf.pages[i]
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text), pages

def extract_text_from_docx(file_bytes: bytes, max_pages: int = 1000) -> str:
    f = io.BytesIO(file_bytes)
    doc = DocxDocument(f)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs), 1

def extract_text_from_txt(file_bytes: bytes, max_pages: int = 1000) -> str:
    return file_bytes.decode("utf-8", errors="ignore"), 1
