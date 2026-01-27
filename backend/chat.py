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
from digital_human_sdk.app.main import run_digital_human_chat
# IntegrityError for unique constraint 
import re
from sqlalchemy.exc import IntegrityError, DataError



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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

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
        )
    )
    db.commit()

# 2️⃣ NOW BUILD CONTEXT
    llm_context = ContextBuilder.build_llm_context(
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
    )
    

    # ==========================================================
    # STREAM RESPONSE
    # ==========================================================
    async def stream_response():
    # 🔥 send initial keep-alive
        yield "data: \n\n"

        full_response = ""
        token_count = 0

        logger.info(
            "🤖 Stream started | session_id=%s | request_id=%s",
            session_id,
            request_id,
        )

        try:
            async for event in run_digital_human_chat(
                llm_messages=llm_context,
                context=agent_context,
            ):
                event_type = event.get("type")

                if event_type == "memory_event":
                    ...
                
                elif event_type == "token":
                    token = event.get("value", "")
                    if token:
                        token_count += 1
                        full_response += token
                        # ✅ SSE FORMAT
                        yield f"data: {token}\n\n"

        except Exception:
            logger.exception("🔥 Streaming failed")
            yield "data: [ERROR]\n\n"
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
        media_type="text/event-stream",
        headers={
            "X-Session-Id": session_id,
            "X-Request-Id": request_id,
        },
    )

# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# import logging
# import uuid
# import time
# from typing import Any
# from dotenv import load_dotenv
# import os
# from contexts.llm_context_builder import build_llm_context
# from contexts.agent_context import AgentContext
# from database import SessionLocal
# from models import ChatSession, ChatMessage
# from auth import get_current_user
# from constants import get_user_config
# from services.memory_action_executor import apply_memory_action
# from clients.digital_human_client import DigitalHumanClient

# load_dotenv()

# digital_human = DigitalHumanClient(
#     base_url=os.getenv("DIGITAL_HUMAN_BASE_URL")
# )

# # ==========================================================
# # Router & Logger
# # ==========================================================
# router = APIRouter(prefix="/chat", tags=["chat"])

# logger = logging.getLogger("chat")
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s",
# )
# logger.info(
#     "🌐 DigitalHuman base_url=%s",
#     os.getenv("DIGITAL_HUMAN_BASE_URL"),
# )

# # ==========================================================
# # DB Dependency
# # ==========================================================
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ==========================================================
# # CHAT ENDPOINT (STREAMING)
# # ==========================================================
# @router.post("")
# async def chat(
#     payload: dict[str, Any],
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     request_id = str(uuid.uuid4())
#     start_time = time.perf_counter()

#     logger.info("📩 Chat request | user_id=%s | request_id=%s", user_id, request_id)

#     user_config = get_user_config(db, user_id)

#     raw_message = payload.get("message")
#     session_id = payload.get("conversation_id")

#     if not raw_message:
#         raise HTTPException(status_code=400, detail="Message missing")

#     user_text = (
#         raw_message.get("content", "")
#         if isinstance(raw_message, dict)
#         else str(raw_message)
#     )

#     if not user_text.strip():
#         raise HTTPException(status_code=400, detail="Empty message")

#     # --------------------
#     # SESSION HANDLING
#     # --------------------
#     if session_id:
#         session = (
#             db.query(ChatSession)
#             .filter(
#                 ChatSession.session_id == session_id,
#                 ChatSession.user_id == user_id,
#             )
#             .first()
#         )
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")
#     else:
#         session = ChatSession(
#             user_id=user_id,
#             session_title=user_text[:50],
#         )
#         db.add(session)
#         db.commit()
#         db.refresh(session)

#     previous_messages = (
#         db.query(ChatMessage)
#         .filter(ChatMessage.session_id == session.session_id)
#         .order_by(ChatMessage.created_at.asc())
#         .all()
#     )

#     chat_history = [
#         {"role": m.role, "content": m.content}
#         for m in previous_messages[-20:]
#     ]

#     # Save user message
#     db.add(
#         ChatMessage(
#             session_id=session.session_id,
#             role="user",
#             content=user_text,
#         )
#     )
#     db.commit()

#     agent_context = AgentContext(
#         user_id=user_id,
#         session_id=session.session_id,
#         chat_history=chat_history,
#         enable_memory=user_config.get("enable_memory", True),
#         enable_tools=user_config.get("enable_tool", True),
#         enable_rag=user_config.get("enable_rag", True),
#         db_factory=SessionLocal,
#         logger=logger,
#     )

