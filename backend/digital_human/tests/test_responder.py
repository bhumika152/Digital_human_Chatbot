from graph.state import AgentState
from agents.responder_agent.agent import responder_agent

state = AgentState(
    request_id="debug-responder",
    user_input="Explain Redis persistence",
    chat_history=[],
    token_budget=4000
)

state.intent = {"type": "information_request"}
state.intent_confidence = 0.9

state.tool_results = {
    "documents": [
        {
            "content": "Redis persistence allows data to be saved using RDB snapshots and AOF logs."
        }
    ]
}

state = responder_agent(state)

print("FINAL RESPONSE:\n")
print(state.final_response)
