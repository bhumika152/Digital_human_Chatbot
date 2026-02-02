from pydantic import BaseModel
from typing import Optional, Callable, Any
from uuid import UUID
from fastapi import Request   
 
class AgentContext(BaseModel):
    user_id: int
    session_id: UUID
 
    enable_memory: bool
    enable_tools: bool
    enable_rag: bool
 
    request: Optional[Request] = None     
 
    db_factory: Optional[Callable] = None
    logger: Optional[Any] = None
 
    model_config = {
        "arbitrary_types_allowed": True
    }
 
    @property
    def db(self):
        if not self.db_factory:
            return None
        return self.db_factory()