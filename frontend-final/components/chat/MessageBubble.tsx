export default function MessageBubble({ message }: any) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`px-3 py-2 rounded max-w-lg ${
          isUser ? "bg-blue-600 text-white" : "bg-gray-200"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
