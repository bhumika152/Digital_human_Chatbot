from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import logging
import json

from dotenv import load_dotenv
load_dotenv()

# =========================
# Database & Models
# =========================
from database import SessionLocal
from models import ChatSession, ChatMessage

# =========================
# Auth & Config
# =========================
from auth import get_current_user
from constants import get_user_config

# =========================
# Memory
# =========================
from services.memory_action_executor import apply_memory_action

# =========================
# Digital Human SDK
# =========================
from digital_human_sdk.app.main import run_digital_human_chat
from digital_human_sdk.app.intelligence.runner import Runner
from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent

# ==========================================================
# Router & Logger
# ==========================================================
router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger("chat")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# ==========================================================
# DB Dependency (short-lived)
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
@router.post("")
async def chat(
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
    session_id = payload.get("conversation_id")
    raw_message = payload.get("message")

    if not raw_message:
        raise HTTPException(status_code=400, detail="Missing message")

    user_text = (
        raw_message.get("content", "")
        if isinstance(raw_message, dict)
        else str(raw_message)
    )

    if not user_text.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    # --------------------
    # SESSION HANDLING
    # --------------------
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"🆕 New session | {session_id}")

    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id)
        .filter(ChatSession.user_id == user_id)
        .first()
    )

    if not session:
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            session_title=user_text[:50],
        )
        db.add(session)
        db.commit()

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

        logger.info(f"🤖 Stream started | session_id={session_id}")

        # =====================================================
        # 1️⃣ PRE-SAFETY (Input moderation)
        # =====================================================
        pre_raw = await Runner.run(
            safe_agent,
            user_text,
            max_turns=1,
        )

        pre = json.loads(pre_raw.final_output)

        if not pre.get("safe", True):
            logger.warning("🚫 Pre-safety blocked input")

            for ch in pre.get("message", "Request blocked by safety policy."):
                yield ch
            return

        # =====================================================
        # 2️⃣ LLM STREAMING
        # =====================================================
        async for event in run_digital_human_chat(
            user_input=user_text,
            chat_history=chat_history,
            user_config=user_config,
        ):
            event_type = event.get("type")

            # TOKEN STREAM
            if event_type == "token":
                token = event.get("value", "")
                full_response += token
                yield token

            # MEMORY EVENT
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
                except Exception as e:
                    db_inner.rollback()
                    logger.error(f"❌ Memory error | {e}")
                finally:
                    db_inner.close()

        # =====================================================
        # 3️⃣ POST-SAFETY (Output moderation)
        # =====================================================
        post_raw = await Runner.run(
            safe_agent,
            full_response,
            max_turns=1,
        )

        post = json.loads(post_raw.final_output)

        if not post.get("safe", True):
            logger.warning("🚫 Post-safety blocked output")

            yield "\n\n⚠️ Response removed due to safety policy."
            return

        # =====================================================
        # 4️⃣ SAVE ASSISTANT MESSAGE
        # =====================================================
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

        logger.info(f"✅ Stream completed | session_id={session_id}")

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
    )
