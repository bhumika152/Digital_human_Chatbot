# import json
# from agents import Runner

# from app.intelligence.our_agents.memory_agent import memory_agent
# from app.intelligence.our_agents.reasoning_agent import reasoning_agent
# from app.intelligence.memory.memory_service import MemoryService


# class Orchestrator:
#     def __init__(self):
#         self.memory_service = MemoryService()

#     async def handle_user_query(
#         self,
#         user_input: str,
#         user_id: int,
#         session_id: str | None = None,
#     ):
#         """
#         Main orchestration entrypoint
#         """

#         # --------------------------------------------------
#         # 1️⃣ Ask MEMORY AGENT what to do
#         # --------------------------------------------------
#         memory_result = await Runner.run(memory_agent, user_input)

#         raw_output = memory_result.final_output
#         print("\n🧠 RAW MEMORY OUTPUT:")
#         print(raw_output)

#         try:
#             memory_decision = json.loads(raw_output)
#         except Exception as e:
#             print("❌ Failed to parse memory decision:", e)
#             memory_decision = {"action": "none"}

#         memory_context = ""

#         # --------------------------------------------------
#         # 2️⃣ Execute MEMORY ACTIONS (DB)
#         # --------------------------------------------------
#         action = memory_decision.get("action")

#         if action == "store":
#             self.memory_service.store_memory(
#                 user_id=user_id,
#                 memory_type=memory_decision["memory_type"],
#                 content=memory_decision["content"],
#                 confidence=memory_decision.get("confidence", 1.0),
#             )

#         elif action == "fetch":
#             memories = self.memory_service.fetch_memory(
#                 user_id=user_id,
#                 memory_type=memory_decision.get("memory_type"),
#             )

#             if memories:
#                 memory_context = "User preferences and past context:\n"
#                 for mem in memories:
#                     memory_context += f"- {mem}\n"

#         # --------------------------------------------------
#         # 3️⃣ Build FINAL PROMPT (🔥 MOST IMPORTANT STEP)
#         # --------------------------------------------------
#         final_prompt = f"""
# {memory_context}

# User query:
# {user_input}

# Instructions:
# - If preferences exist, use them.
# - Be concise and helpful.
# """

#         # --------------------------------------------------
#         # 4️⃣ Call REASONING AGENT
#         # --------------------------------------------------
#         reasoning_result = await Runner.run(
#             reasoning_agent,
#             final_prompt
#         )

#         return reasoning_result.final_output
import json
from agents import Runner

from app.intelligence.our_agents.memory_agent import memory_agent
from app.intelligence.our_agents.reasoning_agent import reasoning_agent
from app.intelligence.memory.memory_service import MemoryService


class Orchestrator:
    def __init__(self):
        self.memory_service = MemoryService()

    async def handle_user_query(
        self,
        user_input: str,
        user_id: int,
        session_id: str | None = None,
    ):
        """
        Main orchestration entrypoint
        """

        # --------------------------------------------------
        # 1️⃣ Ask MEMORY AGENT what to do
        # --------------------------------------------------
        memory_result = await Runner.run(memory_agent, user_input)

        raw_output = memory_result.final_output
        print("\n🧠 RAW MEMORY OUTPUT:")
        print(raw_output)

        try:
            memory_decision = json.loads(raw_output)
        except Exception as e:
            print("❌ Failed to parse memory decision:", e)
            memory_decision = {"action": "none"}

        action = memory_decision.get("action", "none")

        # --------------------------------------------------
        # 2️⃣ Execute MEMORY ACTIONS (DB)
        # --------------------------------------------------
        if action == "store":
            memory_type = memory_decision["memory_type"]
            content = memory_decision["content"]
            confidence = memory_decision.get("confidence", 1.0)

            # 🔁 Check if memory already exists
            existing = self.memory_service.fetch_memory(
                user_id=user_id,
                memory_type=memory_type,
                limit=1,
            )

            if existing:
                print("🔁 Updating existing memory")
                self.memory_service.update_memory(
                    user_id=user_id,
                    memory_type=memory_type,
                    new_value=content,
                    confidence_score=confidence,
                )
            else:
                print("🆕 Storing new memory")
                self.memory_service.store_memory(
                    user_id=user_id,
                    memory_type=memory_type,
                    content=content,
                    confidence=confidence,
                )

        elif action == "forget":
            print("🧹 Soft deleting memory")
            self.memory_service.soft_delete_memory(
                user_id=user_id,
                memory_type=memory_decision.get("memory_type"),
            )

        # --------------------------------------------------
        # 3️⃣ Load ACTIVE MEMORY CONTEXT (🔥 IMPORTANT)
        # --------------------------------------------------
        memory_context = ""
        active_memories = self.memory_service.get_active_memories(user_id)

        if active_memories:
            memory_context = "User memory context:\n"
            for mem in active_memories:
                memory_context += f"- {mem.memory_content}\n"

        # --------------------------------------------------
        # 4️⃣ Build FINAL PROMPT
        # --------------------------------------------------
        final_prompt = f"""
{memory_context}

User query:
{user_input}

Instructions:
- Use user memory if relevant.
- Be concise, helpful, and accurate.
"""

        # --------------------------------------------------
        # 5️⃣ Call REASONING AGENT
        # --------------------------------------------------
        reasoning_result = await Runner.run(
            reasoning_agent,
            final_prompt,
        )

        return reasoning_result.final_output
