from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging
import json
import uuid
import time
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
 
from context.agent_context import AgentContext
from database import SessionLocal
from models import ChatSession, ChatMessage,User
from auth import get_current_user
from constants import get_user_config
from services.memory_action_executor import apply_memory_action
#from digital_human_sdk.app.main import run_digital_human_chat
from context.context_builder import ContextBuilder
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Boolean

from clients.digital_human_client import DigitalHumanClient
import os
from services.memory_service import MemoryService
from services.knowledge_base_service import KnowledgeBaseService
from fastapi import Request


# ==========================================================
# Router & Logger
# ==========================================================
# router = APIRouter(prefix="/chat", tags=["chat"])
chat_router = APIRouter(prefix="/chat", tags=["chat"])
user_router = APIRouter(prefix="/users", tags=["users"])
 
# ------------------------------------
#   Schemas
# ------------------------------------
class UpdateProfileRequest(BaseModel):
   
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
 
 
logger = logging.getLogger("chat")
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s",
# )

# ==========================================================
# DB Dependency
# ==========================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
# ==========================================================
# CHAT ENDPOINT (STREAMING)
# ==========================================================
# @router.post("")
@chat_router.post("")
async def chat(
    payload: dict,
    request: Request,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
 
    logger.info("📩 Chat request | user_id=%s | request_id=%s", user_id, request_id)
 
    # --------------------
    # LOAD USER CONFIG (DICT)
    # --------------------
    user_config = get_user_config(db, user_id)
 
    # --------------------
    # VALIDATE PAYLOAD
    # --------------------
    raw_message = payload.get("message")
    session_id = payload.get("conversation_id")
 
    if not raw_message:
        raise HTTPException(status_code=400, detail="Message missing")
 
    user_text = (
        raw_message.get("content", "")
        if isinstance(raw_message, dict)
        else str(raw_message)
    )
 
    if not user_text.strip():
        raise HTTPException(status_code=400, detail="Empty message")
 
    logger.info("🧑 User message | %.200s", user_text)
 
    # --------------------
    # SESSION HANDLING
    # --------------------
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id,
            )
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            user_id=user_id,
            session_title=user_text[:50],
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = str(session.session_id)
 
        logger.info("🆕 New session created | %s", session_id)
 
   
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
 
   
 
    db.add(
        ChatMessage(
        session_id=session.session_id,
        role="user",
        content=user_text,
        is_summarized=False,
        )
    )
    db.commit()
 
