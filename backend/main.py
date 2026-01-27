# -------------------------------
# LOGGING MUST COME FIRST
# -------------------------------
from digital_human_sdk.app.intelligence.logging_config import setup_logging
setup_logging()

import logging
logger = logging.getLogger("main")

# -------------------------------
# FASTAPI IMPORTS
# -------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import auth, chat
from database import Base, engine

# -------------------------------
# APP INIT
# -------------------------------
app = FastAPI()

logger.info("🚀 FastAPI application starting")

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],
)

# -------------------------------
# ROUTERS
# -------------------------------
app.include_router(auth.router)
app.include_router(chat.chat_router)
app.include_router(chat.user_router)

# -------------------------------
# ROOT
# -------------------------------
@app.get("/")
def root():
    logger.info("🏠 Root endpoint called")
    return {"message": "Backend is running"}

# -------------------------------
# DB INIT
# -------------------------------
Base.metadata.create_all(bind=engine)
logger.info("🗄️ Database tables ensured")
