from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import MemoryStore


class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # STORE MEMORY
    # -----------------------------
    def store_memory(
        self,
        user_id: int,
        memory_type: str,
        content: str,
        confidence: float = 1.0,
        ttl_minutes: int | None = None,
    ):
        expires_at = None

        if memory_type == "short_term" and ttl_minutes:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)

        memory = MemoryStore(
            user_id=user_id,
            memory_type=memory_type,
            memory_content=content,
            confidence_score=confidence,
            expires_at=expires_at,
            is_active=True,
        )

        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

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

    # -----------------------------
    # UPDATE MEMORY
    # -----------------------------
    def update_memory(
        self,
        user_id: int,
        memory_type: str,
        new_value: str,
        confidence_score: float | None = None,
    ):
        memory = (
            self.db.query(MemoryStore)
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

        if confidence_score is not None:
            memory.confidence_score = confidence_score

        self.db.commit()
        self.db.refresh(memory)

        return memory

    # -----------------------------
    # SOFT DELETE (forget)
    # -----------------------------
    def soft_delete_memory(
        self,
        user_id: int,
        memory_type: str | None = None,
    ):
        query = self.db.query(MemoryStore).filter(
            MemoryStore.user_id == user_id,
            MemoryStore.is_active == True,
        )

        if memory_type:
            query = query.filter(MemoryStore.memory_type == memory_type)

        updated = query.update(
            {"is_active": False},
            synchronize_session=False,
        )

        self.db.commit()
        return updated

    # -----------------------------
    # READ ACTIVE MEMORIES
    # -----------------------------
    def get_active_memories(self, user_id: int):
        now = datetime.now(timezone.utc)

        return (
            self.db.query(MemoryStore)
            .filter(
                MemoryStore.user_id == user_id,
                MemoryStore.is_active == True,
                or_(
                    MemoryStore.expires_at.is_(None),
                    MemoryStore.expires_at > now,
                ),
            )
            .order_by(MemoryStore.created_at.asc())
            .all()
        )

    # -----------------------------
    # AUTO CLEANUP (cron / bg task)
    # -----------------------------
    def cleanup_expired_memories(self):
        now = datetime.now(timezone.utc)

        expired = (
            self.db.query(MemoryStore)
            .filter(
                MemoryStore.is_active == True,
                MemoryStore.expires_at.isnot(None),
                MemoryStore.expires_at <= now,
            )
            .update(
                {"is_active": False},
                synchronize_session=False,
            )
        )

        self.db.commit()
        return expired
