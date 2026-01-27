
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
  user_id: string | number;    // BIGINT or string
  session_title: string;
  is_active: boolean;
  created_at: string;
  ended_at?: string;
}

export interface User {
  user_id?: string | number;
  id?: string | number; // Some backends use 'id'
  email?: string;
  user_email?: string; // Variation
  username?: string;
  name?: string; // Variation
  is_active?: boolean;
  created_at?: string;
  [key: string]: any; // Allow for extra fields like tokens
}

export type AuthMode = 'login' | 'signup' | 'forgot-password' | 'reset-password';
export type AppView = 'auth' | 'chat';