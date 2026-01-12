# from dotenv import load_dotenv
# load_dotenv()
# import asyncio
# from app.intelligence.orchestration.orchestrator import Orchestrator

# async def main():
#     orchestrator = Orchestrator()

#     print("---- TURN 1 ----")
#     await orchestrator.handle_user_query(
#         user_input="I prefer cold places like Manali and Shimla.",
#         user_id=1,
#     )

#     print("---- TURN 2 ----")
#     response = await orchestrator.handle_user_query(
#         user_input="Suggest a destination for me",
#         user_id=1,
#     )

#     print(response)


# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio
from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from services.memory_service import MemoryService


async def test_memory_service():
    print("\n🧠 MEMORY SERVICE TEST STARTED")
    print("=" * 60)

    db = SessionLocal()
    memory_service = MemoryService(db)

    user_id = 1

    # ------------------------------------------------
    # 1️⃣ STORE MEMORY (LONG TERM)
    # ------------------------------------------------
    print("\n🔹 Storing long-term memory...")
    memory_service.store_memory(
        user_id=user_id,
        memory_type="long_term",
        content="User prefers cold places like Manali and Shimla",
        confidence=0.95,
    )

    # ------------------------------------------------
    # 2️⃣ STORE MEMORY (SHORT TERM with TTL)
    # ------------------------------------------------
    print("\n🔹 Storing short-term memory with TTL...")
    memory_service.store_memory(
        user_id=user_id,
        memory_type="short_term",
        content="User is planning a vacation",
        confidence=0.8,
        ttl_minutes=1,  # expires quickly
    )

    # ------------------------------------------------
    # 3️⃣ FETCH MEMORY
    # ------------------------------------------------
    print("\n🔹 Fetching long-term memory...")
    memories = memory_service.fetch_memory(
        user_id=user_id,
        memory_type="long_term",
    )

    for mem in memories:
        print("   ➤", mem.memory_content, "| confidence:", mem.confidence_score)

    # ------------------------------------------------
    # 4️⃣ UPDATE MEMORY
    # ------------------------------------------------
    print("\n🔹 Updating long-term memory...")
    updated = memory_service.update_memory(
        user_id=user_id,
        memory_type="long_term",
        new_value="User strongly prefers cold hill stations like Manali, Shimla, and Leh",
        confidence_score=0.99,
    )

    if updated:
        print("   ✅ Updated memory:", updated.memory_content)

    # ------------------------------------------------
    # 5️⃣ GET ACTIVE MEMORIES
    # ------------------------------------------------
    print("\n🔹 Fetching all active memories...")
    active_memories = memory_service.get_active_memories(user_id)

    for mem in active_memories:
        print(
            f"   ➤ [{mem.memory_type}] {mem.memory_content} | active={mem.is_active}"
        )

    # ------------------------------------------------
    # 6️⃣ SOFT DELETE MEMORY
    # ------------------------------------------------
    print("\n🔹 Soft deleting long-term memory...")
    deleted_count = memory_service.soft_delete_memory(
        user_id=user_id,
        memory_type="long_term",
    )

    print(f"   ✅ Soft deleted {deleted_count} memory record(s)")

    # ------------------------------------------------
    # 7️⃣ VERIFY DELETE
    # ------------------------------------------------
    print("\n🔹 Verifying after delete...")
    remaining = memory_service.get_active_memories(user_id)

    for mem in remaining:
        print(
            f"   ➤ [{mem.memory_type}] {mem.memory_content} | active={mem.is_active}"
        )

    # ------------------------------------------------
    # 8️⃣ CLEANUP EXPIRED MEMORIES
    # ------------------------------------------------
    print("\n🔹 Running cleanup for expired memories...")
    expired_count = memory_service.cleanup_expired_memories()
    print(f"   🧹 Cleaned {expired_count} expired memory record(s)")

    db.close()

    print("\n✅ MEMORY SERVICE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_memory_service())
