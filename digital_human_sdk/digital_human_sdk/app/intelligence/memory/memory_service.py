import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


class MemoryService:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL is not set")

        self.conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )

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
            expires_at = datetime.utcnow()

        query = """
        INSERT INTO memory_store (
            user_id,
            memory_type,
            memory_content,
            confidence_score,
            expires_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    user_id,
                    memory_type,
                    content,
                    confidence,
                    expires_at,
                )
            )
            self.conn.commit()

    # -----------------------------
    # FETCH MEMORY
    # -----------------------------
    def fetch_memory(
        self,
        user_id: int,
        memory_type: str,
        limit: int = 5,
    ):
        query = """
        SELECT memory_content, confidence_score
        FROM memory_store
        WHERE user_id = %s
          AND memory_type = %s
          AND is_active = TRUE
          AND (expires_at IS NULL OR expires_at > now())
        ORDER BY created_at DESC
        LIMIT %s
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (user_id, memory_type, limit))
            rows = cur.fetchall()

        return rows
