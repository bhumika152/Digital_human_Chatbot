from pydantic import BaseModel
from typing import Optional

class MemoryAction(BaseModel):
    action: str           # ADD | UPDATE | DELETE | NONE
    key: Optional[str]
    value: Optional[str]
    confidence: float = 1.0
