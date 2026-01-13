export interface Message {
  request_id: string; // UUID from chat_messages
  session_id: string; // UUID from chat_sessions
  role: 'user' | 'assistant' | 'system';
  content: string;
  token_count?: number;
  created_at: string;
}

export interface ChatSession {
  session_id: string; // UUID
  user_id: string;    // BIGINT
  session_title: string;
  is_active: boolean;
  created_at: string;
  ended_at?: string;
}

export interface User {
  user_id: string; // BIGSERIAL
  email: string;
  username: string; // We'll derive this or add it to your users table
  is_active: boolean;
  created_at: string;
}

export type AuthMode = 'login' | 'signup' | 'forgot-password'| 'reset-password';
export type AppView = 'auth' | 'chat';