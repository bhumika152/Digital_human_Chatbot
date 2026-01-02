import MessageBubble from "./MessageBubble";

interface ChatMessagesProps {
    messages: any[];
  }
  
  export default function ChatMessages({ messages }: ChatMessagesProps) {
    return (
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
      </div>
    );
  }
  