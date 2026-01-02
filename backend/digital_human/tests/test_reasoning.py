from graph.state import AgentState
from agents.reasoning_agent.agent import reasoning_agent

state = AgentState(
    request_id="test-001",
    user_input="Compare Redis and Memcached",
    chat_history=[],
    token_budget=4000
)

state = reasoning_agent(state)

print("Intent:", state.intent)
print("Confidence:", state.intent_confidence)