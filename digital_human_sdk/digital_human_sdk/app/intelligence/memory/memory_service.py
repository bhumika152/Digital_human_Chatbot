# import psycopg2
# from psycopg2.extras import RealDictCursor
# from datetime import datetime, timedelta
# from typing import List, Optional
# import os


# class MemoryService:
#     def __init__(self):
#         self.conn = psycopg2.connect(
#             host=os.getenv("POSTGRES_HOST"),
#             port=os.getenv("POSTGRES_PORT"),
#             dbname=os.getenv("POSTGRES_DB"),
#             user=os.getenv("POSTGRES_USER"),
#             password=os.getenv("POSTGRES_PASSWORD"),
#         )

#     # -------------------------
#     # STORE MEMORY
#     # -------------------------
#     def store_memory(
#         self,
#         user_id: int,
#         memory_type: str,
#         content: str,
#         confidence: float,
#     ):
#         expires_at = None

#         # Short-term memory expires (example: 2 hours)
#         if memory_type == "short_term":
#             expires_at = datetime.utcnow() + timedelta(hours=2)

#         with self.conn.cursor() as cur:
#             cur.execute(
#                 """
#                 INSERT INTO memory_store
#                 (user_id, memory_type, memory_content, confidence_score, expires_at)
#                 VALUES (%s, %s, %s, %s, %s)
#                 """,
#                 (user_id, memory_type, content, confidence, expires_at),
#             )
#             self.conn.commit()

#     # -------------------------
#     # FETCH MEMORY
#     # -------------------------
#     def fetch_memory(
#         self,
#         user_id: int,
#         memory_type: str,
#         limit: int = 5,
#     ) -> List[dict]:
#         with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
#             cur.execute(
#                 """
#                 SELECT memory_content, confidence_score, created_at
#                 FROM memory_store
#                 WHERE user_id = %s
#                   AND memory_type = %s
#                   AND is_active = TRUE
#                   AND (expires_at IS NULL OR expires_at > now())
#                 ORDER BY confidence_score DESC NULLS LAST, created_at DESC
#                 LIMIT %s
#                 """,
#                 (user_id, memory_type, limit),
#             )
#             return cur.fetchall()


import os

from datetime import datetime

from typing import Optional, List, Dict
 
import psycopg2

from psycopg2.extras import RealDictCursor
 
 
class MemoryService:

    def __init__(self):

        database_url = os.getenv("DATABASE_URL")

        if not database_url:

            raise RuntimeError("DATABASE_URL is not set")
 
        self.conn = psycopg2.connect(

            database_url,

            cursor_factory=RealDictCursor,

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

        ttl_minutes: Optional[int] = None,

    ) -> None:

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

                ),

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

    ) -> List[Dict]:

        query = """

            SELECT

                memory_content,

                confidence_score

            FROM memory_store

            WHERE user_id = %s

              AND memory_type = %s

              AND is_active = TRUE

              AND (expires_at IS NULL OR expires_at > NOW())

            ORDER BY created_at DESC

            LIMIT %s

        """
 
        with self.conn.cursor() as cur:

            cur.execute(query, (user_id, memory_type, limit))

            rows = cur.fetchall()
 
        return rows

 