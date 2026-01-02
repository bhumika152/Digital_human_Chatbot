from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, chat

app = FastAPI()

# CORS MUST BE HERE (TOP)
app.add_middleware(
    CORSMiddleware,
    # Allow local dev origins (add or relax for development as needed)
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],      # OPTIONS, POST, GET
    allow_headers=["*"],
)

app.include_router(auth.router)




@app.get("/")
def root():
    return {"message": "Backend is running"}


from database import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

# Include chat router
app.include_router(chat.router)

