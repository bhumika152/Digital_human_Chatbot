from pathlib import Path
from agents import Agent
from app.intelligence.models.litellm_model import get_model_name
from app.intelligence.safety.guardrails import output_safety

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "reasoning.md"

reasoning_agent = Agent(
    name="ReasoningAgent",
    model=get_model_name(),
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
    output_guardrails=[output_safety],
)
