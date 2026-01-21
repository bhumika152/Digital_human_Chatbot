from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import MemoryStore
from datetime import datetime, timedelta, timezone

def write_memory(
    db: Session,
    user_id: int,
    memory_type: str,
    memory_content: str,
    confidence_score: float | None = None,
    ttl_days: int = 30  
):
    expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)

    memory = MemoryStore(
        user_id=user_id,
        memory_type=memory_type,
        memory_content=memory_content,
        confidence_score=confidence_score,
        is_active=True,
        expires_at=expires_at
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory

# -------------------------
# UPDATE (only active memory)
# -------------------------
def update_memory(
    db: Session,
    user_id: int,
    memory_type: str,
    new_value: str,
    confidence_score: float | None = None
):
    memory = (
        db.query(MemoryStore)
        .filter(
            MemoryStore.user_id == user_id,
            MemoryStore.memory_type == memory_type,
            MemoryStore.is_active == True
        )
        .first()
    )

    if memory:
        memory.memory_content = new_value
        memory.confidence_score = confidence_score
        db.commit()
        db.refresh(memory)

    return memory


    # -----------------------------
    # FETCH MEMORY
    # -----------------------------
def fetch_memory(
    self,
    user_id: int,
    memory_type: str,
    limit: int = 5,
):
    return (
        self.db.query(MemoryStore)
        .filter(
            MemoryStore.user_id == user_id,
            MemoryStore.memory_type == memory_type,
            MemoryStore.is_active == True,
            or_(
                MemoryStore.expires_at.is_(None),
                MemoryStore.expires_at > datetime.now(timezone.utc),
            ),
        )
        .order_by(MemoryStore.created_at.desc())
        .limit(limit)
        .all()
    )

# -------------------------
# SOFT DELETE
# -------------------------
def soft_delete_memory(
    db: Session,
    user_id: int,
    memory_type: str | None = None
):
    query = db.query(MemoryStore).filter(
        MemoryStore.user_id == user_id,
        MemoryStore.is_active == True
    )

    # delete specific memory type OR all memories
    if memory_type:
        query = query.filter(MemoryStore.memory_type == memory_type)

    updated = query.update(
        {"is_active": False},
        synchronize_session=False
    )

    db.commit()
    return updated


# -------------------------
# READ 
# -------------------------
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


# -------------------------
# AUTO CLEANUP 
# -------------------------
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

def get_conversation_summary(db: Session, session_id):
    """
    Fetch rolling conversation summary for a session.
    Returns None if not present.
    """
    summary_row = (
        db.query(MemoryStore)
        .filter(
            MemoryStore.session_id == session_id,
            MemoryStore.memory_type == "conversation_summary",
            MemoryStore.is_active == True,
        )
        .first()
    )

    return summary_row.memory_content if summary_row else None