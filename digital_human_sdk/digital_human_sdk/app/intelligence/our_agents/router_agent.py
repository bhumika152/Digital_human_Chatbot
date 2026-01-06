from pathlib import Path
from digital_human_sdk.app.intelligence.our_agents.base import create_agent

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "router.md"

router_agent = create_agent(
    name="RouterAgent",
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
)
