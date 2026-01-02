"use client";

import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";

interface ChatWindowProps {
  messages: any[];
  setMessages: React.Dispatch<React.SetStateAction<any[]>>;
  sessionId: string;
}

export default function ChatWindow({
  messages,
  setMessages,
  sessionId,
}: ChatWindowProps) {
  return (
    <div className="flex flex-col h-full">
      <ChatMessages messages={messages} />
      <ChatInput setMessages={setMessages} sessionId={sessionId} />
    </div>
  );
}
