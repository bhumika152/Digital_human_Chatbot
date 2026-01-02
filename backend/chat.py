from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import logging
from database import SessionLocal
from models import ChatSession, ChatMessage
from models import UserConfig 
from auth import get_current_user
from digital_human.services import run_digital_human_chat

from constants import get_user_config
from services.memory_service import cleanup_expired_memories


router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger("chat")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# --------------------
# DB Dependency
# --------------------
def get_db():
    db = SessionLocal()
    cleanup_expired_memories(db)
    try:
        yield db
    finally:
        db.close()


# --------------------
# LIST SESSIONS
# --------------------
@router.get("/sessions")
def list_sessions(
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
            "session_title": s.session_title,
            "created_at": s.created_at,
        }
        for s in sessions
    ]


# --------------------
# CHAT HISTORY
# --------------------
@router.get("/history/{session_id}")
def history(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(ChatMessage)
        .join(ChatSession)
        .filter(ChatSession.session_id == session_id)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in messages
    ]


# --------------------
# CHAT SEND MESSAGE
# --------------------
@router.post("")
def chat(
    payload: dict,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(
        f"📩 Chat request received | user_id={user_id} | payload_keys={list(payload.keys())}"
    )
    user_config = get_user_config(db, user_id)
    session_id = payload.get("conversation_id")
    raw_message = payload.get("message")

    if not raw_message:
        raise HTTPException(status_code=400, detail="Invalid payload")

    if isinstance(raw_message, dict):
        user_text = raw_message.get("content", "")
    else:
        user_text = str(raw_message)

    if not user_text.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    logger.info(
        f"💬 User message parsed | user_id={user_id} | content='{user_text[:100]}'"
    )

    if not session_id:
        session_id = str(uuid.uuid4())

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
        db.flush()

    logger.info(
        f"🧵 Chat session active | user_id={user_id} | session_id={session.session_id}"
    )

    # Load chat history from database BEFORE adding current message
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    
    # Format chat history for digital_human (List[Dict[str, str]])
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]
    
    logger.info(
        f"📚 Chat history loaded | user_id={user_id} | messages_count={len(chat_history)}"
    )

    # Add user message to database
    db.add(
        ChatMessage(
            session_id=session.session_id,
            role="user",
            content=user_text,
        )
    )

    logger.info(
        f"🧠 Digital Human invoked | user_id={user_id} | session_id={session.session_id}"
    )

    # Call digital_human service
    try:
        agent_result = run_digital_human_chat(
            user_input=user_text,
            chat_history=chat_history,
            token_budget=4000,
        )
    except Exception as e:
        logger.error(
            f"❌ Digital Human error | user_id={user_id} | error={str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )




    logger.info(
        f"🤖 Agent response ready | memory_intent={agent_result.get('memory_intent')} | rag_used={agent_result.get('rag_used')}"
    )


    db.add(
        ChatMessage(
            session_id=session.session_id,
            role="assistant",
            content=agent_result["response"],
        )
    )
    

    db.commit()

    logger.info(
        f"✅ Chat persisted | user_id={user_id} | session_id={session.session_id}"
    )

    # return {
    #     "session_id": str(session.session_id),
    #     "response": agent_result["response"],
    #     "memory_written": agent_result.get("memory_written", False),
    #     "rag_used": agent_result.get("rag_used", False),
    # }
    return {
        "session_id": str(session.session_id),
        "response": agent_result["response"],
        "memory_intent": agent_result.get("memory_intent"),
        "rag_used": agent_result.get("rag_used", False),
    }

