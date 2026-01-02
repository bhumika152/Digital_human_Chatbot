# 🤖 Chatbot Project – Digital Human Architecture

This project is a **full‑stack AI chatbot system** built with a modular, agent‑based backend and a modern frontend. It is designed to simulate a **Digital Human** that can reason, retrieve memory, use RAG (Retrieval Augmented Generation), and maintain conversational context.

The architecture is intentionally clean and extensible so that individual agents (decision, memory, RAG, etc.) can evolve independently.

---

## 🧠 Core Capabilities

### 1. Conversational Intelligence

* Accepts user queries from Web UI
* Maintains conversation context per session
* Produces coherent, state‑aware responses

### 2. Decision‑Driven Agent Flow

* A **Decision Agent** determines what actions are required per message:

  * Memory access
  * Chat history lookup
  * RAG (vector search)
  * Direct LLM response

### 3. Memory System (Long‑Term)

* Stores user‑specific memory (preferences, facts, context)
* Backed by **PostgreSQL**
* Accessed only when the Decision Agent deems it necessary


### 4. Chat History Persistence

* Stores full chat history in PostgreSQL
* Allows:

  * Context replay
  * History‑aware responses

### 5. RAG (Retrieval Augmented Generation)

* Uses **pgvector** for semantic search
* Retrieves relevant documents when knowledge grounding is required

### 6. Prompt Engineering Pipeline

* Memory Formatter
* History Formatter
* RAG Formatter
* Unified **Prompt Builder**

### 7. Extensible Agent Architecture

* Each responsibility lives in its own module
* Easy to plug in:

  * New agents
  * New tools
  * New memory strategies

---

## 🧩 High‑Level Architecture Flow

1. **User** sends a message from Frontend UI
2. **FastAPI Gateway** receives the request
3. Pipeline steps:

   * Authentication check
   * Input validation
   * Session lookup
   * Redis state read/write
4. Request forwarded to **Decision Agent**
5. Decision Agent decides:

   * Memory needed?
   * Chat history needed?
   * RAG needed?
   * Or direct LLM call?
6. Required data is fetched and formatted
7. Final prompt is built
8. **LLM Model** generates the response
9. Response is returned to the user

---

## 🧠 Agents Overview

### 🧭 Decision Agent

**Responsibility:**

* Central brain of the system
* Analyzes user input
* Produces a decision plan

**Decisions include:**

* Save memory or not
* Load chat history or not
* Trigger RAG or not

---

### 🧠 Memory Agent

**Responsibility:**

* Persist long‑term user memories
* Fetch relevant memory records

**Storage:**

* PostgreSQL (`memory_store`)

---

### 💬 Chat History Agent

**Responsibility:**

* Retrieve past conversation turns
* Maintain conversational continuity

**Storage:**

* PostgreSQL (`chat_messages`)

---

### 📚 RAG Agent

**Responsibility:**

* Perform semantic search
* Fetch relevant documents

**Storage:**

* PostgreSQL + pgvector

---

### 🧱 Prompt Builder

**Responsibility:**

* Combine:

  * System prompt
  * Memory context
  * Chat history
  * Retrieved documents
* Produce final LLM prompt

---

## 🛠 Tech Stack

### Backend

* Python **3.10 – 3.11 only**
* FastAPI
* SQLAlchemy
* PostgreSQL
* pgvector
* Redis
* Uvicorn

### Frontend

* Next.js / React
* TypeScript
* Modern UI stack

---

## 🚀 Running the Project (Local Setup)

> ⚠️ **Important:** Python 3.10 or 3.11 only. Do NOT use Python 3.12+

---

## 🔧 Backend Setup

### 1️⃣ Go to backend directory

```bash
cd backend
```

### 2️⃣ Delete existing virtual environment (if present)

```bash
# Windows
rmdir /s /q venv
```

### 3️⃣ Create fresh virtual environment

```bash
python -m venv venv
```

### 4️⃣ Activate virtual environment

```bash
# Windows
venv\Scripts\activate
```

### 5️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 6️⃣ Run backend server

```bash
uvicorn main:app --reload --port 8000
```

Backend will run at:

```
http://127.0.0.1:8000
```

---

## 🎨 Frontend Setup

### 1️⃣ Go to frontend directory

```bash
cd frontend
```

### 2️⃣ Install dependencies (only first time or when packages change)

```bash
npm install
```

### 3️⃣ Start frontend dev server

```bash
npm run dev
```

Frontend will run at:

```
http://localhost:3000
```

---

## 📁 Project Structure (Simplified)

```
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
```

---

## 🔒 Environment Notes

* Ensure PostgreSQL, Redis, and pgvector are running
* Environment variables should be configured before production use

---

## 🧩 Future Extensions

* Multi‑agent collaboration
* Tool calling (APIs, DB actions)
* Long‑term memory summarization
* Streaming responses
* User personalization

---

## ✅ Summary

This project is a **production‑grade AI chatbot foundation** with:

* Clean agent boundaries
* Decision‑first architecture
* Memory + RAG integration
* Scalable backend design

Perfect for building **Digital Humans**, AI assistants, or enterprise chat systems 🚀
