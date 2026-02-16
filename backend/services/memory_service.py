# from datetime import datetime, timedelta, timezone
# from typing import Optional, List, Tuple
 
# from sqlalchemy.orm import Session
# from sqlalchemy import or_
 
# from models import MemoryStore, SessionSummary
# from auth import get_db
# from services.embedding_service import get_embedding
# from services.semantic_memory import find_best_semantic_match
# # =====================================================
# # MEMORY SERVICE (ORCHESTRATOR NEVER TOUCHES DB)
# # =====================================================
# class MemoryService:
 
#     @staticmethod
#     def read(
#         *,
#         user_id: int,
#         query: str,
#         limit: int = 3,
#     ) -> List[dict]:
#         """
#         Semantic memory read.
#         Returns JSON-serializable dicts (NOT ORM objects).
#         """
#         if not query:
#             return []
 
#         db = next(get_db())
#         try:
#             query_embedding = get_embedding(query)
#             now = datetime.now(timezone.utc)
 
#             memories: List[MemoryStore] = (
#                 db.query(MemoryStore)
#                 .filter(
#                     MemoryStore.user_id == user_id,
#                     MemoryStore.is_active.is_(True),
#                     or_(
#                         MemoryStore.expires_at.is_(None),
#                         MemoryStore.expires_at > now,
#                     ),
#                 )
#                 .all()
#             )
 
#             scored: List[Tuple[float, MemoryStore]] = []
 
#             for mem in memories:
#                 _, score = find_best_semantic_match([mem], query_embedding)
#                 if score is not None:
#                     scored.append((score, mem))
 
#             scored.sort(key=lambda x: x[0], reverse=True)
 
#             result: List[dict] = []
#             for score, mem in scored[:limit]:
#                 d = memory_to_dict(mem)
#                 d["score"] = score
#                 result.append(d)
 
#             return result
 
#         finally:
#             db.close()
 
 
# # =====================================================
# # ORM → DICT (JSON SAFE)
# # =====================================================
# def memory_to_dict(mem: MemoryStore) -> dict:
#     return {
#         "memory_id": mem.memory_id,
#         "user_id": mem.user_id,
 
#         # 👇 THIS is what LLM actually needs
#         "text": mem.memory_content,
 
#         "confidence": mem.confidence_score,
 
#         "created_at": (
#             mem.created_at.isoformat()
#             if mem.created_at
#             else None
#         ),
 
#         "expires_at": (
#             mem.expires_at.isoformat()
#             if mem.expires_at
#             else None
#         ),
#     }
 
 
 
# # =====================================================
# # MEMORY WRITE / UPDATE (CALLED BY EVENT CONSUMER)
# # =====================================================
# def write_or_update_memory(
#     *,
#     db: Session,
#     user_id: int,
#     memory_text: str,
#     confidence_score: Optional[float] = None,
#     ttl_days: int = 30,
# ) -> Optional[MemoryStore]:
#     """
#     Writes new memory OR updates best semantic match.
#     """
#     if not db or not memory_text:
#         return None
 
#     embedding = get_embedding(memory_text)
#     expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)
 
#     existing_memories = (
#         db.query(MemoryStore)
#         .filter(
#             MemoryStore.user_id == user_id,
#             MemoryStore.is_active.is_(True),
#         )
#         .all()
#     )
 
#     match, score = find_best_semantic_match(existing_memories, embedding)
 
#     if match:
#         match.memory_content = memory_text
#         match.embedding = embedding
#         match.confidence_score = confidence_score
#         match.expires_at = expires_at
#         return match
 
#     memory = MemoryStore(
#         user_id=user_id,
#         memory_content=memory_text,
#         embedding=embedding,
#         confidence_score=confidence_score,
#         expires_at=expires_at,
#         is_active=True,
#     )
 
#     db.add(memory)
#     return memory
 
 
# # =====================================================
# # MEMORY DELETE (SOFT DELETE)
# # =====================================================
# def delete_semantic_memory(
#     *,
#     db: Session,
#     user_id: int,
#     query: str,
# ) -> bool:
#     if not db or not query:
#         return False
 
#     query_embedding = get_embedding(query)
 
#     memories = (
#         db.query(MemoryStore)
#         .filter(
#             MemoryStore.user_id == user_id,
#             MemoryStore.is_active.is_(True),
#         )
#         .all()
#     )
 
#     match, _ = find_best_semantic_match(memories, query_embedding)
 
#     if match:
#         match.is_active = False
#         return True
 
#     return False
 
# # -------------------------
# # READ
# # -------------------------
# def get_active_memories(db: Session, user_id: int):
#     now = datetime.now(timezone.utc)
 
#     return (
#         db.query(MemoryStore)
#         .filter(
#             MemoryStore.user_id == user_id,
#             MemoryStore.is_active == True,
#             or_(
#                 MemoryStore.expires_at.is_(None),
#                 MemoryStore.expires_at > now
#             )
#         )
#         .order_by(MemoryStore.created_at.asc())
#         .all()
#     )
 
 
# # -------------------------
# # AUTO CLEANUP
# # -------------------------
# def cleanup_expired_memories(db: Session):
#     now = datetime.now(timezone.utc)
 
#     expired = (
#         db.query(MemoryStore)
#         .filter(
#             MemoryStore.is_active == True,
#             MemoryStore.expires_at.isnot(None),
#             MemoryStore.expires_at <= now
#         )
#         .update(
#             {"is_active": False},
#             synchronize_session=False
#         )
#     )
 
#     db.commit()
#     return expired
 
 
 
 
# def get_conversation_summary(db, session_id):
#     summary_row = (
#         db.query(SessionSummary)
#         .filter(
#             SessionSummary.session_id == session_id,
#             SessionSummary.is_active.is_(True),
#         )
#         .first()
#     )
 
