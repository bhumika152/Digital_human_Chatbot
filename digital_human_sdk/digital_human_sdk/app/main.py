import json
from dotenv import load_dotenv
from agents import Runner

# -----------------------------
# Agents
# -----------------------------
from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.memory_agent import memory_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.our_agents.reasoning_agent import reasoning_agent

# -----------------------------
# Tool system
# -----------------------------
from digital_human_sdk.app.intelligence.contracts.tool_request import ToolRequest
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor

load_dotenv()


async def run_digital_human_chat(
    *,
    user_input: str,
    chat_history: list,
    user_config: dict,
):
    """
    Digital Human SDK Orchestrator (STREAMING)

    Emits events:
      - { type: "memory_event", payload: {...} }
      - { type: "token", value: "..." }

    SDK does NOT touch DB
    """

    # =====================================================
    # 1️⃣ ROUTER (INTENT ONLY)
    # =====================================================
    router_result = await Runner.run(router_agent, user_input)

    try:
        router_decision = json.loads(router_result.final_output)
    except Exception:
        router_decision = {}

    router_wants_memory = router_decision.get("use_memory", False)
    router_wants_tool = router_decision.get("use_tool", False)

    # =====================================================
    # 2️⃣ USER CONFIG ENFORCEMENT
    # =====================================================
    memory_enabled = user_config.get("memory_enabled", False)
    tool_enabled = user_config.get("tool_enabled", False)

    use_memory = router_wants_memory and memory_enabled
    use_tool = router_wants_tool and tool_enabled

    memory_context = {}
    tool_context = {}

    # =====================================================
    # 3️⃣ MEMORY AGENT (OPTIONAL, NO DB)
    # =====================================================
    if use_memory:
        memory_result = await Runner.run(memory_agent, user_input)

        try:
            memory_context = json.loads(memory_result.final_output)
        except Exception:
            memory_context = {
                "status": "error",
                "error": "Invalid memory agent output",
            }

        # 🔥 emit memory event to backend
        yield {
            "type": "memory_event",
            "payload": memory_context,
        }

    # =====================================================
    # 4️⃣ TOOL AGENT (OPTIONAL)
    # =====================================================
    if use_tool:
        tool_result = await Runner.run(tool_agent, user_input)

        try:
            tool_request_dict = json.loads(tool_result.final_output)
            tool_request = ToolRequest(**tool_request_dict)
            tool_exec_result = ToolExecutor.execute(tool_request)
            tool_context = tool_exec_result.model_dump()
        except Exception as e:
            tool_context = {
                "status": "error",
                "error": str(e),
            }

    # =====================================================
    # 5️⃣ REASONING AGENT (ALWAYS, STREAMING)
    # =====================================================
    reasoning_input = {
        "user_input": user_input,
        "chat_history": chat_history,
        "memory_context": memory_context,
        "tool_context": tool_context,
        "capabilities": {
            "memory_enabled": memory_enabled,
            "tool_enabled": tool_enabled,
        },
    }

    reasoning_result = await Runner.run(
        reasoning_agent,
        json.dumps(reasoning_input),
    )

    for ch in reasoning_result.final_output:
        yield {
            "type": "token",
            "value": ch,
        }
