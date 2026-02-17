
import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../types';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
 
 
interface ChatWindowProps {
  chat: { id: string, messages: Message[] } | undefined;
  onSendMessage: (content: string) => void;
  isTyping: boolean;
  isSidebarOpen: boolean;
}
 
export const ChatWindow: React.FC<ChatWindowProps> = ({ chat, onSendMessage, isTyping,isSidebarOpen}) => {
 
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // scroll system
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const [showScrollDown, setShowScrollDown] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

 
  useEffect(() => {
    const el = chatScrollRef.current;
    if (!el) return;
 
    const handleScroll = () => {
      const threshold = 120;
 
      // show ↓ button when not at bottom
      const isNotAtBottom =
        el.scrollTop + el.clientHeight < el.scrollHeight - threshold;
      setShowScrollDown(isNotAtBottom);
 
      // 🔼 Top pe → trigger pagination
      if (el.scrollTop === 0) {
        const event = new CustomEvent("loadMoreMessages");
        window.dispatchEvent(event);
      }
    };
 
    el.addEventListener("scroll", handleScroll);
    return () => el.removeEventListener("scroll", handleScroll);
  }, []);
 
  // ✅ Session change hone par direct bottom jump
useEffect(() => {
  const el = chatScrollRef.current;
  if (!el) return;
 
  setTimeout(() => {
    el.scrollTop = el.scrollHeight;
  }, 0);
 
}, [chat?.id]);
 
 
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
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


// 🎤 Start Recording
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        audioChunksRef.current.push(e.data);
      }
    };

    mediaRecorder.onstop = sendRecording;

    mediaRecorder.start();
    setIsRecording(true);

  } catch (err) {
    console.error("Mic access error:", err);
    alert("Microphone permission denied!");
  }
};

// ⏹ Stop Recording
const stopRecording = () => {
  if (mediaRecorderRef.current) {
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  }
};

// 📤 Send to Backend
// 📤 Send voice to backend
const sendRecording = async () => {
  try {
    const audioBlob = new Blob(audioChunksRef.current, {
      type: "audio/webm", // browser format
    });

    const formData = new FormData();
    formData.append("file", audioBlob, "voice.webm");

    const res = await fetch("http://localhost:8000/voice", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    console.log("VOICE RESPONSE:", data);

    // ✅ Send user text
    if (data.user_text) {
      onSendMessage(data.user_text);
    }

    // ✅ Play base64 audio
    if (data.audio) {
      const audio = new Audio(
        "data:audio/wav;base64," + data.audio
      );
      audio.play();
    }

  } catch (err) {
    console.error("Voice send error:", err);
  }
};


  return (
    <main className="flex-1 flex flex-col bg-[#0d0d0d] h-full relative overflow-hidden">
        {/* 👇 YE SCROLL CONTAINER HAI */}
      <div
        ref={chatScrollRef}
        className="flex-1 overflow-y-auto no-scrollbar"
      >
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
             
  {/* 💬 CHAT MESSAGES */}
  {chat.messages.map((message) => (
    // <div key={message.request_id} className="flex gap-4">
    <div
  key={message.request_id}
  className={`flex gap-4 ${
    message.role === "user" ? "justify-end" : "justify-start"
  }`}
>
 
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
 
      {/* <div className="flex-1 space-y-1 overflow-hidden"> */}
      <div className="flex flex-col max-w-[80%]">
 
        <div className="font-bold text-sm uppercase tracking-wide text-[#b4b4b4]">
          {message.role === 'user' ? 'You' : 'Assistant'}
        </div>
        {/* <div className="text-base text-[#ececec] leading-relaxed prose prose-invert max-w-none"> */}
        {/* <div
  className={`text-base text-[#ececec] leading-relaxed prose prose-invert px-4 py-2 rounded-2xl bg-[#1e1e1e] ${
    message.role === "user" ? "ml-auto" : ""
  }`}
> */}
 
<div
  className={`text-base leading-relaxed prose prose-invert ${
    message.role === "user"
      ? "px-4 py-2 rounded-2xl bg-[#1e1e1e] text-white ml-auto"
      : "text-[#e6e6e6]"
  }`}
>
 
{/* <div
  className={`
    text-base leading-relaxed prose prose-invert
    ${message.role === "assistant"
      ? "text-[#e6e6e6]"
      : "px-4 py-2 rounded-2xl bg-[#1e1e1e] text-white ml-auto"}
  `}
> */}
 
 
 
 
  {message.content ? (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {message.content}
    </ReactMarkdown>
  ) : (
    isTyping && message.request_id.startsWith('assistant') && (
      <span className="flex gap-1 h-6 items-center">
        <span className="w-1 h-1 bg-white rounded-full animate-bounce"></span>
        <span className="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:0.2s]"></span>
        <span className="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:0.4s]"></span>
      </span>
    )
  )}
</div>
 
      </div>
    </div>
  ))}
 
  <div ref={messagesEndRef} />
</div>
 
        )}
      </div>
 
      {/* changes */}
      {showScrollDown && (
  <button
    onClick={() =>
      chatScrollRef.current?.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: "smooth",
      })
    }
    className="absolute bottom-24 left-1/2 -translate-x-1/2 bg-white text-black w-10 h-10 rounded-full shadow-lg hover:scale-110 transition"
 
  >
    ↓
  </button>
)}
 
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
          <div className="absolute right-3 bottom-3 flex gap-2">

  {/* 🎤 Mic Button */}
  {/* <button
    type="button"
    onClick={isRecording ? stopRecording : startRecording}
    className={`p-2 rounded-xl transition ${
      isRecording
         ? "bg-[#2a2a2a] text-white hover:bg-[#3a3a3a]"
    : "bg-white text-black"
    }`}
  >
<img
  src={
    isRecording
      ? "https://img.icons8.com/material-rounded/24/microphone.png"
      : "https://img.icons8.com/material-outlined/24/microphone.png"
  }
  alt="mic"
  className="w-5 h-5"
/>
  </button> */}
  <button
  type="button"
  onClick={isRecording ? stopRecording : startRecording}
  className={`p-2 rounded-xl transition ${
    isRecording
      ? "bg-black"
      : "bg-[#2f2f2f] hover:bg-[#3a3a3a]"
  }`}
>
  <img
    src={
      isRecording
        ? "https://img.icons8.com/material-rounded/24/ffffff/microphone.png"
        : "https://img.icons8.com/material-outlined/24/ffffff/microphone.png"
    }
    alt="mic"
    className="w-5 h-5"
  />
</button>


  {/* 📤 Send Button */}
  <button
    type="submit"
    disabled={!inputValue.trim() || isTyping}
    className={`p-2 rounded-xl transition ${
      inputValue.trim() && !isTyping
        ? "bg-white text-black hover:bg-[#d1d1d1]"
        : "text-[#676767] bg-[#2f2f2f]"
    }`}
  >
    <svg
      className="w-5 h-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M5 10l7-7m0 0l7 7m-7-7v18"
      />
    </svg>
  </button>

</div>

           
        </form>
      </div>
    </main>
  );
};
 
 
 