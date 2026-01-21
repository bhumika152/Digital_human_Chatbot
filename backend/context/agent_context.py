# # contexts/agent_context.py
# from pydantic import BaseModel
# from typing import Optional
# from uuid import UUID

# class AgentContext:
#     def __init__(
#         self,
#         *,
#         user_id: int,
#         session_id: int,
#         chat_history: list,        # ✅ ADD THIS
#         enable_memory: bool = True,
#         enable_tools: bool = True,
#         enable_rag: bool = True,
#         db_factory=None,
#         logger=None,
#         flags: dict | None = None,
#     ):
#         self.user_id = user_id
#         self.session_id = session_id
#         self.chat_history = chat_history  # ✅ STORE
#         self.enable_memory = enable_memory
#         self.enable_tools = enable_tools
#         self.enable_rag = enable_rag
#         self.db_factory = db_factory
#         self.logger = logger
#         self.flags = flags or {}

#     @property
#     def db(self):
#         return self.db_factory()

# contexts/agent_context.py
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