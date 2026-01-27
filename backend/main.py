
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, chat
from property import property_router

app = FastAPI()

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

app.include_router(property_router)



