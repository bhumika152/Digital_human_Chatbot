🤖 Chatbot Project – Digital Human Architecture
This project is a full‑stack AI chatbot system built with a modular, agent‑based backend and a modern frontend. It is designed to simulate a Digital Human that can reason, retrieve memory, use RAG (Retrieval Augmented Generation), and maintain conversational context.

The architecture is intentionally clean and extensible so that individual agents (decision, memory, RAG, etc.) can evolve independently.


🛠 Tech Stack
Backend
Python 3.10 – 3.11 only
FastAPI
SQLAlchemy
PostgreSQL
pgvector
Redis
Uvicorn
Frontend
Next.js / React
TypeScript
Modern UI stack
🚀 Running the Project (Local Setup)
⚠️ Important: Python 3.10 or 3.11 only. Do NOT use Python 3.12+

🔧 Backend Setup
1️⃣ Go to backend directory
cd backend
2️⃣ Delete existing virtual environment (if present)
# Windows
rmdir /s /q venv
3️⃣ Create fresh virtual environment
python -m venv venv
4️⃣ Activate virtual environment
# Windows
venv\Scripts\activate
5️⃣ Install dependencies
pip install -r requirements.txt
6️⃣ Run backend server
uvicorn main:app --reload --port 8000
Backend will run at:

http://127.0.0.1:8000
🎨 Frontend Setup
1️⃣ Go to frontend directory
cd frontend
2️⃣ Install dependencies (only first time or when packages change)
npm install
3️⃣ Start frontend dev server
npm run dev
Frontend will run at:

http://localhost:3000
📁 Project Structure (Simplified)
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
🔒 Environment Notes
Ensure PostgreSQL, Redis, and pgvector are running
Environment variables should be configured before production use


Create .env file
SECRET_KEY= --
DATABASE_URL=--
OPENAI_API_KEY = --