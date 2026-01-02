from graph.state import AgentState
from graph.graph import run_digital_human

state = AgentState(
    request_id="debug-tool",
    user_input="Explain Redis persistence",
    chat_history=[],
    token_budget=4000
)

final_state = run_digital_human(state)

print("\n=== TOOL TEST ===")
print("needs_tools:", state.needs_tools)
print("tool_request:", state.tool_request)
print("tool_results:", state.tool_results)
print("final_response:", state.final_response)
