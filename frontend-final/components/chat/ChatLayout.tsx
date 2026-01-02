"use client";

import SessionSidebar from "./SessionSidebar";
import MemoryDebugPanel from "./MemoryDebugPanel";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <SessionSidebar />
      <div className="flex-1">{children}</div>
      <MemoryDebugPanel />
    </div>
  );
}
