# backend/services/knowledge_base/kb_retrieval.py
from typing import List, Tuple
from sqlalchemy.orm import Session
 
from models import KnowledgeBaseEmbedding
from services.embedding_service import get_embedding
from services.admin_knowledgeBase.kb_faiss_index import KBVectorIndex
from services.admin_knowledgeBase.kb_reranker import rerank
 
 
class KBRetriever:
    """
    Handles:
    - Query embedding
    - ANN search
    - Metadata filtering
    - Reranking
    """
 
    _vector_index: KBVectorIndex | None = None
 
    @classmethod
    def rebuild_index(cls, db: Session):
        cls._vector_index = KBVectorIndex()
        cls._vector_index.build(db)
 
    @classmethod
    def _get_index(cls, db: Session) -> KBVectorIndex:

        if cls._vector_index is None:
            print("DEBUG: Building new KB index")
            cls.rebuild_index(db)

        if cls._vector_index.index is None:
            print("DEBUG: Index empty, rebuilding")
            cls.rebuild_index(db)

        return cls._vector_index
 
    @classmethod
    def retrieve(
        cls,
        *,
        db: Session,
        query: str,
        limit: int = 5,
        document_types: List[str] | None = None,
        industry: str | None = None,
        language: str = "en",
    ) -> List[KnowledgeBaseEmbedding]:
 
        # 1️⃣ Embed query
        query_embedding = get_embedding(query)
 
        # 2️⃣ ANN search (top 20)
        index = cls._get_index(db)
 
        candidates: List[Tuple[KnowledgeBaseEmbedding, float]] = (
            index.search(query_embedding, top_k=20)
        )
 
        if not candidates:
            return []
 
        # 3️⃣ Metadata filtering
        filtered = []
        for record, score in candidates:
 
            if record.language != language:
                continue
 
            if document_types and record.document_type not in document_types:
                continue
 
            if industry and record.industry != industry:
                continue
 
            filtered.append((record, score))
 
        if not filtered:
            return []
 
        # 4️⃣ Rerank
        top_records = rerank(
            query=query,
            candidates=filtered,
            top_k=limit,
        )
 
        return top_records

    