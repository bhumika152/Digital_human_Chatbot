from langgraph.graph import StateGraph, END
from digital_human.graph.state import AgentState

# --------------------
# Agent imports (LangGraph-safe only)
# --------------------
from digital_human.agents.orchestrator import orchestrator_agent
from digital_human.agents.reasoning_agent.agent import reasoning_agent
from digital_human.agents.memory_agent.agent import memory_agent
from digital_human.agents.tool_agent.agent import tool_agent
from digital_human.agents.responder_agent.agent import responder_node

# --------------------
# Executors
# --------------------
from digital_human.executors.tool_executor import execute_tool


# --------------------------------------------------
# Tool execution node
# --------------------------------------------------
def tool_execution_node(state: AgentState) -> AgentState:
    """
    Executes tool requests decided by Tool Agent.
    """
    if state.tool_request:
        state.tool_results = execute_tool(state.tool_request)
    return state


# --------------------------------------------------
# Build LangGraph
# --------------------------------------------------
def build_graph():
    graph = StateGraph(AgentState)

    # -------- Nodes --------
    graph.add_node("orchestrator", orchestrator_agent)
    graph.add_node("reasoning", reasoning_agent)
    graph.add_node("memory", memory_agent)
    graph.add_node("tool_agent", tool_agent)
    graph.add_node("tool_executor", tool_execution_node)
    graph.add_node("responder", responder_node)  # ⚠️ NON-streaming only

    # -------- Entry --------
    graph.set_entry_point("orchestrator")

    # -------- Core Flow --------
    graph.add_edge("orchestrator", "reasoning")
    graph.add_edge("reasoning", "memory")

    # -------- Conditional Routing --------
    graph.add_conditional_edges(
        "memory",
        lambda state: "tool_agent" if state.needs_tools else "responder"
    )

    graph.add_edge("tool_agent", "tool_executor")
    graph.add_edge("tool_executor", "responder")

    # -------- End --------
    graph.add_edge("responder", END)

    return graph.compile()


# --------------------------------------------------
# Compiled graph (singleton)
# --------------------------------------------------
digital_human_graph = build_graph()


# --------------------------------------------------
# Public entry point
# --------------------------------------------------
def run_digital_human(state: AgentState):
    """
    Runs the complete Digital Human – Phase 1 pipeline.

    NOTE:
    LangGraph returns a dict-like state.
    Streaming is handled OUTSIDE this function.
    """
    return digital_human_graph.invoke(state)
