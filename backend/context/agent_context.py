from pydantic import BaseModel
from typing import Optional
from uuid import UUID
 
class AgentContext(BaseModel):
    user_id: int
    session_id: UUID
 
    enable_memory: bool
    enable_tools: bool
    enable_rag:bool
 
    db: Optional[object] = None
    logger: Optional[object] = None
 
    model_config = {
        "arbitrary_types_allowed": True
    }