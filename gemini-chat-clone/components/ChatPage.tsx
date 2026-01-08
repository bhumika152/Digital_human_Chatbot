import React, { useState } from 'react';
import { User, Message } from '../types';
import { Sidebar } from './Sidebar';
import { ChatWindow } from './ChatWindow';
import { chatService } from '../services/chatService';

interface ChatPageProps {
  user: User | null;
  onLogout: () => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ user, onLogout }) => {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTyping, setIsTyping] = useState(false);

  /* ----------------------------
     NEW CHAT
  ---------------------------- */
  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  /* ----------------------------
     SEND MESSAGE (CORE LOGIC)
  ---------------------------- */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return;

    const token = localStorage.getItem('access_token');
    if (!token) return alert("Please login again");

    // 1️⃣ Show user message instantly
    const userMsg: Message = {
      request_id: 'user-' + Date.now(),
      session_id: currentSessionId ?? '',
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    // 2️⃣ Assistant placeholder
    const assistantTempId = 'assistant-' + Date.now();
    setMessages(prev => [
      ...prev,
      {
        request_id: assistantTempId,
        session_id: currentSessionId ?? '',
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      let fullResponse = "";

      await chatService.sendChatMessageStreaming(
        token,
        currentSessionId, // null = new chat
        content,
        (chunk) => {
          fullResponse += chunk;

          setMessages(prev =>
            prev.map(m =>
              m.request_id === assistantTempId
                ? { ...m, content: fullResponse }
                : m
            )
          );
        }
      );

      // 🔑 IMPORTANT:
      // backend automatically creates session if needed
      // but frontend ko session_id abhi nahi milta
      // isliye first chat ke baad sidebar logic baad me add karenge

    } catch (err) {
      setMessages(prev =>
        prev.map(m =>
          m.request_id === assistantTempId
            ? { ...m, content: "❌ Error connecting to backend" }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  /* ----------------------------
     DELETE CHAT (UI ONLY)
  ---------------------------- */
  const handleDeleteChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        chats={[]}               // ⏳ sessions API baad me
        currentChatId={currentSessionId}
        onSelectChat={() => {}}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onLogout={onLogout}
        user={user}
      />

      <ChatWindow
        chat={
          currentSessionId
            ? { id: currentSessionId, messages }
            : { id: 'new', messages }
        }
        onSendMessage={handleSendMessage}
        isTyping={isTyping}
        isSidebarOpen={isSidebarOpen}
      />
    </div>
  );
};
