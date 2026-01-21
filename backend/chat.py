from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging

from pydantic import BaseModel
from typing import Optional 

from database import SessionLocal
from models import ChatSession, ChatMessage,User
from auth import get_current_user
from constants import get_user_config
from services.memory_action_executor import apply_memory_action
from digital_human_sdk.app.main import run_digital_human_chat
# IntegrityError for unique constraint 
from sqlalchemy.exc import IntegrityError

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
logger.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ==========================================================
# DB Dependency
# ==========================================================
def get_db():
    db = SessionLocal()
    logger.debug("🗄️ DB session opened")
    try:
        yield db
    finally:
        db.close()
        logger.debug("🗄️ DB session closed")


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
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        f"📩 Chat request received | request_id={request_id} | user_id={user_id}"
    )
    logger.info(f"📦 Payload keys | {list(payload.keys())}")

    # --------------------
    # LOAD USER CONFIG
    # --------------------
    user_config = get_user_config(db, user_id)
    logger.info(f"⚙️ User config loaded | {user_config}")

    # --------------------
    # VALIDATE PAYLOAD
    # --------------------
    raw_message = payload.get("message")
    session_id = payload.get("conversation_id")

    if not raw_message:
        logger.error("❌ Message missing in payload")
        raise HTTPException(status_code=400, detail="Message missing")

    user_text = (
        raw_message.get("content", "")
        if isinstance(raw_message, dict)
        else str(raw_message)
    )

    if not user_text.strip():
        logger.error("❌ Empty user message")
        raise HTTPException(status_code=400, detail="Empty message")

    logger.info(f"🧑 User message | {user_text[:200]}")

    # --------------------
    # SESSION HANDLING
    # --------------------
    if session_id:
        logger.info(f"🔎 Looking up session | session_id={session_id}")
        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )
            .first()
        )

        if not session:
            logger.error("❌ Session not found or unauthorized")
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info("✅ Existing session loaded")
    else:
        logger.info("🆕 Creating new chat session")
        session = ChatSession(
            user_id=user_id,
            session_title=user_text[:50]
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = str(session.session_id)

        logger.info(f"🆕 New session created | session_id={session_id}")

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

    logger.info(f"📚 Loaded chat history | messages={len(chat_history)}")

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

    logger.info("💾 User message saved to DB")

    # ==========================================================
    # STREAM RESPONSE
    # ==========================================================
    async def stream_response():
        full_response = ""
        token_count = 0

        logger.info(
            f"🤖 Stream started | session_id={session_id} | request_id={request_id}"
        )
        try:
            logger.info(
            f"🤖 Running digital human"
        )
            async for event in run_digital_human_chat(
                user_input=user_text,
                
            ):
                event_type = event.get("type")

                logger.debug(f"📡 Event received | type={event_type}")

                # --------------------
                # MEMORY EVENT (side-effect)
                # --------------------
                if event_type == "memory_event":
                    memory_action = event.get("payload", {})
                    logger.info(f"🧠 Memory event | {memory_action}")

                    db_inner = SessionLocal()
                    try:
                        apply_memory_action(
                            db=db_inner,
                            user_id=user_id,
                            action=memory_action,
                        )
                        db_inner.commit()
                        logger.info("🧠 Memory persisted successfully")
                    except Exception as e:
                        db_inner.rollback()
                        logger.exception("🔥 Memory persistence failed", exc_info=e)
                    finally:
                        db_inner.close()

                # --------------------
                # TOKEN STREAM (always)
                # --------------------
                if event_type == "token":
                    token = event.get("value", "")
                    token_count += 1
                    full_response += token
                    yield token

        except Exception as e:
            logger.exception(
                f"🔥 Streaming error | session_id={session_id}", exc_info=e
            )
            yield "\n[Error generating response]"
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

            elapsed = round(time.time() - start_time, 2)
            logger.info(
                f"✅ Stream completed | tokens={token_count} | time={elapsed}s"
            )
        finally:
            db_final.close()

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "X-Session-Id": session_id,
            "X-Request-Id": request_id,
        }
    )


# ==========================================================
# GET ALL SESSIONS
# ==========================================================
# @router.get("/sessions")
@chat_router.get("/sessions")
def get_chat_sessions(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"📂 Fetching sessions | user_id={user_id}")

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )

    logger.info(f"📂 Sessions found | count={len(sessions)}")

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
    logger.info(f"🆕 Creating empty chat session | user_id={user_id}")

    session = ChatSession(
        user_id=user_id,
        session_title="New Chat"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"🆕 Session created | session_id={session.session_id}")

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
    logger.info(
        f"📨 Fetching messages | session_id={session_id} | limit={limit} | offset={offset}"
    )

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not session:
        logger.error("❌ Session not found while fetching messages")
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    logger.info(f"📨 Messages fetched | count={len(messages)}")

    return [
        {
            "message_id": m.message_id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in reversed(messages)
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
    logger.info(f"🗑️ Delete request | session_id={session_id} | user_id={user_id}")

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not session:
        logger.error("❌ Session not found for deletion")
        raise HTTPException(status_code=404, detail="Chat session not found")

    db.delete(session)
    db.commit()

    logger.info(f"🗑️ Session deleted | session_id={session_id}")

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
