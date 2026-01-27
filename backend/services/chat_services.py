from sqlalchemy.orm import Session
from models import ChatSession, ChatMessage
import uuid

def get_or_create_session(
    db: Session,
    user_id: int,
    conversation_id: str | None,
    first_message: str
) -> ChatSession:

    if conversation_id:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == conversation_id,
            ChatSession.user_id == user_id
        ).first()
        if session:
            return session

    session = ChatSession(
        session_id=uuid.uuid4(),
        user_id=user_id,
        session_title=first_message[:50]
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def save_message(
    db: Session,
    session_id,
    role: str,
    content: str,
    token_count: int | None = None
):
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        token_count=token_count
    )
    db.add(msg)
    db.commit()
   
    
def get_recent_messages(
    db: Session,
    session_id,
    limit: int = 10
):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
