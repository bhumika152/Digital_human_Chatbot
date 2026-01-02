from graph.state import AgentState
from agents.tool_agent.agent import tool_agent

# Create a fake state (as if Reasoning + Orchestrator already ran)
state = AgentState(
    request_id="debug-1",
    user_input="Explain Redis persistence",
    chat_history=[],
    token_budget=4000
)

# Simulate Reasoning Agent output
state.intent = {"type": "information_request"}
state.intent_confidence = 0.85
state.needs_tools = True

# Run Tool Agent
state = tool_agent(state)

print("=== TOOL AGENT OUTPUT ===")
print(state.tool_intent)
