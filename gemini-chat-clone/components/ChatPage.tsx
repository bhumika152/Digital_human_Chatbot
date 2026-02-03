import React, { useEffect, useState } from "react";
import { User, Message, ChatSession } from "../types";
import { Sidebar } from "./Sidebar";
import { ChatWindow } from "./ChatWindow";
import { chatService } from "../services/chatService";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { confirmToast } from "../utils/confirmToast";
 
interface ChatPageProps {
  user: User | null;
  onLogout: () => void;
}
 
export const ChatPage: React.FC<ChatPageProps> = ({ user, onLogout }) => {
  const PAGE_SIZE = 20;
 
  /* =========================
     CORE STATE
  ========================== */
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(() => {
    const id = localStorage.getItem("active_session_id");
    return id;
  });
 
  const [sessionSource, setSessionSource] =
    useState<"sidebar" | "send" | "restore" | null>(() => {
      return localStorage.getItem("active_session_id") ? "restore" : null;
    });
 
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isRestoringSession, setIsRestoringSession] = useState(true);
 
  /* =========================
     LOAD SIDEBAR SESSIONS
  ========================== */
  useEffect(() => {
    if (!user) return;
 
    chatService
      .getSessions()
      .then(setSessions)
      .catch(() => toast.error("Failed to load chats"));
  }, [user]);
 
  /* =========================
     LOAD CHAT HISTORY
     (SINGLE SOURCE OF TRUTH)
  ========================== */
  useEffect(() => {
    if (!currentSessionId) {
      setIsRestoringSession(false);
      return;
    }
 
    // 🔥 First message flow → keep optimistic UI
    if (sessionSource === "send") {
      setSessionSource(null);
      setIsRestoringSession(false);
      return;
    }
 
    const loadHistory = async () => {
      try {
        const history = await chatService.getMessages(
          currentSessionId,
          PAGE_SIZE,
          0
        );
 
        setMessages(history);
        setOffset(history.length);
        setHasMore(history.length === PAGE_SIZE);
      } catch {
        toast.error("Failed to load chat history");
      } finally {
        setIsRestoringSession(false);
        setSessionSource(null);
      }
    };
 
    loadHistory();
  }, [currentSessionId]);
 
  /* =========================
     PAGINATION (OLDER MESSAGES)
  ========================== */
  const loadMoreMessages = async () => {
    if (!currentSessionId || !hasMore) return;
 
    try {
      const older = await chatService.getMessages(
        currentSessionId,
        PAGE_SIZE,
        offset
      );
 
      setMessages(prev => [...older, ...prev]);
      setOffset(prev => prev + older.length);
      setHasMore(older.length === PAGE_SIZE);
    } catch {
      console.error("Pagination failed");
    }
  };
 
  useEffect(() => {
    const handler = () => {
      if (hasMore) loadMoreMessages();
    };
 
    window.addEventListener("loadMoreMessages", handler);
    return () => window.removeEventListener("loadMoreMessages", handler);
  }, [hasMore, offset, currentSessionId]);
 
  /* =========================
     SEND MESSAGE
  ========================== */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return;
 
    const token = localStorage.getItem("access_token");
    if (!token) return;
 
    const userMsg: Message = {
      request_id: `user-${Date.now()}`,
      session_id: currentSessionId ?? "",
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
 
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);
 
    const assistantId = `assistant-${Date.now()}`;
    setMessages(prev => [
      ...prev,
      {
        request_id: assistantId,
        session_id: currentSessionId ?? "",
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
      },
    ]);
 
    let fullResponse = "";
 
    try {
      await chatService.sendChatMessageStreaming(
        token,
        currentSessionId,
        content,
        chunk => {
          fullResponse += chunk;
          setMessages(prev =>
            prev.map(m =>
              m.request_id === assistantId
                ? { ...m, content: fullResponse }
                : m
            )
          );
        },
        newSessionId => {
          setSessionSource("send"); // 🔥 KEY FIX
          setCurrentSessionId(prev => {
            if (!prev) {
              localStorage.setItem("active_session_id", newSessionId);
              return newSessionId;
            }
            return prev;
          });
        }
      );
 
      setSessions(await chatService.getSessions());
    } catch {
      setMessages(prev =>
        prev.map(m =>
          m.request_id === assistantId
            ? { ...m, content: "Error generating response" }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };
 
  /* =========================
     NEW CHAT
  ========================== */
  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setOffset(0);
    setHasMore(true);
    localStorage.removeItem("active_session_id");
  };
 
  /* =========================
     DELETE CHAT
  ========================== */
  const handleDeleteChat = (sessionId: string) => {
    confirmToast("Delete this chat?", async () => {
      try {
        await chatService.deleteSession(sessionId);
 
        setSessions(prev =>
          prev.filter(s => s.session_id !== sessionId)
        );
 
        if (currentSessionId === sessionId) {
          handleNewChat();
        }
 
        toast.success("Chat deleted");
      } catch {
        toast.error("Delete failed");
      }
    });
  };
 
  /* =========================
     RENDER
  ========================== */
  return (
    <div className="flex h-screen overflow-hidden">
      <ToastContainer />
 
      <Sidebar
        chats={sessions.map(s => ({
          id: s.session_id,
          title: s.session_title,
        }))}
        currentChatId={currentSessionId}
        onSelectChat={(id) => {
          if (id === currentSessionId) return;
          setSessionSource("sidebar");
          setIsRestoringSession(true);
          setCurrentSessionId(id);
          localStorage.setItem("active_session_id", id);
        }}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onLogout={onLogout}
        user={user}
        onEditProfile={() => {}}
      />
 
      {isRestoringSession ? (
        <div className="flex-1 bg-[#0f0f0f]" />
      ) : (
        <ChatWindow
          chat={
            currentSessionId || messages.length > 0
              ? { id: currentSessionId ?? "new", messages }
              : undefined
          }
          onSendMessage={handleSendMessage}
          isTyping={isTyping}
          isSidebarOpen={isSidebarOpen}
        />
      )}
    </div>
  );
};
 
 