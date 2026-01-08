import json
from dotenv import load_dotenv
from agents import Runner

from digital_human_sdk.app.intelligence.safety.safety_agent import safe_agent
from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent

from digital_human_sdk.app.intelligence.contracts.tool_request import ToolRequest
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor

load_dotenv()
from agents.models import set_default_model_provider
from agents.models.gemini_provider import GeminiProvider
import os

set_default_model_provider(
    GeminiProvider(
        api_key=os.getenv("GEMINI_API_KEY")
    )
)
async def run_digital_human_chat(
    *,
    user_input: str,
    chat_history: list,
    user_config: dict,
):
    # =====================================================
    # 0️⃣ SAFETY PRE-CHECK (ChatGPT style)
    # =====================================================
    safety_raw = await Runner.run(
        safe_agent,
        user_input,
        max_turns=1,
    )

    safety = json.loads(safety_raw.final_output)

    if not safety["safe"]:
        for ch in safety["message"]:
            yield {"type": "token", "value": ch}
        return

    # =====================================================
    # 1️⃣ ROUTER
    # =====================================================
    router_raw = await Runner.run(router_agent, user_input)
    router = json.loads(router_raw.final_output or "{}")

    use_memory = router.get("use_memory") and user_config.get("memory_enabled", False)
    use_tool = router.get("use_tool") and user_config.get("tool_enabled", False)

    memory_context = {}
    tool_context = {}

    # =====================================================
    # 2️⃣ MEMORY
    # =====================================================
    if use_memory:
        mem_raw = await Runner.run(memory_agent, user_input)
        memory_context = json.loads(mem_raw.final_output or "{}")
        yield {"type": "memory_event", "payload": memory_context}

    # =====================================================
    # 3️⃣ TOOL
    # =====================================================
    if use_tool:
        tool_raw = await Runner.run(tool_agent, user_input)
        try:
            req = ToolRequest(**json.loads(tool_raw.final_output))
            tool_context = ToolExecutor.execute(req)
        except Exception:
            tool_context = {"error": "Tool failed"}

    # =====================================================
    # 4️⃣ REASONING
    # =====================================================
    reasoning_input = {
        "user_input": user_input,
        "chat_history": chat_history,
        "memory_context": memory_context,
        "tool_context": tool_context,
        "capabilities": user_config,
    }

    reasoning_raw = await Runner.run(
        reasoning_agent,
        json.dumps(reasoning_input),
    )

    # =====================================================
    # 5️⃣ POST-SAFETY (Output moderation)
    # =====================================================
    post_safety = await Runner.run(
        safe_agent,
        reasoning_raw.final_output,
        max_turns=1,
    )

    post = json.loads(post_safety.final_output)

    if not post["safe"]:
        for ch in post["message"]:
            yield {"type": "token", "value": ch}
        return

    for ch in reasoning_raw.final_output:
        yield {"type": "token", "value": ch}
