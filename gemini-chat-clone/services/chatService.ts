import { ChatSession, Message } from '../types';

const API_BASE_URL = 'http://localhost:8000';

// 🔐 helper for auth headers
const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
});

export const chatService = {
  /* ============================
     🆕 CREATE NEW CHAT SESSION
     ============================ */
  async createSession(): Promise<ChatSession> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: 'POST',
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    return response.json();
  },

  /* ============================
     📂 SIDEBAR: GET ALL SESSIONS
     ============================ */
  async getSessions(): Promise<ChatSession[]> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: 'GET',
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to load chat sessions');
    }

    return response.json();
  },

  /* ============================
     💬 GET MESSAGES OF SESSION
     ============================ */
  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await fetch(
      `${API_BASE_URL}/chat/sessions/${sessionId}/messages`,
      {
        method: 'GET',
        headers: authHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to load messages');
    }

    return response.json();
  },

  /* ============================
     🤖 SEND MESSAGE (STREAMING)
     ============================ */
  async sendChatMessageStreaming(
    token: string,
    conversationId: string | null,
    message: string,
    onChunk: (chunk: string) => void,
    onSessionId?: (sessionId: string) => void
  ) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        conversation_id: conversationId, // null only for FIRST message
        message: {
          role: 'user',
          content: message,
        },
      }),
    });

    // 🔑 READ SESSION ID FROM HEADER (FIRST MESSAGE ONLY)
    const newSessionId = response.headers.get('X-Session-Id');
    console.log('HEADER SESSION:', newSessionId);

    if (!conversationId && newSessionId && onSessionId) {
      onSessionId(newSessionId);
    }

    if (!response.body) {
      throw new Error('Streaming not supported');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      onChunk(decoder.decode(value));
    }
  },

  /* ============================
     🗑️ DELETE CHAT SESSION
     ============================ */
  async deleteSession(sessionId: string): Promise<void> {
  const token = localStorage.getItem('access_token');

  if (!token) {
    throw new Error('No auth token found');
  }

  const response = await fetch(
    `http://localhost:8000/chat/sessions/${sessionId}`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`, // 🔥 REQUIRED
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to delete chat session');
  }
}
};