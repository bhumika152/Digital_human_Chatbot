from pydantic import BaseModel

class MemoryIntent(BaseModel):
    action: str       # save, update, delete
    key: str
    value: str
    confidence: float
