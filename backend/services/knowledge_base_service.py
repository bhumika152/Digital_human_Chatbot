from typing import List, Optional
from sqlalchemy.orm import Session

from models import KnowledgeBaseEmbedding
from auth import get_db
from services.admin_knowledgeBase.kb_retrieval import KBRetriever

class KnowledgeBaseService:
    """
    Orchestrates KB retrieval.
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

        if not query:
            return []

        db = next(get_db())

        try:
            records = KBRetriever.retrieve(
                db=db,
                query=query,
                limit=limit,
                document_types=document_types,
                industry=industry,
                language=language,
            )

            return [kb_to_dict(r) for r in records]

        finally:
            db.close()


def kb_to_dict(kb: KnowledgeBaseEmbedding) -> dict:
    return {
        "kb_id": kb.kb_id,
        "document_id": str(kb.document_id),
        "title": kb.document_title,
        "type": kb.document_type,
        "industry": kb.industry,
        "language": kb.language,
        "version": kb.version,
        "content": kb.content,
        "created_at": kb.created_at.isoformat()
        if kb.created_at
        else None,
        "updated_at": kb.updated_at.isoformat()
        if kb.updated_at
        else None,
    }