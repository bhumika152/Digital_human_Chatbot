"use client";

import { useEffect, useState } from "react";
import ChatHome from "./ChatHome";
import ChatWindow from "./ChatWindow";

export default function ChatContainer() {
  const [messages, setMessages] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("active_session");
    if (!stored) return;

    setSessionId(stored);

    fetch(`http://localhost:8000/chat/history/${stored}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((r) => r.json())
      .then(setMessages);
  }, []);

  if (!sessionId) {
    return <ChatHome setSessionId={setSessionId} />;
  }

  return (
    <ChatWindow
      messages={messages}
      setMessages={setMessages}
      sessionId={sessionId}
    />
  );
}
