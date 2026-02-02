import React from 'react';
import { User } from '../types';

interface SidebarProps {
  chats: { id: string; title: string }[];
  currentChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
  isOpen: boolean;
  toggleSidebar: () => void;
  onLogout: () => void;
  user: User | null;
  onEditProfile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  chats,
  currentChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  isOpen,
  toggleSidebar,
  onLogout,
  user,
  onEditProfile,
}) => {
  return (
    <aside
      className={`bg-[#171717] transition-all duration-300 flex flex-col h-full border-r border-[#303030] ${
        isOpen ? 'w-64' : 'w-0'
      }`}
    >
      <div className={`flex flex-col h-full overflow-hidden ${!isOpen && 'opacity-0'}`}>
        {/* NEW CHAT */}
        <div className="p-3">
          <button
            onClick={onNewChat}
            className="flex items-center gap-3 w-full p-3 text-sm font-medium rounded-lg hover:bg-[#212121] transition border border-[#424242]"
          >
            <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
              <svg className="w-4 h-4 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <span>New Chat</span>
          </button>
        </div>

        {/* HISTORY */}
        <div className="flex-1 overflow-y-auto no-scrollbar p-3 space-y-2">
          <div className="text-xs font-semibold text-[#b4b4b4] px-3 py-2 uppercase tracking-wider">
            History
          </div>

          {chats.length === 0 ? (
            <div className="px-3 py-10 text-center text-sm text-[#676767]">
              No conversations yet
            </div>
          ) : (
            chats.map(chat => (
              <div
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`group flex items-center gap-2 p-3 text-sm rounded-lg cursor-pointer transition relative ${
                  currentChatId === chat.id ? 'bg-[#212121]' : 'hover:bg-[#212121]'
                }`}
              >
                <span className="truncate flex-1 pr-6">{chat.title}</span>

                {/* DELETE BUTTON */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    const confirmDelete = window.confirm("Delete this chat?");
                    if (confirmDelete) {
                      onDeleteChat(chat.id);
                    }
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 absolute right-2 transition"
                  title="Delete chat"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>

        {/* PROFILE + LOGOUT */}
        <div className="p-3 mt-auto border-t border-[#303030]">
          <div
            onClick={onEditProfile}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#212121] transition cursor-pointer"
          >
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-sm">
              {user?.username?.[0]?.toUpperCase() ||
                user?.email?.[0]?.toUpperCase() ||
                '?'}
            </div>
            <div className="flex-1 overflow-hidden">
              <div className="text-sm font-medium truncate">
                {user?.username || 'User'}
              </div>
              <div className="text-xs text-[#b4b4b4] truncate">
                {user?.email}
              </div>
            </div>
          </div>

          <button
            onClick={onLogout}
            className="w-full mt-2 flex items-center gap-3 p-3 text-sm text-[#b4b4b4] hover:text-white hover:bg-[#212121] rounded-lg transition"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            <span>Log out</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
