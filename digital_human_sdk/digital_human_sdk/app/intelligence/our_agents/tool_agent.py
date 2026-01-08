from pathlib import Path
from agents import Agent

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "tool.md"

tool_agent = Agent(
    name="ToolAgent",
    model="litellm/gemini/gemini-2.5-flash",
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
)