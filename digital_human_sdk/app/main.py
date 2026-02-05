from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.chat import router as chat_router
from app.intelligence.logging_config import setup_logging

load_dotenv()
setup_logging()   # 👈 MUST be called BEFORE app starts

app = FastAPI(title="Digital Human Service")

from app.api.chat import router as chat_router
app.include_router(chat_router)