# 2️⃣ NOW BUILD CONTEXT
    llm_context = ContextBuilder.build_llm_context(
        db=db,
        session_id=session.session_id,
        user_input=user_text,
    )

    router_context = ContextBuilder.build_router_context(
        db=db,
        session_id=session.session_id,
        user_input=user_text,
)


    agent_context = {
        "user_id": user_id,
        "session_id": session.session_id,
        "enable_memory": user_config.get("enable_memory", True),
        "enable_tools": user_config.get("enable_tools", True),
        "enable_rag": user_config.get("enable_rag", True),
        "db_factory": SessionLocal,
        "logger": logger,
        "request": request,
        
    }
 
    # --------------------
    # BUILD AGENT CONTEXT
    # --------------------
    agent_context = AgentContext(
        user_id=user_id,
        session_id=session.session_id,
        enable_memory=user_config.get("enable_memory", True),
        enable_tools=user_config.get("enable_tool", True),
        enable_rag=user_config.get("enable_rag", True),
        db_factory=SessionLocal,   # 🔑 SAFE FOR STREAMING
        logger=logger,
        request= request,
    )
    
    semantic_memory = MemoryService.read(
        user_id=user_id,
        query=user_text,
        limit=3,
    )

    kb_data = []
    kb_found = False
 
    try:
        logger.info("enable_rag: %s", agent_context.enable_rag)

        kb_data = KnowledgeBaseService.read(
            query=user_text,
            limit=5,
            document_types=["FAQ", "POLICY"],
            # industry="fintech",  

        )
        logger.info("KB RAW RESULT COUNT: %d", len(kb_data))
        logger.info("KB RAW RESULT: %s", kb_data)
        kb_found = bool(kb_data)
        logger.info(f"📚 KB found: {kb_found}")
    except Exception:
        logger.exception("❌ Knowledge base read failed")

    # ==========================================================
    # STREAM RESPONSE
    # ==========================================================
    async def stream_response():
    # 🔥 send initial keep-alive
 
        full_response = ""
        token_count = 0
 
        logger.info(
            "🤖 Stream started | session_id=%s | request_id=%s",
            session_id,
            request_id,
        )
        auth_header = request.headers.get("Authorization")
        logger.info("🔐 Incoming Authorization: %s", request.headers.get("Authorization"))

        dh_client = DigitalHumanClient(os.getenv("DIGITAL_HUMAN_BASE_URL"))
        try:
            async for event in dh_client.stream_chat(
                user_input=user_text,
                llm_context=llm_context,
                auth_token=auth_header,
                flags = {
                "user_id": int(user_id),
                "session_id": str(session.session_id), 
                "enable_memory": bool(agent_context.enable_memory),
                "enable_tools": bool(agent_context.enable_tools),
                "enable_rag": bool(agent_context.enable_rag),
                "router_context": router_context,
                "memory_data": semantic_memory,
                "kb_data": kb_data,
                "kb_found": kb_found,
                
            },
            request_id=request_id,
            ):
                event_type = event.get("type")
 
                if event_type == "memory_event":
                    # 🔎 Extract memory action safely (FINAL)
                    memory_action = (
                        event.get("payload")
                        or event.get("value")
                        or event.get("memory_action")
                        or event.get("data")
                    )

                    # Handle wrapped payloads
                    if isinstance(memory_action, dict) and "memory_action" in memory_action:
                        memory_action = memory_action["memory_action"]

                    if not memory_action:
                        logger.error(
                            "❌ memory_event received without payload | event=%s",
                            event,
                        )
                        continue

                    logger.info("🧠 MEMORY_EVENT_RECEIVED | %s", memory_action)

                    if not agent_context.enable_memory:
                        logger.info("🧠 Memory disabled — skipping")
                        continue

                    db_mem = agent_context.db_factory()
                    try:
                        apply_memory_action(
                            db=db_mem,
                            user_id=agent_context.user_id,
                            action=memory_action,
                        )
                    finally:
                        db_mem.close()
                
                elif event_type == "token":
                    token = event.get("value", "")
                    if token:
                        token_count += 1
                        full_response += token
                        # ✅ SSE FORMAT
                        # yield f"{token}\n\n"
                        yield token
 
        except Exception:
            logger.exception("🔥 Streaming failed")
            # yield "data: [ERROR]\n\n"
            return
 
        # --------------------
        # SAVE ASSISTANT MESSAGE
        # --------------------
        db_final = SessionLocal()
        try:
            db_final.add(
                ChatMessage(
                    session_id=session.session_id,
                    role="assistant",
                    content=full_response,
                    is_summarized=False,   
                )
            )
            db_final.commit()

            
            from services.summary_manager import maybe_update_summary
            maybe_update_summary(db_final, session.session_id)

            elapsed = round(time.perf_counter() - start_time, 2)
            logger.info(
                "✅ Stream complete | tokens=%s | time=%ss",
                token_count,
                elapsed,
            )
        finally:
            db_final.close()
 
    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
        headers={
            "X-Session-Id": session_id,
            "X-Request-Id": request_id,
        },
    )
 
# ==========================================================
# GET ALL SESSIONS (SIDEBAR)
# ==========================================================
@chat_router.get("/sessions")
def get_chat_sessions(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id,
                ChatSession.is_active == True )
        .order_by(ChatSession.created_at.desc())
        .all()
    )
 
    return [
        {
            "session_id": str(s.session_id),
            "session_title": s.session_title or "New Chat",
            "created_at": s.created_at,
        }
        for s in sessions
    ]
 
# ==========================================================
# CREATE NEW CHAT SESSION
# ==========================================================
# @router.post("/sessions")
@chat_router.post("/sessions")
def create_chat_session(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = ChatSession(
        user_id=user_id,
        session_title="New Chat",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
 
    return {
        "session_id": str(session.session_id),
        "session_title": session.session_title,
    }
 
# ==========================================================
# GET MESSAGES OF A SESSION
# ==========================================================
# @router.get("/sessions/{session_id}/messages")
@chat_router.get("/sessions/{session_id}/messages")
def get_chat_messages(
    session_id: str,
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        )
        .first()
    )
 
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
 
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.session_id)
        .order_by(ChatMessage.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
 
    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in reversed(messages)
    ]
 
# ==========================================================
# DELETE CHAT SESSION
# ==========================================================
@chat_router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_active == True   # 🔥 only active
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # ✅ SOFT DELETE
    session.is_active = False
    session.ended_at = datetime.utcnow()

    db.commit()

    return {"message": "Chat deleted successfully"}

#------------------------------------
#   Get user data
#------------------------------------
@user_router.get("/me")
def get_me(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == user_id).first()
 
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
 
    return {
        "user_id": user.user_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "bio": user.bio,
        "created_at": user.created_at,
 
    }
 
#------------------------------------
#   Update user data
#------------------------------------
@user_router.put("/me")
def update_me(
    payload: UpdateProfileRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
 
    # ✅ update fields
    if payload.first_name is not None:
        user.first_name = payload.first_name
 
    if payload.last_name is not None:
        user.last_name = payload.last_name
 
    if payload.username is not None:
        user.username = payload.username
 
    if payload.phone is not None:
        user.phone = payload.phone
 
    if payload.bio is not None:
        user.bio = payload.bio
 
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    db.refresh(user)
    return {
        "message": "User updated successfully",
        "user": {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "bio": user.bio,
        },
    }