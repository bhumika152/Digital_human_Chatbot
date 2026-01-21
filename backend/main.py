from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, chat
# import  property
from property import property_router
app = FastAPI()


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
    # Allow local dev origins (add or relax for development as needed)
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],      # OPTIONS, POST, GET
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],
)
#  auth router 
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}


from database import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

# Include chat router
app.include_router(chat.chat_router)
# Include chat router WITH PREFIX
# app.include_router(chat.router)

# ✅ Include user router (NEW)
app.include_router(chat.user_router)


# Include property router
# app.include_router(property.property_router)

app.include_router(property_router)

print("✅ REGISTERED ROUTES:")
for r in app.routes:
    if hasattr(r, "methods"):
        print(r.path, r.methods)
