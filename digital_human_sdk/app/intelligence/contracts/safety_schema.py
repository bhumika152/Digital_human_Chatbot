from pydantic import BaseModel
from typing import Optional

class SafetySchema(BaseModel):
    safe: bool
    message: str
