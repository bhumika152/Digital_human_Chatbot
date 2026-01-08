from dotenv import load_dotenv
load_dotenv()

import json
import asyncio

from agents import Runner
from digital_human_sdk.app.intelligence.our_agents.router_agent import router_agent
from digital_human_sdk.app.intelligence.our_agents.tool_agent import tool_agent
from digital_human_sdk.app.intelligence.tools.tool_executor import ToolExecutor
from digital_human_sdk.app.intelligence.utils.agent_output import extract_text

runner = Runner()
executor = ToolExecutor()

async def test_query(user_input: str):
    print("\nUSER:", user_input)

    # 1. Router Agent
    router_result = await runner.run(router_agent, user_input)
    route = extract_text(router_result).strip().lower()
    print("ROUTER:", route)

    if route != "tool":
        print(" Not routed to tool")
        return

    # 2. Tool Agent
    tool_result = await runner.run(tool_agent, user_input)
    tool_text = extract_text(tool_result)
    print("RAW TOOL AGENT OUTPUT:", tool_text)

    # 3. Parse JSON
    try:
        tool_call = json.loads(tool_text)
    except json.JSONDecodeError:
        print("ToolAgent did not return valid JSON")
        return

    print("PARSED TOOL CALL:", tool_call)

    # 4. Execute tool
    result = executor.execute(
        tool_call["tool"],
        tool_call["arguments"]
    )

    print("TOOL RESULT:", result)


async def main():
    await test_query("What is the weather in Delhi today?")
    await test_query("Calculate (45 * 12) / 3")
    await test_query("Search latest iPhone price")
    await test_query("Explain machine learning")


if __name__ == "__main__":
    asyncio.run(main())
