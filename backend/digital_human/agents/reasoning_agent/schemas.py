# reasoning_agent/schemas.py
from pydantic import BaseModel
from typing import Optional


class ReasoningOutput(BaseModel):
    intent_type: str
    topic: Optional[str]
    confidence: float
