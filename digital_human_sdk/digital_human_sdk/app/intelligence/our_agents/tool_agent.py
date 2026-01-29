from pathlib import Path
from digital_human_sdk.app.intelligence.our_agents.base import create_agent
#from digital_human_sdk.app.intelligence.tools.user_info import get_user_info
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "tool.md"

tool_agent = create_agent(
    name="ToolAgent",
    #model="litellm/gemini/gemini-2.5-flash",
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
    # tools=[get_user_info],
    
)