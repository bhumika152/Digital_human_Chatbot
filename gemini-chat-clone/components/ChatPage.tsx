
// import React, { useState, useEffect, useCallback } from 'react';
// import { User, ChatSession, Message } from '../types';
// import { Sidebar } from './Sidebar';
// import { ChatWindow } from './ChatWindow';
// import { geminiService } from '../services/geminiService';
// import { chatService } from '../services/chatService';

// interface ChatPageProps {
//   user: User | null;
//   onLogout: () => void;
// }

// export const ChatPage: React.FC<ChatPageProps> = ({ user, onLogout }) => {
//   const [sessions, setSessions] = useState<ChatSession[]>([]);
//   const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [isSidebarOpen, setIsSidebarOpen] = useState(true);
//   const [isTyping, setIsTyping] = useState(false);

//   // Load chat history (sessions) from DB when user is logged in
//   useEffect(() => {
//     if (user?.user_id) {
//       chatService.getSessions(user.user_id)
//         .then(setSessions)
//         .catch(err => console.error("Error loading sessions:", err));
//     }
//   }, [user?.user_id]);

//   // Load messages from DB when a specific session is selected
//   useEffect(() => {
//     if (currentSessionId) {
//       chatService.getMessages(currentSessionId)
//         .then(setMessages)
//         .catch(err => console.error("Error loading messages:", err));
//     } else {
//       setMessages([]);
//     }
//   }, [currentSessionId]);

//   const handleNewChat = async () => {
//     if (!user) return;
//     try {
//       const newSession = await chatService.createSession(user.user_id, 'New Chat');
//       setSessions(prev => [newSession, ...prev]);
//       setCurrentSessionId(newSession.session_id);
//     } catch (err) {
//       console.error("Failed to create new chat:", err);
//     }
//   };

//   const handleSendMessage = async (content: string) => {
//     if (!content.trim() || !user) return;

//     let sessionId = currentSessionId;

//     // Auto-create session if it's a new chat
//     if (!sessionId) {
//       try {
//         const title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
//         const newSession = await chatService.createSession(user.user_id, title);
//         setSessions(prev => [newSession, ...prev]);
//         sessionId = newSession.session_id;
//         setCurrentSessionId(sessionId);
//       } catch (err) {
//         return console.error("Failed to initiate session:", err);
//       }
//     }

//     // 1. Save User Message to DB
//     try {
//       const savedUserMsg = await chatService.saveMessage(sessionId, 'user', content);
//       setMessages(prev => [...prev, savedUserMsg]);
//     } catch (err) {
//       return console.error("Failed to save user message:", err);
//     }

//     setIsTyping(true);

//     // Prepare Gemini History
//     const history: { role: 'user' | 'model'; parts: { text: string }[] }[] = messages.map(m => ({
//       role: m.role === 'user' ? 'user' : 'model',
//       parts: [{ text: m.content }]
//     }));

//     // Create UI placeholder for streaming response
//     const tempId = 'temp-' + Date.now();
//     const tempMsg: Message = {
//       request_id: tempId,
//       session_id: sessionId,
//       role: 'assistant',
//       content: '',
//       created_at: new Date().toISOString()
//     };
//     setMessages(prev => [...prev, tempMsg]);

//     try {
//       let fullResponse = "";
//       await geminiService.streamChat(content, history, (chunk) => {
//         fullResponse += chunk;
//         setMessages(prev => prev.map(m => 
//           m.request_id === tempId ? { ...m, content: fullResponse } : m
//         ));
//       });

//       // 2. Save Assistant Message to DB after streaming is done
//       const savedAiMsg = await chatService.saveMessage(sessionId, 'assistant', fullResponse);
      
//       // Update local state with real DB object (containing real request_id)
//       setMessages(prev => prev.map(m => 
//         m.request_id === tempId ? savedAiMsg : m
//       ));

//     } catch (err) {
//       setMessages(prev => prev.map(m => 
//         m.request_id === tempId ? { ...m, content: "Error connecting to AI." } : m
//       ));
//     } finally {
//       setIsTyping(false);
//     }
//   };

//   const handleDeleteChat = (id: string) => {
//     // Implement delete API call if needed
//     setSessions(prev => prev.filter(s => s.session_id !== id));
//     if (currentSessionId === id) setCurrentSessionId(null);
//   };
  

//   return (
//     <div className="flex h-screen overflow-hidden">
//       <Sidebar
//         chats={sessions.map(s => ({ id: s.session_id, title: s.session_title }))}
//         currentChatId={currentSessionId}
//         onSelectChat={setCurrentSessionId}
//         onNewChat={handleNewChat}
//         onDeleteChat={handleDeleteChat}
//         isOpen={isSidebarOpen}
//         toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
//         onLogout={onLogout}
//         user={user}
//       />

//       <ChatWindow
//         chat={currentSessionId ? { id: currentSessionId, messages } : undefined}
//         onSendMessage={handleSendMessage}
//         isTyping={isTyping}
//         isSidebarOpen={isSidebarOpen}
//       />
//     </div>
//   );
// };
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
