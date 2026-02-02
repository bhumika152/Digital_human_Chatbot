
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
#from pgvector.sqlalchemy import Vector
from database import Base
import uuid
from sqlalchemy import TIMESTAMP
from datetime import datetime


# =========================
# KNOWLEDGE BASE (ADMIN DOCS)
# =========================
class KnowledgeBaseEmbedding(Base):
    __tablename__ = "knowledge_base_embeddings"

    kb_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    document_id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        index=True
    )

    document_title = Column(
        String(255),
        nullable=False
    )

    document_type = Column(
        String(50),
        nullable=False
    )
    # FAQ | POLICY | TERMS | GUIDELINE | SUPPORT

    industry = Column(
        String(100),
        nullable=True,
        index=True
    )

    language = Column(
        String(10),
        default="en"
    )

    content = Column(
        Text,
        nullable=False
    )

    # Using FLOAT[] instead of pgvector
    embedding = Column(
        ARRAY(Float),
        nullable=False
    )

    extra_metadata = Column("metadata", JSONB)

    version = Column(
        Integer,
        default=1
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"

    # BIGSERIAL handled by PostgreSQL sequence
    user_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(Text) 

     # (new fields)
    first_name = Column(String(20), nullable=True)
    last_name = Column(String(20), nullable=True)
    phone = Column(String(10), nullable=True)
    bio = Column(String(500), nullable=True)

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
    summary = relationship("SessionSummary", back_populates="user", cascade="all, delete")



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
    summary = relationship(
        "SessionSummary",
        back_populates="session",
        uselist=False,
        cascade="all, delete"
    )

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
    is_summarized = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

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
  
 
    memory_content = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    confidence_score = Column(Float)

    is_active = Column(Boolean, default=True, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


    user = relationship("User", back_populates="memories")

class SessionSummary(Base):
    __tablename__ = "session_summary"

    summary_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    summary_text = Column(Text, nullable=False)

    summary_type = Column(
        String,
        default="auto"
    )  # auto | manual | system

    confidence_score = Column(Float, nullable=True)

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # 🔗 Relationships
    session = relationship("ChatSession", back_populates="summary")
    user = relationship("User",back_populates="summary")

class Property(Base):
    __tablename__ = "properties"
 
    property_id = Column(BigInteger, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    locality = Column(Text, nullable=False)
    purpose = Column(Text, nullable=False)   # rent / buy
    price = Column(BigInteger, nullable=False)
    bhk = Column(Integer)
    area_sqft = Column(Integer)
    is_legal = Column(Boolean, nullable=False)
    owner_name = Column(Text, nullable=False)
    contact_phone = Column(BigInteger, nullable=False)
    owner_user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
 

class PropertyEnquiry(Base):
    __tablename__ = "property_enquiries"

    enquiry_id = Column(BigInteger, primary_key=True, index=True)

    property_id = Column(
        BigInteger,
        ForeignKey("properties.property_id", ondelete="CASCADE"),
        nullable=False
    )

    buyer_user_id = Column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )

    message = Column(Text)
    status = Column(Text, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
