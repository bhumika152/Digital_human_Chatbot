"""
Decision Agent
--------------
Memory + preference detection (config-aware)
SAFE VERSION (no ORM usage)
"""

from services.memory_service import write_memory, get_active_memories


def decision_agent(
    db,
    user_id: int,
    message: str,
    conversation_id: str,
    user_config: dict,  # ✅ EXPECT DICT, NOT ORM
):
    # ---------------------------------------------
    # NORMALIZE MESSAGE
    # ---------------------------------------------
    user_message = message.lower().strip()

    response_text = "Acknowledged."
    memory_written = False
    rag_used = False

    # ---------------------------------------------
    # MEMORY ENABLE CHECK (SAFE)
    # ---------------------------------------------
    memory_enabled = user_config.get("enable_memory", True)

    # ---------------------------------------------
    # GENERIC REMEMBER
    # ---------------------------------------------
    if memory_enabled and user_message.startswith("remember"):
        content = (
            user_message
            .replace("remember", "")
            .replace("that", "")
            .strip()
        )

        if content:
            write_memory(
                db=db,
                user_id=user_id,
                memory_type="explicit",
                memory_content=content,
                confidence_score=0.9,
            )
            response_text = f"I will remember that {content}."
            memory_written = True
        else:
            response_text = "What should I remember?"

    # ---------------------------------------------
    # LANGUAGE PREFERENCE
    # ---------------------------------------------
    elif memory_enabled and any(
        lang in user_message for lang in ["hindi", "english", "spanish"]
    ):
        if any(w in user_message for w in ["use", "reply", "always"]):
            for lang in ["hindi", "english", "spanish"]:
                if lang in user_message:
                    write_memory(
                        db=db,
                        user_id=user_id,
                        memory_type="preference_language",
                        memory_content=lang,
                        confidence_score=0.85,
                    )
                    response_text = f"Okay. I will use {lang} going forward."
                    memory_written = True
                    break

    # ---------------------------------------------
    # RESPONSE LENGTH PREFERENCE
    # ---------------------------------------------
    elif memory_enabled and any(
        w in user_message for w in ["short", "brief", "long", "detailed"]
    ):
        preference = (
            "short"
            if any(w in user_message for w in ["short", "brief"])
            else "long"
        )

        write_memory(
            db=db,
            user_id=user_id,
            memory_type="preference_response_length",
            memory_content=preference,
            confidence_score=0.85,
        )
        response_text = f"Noted. I will keep responses {preference}."
        memory_written = True

    # ---------------------------------------------
    # MEMORY READ
    # ---------------------------------------------
    elif memory_enabled and "what do you remember" in user_message:
        memories = get_active_memories(db, user_id)
        if memories:
            response_text = "Here is what I remember:\n" + "\n".join(
                f"- {m.memory_content}" for m in memories
            )
        else:
            response_text = "I don't have any memories yet."

    # ---------------------------------------------
    # MEMORY DISABLED
    # ---------------------------------------------
    elif not memory_enabled:
        response_text = "Memory features are disabled for your account."

    # ---------------------------------------------
    # DEFAULT
    # ---------------------------------------------
    else:
        response_text = "Message received. No memory or RAG action taken."

    return {
        "response": response_text,
        "memory_written": memory_written,
        "rag_used": rag_used,
    }
