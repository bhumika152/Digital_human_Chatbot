from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List,Optional


class SignupRequest(BaseModel):
    email: str
    password: str
    username: str

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
    request_id: int
    conversation_id: int
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


class PropertyCreateRequest(BaseModel):
    title: str
    city: str
    locality: Optional[str] = None
    purpose: str               # "rent" or "buy"
    price: int
    bhk: int
    area_sqft: int
    is_legal: bool
    owner_name: str
    contact_phone: str
# --------------------
# UPDATE PROFILE
# --------------------
from pydantic import validator
import re

class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

    # First & Last Name → Only letters (NO space, NO numbers, NO special chars)
    @validator("first_name", "last_name")
    def validate_names(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"[A-Za-z]+", v):
            raise ValueError("Only letters allowed. No spaces, numbers or special characters.")
        return v

    # Username → letters, numbers, underscore only
    @validator("username")
    def validate_username(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"[A-Za-z0-9_]+", v):
            raise ValueError("Username can contain only letters, numbers, and underscore.")
        return v

    # Phone → only digits, exactly 10
    @validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits.")
        return v

    # Bio → letters, numbers and spaces only
    @validator("bio")
    def validate_bio(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"[A-Za-z0-9 ]*", v):
            raise ValueError("Bio can contain only letters, numbers, and spaces.")
        return v
    
class PropertyResponse(BaseModel):
    property_id: int
    title: str
    city: str
    locality: str
    purpose: str
    price: int

    class Config:
        true_attributes = True

# --------------------
# PROPERTY SCHEMAS
# --------------------
# class PropertyCreateRequest(BaseModel):
#     title: str
#     city: str
#     locality: str
#     purpose: str
#     price: int
#     bhk: int
#     area_sqft: int
#     is_legal: bool = False
#     owner_name: str
#     contact_phone: str

class PropertySearchRequest(BaseModel):
    city: str
    purpose: Optional[str] = None
    max_budget: int
    bhk: Optional[int] = None
    locality: Optional[str] = None

class PropertyCreateRequest(BaseModel):
    title: str
    city: str
    locality: Optional[str]=None
    purpose: str
    price: int
    bhk: int
    area_sqft: Optional[int] = None
    is_legal: bool = True
    owner_name: str
    contact_phone: str
 
class PropertyUpdateRequest(BaseModel):
    title: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    purpose: Optional[str] = None
    price: Optional[int] = None
    bhk: Optional[int] = None
    area_sqft: Optional[int] = None
    is_legal: Optional[bool] = None
    owner_name: Optional[str] = None
    contact_phone: Optional[str] = None
 