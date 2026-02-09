from app.intelligence.our_agents.base import create_agent
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "memory.md"
memory_agent = create_agent(
    name="Memory Agent",
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),  
    )