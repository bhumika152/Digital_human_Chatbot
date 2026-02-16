from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import voice
from fastapi.staticfiles import StaticFiles

# --------------------------------
# ENV + LOGGING
# --------------------------------
from logging_config import setup_logging
load_dotenv()
setup_logging()

logger = logging.getLogger("main")

# --------------------------------
# IMPORT ROUTERS & DB
# --------------------------------
import auth
import chat
from property import property_router
from admin.admin_kb import router as admin_kb_router
from database import Base, engine, SessionLocal
from models import MemoryStore
from services.memory_index_manager import memory_index_manager

# --------------------------------
# APP INIT
# --------------------------------
app = FastAPI()
app.mount("/temp", StaticFiles(directory="temp"), name="temp")

logger.info("🚀 FastAPI application starting")


# --------------------------------
# STARTUP: REBUILD PER-USER FAISS
# --------------------------------
@app.on_event("startup")
def rebuild_per_user_faiss():
    logger.info("🧠 Rebuilding per-user FAISS indexes...")

    db = SessionLocal()

    try:
        memories = db.query(MemoryStore).filter(
            MemoryStore.is_active == True
        ).all()

        total_loaded = 0

        for mem in memories:
            if mem.embedding:
                memory_index_manager.add(
                    user_id=mem.user_id,
                    memory_id=mem.memory_id,
                    embedding=mem.embedding,
                )
                total_loaded += 1

        logger.info(
            "✅ FAISS rebuild complete | Loaded %s memory vectors",
            total_loaded
        )

    except Exception as e:
        logger.exception("❌ FAISS rebuild failed: %s", e)

    finally:
        db.close()


# --------------------------------
# VALIDATION ERROR HANDLER
# --------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for err in exc.errors():
        field = err["loc"][-1]

        if err.get("type") == "missing":
            msg = f"{field} is required"
        else:
            msg = err.get("msg")

        errors.append({
            "field": field,
            "message": msg
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
        },
    )


# --------------------------------
# CORS (MUST BE EARLY)
# --------------------------------
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


# --------------------------------
# ROUTERS
# --------------------------------
app.include_router(auth.router)
app.include_router(chat.chat_router)
app.include_router(chat.user_router)
app.include_router(admin_kb_router)
app.include_router(property_router)


# --------------------------------
# ROOT
# --------------------------------
@app.get("/")
def root():
    logger.info("🏠 Root endpoint called")
    return {"message": "Backend is running"}


# --------------------------------
# DB INIT
# --------------------------------
Base.metadata.create_all(bind=engine)
