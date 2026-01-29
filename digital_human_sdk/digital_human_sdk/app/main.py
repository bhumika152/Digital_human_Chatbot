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
from digital_human_sdk.app.intelligence.contracts.safety_schema import SafetySchema
from digital_human_sdk.app.intelligence.safety.safety_agent import safety_response
from services.memory_service import MemoryService
#from services.memory_service import fetch_semantic_memory

load_dotenv()
import logging
from digital_human_sdk.app.intelligence.logging_config import setup_logging

setup_logging()
# --------------------------------------------------
# LOGGER SETUP
# --------------------------------------------------
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
    # --------------------------------------------------
    # 1️⃣ USER INPUT
    # --------------------------------------------------

    logger.info("🔥 LOG TEST: orchestrator started")

    user_input = next(
        msg["content"]
        for msg in reversed(llm_messages)
        if msg["role"] == "user"
    )

    logger.info("🧑 USER_INPUT | %s", user_input)
    logger.info(
        "🧩 CONTEXT | user_id=%s | enable_memory=%s | db=%s",
        getattr(context, "user_id", None),
        getattr(context, "enable_memory", None),
        getattr(context, "db", None),
    )


    # --------------------------------------------------
    # 2️⃣ SAFETY (AUTHORITATIVE)
    # --------------------------------------------------
    logger.info("🛡️ Safety agent called")

    safety_raw = await Runner.run(
        safe_agent,
        user_input,
        context=context,
        max_turns=1,
    )

    parsed = safe_json_loads(safety_raw.final_output, default={})

    try:
        safety_payload = SafetySchema(**parsed).model_dump()
    
    except Exception:
        safety_payload = {
        "safe": False,
        "message": "I can’t help with that request , Invalid safety response(JSON Parsing Fails)"
        }

    if not safety_payload["safe"]:
        logger.warning("🚫 Safety blocked request")
        yield {
            "type": "token",
            "value": safety_payload["message"],
        }
        return


    logger.info("✅ Safety passed")
    # --------------------------------------------------
    # 3️⃣ MEMORY READ
    # --------------------------------------------------
    memory_data = []
    memory_found = False

    if context and context.enable_memory:
        logger.info("📥 Fetching semantic memory (via MemoryService)")

        memory_data = MemoryService.read(
            user_id=context.user_id,
            query=user_input,
            limit=3,
        )

        memory_found = len(memory_data) > 0


    logger.info(
        "🧠 MEMORY_RESULT | found=%s | count=%d",
        memory_found,
        len(memory_data),
    )

    # --------------------------------------------------
    # 4️⃣ ROUTER
    # --------------------------------------------------
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

    logger.info(
        "🧭 ROUTER_DECISION | tool=%s | memory=%s | intent=%s",
        use_tool,
        use_memory,
        intent,
    )

    memory_action = {}
    tool_context = {}
    # --------------------------------------------------
    # 5️⃣ MEMORY WRITE (EVENT EMIT ONLY)
    # --------------------------------------------------
    if use_memory and intent == "write" and context.enable_memory:
        logger.info("🧠 Memory agent called (WRITE)")

        mem_raw = await Runner.run(
            memory_agent,
            user_input,
            context=context,
            max_turns=1,
        )

        memory_action = safe_json_loads(mem_raw.final_output, default={})
        action_type = memory_action.get("action")

        logger.info(
            "🧠 MEMORY_DECISION | %s",
            json.dumps(memory_action, indent=2),
        )

        if action_type in ALLOWED_MEMORY_ACTIONS and action_type != "none":
            # 🔥 ONLY EMIT EVENT
            yield {
                "type": "memory_event",
                "payload": memory_action,
            }

        # Orchestrator should NOT keep memory
        memory_action = {}


    # --------------------------------------------------
    # 6️⃣ TOOL
    # --------------------------------------------------
    if use_tool:
        logger.info("🛠️ Tool agent called")

        tool_raw = await Runner.run(
            tool_agent,
            user_input,
            context=context,
        )

        tool_payload = safe_json_loads(tool_raw.final_output, default={})
        tool_name = tool_payload.get("tool", "none")
        tool_args = tool_payload.get("arguments", {})

        logger.info("🛠️ TOOL_EXEC | name=%s | args=%s", tool_name, tool_args)

        try:
            tool_result = ToolExecutor.execute(tool_name, tool_args)
            tool_context = (
                tool_result.model_dump()
                if hasattr(tool_result, "model_dump")
                else tool_result
            )
        except Exception as exc:
            logger.exception("🔥 Tool execution failed")
            tool_context = {"error": str(exc)}

    # --------------------------------------------------
    # 7️⃣ REASONING
    # --------------------------------------------------
    reasoning_input = {
        "messages": llm_messages,
        "safety": safety_payload,
        "memory_action": memory_action,
        "memory_data": memory_data,
        "memory_found": memory_found,
        "tool_context": tool_context,
    }

    logger.info(
        "🧠 REASONING_INPUT_SNAPSHOT\n%s",
        json.dumps(reasoning_input, indent=2, default=str),
    )

    reasoning_stream = Runner.run_streamed(
        reasoning_agent,
        json.dumps(reasoning_input),
        context=context,
    )

    # --------------------------------------------------
    # 8️⃣ STREAM TOKENS
    # --------------------------------------------------
    async for event in reasoning_stream.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            yield {"type": "token", "value": event.data.delta}
