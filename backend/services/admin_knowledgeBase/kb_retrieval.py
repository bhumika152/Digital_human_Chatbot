
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
    - FAISS ANN search
    - DB record fetch
    - Safe metadata filtering
    - Cross-encoder reranking
    """

    _vector_index: KBVectorIndex | None = None

    # --------------------------------------------------
    # BUILD INDEX
    # --------------------------------------------------
    @classmethod
    def rebuild_index(cls, db: Session):
        cls._vector_index = KBVectorIndex()
        cls._vector_index.build(db)

    @classmethod
    def _get_index(cls, db: Session) -> KBVectorIndex:
        if cls._vector_index is None:
            cls.rebuild_index(db)
        return cls._vector_index

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
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

        if not query:
            return []

        # 1️⃣ Embed query
        query_embedding = get_embedding(query)

        # 2️⃣ FAISS search (top 20 before rerank)
        index = cls._get_index(db)

        if index.index.ntotal == 0:
            print("⚠️ KB FAISS index is empty")
            return []

        candidates = index.search(query_embedding, top_k=20)

        if not candidates:
            return []

        # 3️⃣ Fetch records from DB using IDs
        records: List[Tuple[KnowledgeBaseEmbedding, float]] = []

        for kb_id, score in candidates:
            if kb_id == -1:
                continue

            record = db.get(KnowledgeBaseEmbedding, int(kb_id))
            if record:
                records.append((record, float(score)))

        if not records:
            return []

        # 4️⃣ Safe metadata filtering
        filtered: List[Tuple[KnowledgeBaseEmbedding, float]] = []

        for record, score in records:

            # Language filter (case-insensitive)
            if language and record.language:
                if record.language.lower() != language.lower():
                    continue

            # Document type filter (case-insensitive)
            if document_types:
                if not record.document_type:
                    continue
                if record.document_type.lower() not in [
                    dt.lower() for dt in document_types
                ]:
                    continue

            # Industry filter (allow NULL in DB)
            if industry:
                if record.industry and record.industry.lower() != industry.lower():
                    continue

            filtered.append((record, score))

        if not filtered:
            return []

        # 5️⃣ Cross-encoder reranking
        top_records = rerank(
            query=query,
            candidates=filtered,
            top_k=limit,
        )

        return top_records
