# backend/services/knowledge_base/kb_ingestion.py

import uuid
from pathlib import Path
from typing import List
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from models import KnowledgeBaseEmbedding
from services.admin_knowledgeBase.kb_embedding_service import get_kb_embedding


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    pages = [page.extract_text() for page in reader.pages]
    return "\n".join(filter(None, pages))


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks


def ingest_policy_pdf(
    db: Session,
    file_path: Path,
    document_type: str,
    industry: str | None = None,
    language: str = "en",
):
    """
    Ingests a policy/FAQ PDF into knowledge_base_embeddings
    """

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    document_id = uuid.uuid4()
    title = file_path.stem.replace("_", " ").title()

    for chunk in chunks:
        embedding = get_kb_embedding(chunk)

        kb_row = KnowledgeBaseEmbedding(
            document_id=document_id,
            document_title=title,
            document_type=document_type,
            industry=industry,
            language=language,
            content=chunk,
            embedding=embedding,
        )

        db.add(kb_row)

    db.commit()