#     return summary_row.summary_text if summary_row else None
 
 # services/memory_service.py

from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import MemoryStore, SessionSummary
from auth import get_db
from services.embedding_service import get_embedding
from services.memory_index_manager import memory_index_manager


# =====================================================
# MEMORY SERVICE (ORCHESTRATOR NEVER TOUCHES DB)
# =====================================================
class MemoryService:

    # =====================================================
    # READ (SEMANTIC SEARCH USING PER-USER FAISS)
    # =====================================================
    @staticmethod
    def read(
        *,
        user_id: int,
        query: str,
        limit: int = 3,
    ) -> List[dict]:

        if not query:
            return []

        db = next(get_db())

        try:
            query_embedding = get_embedding(query)

            # 🔥 FAISS Search (per user)
            results = memory_index_manager.search(
                user_id=user_id,
                query_embedding=query_embedding,
                top_k=limit,
            )

            if not results:
                return []

            memory_ids = [mid for mid, _ in results]

            memories = (
                db.query(MemoryStore)
                .filter(
                    MemoryStore.memory_id.in_(memory_ids),
                    MemoryStore.user_id == user_id,
                    MemoryStore.is_active.is_(True),
                )
                .all()
            )

            id_to_score = dict(results)

            final = []
            for mem in memories:
                d = memory_to_dict(mem)
                d["score"] = id_to_score.get(mem.memory_id)
                final.append(d)

            return sorted(final, key=lambda x: x["score"], reverse=True)

        finally:
            db.close()


# =====================================================
# WRITE OR UPDATE MEMORY
# =====================================================
def write_or_update_memory(
    *,
    db: Session,
    user_id: int,
    memory_text: str,
    confidence_score: Optional[float] = None,
    ttl_days: int = 30,
) -> Optional[MemoryStore]:

    if not memory_text:
        return None

    embedding = get_embedding(memory_text)
    expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)

    # -------------------------------------
    # First try semantic match via FAISS
    # -------------------------------------
    results = memory_index_manager.search(
        user_id=user_id,
        query_embedding=embedding,
        top_k=1,
    )

    if results:
        memory_id, score = results[0]

        existing = (
            db.query(MemoryStore)
            .filter(
                MemoryStore.memory_id == memory_id,
                MemoryStore.user_id == user_id,
                MemoryStore.is_active.is_(True),
            )
            .first()
        )

        if existing:
            # 🔁 Update existing
            existing.memory_content = memory_text
            existing.embedding = embedding
            existing.confidence_score = confidence_score
            existing.expires_at = expires_at

            # Update FAISS
            memory_index_manager.remove(user_id, memory_id)
            memory_index_manager.add(user_id, memory_id, embedding)

            return existing

    # -------------------------------------
    # Create new memory
    # -------------------------------------
    memory = MemoryStore(
        user_id=user_id,
        memory_content=memory_text,
        embedding=embedding,
        confidence_score=confidence_score,
        expires_at=expires_at,
        is_active=True,
    )

    db.add(memory)
    db.flush()  # get memory_id before commit

    # Add to FAISS
    memory_index_manager.add(
        user_id=user_id,
        memory_id=memory.memory_id,
        embedding=embedding,
    )

    return memory


# =====================================================
# DELETE MEMORY (SOFT DELETE)
# =====================================================
def delete_semantic_memory(
    *,
    db: Session,
    user_id: int,
    query: str,
) -> bool:

    if not query:
        return False

    query_embedding = get_embedding(query)

    results = memory_index_manager.search(
        user_id=user_id,
        query_embedding=query_embedding,
        top_k=1,
    )

    if not results:
        return False

    memory_id, _ = results[0]

    memory = (
        db.query(MemoryStore)
        .filter(
            MemoryStore.memory_id == memory_id,
            MemoryStore.user_id == user_id,
            MemoryStore.is_active.is_(True),
        )
        .first()
    )

    if memory:
        memory.is_active = False

        # Remove from FAISS
        memory_index_manager.remove(user_id, memory_id)

        return True

    return False


# =====================================================
# ORM → DICT (JSON SAFE)
# =====================================================
def memory_to_dict(mem: MemoryStore) -> dict:
    return {
        "memory_id": mem.memory_id,
        "user_id": mem.user_id,
        "text": mem.memory_content,
        "confidence": mem.confidence_score,
        "created_at": mem.created_at.isoformat() if mem.created_at else None,
        "expires_at": mem.expires_at.isoformat() if mem.expires_at else None,
    }


# =====================================================
# GET ACTIVE MEMORIES
# =====================================================
def get_active_memories(db: Session, user_id: int):
    now = datetime.now(timezone.utc)

    return (
        db.query(MemoryStore)
        .filter(
            MemoryStore.user_id == user_id,
            MemoryStore.is_active == True,
            or_(
                MemoryStore.expires_at.is_(None),
                MemoryStore.expires_at > now
            )
        )
        .order_by(MemoryStore.created_at.asc())
        .all()
    )


# =====================================================
# AUTO CLEANUP
# =====================================================
def cleanup_expired_memories(db: Session):
    now = datetime.now(timezone.utc)

    expired = (
        db.query(MemoryStore)
        .filter(
            MemoryStore.is_active == True,
            MemoryStore.expires_at.isnot(None),
            MemoryStore.expires_at <= now
        )
        .update(
            {"is_active": False},
            synchronize_session=False
        )
    )

    db.commit()
    return expired


# =====================================================
# SESSION SUMMARY
# =====================================================
def get_conversation_summary(db, session_id):
    summary_row = (
        db.query(SessionSummary)
        .filter(
            SessionSummary.session_id == session_id,
            SessionSummary.is_active.is_(True),
        )
        .first()
    )

    return summary_row.summary_text if summary_row else None
