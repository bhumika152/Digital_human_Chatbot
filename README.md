# 🤖 Digital Human Chatbot – Agent-Based Architecture

This project is a full-stack AI chatbot system built with a modular, agent-driven backend and a modern frontend.
It simulates a Digital Human capable of reasoning, memory management, Retrieval-Augmented Generation (RAG), and maintaining long-term conversational context.

The architecture is intentionally clean, scalable, and extensible, allowing individual agents (Decision, Memory, RAG, Response, etc.) to evolve independently without breaking the system.

# 🛠 Tech Stack
Backend

Python (3.10 – 3.11 only)

FastAPI

SQLAlchemy

PostgreSQL

pgvector

Uvicorn

Frontend

Next.js / React

TypeScript

Modern UI stack

# 🚀 Running the Project (Local Setup)
STEP-BY-STEP COMMANDS

1️⃣ Go to backend folder

cd backend



2️⃣ Create virtual environment (ONCE)

py -3.10 -m venv venv

✔ Python 3.10.x only (3.10.9 / 3.10.13 both fine)



3️⃣ Activate venv

venv\Scripts\activate

python --version# Python 3.10.x 



4️⃣ Install backend dependencies (ONCE)

pip install -r requirements.txt



5️⃣ Install Digital Human SDK (editable mode – ONCE)

pip install -e ../digital_human_sdk



6️⃣ Run backend server

uvicorn main:app --reload --port 8000


📍 Backend will be available at:

http://127.0.0.1:8000

🎨 Frontend Setup
1️⃣ Navigate to the frontend directory
cd frontend

2️⃣ Install dependencies

(Required only the first time or when packages change)

npm install

3️⃣ Start the frontend development server
npm run dev


📍 Frontend will be available at:

http://localhost:3000

# 📁 Project Structure (Simplified)

chatbot-project-main/
├── backend/
│   ├── main.py
│   ├── chat.py
│   ├── auth.py
│   ├── digital_human/
│   │   ├── graph/
│   │   │   └── state.py
│   │   └── ...
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── app/
│   ├── package.json
│   └── ...
│
└── README.md

# 🔒 Environment & Services Notes

Ensure the following services are running before starting the application:

PostgreSQL

pgvector/pgArray extension enabled in PostgreSQL

# 🔑 Environment Variables

Create a .env file in the backend directory and configure the following:

SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
OPENAI_API_KEY=your_openai_api_key


⚠️ Never commit .env files to version control.

# ✅ Key Capabilities

Agent-based reasoning pipeline

Context-aware conversation handling

Long-term memory storage and retrieval

RAG-powered knowledge grounding

Scalable Digital Human architecture