from sqlalchemy.orm import Session
from models import ChatMessage, SessionSummary, ChatSession
from constants.summary import (
    SUMMARY_TRIGGER_MESSAGES,
    SUMMARY_CHUNK_SIZE,
    KEEP_LAST_MESSAGES,
)
from services.llm_client import call_llm
import logging

logger = logging.getLogger("session_summary")

SUMMARY_PROMPT = """
You are a conversation compression engine.

TASK:
Produce a SHORTER version of the conversation so far by
merging the existing summary with the new dialogue.

RULES:
- Preserve ALL important topics discussed
- Preserve user questions and assistant answers in brief form
- Preserve decisions, plans, and conclusions
- Remove repetition, filler, and chit-chat
- DO NOT drop entire topics unless trivial
- DO NOT invent new information

INPUTS:

PREVIOUS SUMMARY:
{old_summary}

NEW CONVERSATION CHUNK:
{dialogue}

OUTPUT:
A concise merged summary representing the full conversation so far.

"""


def maybe_update_summary(db: Session, session_id):
    logger.info("🧠 SUMMARY_START | session_id=%s", session_id)

    # 1️⃣ Count UNSUMMARIZED messages only
    total_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.is_summarized.is_(False),
        )
        .count()
    )

    logger.info("📊 Unsummarized messages = %d", total_messages)

    # 2️⃣ Not enough signal → skip
    if total_messages < SUMMARY_TRIGGER_MESSAGES:
        logger.info("⏭️ SUMMARY_SKIP | LOW_MESSAGE_COUNT")
        return

    # 3️⃣ Load session (for user_id)
    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id)
        .first()
    )
    if not session:
        logger.error("❌ SUMMARY_ABORT | Session not found")
        return

    # 4️⃣ Load existing ACTIVE summary (MERGE target)
    summary_row = (
        db.query(SessionSummary)
        .filter(
            SessionSummary.session_id == session_id,
            SessionSummary.is_active.is_(True),
        )
        .first()
    )

    old_summary = summary_row.summary_text if summary_row else ""

    logger.info("📄 Existing summary = %s", bool(summary_row))

    # 5️⃣ Fetch OLDEST unsummarized messages
    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.is_summarized.is_(False),
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(SUMMARY_CHUNK_SIZE)
        .all()
    )

    logger.info("🧾 Messages fetched = %d", len(messages))

    # 6️⃣ Never summarize only recent messages
    if len(messages) <= KEEP_LAST_MESSAGES:
        logger.info("⏭️ SUMMARY_SKIP | ONLY_RECENT_MESSAGES")
        return

    # 7️⃣ Build dialogue chunk
    dialogue = "\n".join(
        f"{m.role.upper()}: {m.content}"
        for m in messages
        if m.content
    )

    logger.info("✍️ Calling LLM for MERGED summary")

    prompt = SUMMARY_PROMPT.format(
        old_summary=old_summary or "None",
        dialogue=dialogue,
    )

    new_summary = call_llm(prompt).strip()

    if not new_summary:
        logger.error("❌ SUMMARY_ABORT | EMPTY_LLM_RESPONSE")
        return

    # 8️⃣ MERGE (not replace)
    if summary_row:
        logger.info("🔄 MERGING INTO EXISTING SUMMARY")
        summary_row.summary_text = new_summary
    else:
        logger.info("🆕 CREATING NEW SUMMARY ROW")
        db.add(
            SessionSummary(
                session_id=session_id,
                user_id=session.user_id,
                summary_text=new_summary,
                summary_type="auto",
                confidence_score=0.85,
                is_active=True,
            )
        )

    # 9️⃣ Mark summarized messages (keep recent window)
    for m in messages[:-KEEP_LAST_MESSAGES]:
        m.is_summarized = True

    db.commit()
    logger.info("✅ SUMMARY_MERGED_SUCCESSFULLY")