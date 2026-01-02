from graph.state import AgentState
from agents.orchestrator import orchestrator_agent


def test_memory_routing():
    state = AgentState(
        request_id="1",
        user_input="Remember that I am preparing for Redis interviews",
        chat_history=[],
        token_budget=4000
    )

    state = orchestrator_agent(state)

    assert state.needs_reasoning is True
    assert state.needs_memory is True
    assert state.needs_tools is False


def test_tool_routing():
    state = AgentState(
        request_id="2",
        user_input="Explain Redis persistence",
        chat_history=[],
        token_budget=4000
    )

    state = orchestrator_agent(state)

    assert state.needs_reasoning is True
    assert state.needs_tools is True
