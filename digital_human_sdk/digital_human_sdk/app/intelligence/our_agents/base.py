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
