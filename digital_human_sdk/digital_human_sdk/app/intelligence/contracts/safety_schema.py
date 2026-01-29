from pydantic import BaseModel
from typing import Optional

class SafetySchema(BaseModel):
    safe: bool
    reason: Optional[str] = None
