from sqlalchemy.orm import Session
from models import ChatMessage, MemoryStore
from constants.summary import (
    SUMMARY_TRIGGER_MESSAGES,
    SUMMARY_CHUNK_SIZE,
    KEEP_LAST_MESSAGES,
)
from services.llm_client import call_llm  # your LLM wrapper
 
 
SUMMARY_PROMPT = """
You are a memory compression system.
 
TASK:
Update the existing conversation summary using the new dialogue below.
 
RULES:
- Preserve facts, decisions, preferences, and open tasks
- Remove chit-chat and repetition
- Do NOT invent new information
- Keep the summary concise and factual
 
EXISTING SUMMARY:
{old_summary}
 
NEW DIALOGUE:
{dialogue}
 
OUTPUT:
Updated summary only.
"""
 
 
def maybe_update_summary(db: Session, session_id):
    # 1️⃣ Count messages
    total_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .count()
    )
 
    # 2️⃣ No pressure → no summarization
    if total_messages < SUMMARY_TRIGGER_MESSAGES:
        return
 
    # 3️⃣ Load existing summary (if any)
    summary_row = (
        db.query(MemoryStore)
        .filter(
            MemoryStore.session_id == session_id,
            MemoryStore.memory_type == "conversation_summary",
            MemoryStore.is_active == True,
        )
        .first()
    )
 
    old_summary = summary_row.memory_content if summary_row else ""
 
    # 4️⃣ Fetch oldest messages to summarize
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(SUMMARY_CHUNK_SIZE)
        .all()
    )
 
    # 5️⃣ Never summarize recent messages
    if len(messages) <= KEEP_LAST_MESSAGES:
        return
 
    dialogue = "\n".join(
        f"{m.role.upper()}: {m.content}"
        for m in messages
    )
 
    prompt = SUMMARY_PROMPT.format(
        old_summary=old_summary or "None",
        dialogue=dialogue,
    )
 
    # 6️⃣ LLM call (ONLY place tokens are used for memory)
    new_summary = call_llm(prompt).strip()
 
    # 7️⃣ Save summary (merge, don’t replace conceptually)
    if summary_row:
        summary_row.memory_content = new_summary
    else:
        db.add(
            MemoryStore(
                session_id=session_id,
                memory_type="conversation_summary",
                memory_content=new_summary,
            )
        )
 
    db.commit()
 
 
