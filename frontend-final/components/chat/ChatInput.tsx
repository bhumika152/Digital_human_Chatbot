"use client";

import { useState } from "react";

export default function ChatInput({
  sessionId,
  setMessages,
}: {
  sessionId: string;
  setMessages: any;
}) {
  const [input, setInput] = useState("");

  async function sendMessage() {
    if (!input.trim()) return;

    const token = localStorage.getItem("access_token"); // 🔑

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`, // ✅ REQUIRED
      },
      body: JSON.stringify({
        conversation_id: sessionId,
        message: input, // IMPORTANT: string
      }),
    });

    const data = await res.json();

    setMessages((prev: any[]) => [
      ...prev,
      { role: "user", content: input },
      { role: "assistant", content: data.messages[1].content },
    ]);

    setInput("");
  }

  return (
    <div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type message"
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
