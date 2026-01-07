
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  updatedAt: number;
}

export interface User {
  id: string;
  email: string;
  username: string;
}

export type AuthMode = 'login' | 'signup';
export type AppView = 'auth' | 'chat';
