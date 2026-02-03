from pydantic import BaseModel

class SafetyResult(BaseModel):
    safe: bool
    reason: str | None = None
    message: str
