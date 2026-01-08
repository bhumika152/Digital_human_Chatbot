// "use client";

// import { useEffect, useState } from "react";

// export default function SessionSidebar() {
//   const [sessions, setSessions] = useState<any[]>([]);

//   useEffect(() => {
//     fetch("http://localhost:8000/chat/sessions", {
        
//       headers: {
//         Authorization: `Bearer ${localStorage.getItem("access_token")}`,
//       },
//     })
//       .then((r) => r.json())
//       .then(setSessions);
//   }, []);

//   function select(id: string) {
//     localStorage.setItem("active_session", id);
//     window.location.reload();
//   }

//   function newChat() {
//     localStorage.removeItem("active_session");
//     window.location.reload();
//   }

//   return (
//     <aside className="w-64 border-r p-3">
//       <button onClick={newChat} className="mb-3 w-full bg-black text-white py-1">
//         + New Chat
//       </button>

//       {sessions.map((s) => (
//         <div
//           key={s.session_id}
//           onClick={() => select(s.session_id)}
//           className="cursor-pointer p-2 hover:bg-gray-200"
//         >
//           {s.session_title || "Untitled"}
//         </div>
//       ))}
//     </aside>
//   );
// }
