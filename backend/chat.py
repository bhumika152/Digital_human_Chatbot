# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# import uuid
# import logging

# from database import SessionLocal
# from models import ChatSession, ChatMessage
# from auth import get_current_user
# from constants import get_user_config
# from services.memory_service import cleanup_expired_memories
# from services.memory_action_executor import apply_memory_action

# # 🔥 IMPORT SDK
# from digital_human_sdk.app.main import run_digital_human_chat

# # --------------------
# # Router & Logger
# # --------------------
# router = APIRouter(prefix="/chat", tags=["chat"])

# logger = logging.getLogger("chat")
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s",
# )

# # --------------------
# # DB Dependency
# # --------------------
# def get_db():
#     db = SessionLocal()
#     cleanup_expired_memories(db)
#     try:
#         yield db
#     finally:
#         db.close()


# # --------------------
# # CHAT (STREAMING)
# # --------------------
# @router.post("")
# def chat(
#     payload: dict,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logger.info(
#         f"📩 Chat request received | user_id={user_id} | payload_keys={list(payload.keys())}"
#     )

#     user_config = get_user_config(db, user_id)
#     logger.info(f"⚙️ User config loaded | user_id={user_id}")

#     session_id = payload.get("conversation_id")
#     raw_message = payload.get("message")

#     if not raw_message:
#         raise HTTPException(status_code=400, detail="Invalid payload")

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
#     if not session_id:
#         session_id = str(uuid.uuid4())
#         logger.info(f"🆕 New session | {session_id}")

#     session = (
#         db.query(ChatSession)
#         .filter(ChatSession.session_id == session_id)
#         .filter(ChatSession.user_id == user_id)
#         .first()
#     )

#     if not session:
#         session = ChatSession(
#             session_id=session_id,
#             user_id=user_id,
#             session_title=user_text[:50],
#         )
#         db.add(session)
#         db.flush()

#     # --------------------
#     # LOAD CHAT HISTORY
#     # --------------------
#     previous_messages = (
#         db.query(ChatMessage)
#         .filter(ChatMessage.session_id == session.session_id)
#         .order_by(ChatMessage.created_at.asc())
#         .all()
#     )

#     chat_history = [
#         {"role": msg.role, "content": msg.content}
#         for msg in previous_messages
#     ]

#     # --------------------
#     # SAVE USER MESSAGE
#     # --------------------
#     db.add(
#         ChatMessage(
#             session_id=session.session_id,
#             role="user",
#             content=user_text,
#         )
#     )
#     db.commit()

#     # --------------------
#     # STREAM RESPONSE
#     # --------------------
#     async def stream_response():
#         full_response = ""

#         logger.info(
#             f"🤖 Digital Human stream started | session_id={session_id}"
#         )

#         async for event in run_digital_human_chat(
#             user_input=user_text,
#             chat_history=chat_history,
#             user_config=user_config,
#         ):
#             if event["type"] == "token":
#                 token = event["value"]
#                 full_response += token
#                 yield token

#             elif event["type"] == "memory_event":
#                 memory_action = event["payload"]
#                 logger.info(
#                     f"🧠 Memory event | status={memory_action.get('status')}"
#                 )

#                 if memory_action.get("status") == "success":
#                     apply_memory_action(
#                         db=db,
#                         user_id=user_id,
#                         action=memory_action,
#                     )

#         # --------------------
#         # SAVE ASSISTANT MESSAGE
#         # --------------------
#         db.add(
#             ChatMessage(
#                 session_id=session.session_id,
#                 role="assistant",
#                 content=full_response,
#             )
#         )
#         db.commit()

#         logger.info(
#             f"✅ Chat completed | session_id={session_id} | chars={len(full_response)}"
#         )

#     return StreamingResponse(
#         stream_response(),
#         media_type="text/plain",
#     )
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import uuid
import logging

from database import SessionLocal
from models import ChatSession, ChatMessage
from auth import get_current_user
from constants import get_user_config
from services.memory_action_executor import apply_memory_action

# 🔥 Digital Human SDK
from digital_human_sdk.app.main import run_digital_human_chat


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
# DB Dependency (SHORT LIVED)
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
    logger.info(f"⚙️ User config loaded | user_id={user_id}")

    # --------------------
    # VALIDATE PAYLOAD
    # --------------------
    session_id = payload.get("conversation_id")
    raw_message = payload.get("message")

    if not raw_message:
        logger.error("❌ Missing message in payload")
        raise HTTPException(status_code=400, detail="Invalid payload")

    user_text = (
        raw_message.get("content", "")
        if isinstance(raw_message, dict)
        else str(raw_message)
    )

    if not user_text.strip():
        logger.error("❌ Empty message received")
        raise HTTPException(status_code=400, detail="Empty message")

    # --------------------
    # SESSION HANDLING
    # --------------------
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"🆕 New session created | session_id={session_id}")

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
        logger.info(f"📌 Session stored | session_id={session_id}")

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

    logger.info(
        f"📜 Loaded chat history | messages={len(chat_history)}"
    )

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
    logger.info("💾 User message saved")

    # ==========================================================
    # STREAM RESPONSE
    # ==========================================================
    async def stream_response():
        full_response = ""

        logger.info(
            f"🤖 Digital Human stream started | session_id={session_id}"
        )

        async for event in run_digital_human_chat(
            user_input=user_text,
            chat_history=chat_history,
            user_config=user_config,
        ):
            event_type = event.get("type")

            # --------------------
            # TOKEN STREAM
            # --------------------
            if event_type == "token":
                token = event.get("value", "")
                full_response += token
                yield token

            # --------------------
            # MEMORY EVENT
            # --------------------
            elif event_type == "memory_event":
                memory_action = event.get("payload", {})
                logger.info(
                    f"🧠 Memory event received | action={memory_action.get('action')} | key={memory_action.get('key')}"
                )

                # 🔒 SHORT-LIVED DB SESSION
                db_inner = SessionLocal()
                try:
                    apply_memory_action(
                        db=db_inner,
                        user_id=user_id,
                        action=memory_action,
                    )
                    db_inner.commit()
                    logger.info("✅ Memory action applied successfully")

                except Exception as e:
                    db_inner.rollback()
                    logger.error(f"❌ Memory action failed | error={e}")

                finally:
                    db_inner.close()

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
            logger.info(
                f"💾 Assistant message saved | chars={len(full_response)}"
            )
        finally:
            db_final.close()

        logger.info(
            f"✅ Chat completed | session_id={session_id}"
        )

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
    )
