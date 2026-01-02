# digital_human/agents/orchestrator.py

from digital_human.graph.state import AgentState
from digital_human.config.settings import MEMORY_TRIGGERS, TOOL_TRIGGERS


def orchestrator_agent(state: AgentState) -> AgentState:
    """
    Orchestrator Agent
    ------------------
    Role:
    - Lightweight routing agent
    - Decides WHICH agents should run

    Reads:
    - state.user_input
    - state.chat_history (optional)

    Writes:
    - state.needs_reasoning
    - state.needs_memory
    - state.needs_tools
    """

    text = state.user_input.lower().strip()

    # 1️⃣ Reasoning always runs (Phase 1)
    state.needs_reasoning = True

    # 2️⃣ Memory routing (semantic hint only)
    state.needs_memory = any(trigger in text for trigger in MEMORY_TRIGGERS)

    # 3️⃣ Tool / RAG routing (semantic hint only)
    state.needs_tools = any(trigger in text for trigger in TOOL_TRIGGERS)

    return state
