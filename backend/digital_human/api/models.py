# digital_human/api/models.py

from typing import List, Optional
from pydantic import BaseModel


class UserInfo(BaseModel):
    user_id: str
    is_authenticated: bool


class SessionInfo(BaseModel):
    session_id: str
    is_new_session: bool
    is_active: bool


class MessagePayload(BaseModel):
    content: str
    language: str


class ContextPayload(BaseModel):
    recent_messages: List[dict]


class SystemConstraints(BaseModel):
    token_budget: int
    latency_ms: Optional[int]


class TeamARequest(BaseModel):
    request_id: str
    user: UserInfo
    session: SessionInfo
    message: MessagePayload
    context: ContextPayload
    system_constraints: SystemConstraints


# ===== Team B Output =====

class MemoryIntent(BaseModel):
    action: str
    type: str
    key: str
    value: str
    confidence: float


class ToolIntent(BaseModel):
    tool: str
    purpose: str
    query: str


class TeamBResponse(BaseModel):
    request_id: str
    final_response: str
    memory_intents: List[MemoryIntent] = []
    tool_intents: List[ToolIntent] = []