#     llm_context = build_llm_context(
#         agent_context=agent_context,
#         user_input=user_text,
#     )

#     async def stream_response():
#         full_response = ""
#         token_count = 0

#         try:
#             async for event in digital_human.stream_chat(
#                 user_input=user_text,
#                 llm_context=llm_context,
#                 flags={
#                     "user_id": user_id,
#                     "session_id": str(session.session_id),
#                     "enable_memory": agent_context.enable_memory,
#                     "enable_tools": agent_context.enable_tools,
#                     "enable_rag": agent_context.enable_rag,
#                 },
#             ):
#                 event_type = event.get("type")

#                 if event_type == "memory_event":
#                     db_inner = SessionLocal()
#                     try:
#                         apply_memory_action(
#                             db=db_inner,
#                             user_id=user_id,
#                             action=event["payload"],
#                         )
#                         db_inner.commit()
#                     finally:
#                         db_inner.close()

#                 elif event_type == "token":
#                     token = event.get("value", "")
#                     if token:
#                         token_count += 1
#                         full_response += token
#                         yield token

#         except Exception:
#             logger.exception("🔥 Streaming failed")
#             yield "\n[Error]"

#         # Save assistant message
#         db_final = SessionLocal()
#         try:
#             db_final.add(
#                 ChatMessage(
#                     session_id=session.session_id,
#                     role="assistant",
#                     content=full_response,
#                 )
#             )
#             db_final.commit()
#         finally:
#             db_final.close()

#     return StreamingResponse(
#         stream_response(),
#         media_type="text/event-stream",
#     )

# ==========================================================
# GET ALL SESSIONS (SIDEBAR)
# ==========================================================
# @router.get("/sessions")
@chat_router.get("/sessions")
def get_chat_sessions(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
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
        .order_by(ChatMessage.created_at.desc())  # latest first
        .offset(offset)
        .limit(limit)
        .all()
    )

    messages.reverse()  # 🔥 oldest → newest for UI

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in messages
    ]



# ==========================================================
# DELETE CHAT SESSION
# ==========================================================
# @router.delete("/sessions/{session_id}")
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
        )
        .first()
    )
 
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
 
    db.delete(session)
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
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Regex patterns (NO SPACES allowed in names & username)
    name_pattern = r"^[A-Za-z]+$"
    username_pattern = r"^[A-Za-z0-9_]+$"
    phone_pattern = r"^\d{10}$"
    bio_pattern = r"^[A-Za-z0-9 .,!?_\-'\n\"]*$"

    # ---------------- FIRST NAME ----------------
    if payload.first_name is not None:
        first_name = payload.first_name.strip()

        if first_name != "":
            if len(first_name) > 20:
                raise HTTPException(status_code=400, detail="First name max 20 characters")

            if not re.fullmatch(name_pattern, first_name):
                raise HTTPException(status_code=400, detail="First name only letters allowed")

            user.first_name = first_name

    # ---------------- LAST NAME ----------------
    if payload.last_name is not None:
        last_name = payload.last_name.strip()

        if last_name != "":
            if len(last_name) > 20:
                raise HTTPException(status_code=400, detail="Last name max 20 characters")

            if not re.fullmatch(name_pattern, last_name):
                raise HTTPException(status_code=400, detail="Last name only letters allowed")

            user.last_name = last_name

    # ---------------- USERNAME ----------------
    if payload.username is not None:
        username = payload.username.strip()

        if username != "":
            if len(username) > 20:
                raise HTTPException(status_code=400, detail="Username max 20 characters")

            if not re.fullmatch(username_pattern, username):
                raise HTTPException(status_code=400, detail="Username only letters, numbers, underscore")

            existing_user = (
                db.query(User)
                .filter(User.username == username, User.user_id != user_id)
                .first()
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already exists")

            user.username = username

    # ---------------- PHONE ----------------
    if payload.phone is not None:
        phone = payload.phone.strip()

        if phone != "":
            if not re.fullmatch(phone_pattern, phone):
                raise HTTPException(status_code=400, detail="Phone must be exactly 10 digits")

            user.phone = phone

    # ---------------- BIO ----------------
    if payload.bio is not None:
        bio = payload.bio.strip()

        if bio != "":
            if len(bio) > 500:
                raise HTTPException(status_code=400, detail="Bio max 500 characters")

            if not re.fullmatch(bio_pattern, bio):
                raise HTTPException(status_code=400, detail="Bio contains invalid characters")

            user.bio = bio

    # ---------------- COMMIT ----------------
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid input: value too long or wrong format")

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
