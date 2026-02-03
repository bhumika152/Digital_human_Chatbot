import json
from app.intelligence.our_agents.tool_agent import tool_agent

def run_tool_agent(user_input: str) -> dict:
    response = tool_agent.run(user_input)

    try:
        tool_call = json.loads(response)
        return tool_call
    except json.JSONDecodeError:
        return {
            "tool": "none",
            "arguments": {}
        }
