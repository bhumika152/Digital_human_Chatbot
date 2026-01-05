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

⚠️ Important
Use Python 3.10 or 3.11 only.
Do NOT use Python 3.12+, as several dependencies are not yet compatible.

🔧 Backend Setup
1️⃣ Navigate to the backend directory
cd backend

2️⃣ Delete existing virtual environment (if present)
# Windows
rmdir /s /q venv

3️⃣ Create a fresh virtual environment
python -m venv venv

4️⃣ Activate the virtual environment
# Windows
venv\Scripts\activate

5️⃣ Install dependencies
pip install -r requirements.txt

6️⃣ Run the backend server
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