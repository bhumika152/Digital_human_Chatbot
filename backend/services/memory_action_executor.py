
import logging

from services.memory_service import (
    write_or_update_memory,
    delete_semantic_memory,
)

logger = logging.getLogger("memory_action_executor")
logger.setLevel(logging.INFO)


def apply_memory_action(db, user_id: int, action: dict) -> bool:
    logger.info(
        "🧠 APPLY_MEMORY_ACTION | user_id=%s | action=%s",
        user_id,
        action,
    )

    # 🔥 CRITICAL FIX
    if db is None:
        logger.error("❌ DB session is None — cannot save memory")
        return False

    try:
        action_type = action.get("action")
        content = action.get("memory_text")  # ✅ CORRECT KEY
        confidence = action.get("confidence", 1.0)

        logger.info(
            "🧠 Memory Parsed | type=%s | content=%s | confidence=%s",
            action_type,
            content,
            confidence,
        )

        if not content:
            logger.warning("⚠️ Memory content empty — skipping save")
            return False

        if action_type in ("save", "update"):
            logger.info("💾 Writing memory to DB")

            write_or_update_memory(
                db=db,
                user_id=user_id,
                memory_text=content,
                confidence_score=confidence,
                action=action_type,
            )

        elif action_type == "delete":
            logger.info("🗑️ Deleting memory from DB")

            delete_semantic_memory(
                db=db,
                user_id=user_id,
                query=content,
            )

        else:
            logger.warning("⚠️ Unknown memory action type: %s", action_type)
            return False

        db.commit()
        logger.info("✅ DB COMMIT SUCCESS")
        return True

    except Exception as e:
        logger.exception("🔥 MEMORY WRITE FAILED — rolling back")
        db.rollback()
        return False
