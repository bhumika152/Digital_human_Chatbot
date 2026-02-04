from agents import Agent
from digital_human_sdk.app.intelligence.models.litellm_model import get_model_name

def create_agent(
    *,
    name: str,
    instructions: str,
    tools: list | None = None,
):
    return Agent(
        name=name,
        instructions=instructions,
        model=get_model_name(),   
        tools=tools or [],
    )


    # return Agent(
    #     name="resolution_agent",
    #     instructions="You are a helpful assistant that resolves ambiguities in user requests. You ask clarifying questions if needed, otherwise you provide a concise resolution by following below route
    #     1. if user wants to know any current affairs, use web_search tool to get latest information.
    #     2. if user wants the status of his order, use order_status tool to get the latest information.
    #     3. always respond in following JSON format: {\"resolution\": \"<your resolution here>\"}  
    #     ",
    #     model=get_model_name("gpt3.5-turbo"),   
    #     tools=tools or ["vegavid_web_search_tool, vegavid_order_status_tool"],
    #     guardrails=True,
    #     input_guardrails="resolution_input_agent_guardrails",
    #     output_guardrails="resolution_output_agent_guardrails",
    #     handoff_tool="human_handoff_tool",
    # )