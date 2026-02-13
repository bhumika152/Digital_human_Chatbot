from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import property
from logging_config import setup_logging
from dotenv import load_dotenv


load_dotenv()
setup_logging()
 
import logging
logger = logging.getLogger("main")
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, chat
from property import property_router
from database import Base, engine
# from routers import admin
from fastapi.staticfiles import StaticFiles

# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# app.include_router(admin.router)

# -------------------------------
# APP INIT
# -------------------------------
app = FastAPI()
logger.info("🚀 FastAPI application starting")
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = err["loc"][-1]
        if err.get("type") == "missing":
            msg = f"{field} is required"
        else:
            msg = err.get("msg")

        errors.append({"field": field, "message": msg})

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = err["loc"][-1]
        if err.get("type") == "missing":
            msg = f"{field} is required"
        else:
            msg = err.get("msg")

        errors.append({"field": field, "message": msg})

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors,
        },
    )

# CORS MUST BE HERE (TOP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        #"http://192.168.0.109:3000",
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

# ADMIN ROUTERS
from admin.admin_kb import router as admin_kb_router
app.include_router(admin_kb_router)

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

# Include chat router
app.include_router(chat.chat_router)
# Include chat router WITH PREFIX
# app.include_router(chat.router)

# ✅ Include user router (NEW)
app.include_router(chat.user_router)


app.include_router(property.property_router)


