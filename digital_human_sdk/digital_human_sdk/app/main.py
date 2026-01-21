import json
import logging
from typing import Optional, Any

from dotenv import load_dotenv
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent
from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor

# --------------------------------------------------
# ENV + LOGGING
# --------------------------------------------------
load_dotenv()

logger = logging.getLogger("orchestrator")
logging.basicConfig(level=logging.INFO)


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
    user_input = next(
        msg["content"]
        for msg in reversed(llm_messages)
        if msg["role"] == "user"
    )

    # =====================================================
    # 0️⃣ SAFETY
    # =====================================================
    logger.info("🛡️ Safety agent called")

    safety_result = await Runner.run(
        safe_agent,
        user_input,
        context=context,
    )
    safety_text = (safety_result.final_output or "").lower()

    if "cannot" in safety_text or "not allowed" in safety_text:
        logger.warning("🚫 Safety blocked request")
        for ch in safety_result.final_output:
            yield {"type": "token", "value": ch}
        return

    # =====================================================
    # 1️⃣ ROUTER (STREAMED)
    # =====================================================
    logger.info("🧭 Router agent called")

    router_stream = Runner.run_streamed(
        router_agent,
        user_input,
        context=context,
    )

    router_raw = ""
    async for event in router_stream.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            router_raw += event.data.delta

    router_raw = router_raw.strip()

    if router_raw.startswith("```"):
        router_raw = router_raw.replace("```json", "").replace("```", "").strip()

    logger.info(f"🧭 Router RAW OUTPUT => {router_raw}")

    try:
        router = json.loads(router_raw)
    except Exception as e:
        logger.error(f"❌ Router JSON invalid: {e}")
        router = {"use_tool": False, "use_memory": False}

    use_tool = router.get("use_tool", True)
    use_memory = router.get("use_memory", True)

    logger.info(f"use_tool={use_tool}, use_memory={use_memory}")

    memory_context = {}
    tool_context = {}

    # =====================================================
    # 2️⃣ MEMORY
    # =====================================================
    if use_memory:
        logger.info("🧠 Memory agent called")

        mem_result = await Runner.run(
            memory_agent,
            user_input,
            context=context,
        )

        try:
            memory_context = json.loads(mem_result.final_output or "{}")
        except Exception:
            memory_context = {}

        yield {"type": "memory_event", "payload": memory_context}

    # =====================================================
    # 3️⃣ TOOL
    # =====================================================
    if use_tool:
        logger.info("🛠️ Tool agent called")

        tool_result = await Runner.run(
            tool_agent,
            user_input,
            context=context,
        )

        logger.info(f"RAW_TOOL_OUTPUT={tool_result.final_output}")

        try:
            tool_payload = json.loads(tool_result.final_output or "{}")
            tool_name = tool_payload.get("tool", "none")
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
    # 4️⃣ REASONING (FULL LLM CONTEXT)
    # =====================================================
    logger.info("🧠 Reasoning agent called")

    reasoning_input = {
        "messages": llm_messages,
        "memory_context": memory_context,
        "tool_context": tool_context,
    }

    reasoning_stream = Runner.run_streamed(
        reasoning_agent,
        json.dumps(reasoning_input),
        context=context,
    )

    # =====================================================
    # 5️⃣ STREAM FINAL ANSWER
    # =====================================================
    async for event in reasoning_stream.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            yield {"type": "token", "value": event.data.delta}
