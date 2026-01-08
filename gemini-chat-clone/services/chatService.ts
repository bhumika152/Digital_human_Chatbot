
// import { ChatSession, Message } from '../types';

// const API_BASE_URL = 'http://localhost:8000/api';

// /**
//  * ChatService connects to FastAPI endpoints handling chat_sessions and chat_messages.
//  */
// export const chatService = {
//   // GET all sessions for a user using query params
//   async getSessions(userId: string): Promise<ChatSession[]> {
//     const response = await fetch(`${API_BASE_URL}/sessions?user_id=${userId}`, {
//       method: 'GET',
//       headers: { 'Accept': 'application/json' },
//     });
//     if (!response.ok) {
//       const error = await response.json();
//       throw new Error(error.detail || 'Failed to load chat history');
//     }
//     return response.json();
//   },

//   // POST a new session - Body matches a Pydantic model
//   async createSession(userId: string, title: string): Promise<ChatSession> {
//     const response = await fetch(`${API_BASE_URL}/sessions`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ user_id: userId, session_title: title }),
//     });
//     if (!response.ok) {
//       const error = await response.json();
//       throw new Error(error.detail || 'Failed to create session');
//     }
//     return response.json();
//   },

//   // GET messages for a session using path or query params
//   async getMessages(sessionId: string): Promise<Message[]> {
//     const response = await fetch(`${API_BASE_URL}/messages?session_id=${sessionId}`, {
//       method: 'GET',
//       headers: { 'Accept': 'application/json' },
//     });
//     if (!response.ok) {
//       const error = await response.json();
//       throw new Error(error.detail || 'Failed to load messages');
//     }
//     return response.json();
//   },

//   // POST a new message - Body matches a Pydantic model
//   async saveMessage(sessionId: string, role: string, content: string): Promise<Message> {
//     const response = await fetch(`${API_BASE_URL}/messages`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ 
//         session_id: sessionId, 
//         role: role, 
//         content: content 
//       }),
//     });
//     if (!response.ok) {
//       const error = await response.json();
//       throw new Error(error.detail || 'Failed to save message');
//     }
//     return response.json();
//   }
// };

import { ChatSession, Message } from '../types';

const API_BASE_URL = 'http://localhost:8000';

/**
 * ChatService connects to FastAPI endpoints
 */
export const chatService = {

  /* ------------------------------
     ❌ OLD APIs (backend me nahi)
     tum baad me hata sakti ho
  ------------------------------ */

  async getSessions(userId: string): Promise<ChatSession[]> {
    const response = await fetch(`${API_BASE_URL}/api/sessions?user_id=${userId}`);
    return response.json();
  },

  async createSession(userId: string, title: string): Promise<ChatSession> {
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, session_title: title }),
    });
    return response.json();
  },

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE_URL}/api/messages?session_id=${sessionId}`);
    return response.json();
  },

  async saveMessage(sessionId: string, role: string, content: string): Promise<Message> {
    const response = await fetch(`${API_BASE_URL}/api/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, role, content }),
    });
    return response.json();
  },

  /* =====================================================
     ✅ REAL CHAT API (STREAMING) – IMPORTANT PART
  ===================================================== */

  async sendChatMessageStreaming(
    token: string,
    conversationId: string | null,
    message: string,
    onChunk: (chunk: string) => void
  ) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`, // 🔐 JWT token
      },
      body: JSON.stringify({
        conversation_id: conversationId,   // null = new chat
        message: {
          role: 'user',
          content: message,
        },
      }),
    });

    if (!response.body) {
      throw new Error('Streaming not supported by browser');
    }

    // 🔁 STREAM READER
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      onChunk(chunk); // 👈 har token yahan milta hai
    }
  }
};
