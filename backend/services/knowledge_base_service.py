from typing import List, Tuple, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_

from models import KnowledgeBaseEmbedding
from auth import get_db
from services.embedding_service import get_embedding
from services.admin_knowledgeBase.kb_semantic_search import semantic_search_kb


# =====================================================
# KNOWLEDGE BASE SERVICE (READ-ONLY, ADMIN DOCS)
# =====================================================
class KnowledgeBaseService:
    """
    Orchestrates semantic retrieval from admin knowledge base.
    This service NEVER mutates DB.
    """

    @staticmethod
    def read(
        *,
        query: str,
        limit: int = 5,
        document_types: Optional[List[str]] = None,
        industry: Optional[str] = None,
        language: str = "en",
    ) -> List[dict]:
        """
        Semantic KB read.
        Returns JSON-serializable dicts (NOT ORM objects).
        """

        if not query:
            return []

        db = next(get_db())
        try:
            query_embedding = get_embedding(query)

            q = db.query(KnowledgeBaseEmbedding).filter(
                KnowledgeBaseEmbedding.is_active.is_(True),
                KnowledgeBaseEmbedding.language == language,
            )

            if document_types:
                q = q.filter(
                    KnowledgeBaseEmbedding.document_type.in_(document_types)
                )

            if industry:
                q = q.filter(
                    KnowledgeBaseEmbedding.industry == industry
                )

            records: List[KnowledgeBaseEmbedding] = q.all()

            scored: List[
                Tuple[KnowledgeBaseEmbedding, float]
            ] = semantic_search_kb(
                records=records,
                query_embedding=query_embedding,
                top_k=limit,
            )

            result: List[dict] = []
            for record, score in scored:
                d = kb_to_dict(record)
                d["score"] = score
                result.append(d)

            return result

        finally:
            db.close()


# =====================================================
# ORM → DICT (JSON SAFE)
# =====================================================
def kb_to_dict(kb: KnowledgeBaseEmbedding) -> dict:
    return {
        "kb_id": kb.kb_id,

        # Document identity
        "document_id": str(kb.document_id),
        "title": kb.document_title,
        "type": kb.document_type,

        # Metadata
        "industry": kb.industry,
        "language": kb.language,
        "version": kb.version,

        # 👇 This is what LLM actually consumes
        "content": kb.content,

        "created_at": (
            kb.created_at.isoformat()
            if kb.created_at
            else None
        ),
        "updated_at": (
            kb.updated_at.isoformat()
            if kb.updated_at
            else None
        ),
    }
