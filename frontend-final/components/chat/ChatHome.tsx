"use client";

import ChatEmptyState from "./ChatEmptyState";
import { v4 as uuidv4 } from "uuid";

export default function ChatHome({ setSessionId }: any) {
  function startNewChat() {
    const id = uuidv4();
    localStorage.setItem("active_session", id);
    setSessionId(id);
  }

  return (
    <div className="h-full flex items-center justify-center">
      <ChatEmptyState onStart={startNewChat} />
    </div>
  );
}
