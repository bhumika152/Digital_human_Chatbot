# from pathlib import Path
# from digital_human_sdk.app.intelligence.our_agents.base import create_agent


# PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "router.md"

# router_agent = create_agent(
#     name="RouterAgent",
#     instructions=PROMPT_PATH.read_text(encoding="utf-8"),
    
   
# )
from agents import Agent
from pathlib import Path
from digital_human_sdk.app.intelligence.models.litellm_model import get_model_name
from digital_human_sdk.app.intelligence.safety.guardrails import input_safety
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "router.md"

router_agent = Agent(
    name="RouterAgent",
    model=get_model_name(),
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
    input_guardrails=[input_safety],
)
