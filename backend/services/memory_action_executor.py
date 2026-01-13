# from services.memory_service import (
#     write_memory,
#     update_memory,
#     soft_delete_memory,
#     fetch_memory,
#     get_active_memories,
# )
# def apply_memory_action(db, user_id: int, action: dict):
#     try:
#         action_type = action["action"]
#         key = action["key"]
#         value = action.get("value")
#         confidence = action.get("confidence")

#         if action_type == "save":
#             write_memory(
#                 db=db,
#                 user_id=user_id,
#                 memory_type=key,
#                 memory_content=value,
#                 confidence_score=confidence,
#             )

#         elif action_type == "update":
#             update_memory(
#                 db=db,
#                 user_id=user_id,
#                 memory_type=key,
#                 new_value=value,
#                 confidence_score=confidence,
#             )

#         elif action_type =="fetch":
#             fetch_memory(
#                 db=db,
#                 user_id=user_id,
#                 memory_type =key,
#                 new_value=value,
#                 confidence_score= confidence,
#             )

#         elif action_type == "delete":
#             soft_delete_memory(
#                 db=db,
#                 user_id=user_id,
#                 memory_type=key,
#             )

#         else:
#             raise ValueError(f"Unknown memory action: {action_type}")

#         db.commit()
#         return True

#     except Exception:
#         db.rollback()
#         raise
from services.memory_service import (
    write_memory,
    update_memory,
    soft_delete_memory,
    fetch_memory,
)

def apply_memory_action(db, user_id: int, action: dict):
    try:
        action_type = action["action"]
        key = action["key"]
        value = action.get("value")
        confidence = action.get("confidence")

        # -------------------------
        # SAVE / UPDATE (UPSERT)
        # -------------------------
        if action_type in ("save", "update"):
            updated = update_memory(
                db=db,
                user_id=user_id,
                memory_type=key,
                new_value=value,
                confidence_score=confidence,
            )

            # If no active memory → WRITE new
            if updated is None:
                write_memory(
                    db=db,
                    user_id=user_id,
                    memory_type=key,
                    memory_content=value,
                    confidence_score=confidence,
                )

        # -------------------------
        # DELETE (SOFT)
        # -------------------------
        elif action_type == "delete":
            soft_delete_memory(
                db=db,
                user_id=user_id,
                memory_type=key,
            )

        else:
            raise ValueError(f"Unknown memory action: {action_type}")

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise
