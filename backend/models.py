
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Float,
    Integer,
    BigInteger,
    ForeignKey,
    func,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base
import uuid
from sqlalchemy import Column, BigInteger, Text, Integer, Boolean, TIMESTAMP
from sqlalchemy.sql import func
 
# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"

    # BIGSERIAL handled by PostgreSQL sequence
    user_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False, index=True) 

     # (new fields)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    reset_token = Column(String, nullable=True, index=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    config = relationship("UserConfig", back_populates="user", uselist=False)
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete")
    memories = relationship("MemoryStore", back_populates="user", cascade="all, delete")
    vectors = relationship("VectorDBRAG", back_populates="user", cascade="all, delete")


# =========================
# USER CONFIG
# =========================
class UserConfig(Base):
    __tablename__ = "user_config"

    config_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True)
    enable_memory = Column(Boolean , default =True)
    enable_multichat = Column(Boolean, default=True)
    enable_chat_history = Column(Boolean, default=True)
    enable_rag = Column(Boolean, default=True)
    enable_tool = Column(Boolean, default=True)

    max_sessions = Column(Integer, default=5)
    max_tokens = Column(Integer, default=4096)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="config")


# =========================
# CHAT SESSIONS
# =========================
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)

    session_title = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")

# =========================
# CHAT MESSAGES
# =========================
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    role = Column(String, nullable=False)
    content = Column(Text)
    token_count = Column(Integer)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    session = relationship("ChatSession", back_populates="messages")

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="chat_message_role_check"
        ),
    )


# =========================
# MEMORY STORE
# =========================
class MemoryStore(Base):
    __tablename__ = "memory_store"

    memory_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # ✅ ADD THIS (CRITICAL)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        index=True,
        nullable=True   # nullable = allows user-level memory + session-level memory
    )
 

    memory_type = Column(String, nullable=False)
    memory_content = Column(Text, nullable=False)
    confidence_score = Column(Float)

    is_active = Column(Boolean, default=True, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User", back_populates="memories")

# =========================
# VECTOR DB RAG
# =========================
class VectorDBRAG(Base):
    __tablename__ = "vector_db_rag"

    document_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    embedding = Column(ARRAY(Float), nullable=False)

    meta_data = Column("metadata", JSONB)

    user = relationship("User", back_populates="vectors")

