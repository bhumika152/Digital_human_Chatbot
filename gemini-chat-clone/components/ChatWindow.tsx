
import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types';

interface ChatWindowProps {
  chat: { id: string, messages: Message[] } | undefined;
  onSendMessage: (content: string) => void;
  isTyping: boolean;
  isSidebarOpen: boolean;
  
 hasMore: boolean;        // ✅ REQUIRED
  onLoadMore: () => void;  // ✅ REQUIRED
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ chat, onSendMessage, isTyping,isSidebarOpen,hasMore,onLoadMore }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat?.messages.length, chat?.messages[chat?.messages.length - 1]?.content]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isTyping) return;
    onSendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <main className="flex-1 flex flex-col bg-[#0d0d0d] h-full relative overflow-hidden">
      <div className="flex-1 overflow-y-auto no-scrollbar scroll-smooth">
        {!chat || chat.messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-8">
            <div className="w-16 h-16 bg-[#171717] rounded-full flex items-center justify-center mb-6 border border-[#303030]">
              <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-4 text-center">How can I help you today?</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
              {[
                "Explain quantum computing in simple terms",
                "Suggest 10 healthy snack ideas",
                "Write a poem about summer rain",
                "Help me debug a React useEffect loop"
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(suggestion)}
                  className="p-4 text-left border border-[#303030] rounded-xl hover:bg-[#171717] transition text-sm text-[#b4b4b4]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="w-full max-w-3xl mx-auto py-8 px-4 space-y-8">

  {/* 🔥 LOAD OLDER MESSAGES BUTTON (TOP) */}
  {hasMore && (
    <div className="flex justify-center mb-4">
      <button
        onClick={onLoadMore}
        className="text-xs text-[#b4b4b4] hover:text-white px-3 py-1 rounded-lg border border-[#303030] hover:bg-[#171717] transition"
      >
        Load older messages
      </button>
    </div>
  )}

  {/* 💬 CHAT MESSAGES */}
  {chat.messages.map((message) => (
    <div key={message.request_id} className="flex gap-4">
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          message.role === 'user' ? 'bg-indigo-600' : 'bg-emerald-600'
        }`}
      >
        {message.role === 'user' ? (
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
          </svg>
        )}
      </div>

      <div className="flex-1 space-y-1 overflow-hidden">
        <div className="font-bold text-sm uppercase tracking-wide text-[#b4b4b4]">
          {message.role === 'user' ? 'You' : 'Assistant'}
        </div>
        <div className="text-base text-[#ececec] whitespace-pre-wrap leading-relaxed">
          {message.content || (isTyping && message.request_id.startsWith('temp') ? (
            <span className="flex gap-1 h-6 items-center">
              <span className="w-1 h-1 bg-white rounded-full animate-bounce"></span>
              <span className="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </span>
          ) : null)}
        </div>
      </div>
    </div>
  ))}

  <div ref={messagesEndRef} />
</div>

        )}
      </div>

      <div className="p-4 bg-gradient-to-t from-[#0d0d0d] via-[#0d0d0d] to-transparent">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group">
          <textarea
            rows={1}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message..."
            className="w-full bg-[#171717] text-[#ececec] border border-[#303030] rounded-2xl pl-4 pr-14 py-4 focus:outline-none focus:ring-1 focus:ring-[#676767] resize-none overflow-hidden max-h-48 transition"
            style={{ height: 'auto' }}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className={`absolute right-3 bottom-3 p-2 rounded-xl transition ${
              inputValue.trim() && !isTyping ? 'bg-white text-black hover:bg-[#d1d1d1]' : 'text-[#676767] bg-[#2f2f2f]'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </form>
      </div>
    </main>
  );
};
