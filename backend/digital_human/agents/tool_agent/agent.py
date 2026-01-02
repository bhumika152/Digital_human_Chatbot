# agents/tool_agent/agent.py

from digital_human.graph.state import AgentState
from digital_human.agents.tool_agent.schemas import ToolRequest
from digital_human.agents.tool_agent.rules import INTENT_TO_TOOL


MIN_CONFIDENCE_FOR_TOOL = 0.6


def tool_agent(state: AgentState) -> AgentState:
    """
    Tool Agent
    ----------
    Plans external tool usage.
    Does NOT execute tools.
    """

    # ---------- Guard Layer ----------
    if not state.needs_tools:
        return state

    if state.intent_confidence is None or state.intent_confidence < MIN_CONFIDENCE_FOR_TOOL:
        return state

    intent_type = state.intent.get("type")

    if intent_type not in INTENT_TO_TOOL:
        return state

    # ---------- Decision Layer ----------
    tool_name = INTENT_TO_TOOL[intent_type]

    # ---------- Parameter Construction ----------
    query = state.user_input

    tool_request = ToolRequest(
        tool_name=tool_name,
        parameters={
            "query": query,
            "top_k": 5
        }
    )

    state.tool_request = tool_request.model_dump()

    return state
