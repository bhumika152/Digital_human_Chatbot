
from services.memory_service import (
    write_memory,
    update_memory,
    fetch_memory,
    soft_delete_memory,
    fetch_memory,
)
import re
import unicodedata

def normalize_text(text: str | None) -> str | None:
    if not text:
        return text

    text = unicodedata.normalize("NFKC", text)   # Unicode safe
    text = text.lower().strip()                  # lowercase + trim
    text = re.sub(r"\s+", " ", text)             # collapse ALL spaces
    return text


def apply_memory_action(db, user_id: int, action: dict):
    try:
        action_type = action["action"]
        key = normalize_text(action["key"])
        value = normalize_text(action.get("value"))
        confidence = action.get("confidence")

        if action_type in ("save", "update"):
            memory = update_memory(
                db=db,
                user_id=user_id,
                memory_type=key,
                new_value=value,
                confidence_score=confidence,
            )

            if memory is None:
                write_memory(
                    db=db,
                    user_id=user_id,
                    memory_type=key,
                    memory_content=value,
                    confidence_score=confidence,
                )

        elif action_type == "delete":
            soft_delete_memory(
                db=db,
                user_id=user_id,
                memory_type=key,
            )

        else:
            raise ValueError(f"Unknown memory action: {action_type}")

        db.commit()   # ✅ ONE COMMIT
        return True

    except Exception:
        db.rollback()
        raise
