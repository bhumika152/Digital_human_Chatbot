from app.intelligence.our_agents.router_agent import router_agent
from app.intelligence.our_agents.tool_agent_runner import run_tool_agent
from app.intelligence.tools.tool_executor import ToolExecutor
from app.intelligence.our_agents.memory_agent import memory_agent
from app.intelligence.our_agents.reasoning_agent import reasoning_agent

executor = ToolExecutor()

def handle_user_input(user_input: str):
    route = router_agent.run(user_input).strip().lower()

    if route == "tool":
        plan = run_tool_agent(user_input)
        return executor.execute(
            plan["tool"],
            plan["arguments"]
        )

    if route == "memory":
        return memory_agent.run(user_input)

    if route == "reasoning":
        return reasoning_agent.run(user_input)

    return "General response"
