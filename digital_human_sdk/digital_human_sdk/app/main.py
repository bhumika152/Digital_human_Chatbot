
import json
from typing import Any, Optional

from dotenv import load_dotenv
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent
from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
from digital_human_sdk.app.intelligence.utils.json_utils import safe_json_loads

from services.memory_service import fetch_memory

# --------------------------------------------------
# ENV + LOGGING
# --------------------------------------------------
load_dotenv()

import logging
from digital_human_sdk.app.intelligence.logging_config import setup_logging

setup_logging()

logger = logging.getLogger("orchestrator")

ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}


# --------------------------------------------------
# CORE CHAT ORCHESTRATOR
# --------------------------------------------------
async def run_digital_human_chat(
    *,
    llm_messages: list,
    context: Optional[Any] = None,
):
    """
    llm_messages:
        [
            {"role": "system", "content": "..."},
            {"role": "system", "content": "Conversation summary..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "current input"}
        ]
    """
 
    # --------------------------------------------------
    # Extract CURRENT user input (last user message)
    # --------------------------------------------------

    logger.info("🔥 LOG TEST: orchestrator started")

    user_input = next(
        msg["content"]
        for msg in reversed(llm_messages)
        if msg["role"] == "user"
    )
 
    """
    Streaming Orchestrator (PRODUCTION SAFE)

    Contract:
    - user_input + context
    - LLM Context summary
    - memory/tool before reasoning
    - ONLY reasoning is streamed
    """

    # =====================================================
    # 1️⃣ SAFETY
    # =====================================================
    logger.info("🛡️ Safety agent called")

    safety_raw = await Runner.run(
        safe_agent,
        user_input,
        context=context,
        max_turns=1,
    )

    safety_text = (safety_raw.final_output or "").lower()
    if "not allowed" in safety_text or "cannot" in safety_text:
        logger.warning("🚫 Safety blocked request")
        for ch in safety_raw.final_output or "":
            yield {"type": "token", "value": ch}
        return

    logger.info("✅ Safety passed")

    # =====================================================
    # 2️⃣ ROUTER
    # =====================================================
    logger.info("🧭 Router agent called")

    router_raw = await Runner.run(
        router_agent,
        user_input,
        context=context,
        max_turns=1,
    )

    router = safe_json_loads(router_raw.final_output, default={})

    use_tool = router.get("use_tool", False)
    use_memory = router.get("use_memory", False)
    intent = router.get("intent")
    memory_key = router.get("memory_key")

    logger.info(
        "🧭 Router | tool=%s memory=%s intent=%s",
        use_tool,
        use_memory,
        intent,
    )

    memory_action = {}
    memory_data = []
    tool_context = {}

    # =====================================================
    # 3️⃣ MEMORY WRITE
    # =====================================================
    if use_memory and intent == "write" and context.enable_memory:
        logger.info("🧠 Memory agent called (WRITE)")

        mem_raw = await Runner.run(
            memory_agent,
            user_input,
            context=context,
            max_turns=1,
        )

        memory_action = safe_json_loads(mem_raw.final_output, default={})
        action = memory_action.get("action")

        if action in ALLOWED_MEMORY_ACTIONS and action != "none":
            yield {"type": "memory_event", "payload": memory_action}
        else:
            memory_action = {}

    # =====================================================
    # 4️⃣ MEMORY READ
    # =====================================================
    if use_memory and intent == "read" and memory_key and context.enable_memory:
        logger.info("📥 Fetching memory from DB")

        memory_data = fetch_memory(
            db=context.db,
            user_id=context.user_id,
            memory_type=memory_key,
            limit=1,
        )

    # =====================================================
    # 5️⃣ TOOL
    # =====================================================
    # if use_tool and context.enable_tools:
    #     logger.info("🛠️ Tool agent called")

    #     tool_raw = await Runner.run(
    #         tool_agent,
    #         user_input,
    #         context=context,
    #         max_turns=1,
    #     )


    #     tool_payload = safe_json_loads(tool_raw.final_output, default={})
    #     tool_name = tool_payload.get("tool_name") or tool_payload.get("tool")
    #     tool_args = tool_payload.get("arguments", {})
        

    #     logger.info(
    #         f"🛠️ Tool selected | tool={tool_name} | args={tool_args}"
    #     )


    #     if tool_name:
    #         try:
                
    #             tool_result = ToolExecutor.execute(tool_name, tool_args)
    #             tool_context = (
    #                 tool_result.model_dump()
    #                 if hasattr(tool_result, "model_dump")
    #                 else tool_result
    #             )
    #         except Exception as exc:
    #             logger.exception("🔥 Tool execution failed")
    #             tool_context = {"error": str(exc)}
    if use_tool:
            logger.info("🛠️ Tool agent called")
    
            tool_result = await Runner.run(
                tool_agent,
                user_input,
                context=context,
            )
    
            logger.info(f"RAW_TOOL_OUTPUT={tool_result.final_output}")
    
            try:
                tool_payload = safe_json_loads(tool_result.final_output, default={})

                tool_name = (
                    tool_payload.get("tool_name")
                    or tool_payload.get("tool")
                    or "none"
                )

                tool_args = tool_payload.get("arguments", {})
    
                logger.info(f"EXECUTING_TOOL name={tool_name}, args={tool_args}")
    
                tool_exec_result = ToolExecutor.execute(tool_name, tool_args)
    
                if hasattr(tool_exec_result, "model_dump"):
                    tool_context = tool_exec_result.model_dump()
                else:
                    tool_context = tool_exec_result
    
                logger.info(f"TOOL_RESULT={tool_context}")
    
            except Exception as e:
                logger.exception("❌ Tool execution failed")
                tool_context = {"error": str(e)}
    
 
    # =====================================================
    # 6️⃣ REASONING (STREAMED)
    # =====================================================
    logger.info("🧠 Reasoning agent called")

    reasoning_input = {
        "messages": llm_messages,
        "memory_action": memory_action,
        "memory_data": memory_data,
        "tool_context": tool_context,
    }

    reasoning_stream = Runner.run_streamed(
        reasoning_agent,
        json.dumps(reasoning_input),
        context=context,  # 🔑 REQUIRED
    )

    # =====================================================
    # 7️⃣ STREAM TOKENS
    # =====================================================
    async for event in reasoning_stream.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            yield {"type": "token", "value": event.data.delta}
