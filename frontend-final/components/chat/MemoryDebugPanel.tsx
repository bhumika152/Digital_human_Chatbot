"use client";

import { useEffect, useState } from "react";

export default function MemoryDebugPanel() {
  const [memories, setMemories] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/auth/debug", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((r) => r.json())
      .then(setMemories);
  }, []);

  return (
    <aside className="w-72 border-l p-3 bg-gray-50">
      <h3 className="font-bold mb-2">🧠 Memory Debug</h3>

      {memories.map((m) => (
        <div key={m.memory_id} className="mb-2 text-sm">
          <b>{m.memory_type}</b>
          <p>{m.memory_content}</p>
          <small>confidence: {m.confidence_score}</small>
        </div>
      ))}
    </aside>
  );
}
