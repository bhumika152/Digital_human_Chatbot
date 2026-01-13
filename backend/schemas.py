from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List,Optional


class SignupRequest(BaseModel):
    email: str
    password: str

    # config checkboxes (optional)
    enable_memory: Optional[bool] = True
    enable_multichat: Optional[bool] = True
    enable_chat_history: Optional[bool] = True
    enable_rag: Optional[bool] = True
    enable_tool: Optional[bool] = True


class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 👇 ye NEW add hoga (chat ke liye)
class Message(BaseModel):
    role: str
    content: str

class SessionInfo(BaseModel):
    started_at: datetime
    expires_at: datetime

class Constraints(BaseModel):
    max_tokens: int
    response_style: str

class ChatRequest(BaseModel):
    request_id: str
    conversation_id: str
    message: Message
    recent_messages: List[Message]
    session: SessionInfo
    constraints: Constraints

# --------------------
# FORGOT PASSWORD
# --------------------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# --------------------
# RESET PASSWORD
# --------------------
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str