export default function ChatEmptyState({ onStart }: any) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-bold">Start a new chat</h2>
        <p className="text-gray-500">Your AI assistant is ready</p>
        <button
          onClick={onStart}
          className="mt-4 px-4 py-2 bg-black text-white rounded"
        >
          New Chat
        </button>
      </div>
    );
  }
  