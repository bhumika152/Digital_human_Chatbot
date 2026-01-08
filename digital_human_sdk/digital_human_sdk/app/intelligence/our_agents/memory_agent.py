from agents import Agent
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "memory.md"
memory_agent = Agent(
    name="Memory Agent",
    model="litellm/gemini/gemini-2.5-flash",
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
)