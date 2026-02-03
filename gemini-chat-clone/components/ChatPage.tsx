import React, { useEffect, useState } from "react";
import { User, Message, ChatSession } from "../types";
import { Sidebar } from "./Sidebar";
import { ChatWindow } from "./ChatWindow";
import { chatService } from "../services/chatService";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export const ChatPage: React.FC<{
  user: User | null;
  onLogout: () => void;
}> = ({ user, onLogout }) => {
  const PAGE_SIZE = 20;

  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [isTyping, setIsTyping] = useState(false);

  // 🔑 THIS is the missing piece
  const [sessionSource, setSessionSource] =
    useState<"sidebar" | "send" | null>(null);

  /* =========================
     LOAD SIDEBAR SESSIONS
  ========================== */
  useEffect(() => {
    if (!user) return;
    chatService.getSessions().then(setSessions);
  }, [user]);

  /* =========================
     LOAD CHAT HISTORY
  ========================== */
  useEffect(() => {
    if (!currentSessionId) return;

    // 🔥 If session was created by sending first message,
    // keep optimistic UI, do NOT refetch
    if (sessionSource === "send") {
      setSessionSource(null);
      return;
    }

    const loadMessages = async () => {
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
      }
    };

    loadMessages();
  }, [currentSessionId]);

  /* =========================
     LOAD OLDER MESSAGES
  ========================== */
  const loadMoreMessages = async () => {
    if (!currentSessionId || !hasMore) return;

    const older = await chatService.getMessages(
      currentSessionId,
      PAGE_SIZE,
      offset
    );

    setMessages(prev => [...older, ...prev]);
    setOffset(prev => prev + older.length);
    setHasMore(older.length === PAGE_SIZE);
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
        setSessionSource("send");        // 🔥 KEY
        setCurrentSessionId(prev => prev ?? newSessionId);
      }
    );

    setIsTyping(false);
    setSessions(await chatService.getSessions());
  };

  /* =========================
     DELETE CHAT
  ========================== */
  const handleDeleteChat = async (sessionId: string) => {
    await chatService.deleteSession(sessionId);

    setSessions(prev => prev.filter(s => s.session_id !== sessionId));

    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
      setMessages([]);
      setOffset(0);
      setHasMore(true);
    }

    toast.success("Chat deleted");
  };

  return (
    <div className="flex h-screen">
      <ToastContainer />

      <Sidebar
        chats={sessions.map(s => ({
          id: s.session_id,
          title: s.session_title,
        }))}
        currentChatId={currentSessionId}
        onSelectChat={id => {
          setSessionSource("sidebar");   // 🔥 IMPORTANT
          setCurrentSessionId(id);
          setMessages([]);
          setOffset(0);
          setHasMore(true);
        }}
        onNewChat={() => {
          setCurrentSessionId(null);
          setMessages([]);
          setOffset(0);
          setHasMore(true);
        }}
        onDeleteChat={handleDeleteChat}
        isOpen={true}
        toggleSidebar={() => {}}
        onLogout={onLogout}
        user={user}
        onEditProfile={() => {}}
      />

      <ChatWindow
        chat={{ id: currentSessionId ?? "new", messages }}
        onSendMessage={handleSendMessage}
        isTyping={isTyping}
        isSidebarOpen={true}
      />
    </div>
  );
};
