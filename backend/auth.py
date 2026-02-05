from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta,timezone
import bcrypt
import secrets
from schemas import ForgotPasswordRequest, ResetPasswordRequest
import secrets
from database import SessionLocal
from models import User, UserConfig, MemoryStore
from schemas import SignupRequest, LoginRequest, TokenResponse
from utils import create_access_token, SECRET_KEY, ALGORITHM
from database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter(prefix="/auth", tags=["auth"])


# --------------------
# AUTH Dependency
# --------------------
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    try:
        token = credentials.credentials   # "Bearer" ke baad wala token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["user_id"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --------------------
# SIGNUP
# --------------------
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):

    # 1️⃣ Check existing user
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2️⃣ Hash password
    hashed = bcrypt.hashpw(
        data.password.encode(),
        bcrypt.gensalt()
    ).decode()

    # 3️⃣ Create user
    user = User(
        email=data.email,
        username=data.username,  
        password_hash=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 4️⃣ Create user config using frontend values
    config = UserConfig(
        user_id=user.user_id,
        enable_memory=data.enable_memory,
        enable_multichat=data.enable_multichat,
        enable_chat_history=data.enable_chat_history,
        enable_rag=data.enable_rag,
        enable_tool=data.enable_tool,
    )

    db.add(config)
    db.commit()

    return {
        "message": "User created successfully",
        "user_id": user.user_id
    }


@router.get("/signup")
def signup_help():
    return {"message": "Use POST /auth/signup"}

# --------------------
# LOGIN
# --------------------
# @router.post("/login", response_model=TokenResponse)
# def login(data: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     if not bcrypt.checkpw(
#         data.password.encode(),
#         user.password_hash.encode()
#     ):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"user_id": str(user.user_id)})
#     return {"access_token": token, "token_type": "bearer"}
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
 
    if not bcrypt.checkpw(
        data.password.encode(),
        user.password_hash.encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
 
    # ✅ update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
 
    token = create_access_token({"user_id": str(user.user_id)})
 
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {                       # 🔥 ADD THIS
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username
        }
    }
 

@router.get("/login")
def login_help():
    return {"message": "Use POST /auth/login"}

# --------------------
# FORGOT PASSWORD
# --------------------
@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔑 1. Generate reset token
    reset_token = secrets.token_urlsafe(32)

    # ⏰ 2. Save token + expiry
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

    db.commit()

    # 🔗 3. Generate correct reset link
    reset_link = f"http://localhost:3000/?token={reset_token}"

    # 📩 4. For now just print (email later)
    print("RESET PASSWORD LINK:", reset_link)

    return {
        "message": "Reset password link sent to your email"
    }

# --------------------
# RESET PASSWORD
# --------------------
@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(
            User.reset_token == payload.token,
            User.reset_token_expiry > datetime.utcnow()
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    hashed = bcrypt.hashpw(
        payload.new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    user.password_hash = hashed
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {
        "message": "Password reset successful"
    }



# --------------------
# MEMORY DEBUG
# --------------------
@router.get("/debug")
def debug_memory(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(MemoryStore)
        .filter(MemoryStore.user_id == user_id)
        .order_by(MemoryStore.created_at.desc())
        .all()
    )
