
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { User, Chat, Message } from '../types';
import { Sidebar } from './Sidebar';
import { ChatWindow } from './ChatWindow';
import { geminiService } from '../services/geminiService';

interface ChatPageProps {
  user: User | null;
  onLogout: () => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ user, onLogout }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTyping, setIsTyping] = useState(false);

  // Load chats from localStorage on mount
  useEffect(() => {
    if (user) {
      const savedChats = localStorage.getItem(`chats_${user.id}`);
      if (savedChats) {
        setChats(JSON.parse(savedChats));
      }
    }
  }, [user]);

  // Persist chats to localStorage whenever they change
  useEffect(() => {
    if (user && chats.length > 0) {
      localStorage.setItem(`chats_${user.id}`, JSON.stringify(chats));
    }
  }, [chats, user]);

  const activeChat = chats.find(c => c.id === currentChatId);

  const handleNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      updatedAt: Date.now(),
    };
    setChats(prev => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    let chatId = currentChatId;
    let currentMessages: Message[] = [];

    // Auto-create chat if none selected
    if (!chatId) {
      const newChat: Chat = {
        id: Date.now().toString(),
        title: content.substring(0, 30) + (content.length > 30 ? '...' : ''),
        messages: [],
        updatedAt: Date.now(),
      };
      setChats(prev => [newChat, ...prev]);
      setCurrentChatId(newChat.id);
      chatId = newChat.id;
    } else {
      currentMessages = activeChat?.messages || [];
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };

    // Update UI immediately with user message
    setChats(prev => prev.map(c => 
      c.id === chatId ? { ...c, messages: [...c.messages, userMessage], updatedAt: Date.now() } : c
    ));

    setIsTyping(true);

    // Fix: Explicitly type history to match the Gemini service expected role types ('user' | 'model')
    const history: { role: 'user' | 'model'; parts: { text: string }[] }[] = currentMessages.map(m => ({
      role: m.role === 'user' ? 'user' : 'model',
      parts: [{ text: m.content }]
    }));

    // Create placeholder for assistant message
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    };

    setChats(prev => prev.map(c => 
      c.id === chatId ? { ...c, messages: [...c.messages, assistantMessage] } : c
    ));

    try {
      let fullAssistantResponse = "";
      await geminiService.streamChat(content, history, (chunk) => {
        fullAssistantResponse += chunk;
        setChats(prev => prev.map(c => 
          c.id === chatId ? {
            ...c,
            messages: c.messages.map(m => m.id === assistantMessageId ? { ...m, content: fullAssistantResponse } : m)
          } : c
        ));
      });

      // Update chat title if it's the first exchange
      if (currentMessages.length === 0) {
        setChats(prev => prev.map(c => 
          c.id === chatId ? { ...c, title: content.substring(0, 40) + (content.length > 40 ? '...' : '') } : c
        ));
      }

    } catch (err) {
      setChats(prev => prev.map(c => 
        c.id === chatId ? {
          ...c,
          messages: c.messages.map(m => m.id === assistantMessageId ? { ...m, content: "Sorry, I encountered an error. Please try again." } : m)
        } : c
      ));
    } finally {
      setIsTyping(false);
    }
  };

  const handleDeleteChat = (id: string) => {
    setChats(prev => prev.filter(c => c.id !== id));
    if (currentChatId === id) setCurrentChatId(null);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onSelectChat={setCurrentChatId}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onLogout={onLogout}
        user={user}
      />

      {/* Main Chat Area */}
      <ChatWindow
        chat={activeChat}
        onSendMessage={handleSendMessage}
        isTyping={isTyping}
        isSidebarOpen={isSidebarOpen}
      />
    </div>
  );
};
