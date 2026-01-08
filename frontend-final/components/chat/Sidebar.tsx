// "use client";

// export default function Sidebar() {
//   return (
//     <div className="sidebar">
//       <div className="sidebar-header">
//         <h2>ChatGPT</h2>
//       </div>

//       <button className="new-chat-btn">+ New chat</button>

//     </div>
    
//   );
// }

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type Chat = {
  id: string;
  title: string;
};

export default function Sidebar() {
  const router = useRouter();

  // Dummy data (baad me API se aayega)
  const [chats, setChats] = useState<Chat[]>([
    { id: "1", title: "API design for chat" },
    { id: "2", title: "Frontend Layout CSS" },
  ]);

  const [openMenu, setOpenMenu] = useState<string | null>(null);

  // 👉 New chat
  const handleNewChat = () => {
    router.push("/chat");
  };

  // 👉 Chat open
  const openChat = (id: string) => {
    router.push(`/chat/${id}`);
  };

  // 👉 3 dots toggle
  const toggleMenu = (id: string) => {
    setOpenMenu(openMenu === id ? null : id);
  };

  // 👉 Delete chat
  const deleteChat = (id: string) => {
    setChats(prev => prev.filter(chat => chat.id !== id));
    setOpenMenu(null);
  };

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <h2>ChatGPT</h2>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={handleNewChat}>
        + New chat
      </button>

      {/* Chat List */}
      <div className="chat-list">
        {chats.map(chat => (
          <div key={chat.id} className="chat-item">
            <span onClick={() => openChat(chat.id)}>
              {chat.title}
            </span>

            <button onClick={() => toggleMenu(chat.id)}>⋯</button>

            {openMenu === chat.id && (
              <div className="menu">
                <button onClick={() => deleteChat(chat.id)}>
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
