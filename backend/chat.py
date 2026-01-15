from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import ChatSession, ChatMessage,User
from auth import get_current_user
from constants import get_user_config
from services.memory_action_executor import apply_memory_action

# 🔥 Digital Human SDK
from digital_human_sdk.app.main import run_digital_human_chat


# ==========================================================
# Router & Logger
# ==========================================================
# router = APIRouter(prefix="/chat", tags=["chat"])
chat_router = APIRouter(prefix="/chat", tags=["chat"])
user_router = APIRouter(prefix="/users", tags=["users"])

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
def chat(
    payload: dict,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        f"📩 Chat request | user_id={user_id} | payload_keys={list(payload.keys())}"
    )

    # --------------------
    # LOAD USER CONFIG
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

    # --------------------
    # SESSION HANDLING (FIXED)
    # --------------------
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            user_id=user_id,
            session_title=user_text[:50]
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = str(session.session_id)

        logger.info(f"🆕 New session created | {session_id}")

    # --------------------
    # LOAD CHAT HISTORY
    # --------------------
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]

    # --------------------
    # SAVE USER MESSAGE
    # --------------------
    db.add(
        ChatMessage(
            session_id=session.session_id,
            role="user",
            content=user_text,
        )
    )
    db.commit()

    # ==========================================================
    # STREAM RESPONSE
    # ==========================================================
    async def stream_response():
        full_response = ""

        async for event in run_digital_human_chat(
            user_input=user_text,
            chat_history=chat_history,
            user_config=user_config,
        ):
            event_type = event.get("type")

            if event_type == "token":
                token = event.get("value", "")
                full_response += token
                yield token

            elif event_type == "memory_event":
                memory_action = event.get("payload", {})

                db_inner = SessionLocal()
                try:
                    apply_memory_action(
                        db=db_inner,
                        user_id=user_id,
                        action=memory_action,
                    )
                    db_inner.commit()
                except Exception:
                    db_inner.rollback()
                finally:
                    db_inner.close()

        # SAVE ASSISTANT MESSAGE
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
        finally:
            db_final.close()

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
        headers={
            "X-Session-Id": session_id
        }
    )


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
        session_title="New Chat"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": str(session.session_id),
        "session_title": session.session_title
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
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())  # 🔥 newest first
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "request_id": str(m.request_id),
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in reversed(messages)  # 🔥 UI me oldest → newest
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
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    db.delete(session)
    db.commit()

    return {"message": "Chat deleted successfully"}

#   Get user data 
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


