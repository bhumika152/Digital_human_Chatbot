# backend/services/knowledge_base/kb_ingestion.py

import uuid
import logging
from pathlib import Path
from typing import List

from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from models import KnowledgeBaseEmbedding
from services.admin_knowledgeBase.kb_embedding_service import get_kb_embedding
from services.admin_knowledgeBase.kb_retrieval import KBRetriever
logger = logging.getLogger(__name__)


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------
def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    pages = [page.extract_text() for page in reader.pages]
    return "\n".join(filter(None, pages))


# --------------------------------------------------
# TEXT CHUNKING
# --------------------------------------------------
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[str]:
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = max(end - overlap, 0)

    return chunks


# --------------------------------------------------
# INGEST PDF INTO KNOWLEDGE BASE
# --------------------------------------------------
def ingest_policy_pdf(
    db: Session,
    file_path: Path,
    document_type: str,
    industry: str | None = None,
    language: str = "en",
    original_filename: str = None,
):
    """
    Ingests a policy / FAQ PDF into knowledge_base_embeddings
    with:
    - duplicate document protection
    - rich metadata (never NULL)
    """

    # title = file_path.stem.replace("_", " ").title()
    if original_filename:
        title = original_filename
    else:
        title = file_path.name


    # --------------------------------------------------
    # 1️⃣ DUPLICATE CHECK (IMPORTANT)
    # --------------------------------------------------
    existing_doc = (
        db.query(KnowledgeBaseEmbedding)
        .filter(
            KnowledgeBaseEmbedding.document_title == title,
            KnowledgeBaseEmbedding.document_type == document_type,
        )
        .first()
    )

    if existing_doc:
        logger.warning(
            "⚠️ Document already ingested. Skipping: %s", file_path.name
        )
        return

    logger.info("📥 Ingesting document: %s", file_path.name)

    # --------------------------------------------------
    # 2️⃣ TEXT EXTRACTION + CHUNKING
    # --------------------------------------------------
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        logger.warning("⚠️ Empty PDF content: %s", file_path.name)
        return

    chunks = chunk_text(text)
    total_chunks = len(chunks)

    document_id = uuid.uuid4()

    # --------------------------------------------------
    # 3️⃣ STORE CHUNKS + METADATA
    # --------------------------------------------------
    for idx, chunk in enumerate(chunks):
        embedding = get_kb_embedding(chunk)

        kb_row = KnowledgeBaseEmbedding(
            document_id=document_id,
            document_title=title,
            document_type=document_type,
            industry=industry,
            language=language,
            content=chunk,
            embedding=embedding,
            metadata={
                "file_name": file_path.name,
                "file_path": str(file_path),
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "language": language,
                "industry": industry,
            },
        )

        db.add(kb_row)

    db.commit()
    KBRetriever.rebuild_index(db)

    logger.info(
        "✅ Ingestion complete: %s | chunks=%d",
        file_path.name,
        total_chunks,
    )