# import json
# import logging
# from typing import Any, Optional

# from dotenv import load_dotenv
# from agents import Runner
# from openai.types.responses import ResponseTextDeltaEvent

# from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent
# from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
# from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
# from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
# from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
# from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
# from digital_human_sdk.app.intelligence.utils.json_utils import safe_json_loads

# from services.memory_service import fetch_memory

# load_dotenv()

# logger = logging.getLogger("orchestrator")
# logger.setLevel(logging.INFO)

# ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}


# async def run_digital_human_chat(
#     *,
#     user_input: str,
#     llm_context: dict,
#     context: Optional[Any] = None,
# ):
#     """
#     Streaming Orchestrator (PRODUCTION SAFE)

#     Contract:
#     - user_input → raw user message
#     - llm_context → prepared context (history, system, etc.)
#     - context → AgentContext (db, user_id, flags)
#     """

#     # =====================================================
#     # 1️⃣ SAFETY
#     # =====================================================
#     logger.info("🛡️ Safety agent called")

#     safety_raw = await Runner.run(
#         safe_agent,
#         user_input,
#         context=context,
#         max_turns=1,
#     )

#     safety_text = (safety_raw.final_output or "").lower()
#     if "not allowed" in safety_text or "cannot" in safety_text:
#         logger.warning("🚫 Safety blocked request")
#         for ch in safety_raw.final_output or "":
#             yield {"type": "token", "value": ch}
#         return

#     logger.info("✅ Safety passed")

#     # =====================================================
#     # 2️⃣ ROUTER
#     # =====================================================
#     logger.info("🧭 Router agent called")

#     router_raw = await Runner.run(
#         router_agent,
#         user_input,
#         context=context,
#         max_turns=1,
#     )

#     router = safe_json_loads(router_raw.final_output, default={})

#     use_tool = router.get("use_tool", False)
#     use_memory = router.get("use_memory", False)
#     intent = router.get("intent")
#     memory_key = router.get("memory_key")

#     logger.info(
#         "🧭 Router | tool=%s memory=%s intent=%s",
#         use_tool,
#         use_memory,
#         intent,
#     )

#     memory_action = {}
#     memory_data = []
#     tool_context = {}

#     # =====================================================
#     # 3️⃣ MEMORY WRITE
#     # =====================================================
#     if use_memory and intent == "write" and context.enable_memory:
#         logger.info("🧠 Memory agent called (WRITE)")

#         mem_raw = await Runner.run(
#             memory_agent,
#             user_input,
#             context=context,
#             max_turns=1,
#         )

#         memory_action = safe_json_loads(mem_raw.final_output, default={})
#         action = memory_action.get("action")

#         if action in ALLOWED_MEMORY_ACTIONS and action != "none":
#             yield {"type": "memory_event", "payload": memory_action}
#         else:
#             memory_action = {}

#     # =====================================================
#     # 4️⃣ MEMORY READ
#     # =====================================================
#     if use_memory and intent == "read" and memory_key and context.enable_memory:
#         logger.info("📥 Fetching memory from DB")

#         memory_data = fetch_memory(
#             db=context.db,
#             user_id=context.user_id,
#             memory_type=memory_key,
#             limit=1,
#         )

#     # =====================================================
#     # 5️⃣ TOOL
#     # =====================================================
#     if use_tool and context.enable_tools:
#         logger.info("🛠️ Tool agent called")

#         tool_raw = await Runner.run(
#             tool_agent,
#             user_input,
#             context=context,
#             max_turns=1,
#         )

#         tool_payload = safe_json_loads(tool_raw.final_output, default={})
#         tool_name = tool_payload.get("tool_name") or tool_payload.get("tool")
#         tool_args = tool_payload.get("arguments", {})

#         if tool_name:
#             try:
#                 tool_result = ToolExecutor.execute(tool_name, tool_args)
#                 tool_context = (
#                     tool_result.model_dump()
#                     if hasattr(tool_result, "model_dump")
#                     else tool_result
#                 )
#             except Exception as exc:
#                 logger.exception("🔥 Tool execution failed")
#                 tool_context = {"error": str(exc)}

#     # =====================================================
#     # 6️⃣ REASONING (STREAMED)
#     # =====================================================
#     logger.info("🧠 Reasoning agent called")

#     reasoning_stream = Runner.run_streamed(
#         reasoning_agent,
#         json.dumps(llm_context),
#         context=context,  # 🔑 VERY IMPORTANT
#     )

#     # =====================================================
#     # 7️⃣ STREAM TOKENS
#     # =====================================================
#     async for event in reasoning_stream.stream_events():
#         if (
#             event.type == "raw_response_event"
#             and isinstance(event.data, ResponseTextDeltaEvent)
#         ):
#             yield {"type": "token", "value": event.data.delta}
