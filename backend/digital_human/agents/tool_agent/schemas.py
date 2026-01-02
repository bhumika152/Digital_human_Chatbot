# agents/tool_agent/schemas.py
from pydantic import BaseModel
from typing import Dict, Any


class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
