
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatPage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // AUTH GUARD
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) router.replace("/login");
  }, [router]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const token = localStorage.getItem("token");
    if (!token) return;

    const userText = input;

    setMessages(prev => [...prev, { role: "user", content: userText }]);
    setInput("");

    // Placeholder bot message (empty)
    setMessages(prev => [...prev, { role: "assistant", content: "" }]);

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: { content: userText },
      }),
    });

    if (!conversationId) {
      const newId = res.headers.get("x-session-id");
      if (newId) setConversationId(newId);
    }

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    let botText = "";

    if (!reader) return;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      botText += chunk;

      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: botText,
        };
        return updated;
      });
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={m.role}>
            <p>{m.content}</p>
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Ask anything..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
