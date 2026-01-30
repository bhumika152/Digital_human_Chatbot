from fastapi import FastAPI
from dotenv import load_dotenv

from digital_human_sdk.app.api.chat import router as chat_router
from digital_human_sdk.app.intelligence.logging_config import setup_logging

load_dotenv()
setup_logging()

app = FastAPI(title="Digital Human Service")
app.include_router(chat_router)
