from typing import List, Dict
from sqlalchemy.orm import Session
from models import ChatMessage
from services.memory_service import get_conversation_summary
 
MAX_RECENT_MESSAGES = 6
 
SYSTEM_PROMPT = """
You are a helpful AI assistant.
 
You may answer ANY general knowledge question.
 
Conversation summaries and memories are ONLY to provide helpful context
(e.g. preferences, ongoing plans).
 
If a user asks something unrelated to the current topic,
answer it normally using general knowledge.
 
Do NOT restrict yourself to previous topics unless the user explicitly asks.
"""
 
class ContextBuilder:
    @staticmethod
    def build_llm_context(
        db: Session,
        session_id,
        user_input: str
    ) -> List[Dict[str, str]]:
        messages = []
 
        # 1️⃣ System prompt
        messages.append({
            "role": "system",
            "content": SYSTEM_PROMPT.strip()
        })
 
        # 2️⃣ Conversation summary (rolling)
        summary = get_conversation_summary(db, session_id)
        if summary:
            messages.append({
                "role": "system",
                "content": f"Compressed conversation so far:\n{summary}"
            })
 
        # 3️⃣ Recent messages
        recent_msgs = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.session_id == session_id,
                ChatMessage.is_summarized.is_(False)
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(MAX_RECENT_MESSAGES)
            .all()
        )
 
        for msg in reversed(recent_msgs):
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
 
        # 4️⃣ Current user message
        messages.append({
            "role": "user",
            "content": user_input
        })
 
        return messages
    
    def build_router_context(
        db: Session,
        session_id,
        user_input: str
    ) -> str:
        parts = []

        # 1️⃣ Summary
        summary = get_conversation_summary(db, session_id)
        if summary:
            parts.append(f"Conversation summary:\n{summary}")

        # 2️⃣ Recent user messages only
        recent_msgs = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.session_id == session_id,
                ChatMessage.role == "user"
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(3)
            .all()
        )

        if recent_msgs:
            parts.append("Recent user messages:")
            for m in reversed(recent_msgs):
                parts.append(f"- {m.content}")

        # 3️⃣ Current input
        parts.append(f"\nCurrent request:\n{user_input}")

        return "\n".join(parts)