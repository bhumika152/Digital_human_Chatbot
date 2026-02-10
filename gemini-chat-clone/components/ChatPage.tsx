import React, { useEffect, useState } from "react";
import { User, Message, ChatSession } from "../types";
import { Sidebar } from "./Sidebar";
import { ChatWindow } from "./ChatWindow";
import { chatService } from "../services/chatService";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { confirmToast } from "../utils/confirmToast";
 
/* ==========================================================
    EDIT PROFILE UI COMPONENT
========================================================== */
 
const EditProfileUI: React.FC<{
  onClose: () => void;
  onProfileUpdated: (updatedUser: User) => void;
}> = ({ onClose, onProfileUpdated }) => {
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          console.log("No token found");
          return;
        }
 
        const me = await chatService.getMe();
 
        setFirstName(me.first_name || "");
        setLastName(me.last_name || "");
        setUsername(me.username || "");
        setEmail(me.email || "");
        setPhone(me.phone || "");
        setBio(me.bio || "");
 
        //  store original values
        setOriginalData({
          firstName: me.first_name || "",
          lastName: me.last_name || "",
          username: me.username || "",
          phone: me.phone || "",
          bio: me.bio || ""
        });
 
      } catch (err) {
        console.error("Failed to fetch profile:", err);
      }
    };
 
    fetchProfile();
  }, []);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [bio, setBio] = useState("");
  //  field error state
  const [errors, setErrors] = useState({
    firstName: "",
    lastName: "",
    username: "",
    phone: "",
    bio: ""
  });
 
  //  store original values to detect changes
  const [originalData, setOriginalData] = useState({
    firstName: "",
    lastName: "",
    username: "",
    phone: "",
    bio: ""
  });
 
  const hasErrors = Object.values(errors).some(error => error !== "");
 
 
  const validateField = (name: string, value: string) => {
    let message = "";
 
    // If field is empty → NO error (backend old value rakhega)
    if (value.trim() === "") {
      setErrors(prev => ({ ...prev, [name]: "" }));
      return;
    }
 
    // ---------------- FIRST NAME & LAST NAME ----------------
    if (name === "firstName" || name === "lastName") {
      if (value.length > 20) {
        message = "Maximum 20 characters allowed.";
      } else if (/[^A-Za-z]/.test(value)) {
        message = "Only letters allowed. No spaces or special characters.";
      }
    }
 
    // ---------------- USERNAME ----------------
    if (name === "username") {
      if (value.length > 20) {
        message = "Maximum 20 characters allowed.";
      } else if (/[^A-Za-z0-9_]/.test(value)) {
        message = "Only letters, numbers and underscore allowed.";
      }
    }
 
    // ---------------- PHONE ----------------
    if (name === "phone") {
      if (!/^\d{10}$/.test(value)) {
        message = "Phone number must be exactly 10 digits.";
      }
    }
 
    // ---------------- BIO ----------------
    if (name === "bio") {
      if (value.length > 500) {
        message = "Bio cannot exceed 500 characters.";
      }
      else if (!/^[A-Za-z0-9 .,!?_\-'\n"]*$/.test(value)) {
        message = "Bio contains invalid characters.";
      }
    }
 
 
    setErrors(prev => ({ ...prev, [name]: message }));
  };
 
  // const handleSave = () => {
  //   alert(" UI Working (no api yet)");
  //   onClose();
  // };
  const handleSave = async () => {
    // 🔵 No changes check
    if (
      firstName === originalData.firstName &&
      lastName === originalData.lastName &&
      username === originalData.username &&
      phone === originalData.phone &&
      bio === originalData.bio
    ) {
      toast.info("No changes ");
      return;
    }
 
    if (hasErrors) return; // extra safety
    try {
      const payload: any = {};
 
      if (firstName.trim() !== "") payload.first_name = firstName;
      if (lastName.trim() !== "") payload.last_name = lastName;
      if (username.trim() !== "") payload.username = username;
      if (phone.trim() !== "") payload.phone = phone;
      if (bio.trim() !== "") payload.bio = bio;
 
 
      const res = await chatService.updateMe(payload); // put api call
      //alert(res.message || "Profile updated successfully");
      toast.success(res.message || "Profile updated successfully ");
 
      // sidebar instantly update
      onProfileUpdated(res.user as User);
      localStorage.setItem("user", JSON.stringify(res.user));
      onClose();
    } catch (err: any) {
      console.log(" SERVER ERROR:", err);
 
      const message =
        err?.detail ||               // FastAPI HTTPException
        err?.message ||              // fallback
        "Update failed. Try again.";
 
      toast.error(message);
    }
 
 
  };
 
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center overflow-y-auto">
      <div className="w-full max-w-2xl my-10 bg-[#171717] border border-[#303030] rounded-2xl p-6">
 
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold">Edit Profile</h1>
          {/* <button
            onClick={onClose}
            className="text-sm text-[#b4b4b4] hover:text-white transition"
          >
            ✕ Close
          </button> */}
        </div>
 
        {/* Form */}
        {/* <div className="space-y-5"> */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
 
          {/* First + Last Name */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[#b4b4b4] mb-2">
                First Name
              </label>
              <input
                // maxLength={20}
                value={firstName}
                onChange={(e) => {
                  const val = e.target.value;
                  setFirstName(val);
                  validateField("firstName", val);
                }}
 
                placeholder="Enter first name"
                className={`w-full bg-[#0f0f0f] border rounded-lg px-4 py-2 outline-none ${errors.firstName
                    ? "border-red-500 focus:border-red-500"
                    : "border-[#303030] focus:border-indigo-500"
                  }`}
              />
              {errors.firstName && (
                <p className="text-red-500 text-xs mt-1">{errors.firstName}</p>
              )}
 
            </div>
 
            <div>
              <label className="block text-sm text-[#b4b4b4] mb-2">
                Last Name
              </label>
              <input
                // maxLength={20}
                value={lastName}
                onChange={(e) => {
                  const val = e.target.value;
                  setLastName(val);
                  validateField("lastName", val);
                }}
 
                className={`w-full bg-[#0f0f0f] border rounded-lg px-4 py-2 outline-none ${errors.lastName ? "border-red-500" : "border-[#303030]"
                  }`}
              />
              {errors.lastName && (
                <p className="text-red-500 text-xs mt-1">{errors.lastName}</p>
              )}
 
            </div>
          </div>
 
          {/* Username */}
          <div>
            <label className="block text-sm text-[#b4b4b4] mb-2">
              Username
            </label>
            <input
              // maxLength={20}
              value={username}
              onChange={(e) => {
                const val = e.target.value;
                setUsername(val);
                validateField("username", val);
              }}
 
              className={`w-full bg-[#0f0f0f] border rounded-lg px-4 py-2 outline-none ${errors.username ? "border-red-500" : "border-[#303030]"
                }`}
            />
            {errors.username && (
              <p className="text-red-500 text-xs mt-1">{errors.username}</p>
            )}
 
          </div>
 
          {/* Email (read-only) */}
          <div>
            <label className="block text-sm text-[#b4b4b4] mb-2">
              Email (Read only)
            </label>
            <input
              value={email}
              readOnly
 
              className="w-full bg-[#0f0f0f] border border-[#303030] rounded-lg px-4 py-2 outline-none opacity-60 cursor-not-allowed"
            />
          </div>
 
          {/* Phone */}
          <div>
            <label className="block text-sm text-[#b4b4b4] mb-2">
              Phone Number
            </label>
            <input
              // maxLength={10}
              value={phone}
              onChange={(e) => {
                const val = e.target.value;
                setPhone(val);
                validateField("phone", val);
              }}
 
              className={`w-full bg-[#0f0f0f] border rounded-lg px-4 py-2 outline-none ${errors.phone ? "border-red-500" : "border-[#303030]"
                }`}
            />
            {errors.phone && (
              <p className="text-red-500 text-xs mt-1">{errors.phone}</p>
            )}
 
          </div>
 
          {/* Bio */}
          <div>
            <label className="block text-sm text-[#b4b4b4] mb-2">Bio</label>
            <textarea
              // maxLength={500}
              value={bio}
              onChange={(e) => {
                const val = e.target.value;
                setBio(val);
                validateField("bio", val);
              }}
 
              className={`w-full bg-[#0f0f0f] border rounded-lg px-4 py-2 outline-none ${errors.bio ? "border-red-500" : "border-[#303030]"
                }`}
            />
            {errors.bio && (
              <p className="text-red-500 text-xs mt-1">{errors.bio}</p>
            )}
 
          </div>
 
          {/* Buttons */}
          <div className="p-6 border-t border-[#303030] bg-[#171717] flex gap-3">
            <button
              onClick={handleSave}
              disabled={hasErrors}
              className={`w-1/2 rounded-lg py-3 font-medium transition
      ${hasErrors
                  ? "bg-gray-600 cursor-not-allowed opacity-60"
                  : "bg-indigo-600 hover:bg-indigo-700"}`}
            >
              Save Changes
            </button>
 
            <button
              onClick={onClose}
              className="w-1/2 bg-[#2a2a2a] hover:bg-[#333] rounded-lg py-3 font-medium"
            >
              Cancel
            </button>
          </div>
 
 
        </div>
      </div>
    </div>
  );
};
 
interface ChatPageProps {
  user: User | null;
  onLogout: () => void;
}
 
export const ChatPage: React.FC<ChatPageProps> = ({ user, onLogout }) => {
  const PAGE_SIZE = 20;
 
  /* =========================
     CORE STATE
  ========================== */
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(() => {
    const id = localStorage.getItem("active_session_id");
    return id;
  });
 
  const [sessionSource, setSessionSource] =
    useState<"sidebar" | "send" | "restore" | null>(() => {
      return localStorage.getItem("active_session_id") ? "restore" : null;
    });
 
  const [messages, setMessages] = useState<Message[]>([]);
  const loadedIdsRef = React.useRef<Set<string>>(new Set());
 
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
 
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [profileUser, setProfileUser] = useState<User | null>(user);
  const [isRestoringSession, setIsRestoringSession] = useState(true);
 
  /* =========================
     LOAD SIDEBAR SESSIONS
  ========================== */
  useEffect(() => {
    if (!user) return;
 
    chatService
      .getSessions()
      .then(setSessions)
      .catch(() => toast.error("Failed to load chats"));
  }, [user]);
 
  /* =========================
     LOAD CHAT HISTORY
     (SINGLE SOURCE OF TRUTH)
  ========================== */
  useEffect(() => {
    if (!currentSessionId) {
      setIsRestoringSession(false);
      return;
    }
 
    // 🔥 First message flow → keep optimistic UI
    if (sessionSource === "send") {
      setSessionSource(null);
      setIsRestoringSession(false);
      return;
    }
 
    const loadHistory = async () => {
      try {
        const history = await chatService.getMessages(
          currentSessionId,
          PAGE_SIZE,
          0
        );
 
        // setMessages(history);
        setMessages(() => {
  loadedIdsRef.current.clear(); // naya session ya fresh load
 
  history.forEach(m => loadedIdsRef.current.add(m.request_id));
 
  return history;
});
 
        setOffset(history.length);
        setHasMore(history.length === PAGE_SIZE);
      } catch {
        toast.error("Failed to load chat history");
      } finally {
        setIsRestoringSession(false);
        setSessionSource(null);
      }
    };
 
    loadHistory();
  }, [currentSessionId]);
 
  /* =========================
     PAGINATION (OLDER MESSAGES)
  ========================== */
  const loadMoreMessages = async () => {
    if (!currentSessionId || !hasMore) return;
 
    try {
      const older = await chatService.getMessages(
        currentSessionId,
        PAGE_SIZE,
        offset
      );
 
      // setMessages(prev => [...older, ...prev]);
      setMessages(prev => {
  const uniqueOlder = older.filter(m => !loadedIdsRef.current.has(m.request_id));
 
  uniqueOlder.forEach(m => loadedIdsRef.current.add(m.request_id));
 
  return [...uniqueOlder, ...prev];
});
 
      setOffset(prev => prev + older.length);
      setHasMore(older.length === PAGE_SIZE);
    } catch {
      console.error("Pagination failed");
    }
  };
 
  useEffect(() => {
    const handler = () => {
      if (hasMore) loadMoreMessages();
    };
 
    window.addEventListener("loadMoreMessages", handler);
    return () => window.removeEventListener("loadMoreMessages", handler);
  }, [hasMore, offset, currentSessionId]);
 
  /* =========================
     SEND MESSAGE
  ========================== */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return;
 
    const token = localStorage.getItem("access_token");
    if (!token) return;
 
    const userMsg: Message = {
      request_id: `user-${Date.now()}`,
      session_id: currentSessionId ?? "",
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    loadedIdsRef.current.add(userMsg.request_id);   // ✅ TRACK USER MSG
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);
   
    const assistantId = `assistant-${Date.now()}`;
    loadedIdsRef.current.add(assistantId);          // ✅ TRACK ASSISTANT MSG
    setMessages(prev => [
      ...prev,
      {
        request_id: assistantId,
        session_id: currentSessionId ?? "",
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
      },
    ]);
 
    let fullResponse = "";
 
    try {
      await chatService.sendChatMessageStreaming(
        token,
        currentSessionId,
        content,
        chunk => {
          fullResponse += chunk;
          // setMessages(prev =>
          //   prev.map(m =>
          //     m.request_id === assistantId
          //       ? { ...m, content: fullResponse }
          //       : m
          //   )
          // );
          setMessages(prev => {
  const exists = prev.some(m => m.request_id === assistantId);
 
  if (!exists) {
    // If somehow missing, add it back instead of creating duplicate later
    return [
      ...prev,
      {
        request_id: assistantId,
        session_id: currentSessionId ?? "",
        role: "assistant",
        content: fullResponse,
        created_at: new Date().toISOString(),
      }
    ];
  }
 
  return prev.map(m =>
    m.request_id === assistantId
      ? { ...m, content: fullResponse }
      : m
  );
});
 
        },
        newSessionId => {
          setSessionSource("send"); // 🔥 KEY FIX
          setCurrentSessionId(prev => {
            if (!prev) {
              localStorage.setItem("active_session_id", newSessionId);
              return newSessionId;
            }
            return prev;
          });
        }
      );
 
      setSessions(await chatService.getSessions());
    } catch {
      setMessages(prev =>
        prev.map(m =>
          m.request_id === assistantId
            ? { ...m, content: "Error generating response" }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };
 
  /* =========================
     NEW CHAT
  ========================== */
  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setOffset(0);
    setHasMore(true);
    localStorage.removeItem("active_session_id");
  };
 
  /* =========================
     DELETE CHAT
  ========================== */
  const handleDeleteChat = (sessionId: string) => {
    confirmToast("Delete this chat?", async () => {
      try {
        await chatService.deleteSession(sessionId);
 
        setSessions(prev =>
          prev.filter(s => s.session_id !== sessionId)
        );
 
        if (currentSessionId === sessionId) {
          handleNewChat();
        }
 
        toast.success("Chat deleted");
      } catch {
        toast.error("Delete failed");
      }
    });
  };
 
  /* =========================
     RENDER
  ========================== */
  return (
    <div className="flex h-screen overflow-hidden">
      <ToastContainer />
 
      <Sidebar
        chats={sessions.map(s => ({
          id: s.session_id,
          title: s.session_title,
        }))}
        currentChatId={currentSessionId}
        onSelectChat={(id) => {
          if (id === currentSessionId) return;
          setSessionSource("sidebar");
          setIsRestoringSession(true);
          setCurrentSessionId(id);
          localStorage.setItem("active_session_id", id);
        }}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onLogout={onLogout}
        user={profileUser}
        onEditProfile={() => setShowEditProfile(true)}
 
      />
 
      {showEditProfile ? (
      <EditProfileUI
        onClose={() => setShowEditProfile(false)}
        onProfileUpdated={(updatedUser) => setProfileUser(updatedUser)}
      />
    ) : isRestoringSession ? (
      <div className="flex-1 bg-[#0f0f0f]" />
    ) : (
      <ChatWindow
        chat={
          currentSessionId || messages.length > 0
            ? { id: currentSessionId ?? "new", messages }
            : undefined
        }
        onSendMessage={handleSendMessage}
        isTyping={isTyping}
        isSidebarOpen={isSidebarOpen}
      />
    )}
    </div>
  );
};