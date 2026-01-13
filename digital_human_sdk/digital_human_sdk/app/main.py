
import json
import logging
from dotenv import load_dotenv
from agents import Runner

from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent
from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
from digital_human_sdk.app.intelligence.contracts.tool_request import ToolRequest
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
from digital_human_sdk.app.intelligence.utils.json_utils import safe_json_loads
from services.memory_service import fetch_memory
from digital_human_sdk.app.litellm_streaming import stream_llm_response

load_dotenv()

logger = logging.getLogger("orchestrator")
logger.setLevel(logging.INFO)

ALLOWED_MEMORY_ACTIONS = {"save", "update", "delete", "none"}

async def run_digital_human_chat(*, user_input: str, db=None, user_id=None):
    """
    Streaming Orchestrator
    """

    # =====================================================
    # 1️⃣ SAFETY
    # =====================================================
    logger.info("🛡️ Safety agent called")

    safety_raw = await Runner.run(safe_agent, user_input, max_turns=1)
    safety_text = (safety_raw.final_output or "").lower()

    if "not allowed" in safety_text or "cannot" in safety_text:
        logger.warning("🚫 Safety blocked request")
        for ch in safety_raw.final_output:
            yield {"type": "token", "value": ch}
        return

    logger.info("✅ Safety passed")

    # =====================================================
    # 2️⃣ ROUTER
    # =====================================================
    logger.info("🧭 Router agent called")

    router_raw = await Runner.run(router_agent, user_input)

    try:
        router = safe_json_loads(router_raw.final_output, default={})

    except json.JSONDecodeError:
        logger.error("❌ Router returned invalid JSON")
        router = {}

    use_tool = router.get("use_tool", False)
    use_memory = router.get("use_memory", False)
    intent = router.get("intent")              # "read" | "write"
    memory_key = router.get("memory_key")      # e.g. "food_preference"

    logger.info(
        f"🧭 Router | tool={use_tool}, memory={use_memory}, intent={intent}"
    )

    memory_action = {}
    memory_data = []
    tool_context = {}

# =====================================================
# 3️⃣ MEMORY WRITE (save / update / delete)
# =====================================================
    if use_memory and intent == "write":
        logger.info("🧠 Memory agent called (WRITE)")

        mem_raw = await Runner.run(memory_agent, user_input)

        memory_action = safe_json_loads(mem_raw.final_output, default={})
        action = memory_action.get("action")

        logger.info(f"🧠 Parsed memory action: {memory_action}")

        if action in {"save", "update", "delete"}:
            yield {
                "type": "memory_event",
                "payload": memory_action,
            }
        else:
            logger.info(f"🧠 No-op memory action: {action}")
            memory_action = {}

    # =====================================================
    # 4️⃣ MEMORY READ (backend fetch)
    # =====================================================
    if use_memory and intent == "read" and memory_key:
        logger.info("📥 Fetching active memory from DB")

        memory_data = fetch_memory(
            db=db,
            user_id=user_id,
            memory_type=memory_key,
            limit=1,
        )
 
    # =====================================================
    # 3️⃣ TOOL
    # =====================================================
    if use_tool:
        logger.info("🛠️ Tool agent called")

        tool_raw = await Runner.run(tool_agent, user_input)
        logger.info(f"RAW_TOOL_OUTPUT={tool_raw.final_output}")

        tool_payload = safe_json_loads(tool_raw.final_output, default={})

        tool_name = tool_payload.get("tool_name") or tool_payload.get("tool")
        tool_args = tool_payload.get("arguments", {})

        if tool_name:
            try:
                logger.info(f"EXECUTING_TOOL name={tool_name}, args={tool_args}")

                tool_result = ToolExecutor.execute(tool_name, tool_args)

                if hasattr(tool_result, "model_dump"):
                    tool_context = tool_result.model_dump()
                else:
                    tool_context = tool_result

                logger.info(f"TOOL_RESULT={tool_context}")

            except Exception as e:
                logger.exception("Tool failed")
                tool_context = {"error": str(e)}
        else:
            tool_context = {}

 
        # =====================================================
    # 6️⃣ REASONING (NON-STREAMING)
    # =====================================================
    logger.info("🧠 Reasoning agent called")

    reasoning_input = {
        "user_input": user_input,
        "memory_action": memory_action,
        "memory_data": memory_data,
        "tool_context": tool_context,
    }

    reasoning_raw = await Runner.run(
        reasoning_agent,
        json.dumps(reasoning_input),
    )

    final_text = reasoning_raw.final_output or ""

    # =====================================================
    # 7️⃣ REAL TOKEN STREAMING (LLM ONLY)
    # =====================================================

    async for token in stream_llm_response(final_text):
        if not token:
            continue

        yield {
            "type": "token",
            "value": token,
        }
