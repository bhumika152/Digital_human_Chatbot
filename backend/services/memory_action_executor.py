from memory_service import (
    write_memory,
    update_memory,
    delete_memory,
    get_active_memories
)

def apply_memory_action(db, user_id: int, action: dict):
    action_type = action["action"]
    key = action["key"]
    value = action.get("value")
    confidence = action.get("confidence")

    if action_type == "save":
        write_memory(
            db=db,
            user_id=user_id,
            memory_type=key,
            memory_content=value,
            confidence_score=confidence
        )

    elif action_type == "update":
        update_memory(
            db=db,
            user_id=user_id,
            memory_type=key,
            new_value=value,
            confidence_score=confidence
        )

    elif action_type == "delete":
        soft_delete_memory(
            db=db,
            user_id=user_id,
            memory_type=key
        )
