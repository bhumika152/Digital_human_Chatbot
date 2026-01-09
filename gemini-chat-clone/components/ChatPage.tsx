import React, { useState, useEffect } from 'react';
import { User, Message, ChatSession } from '../types';
import { Sidebar } from './Sidebar';
import { ChatWindow } from './ChatWindow';
import { chatService } from '../services/chatService';

interface ChatPageProps {
  user: User | null;
  onLogout: () => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ user, onLogout }) => {
  // 🔑 SINGLE SOURCE OF TRUTH
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTyping, setIsTyping] = useState(false);

    // 👇 👇 👇 YAHI ADD KARNA HAI
  const PAGE_SIZE = 20;
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true); 

//    // ✅👇 YAHAN ADD KARO (TEMP TEST)
//   useEffect(() => {
//   const fakeMessages = Array.from({ length: 40 }, (_, i) => ({
//     request_id: `fake-${i}`,
//     session_id: 'test',
//     role: i % 2 === 0 ? 'user' : 'assistant',
//     content: `Fake message ${i}`,
//     created_at: new Date().toISOString(),
//   }));

//   // 🔥 ONLY LAST 20 LOAD FIRST
//   setMessages(fakeMessages.slice(20));
//   setOffset(20);
//   setHasMore(true);
// }, []);

// // ✅ 3. 🔥 YAHI ADD KARNA HAI (TESTING FUNCTION)
//   const loadMoreMessages = async () => {
//     const older = Array.from({ length: 20 }, (_, i) => ({
//       request_id: `old-${i}`,
//       session_id: 'test',
//       role: i % 2 === 0 ? 'user' : 'assistant',
//       content: `OLDER message ${i}`,
//       created_at: new Date().toISOString(),
//     }));

//     setMessages(prev => [...older, ...prev]);
//     // setHasMore(false); // 👈 ek hi baar load
//   };
  /* ----------------------------
     LOAD SIDEBAR SESSIONS  
  ---------------------------- */
  useEffect(() => {
    if (!user) return;

    chatService
      .getSessions()
      .then(setSessions)
      .catch(err => console.error('Failed to load sessions', err));
  }, [user]);

  /* ----------------------------
   LOAD CHAT HISTORY ON SIDEBAR CLICK
  ---------------------------- */
useEffect(() => {
  if (!currentSessionId) return;

  const loadMessages = async () => {
    try {
      const history = await chatService.getMessages(
        currentSessionId,
        PAGE_SIZE,
        0
      );

      setMessages(history);
      setOffset(history.length);                 // 🔥 REQUIRED
      setHasMore(history.length === PAGE_SIZE);  // 🔥 REQUIRED
    } catch (err) {
      console.error('Failed to load chat history', err);
    }
  };

  loadMessages();
}, [currentSessionId]);

/* ----------------------------
   LOAD OLDER MESSAGES (PAGINATION)
---------------------------- */
const loadMoreMessages = async () => {
  if (!currentSessionId) return;

  try {
    const olderMessages = await chatService.getMessages(
      currentSessionId,
      PAGE_SIZE,
      offset
    );

    setMessages(prev => [...olderMessages, ...prev]); // ⬆️ prepend
    setOffset(prev => prev + olderMessages.length);
    // hasMore ko yahan touch hi nahi karna
  } catch (err) {
    console.error('Failed to load older messages', err);
  }
};


  /* ----------------------------
     NEW CHAT
  ---------------------------- */
  const handleNewChat = async () => {
  try {
    // 🔥 BACKEND ME NEW SESSION CREATE
    const newSession = await chatService.createSession();

    // 🔑 SET NEW SESSION ID
    setCurrentSessionId(newSession.session_id);

    // 🧹 clear UI
    setMessages([]);

    // 🔄 refresh sidebar
    const updatedSessions = await chatService.getSessions();
    setSessions(updatedSessions);
  } catch (err) {
    console.error("Failed to create new chat", err);
  }
};

  /* ----------------------------
     SEND MESSAGE (CORE FIX)
  ---------------------------- */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please login again');
      return;
    }

    // 👤 show user message instantly
    const userMsg: Message = {
      request_id: 'user-' + Date.now(),
      session_id: currentSessionId ?? '',
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    // 🤖 assistant placeholder
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
      let fullResponse = '';

      await chatService.sendChatMessageStreaming(
        token,
        currentSessionId, // 🔥 SAME session id reuse hoti hai
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
        },
        (newSessionId) => {
          // 🔑 ONLY FIRST MESSAGE ME SAVE HOGA
          setCurrentSessionId(prev => prev ?? newSessionId);
          }
        
      );

      // 🔄 refresh sidebar
      const updatedSessions = await chatService.getSessions();
      setSessions(updatedSessions);

    } catch (err) {
      setMessages(prev =>
        prev.map(m =>
          m.request_id === assistantTempId
            ? { ...m, content: '❌ Error connecting to backend' }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  /* ----------------------------
     DELETE CHAT
  ---------------------------- */
  const handleDeleteChat = async (sessionId: string) => {
    if (!window.confirm('Delete this chat?')) return;

    try {
      await chatService.deleteSession(sessionId);

      setSessions(prev => prev.filter(s => s.session_id !== sessionId));

      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Delete failed', err);
      alert('Unable to delete chat');
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        chats={sessions.map(s => ({
          id: s.session_id,
          title: s.session_title,
        }))}
        currentChatId={currentSessionId}
        onSelectChat={(id) => setCurrentSessionId(id)}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onLogout={onLogout}
        user={user}
      />

      <ChatWindow
        chat={{
          id: currentSessionId ?? 'new',
          messages,
        }}
        onSendMessage={handleSendMessage}
        isTyping={isTyping}
        isSidebarOpen={isSidebarOpen}
        hasMore={hasMore}                 // 👈 MUST
        onLoadMore={loadMoreMessages}     // 👈 MUST
      />
    </div>
  );
};
