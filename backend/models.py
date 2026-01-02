# from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, ForeignKey, func
# from sqlalchemy.dialects.postgresql import UUID
# from database import Base
# import uuid


# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     email = Column(String, unique=True, index=True, nullable=False)
#     password_hash = Column(String, nullable=False)
#     is_active = Column(Boolean, default=True, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())


# class ChatSession(Base):
#     __tablename__ = "chat_sessions"
#     session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, server_default=func.now())


# class ChatMessage(Base):
#     __tablename__ = "chat_messages"
#     message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id"))
#     role = Column(String)
#     content = Column(Text)
#     created_at = Column(DateTime, server_default=func.now())


# class MemoryStore(Base):
#     __tablename__ = "memory_store"
#     memory_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
#     memory_type = Column(String)
#     memory_content = Column(Text)
#     confidence_score = Column(Float)
#     version = Column(Integer)

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


# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"

    # BIGSERIAL handled by PostgreSQL sequence
    user_id = Column(BigInteger, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

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

    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        index=True
    )

    role = Column(String, nullable=False)
    content = Column(Text)
    token_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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

    # 🔑 Primary Key
    memory_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 🔗 User relation
    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # 🧠 Memory content
    memory_type = Column(String, nullable=False)
    memory_content = Column(Text, nullable=False)
    confidence_score = Column(Float)

    # ✅ Soft delete flag (user "forget")
    is_active = Column(Boolean, default=True, nullable=False)

    # ⏳ Auto cleanup support
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # 🕒 Metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # 🔁 ORM relationship
    user = relationship("User", back_populates="memories")


# =========================
# VECTOR DATABASE (RAG)
# =========================
# class VectorDBRAG(Base):
#     __tablename__ = "vector_db_rag"

#     document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)

#     embedding = Column(Vector(1536))
#     metadata = Column(JSONB)

#     user = relationship("User", back_populates="vectors")
class VectorDBRAG(Base):
    __tablename__ = "vector_db_rag"

    document_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    embedding = Column(ARRAY(Float), nullable=False)

    meta_data = Column("metadata", JSONB)

    user = relationship("User", back_populates="vectors")
