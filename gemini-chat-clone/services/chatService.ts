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
