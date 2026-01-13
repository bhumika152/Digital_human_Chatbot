from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any

class ToolRequest(BaseModel):
    action: Literal["call_tool", "none"]
    tool_name: Optional[
        Literal["weather", "calculator", "web_search", "browser"]
    ] = None
    arguments: Optional[Dict[str, Any]] = None
