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
    return memory

#----------------------
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
            MemoryStore.is_active == True,
        )
        .first()
    )

    if not memory:
        return None

    memory.memory_content = new_value
    memory.confidence_score = confidence_score
    memory.updated_at = datetime.now(timezone.utc)
    return memory



def fetch_memory(
    db: Session,
    user_id: int,
    memory_type: str,
    limit: int = 5,
):
    now = datetime.now(timezone.utc)

    return (
        db.query(MemoryStore)
        .filter(
            MemoryStore.user_id == user_id,
            MemoryStore.memory_type == memory_type,
            MemoryStore.is_active == True,
            or_(
                MemoryStore.expires_at.is_(None),
                MemoryStore.expires_at > now,
            ),
        )
        .order_by(MemoryStore.created_at.desc())
        .limit(limit)
        .all()
    )

# -------------------------
# SOFT DELETE (user says "forget")
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

    if memory_type:
        query = query.filter(MemoryStore.memory_type == memory_type)

    query.update(
        {"is_active": False},
        synchronize_session=False
    )



# -------------------------
# READ (only active + not expired)
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
# AUTO CLEANUP (optional cron / background task)
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
