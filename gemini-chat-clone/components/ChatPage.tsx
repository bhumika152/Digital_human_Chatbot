import React, { useState, useEffect } from 'react';
import { User, Message, ChatSession } from '../types';
import { Sidebar } from './Sidebar';
import { ChatWindow } from './ChatWindow';
import { chatService } from '../services/chatService';
 
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { ToastContainer } from "react-toastify";
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
  console.log("ChatPage rendered on:", window.location.pathname); // changes
  // 🔑 SINGLE SOURCE OF TRUTH
  // const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(() => {
    return localStorage.getItem("active_session_id");
  });
 
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false); // changes
  const [profileUser, setProfileUser] = useState<User | null>(user);
  const [isRestoringSession, setIsRestoringSession] = useState(true);
 
  // useEffect(() => {
  //   setProfileUser(user);
  // }, [user]);
  // 👇 👇 👇
  const PAGE_SIZE = 20;
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
 
  //    // ✅👇 YAHAN ADD KARO (TEMP TEST)
  //   useEffect(() => {
  //   const fakeMessages = Array.from({ length: 40 }, (_, i) => ({
  //     request_id: `fake-${i}`,
  //     session_id: 'test',
  //     role: i % 2 === 0 ? 'user' : 'assistant',
  //     content: `Fake message ${i}`,
  //     created_at: new Date().toISOString(),
  //   }));
 
  //   // 🔥 ONLY LAST 20 LOAD FIRST
  //   setMessages(fakeMessages.slice(20));
  //   setOffset(20);
  //   setHasMore(true);
  // }, []);
 
  // // ✅ 3. 🔥 YAHI ADD KARNA HAI (TESTING FUNCTION)
  //   const loadMoreMessages = async () => {
  //     const older = Array.from({ length: 20 }, (_, i) => ({
  //       request_id: `old-${i}`,
  //       session_id: 'test',
  //       role: i % 2 === 0 ? 'user' : 'assistant',
  //       content: `OLDER message ${i}`,
  //       created_at: new Date().toISOString(),
  //     }));
 
  //     setMessages(prev => [...older, ...prev]);
  //     // setHasMore(false); // 👈 ek hi baar load
  //   };
  /* ----------------------------
     LOAD SIDEBAR SESSIONS  
  ---------------------------- */
  useEffect(() => {
    if (!user) return;
 
    chatService
      .getSessions()
      .then(setSessions)
      .catch(err => console.error('Failed to load sessions', err));
  }, [user]);
 
  //  RESTORE ACTIVE SESSION ON PAGE REFRESH
  // useEffect(() => {
  //   const savedSessionId = localStorage.getItem("active_session_id");
 
  //   if (savedSessionId) {
  //     setCurrentSessionId(savedSessionId);
  //   }
  // }, []);
 
  /* ----------------------------
   LOAD CHAT HISTORY ON SIDEBAR CLICK
  ---------------------------- */
  useEffect(() => {
    if (!currentSessionId) return;
 
    const loadMessages = async () => {
      try {
        const history = await chatService.getMessages(
          currentSessionId,
          PAGE_SIZE,
          0
        );
 
        setMessages(history);          // latest 20
        setOffset(PAGE_SIZE);          // next page should skip these
        setHasMore(history.length === PAGE_SIZE);
 
 
      } catch (err) {
        console.error('Failed to load chat history', err);
      }
    };
 
    loadMessages();
  }, [currentSessionId]);
 
  useEffect(() => {
    // NEW CHAT case → no session to restore
    if (!currentSessionId) {
      setIsRestoringSession(false);
      return;
    }
 
    const loadMessages = async () => {
      try {
        const history = await chatService.getMessages(
          currentSessionId,
          PAGE_SIZE,
          0
        );
 
        setMessages(history);
        setOffset(PAGE_SIZE);
        setHasMore(history.length === PAGE_SIZE);
      } catch (err) {
        console.error('Failed to load chat history', err);
      } finally {
        setIsRestoringSession(false); // 🔥 session ready
      }
    };
 
    loadMessages();
  }, [currentSessionId]);
 
 
  /* ----------------------------
     LOAD OLDER MESSAGES (PAGINATION)
  ---------------------------- */
  const loadMoreMessages = async () => {
    if (!currentSessionId || !hasMore) return;
 
    try {
      const olderMessages = await chatService.getMessages(
        currentSessionId,
        PAGE_SIZE,
        offset
      );
 
      setMessages(prev => [...olderMessages, ...prev]);
      setOffset(prev => prev + olderMessages.length);
      setHasMore(olderMessages.length === PAGE_SIZE);
 
 
 
    } catch (err) {
      console.error('Failed to load older messages', err);
    }
  };
 
 
  useEffect(() => {
    const handler = () => {
      if (hasMore) loadMoreMessages();
    };
 
    window.addEventListener("loadMoreMessages", handler);
    return () => window.removeEventListener("loadMoreMessages", handler);
  }, [hasMore, offset, currentSessionId]);
 
 
 
  /* ----------------------------
     NEW CHAT
  ---------------------------- */
  const handleNewChat = async () => {
    try {
      // 🔥 BACKEND ME NEW SESSION CREATE
 
      setCurrentSessionId(null);   // 🔥 VERY IMPORTANT
      setMessages([]);             // 🔥 CLEAR UI
      setOffset(0);
      setHasMore(true);
      // IMPORTANT: active session remove
      localStorage.removeItem("active_session_id");
 
      // 🔄 refresh sidebar
      const updatedSessions = await chatService.getSessions();
      setSessions(updatedSessions);
    } catch (err) {
      console.error("Failed to create new chat", err);
    }
  };
 
  /* ----------------------------
     SEND MESSAGE (CORE FIX)
  ---------------------------- */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return;
 
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please login again');
      return;
    }
 
    // 👤 show user message instantly
    const userMsg: Message = {
      request_id: 'user-' + Date.now(),
      session_id: currentSessionId ?? '',
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
 
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);
 
    // 🤖 assistant placeholder
    const assistantTempId = 'assistant-' + Date.now();
    setMessages(prev => [
      ...prev,
      {
        request_id: assistantTempId,
        session_id: currentSessionId ?? '',
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      },
    ]);
 
    try {
      let fullResponse = '';
 
      await chatService.sendChatMessageStreaming(
        token,
        currentSessionId, //  SAME session id reuse hoti hai
        content,
        (chunk) => {
          fullResponse += chunk;
 
          setMessages(prev =>
            prev.map(m =>
              m.request_id === assistantTempId
                ? { ...m, content: fullResponse }
                : m
            )
          );
        },
        // (newSessionId) => {
        //   // 🔑 ONLY FIRST MESSAGE ME SAVE HOGA
        //   setCurrentSessionId(prev => prev ?? newSessionId);
        //   //  // FIRST MESSAGE KE BAAD HI SESSION SAVE HOGA
        //   // if (!currentSessionId) {
        //   // localStorage.setItem("active_session_id", newSessionId);
        //   // }
        // }
        (newSessionId) => {
          setCurrentSessionId(prev => {
            if (!prev) {
              localStorage.setItem("active_session_id", newSessionId);
              return newSessionId;
            }
            return prev;
          });
        }
       
 
      );
 
      // 🔄 refresh sidebar
      const updatedSessions = await chatService.getSessions();
      setSessions(updatedSessions);
 
    } catch (err) {
      setMessages(prev =>
        prev.map(m =>
          m.request_id === assistantTempId
            ? { ...m, content: 'Error connecting to backend' }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };
 
  /* ----------------------------
     DELETE CHAT
  ---------------------------- */
  const handleDeleteChat = (sessionId: string) => {
    confirmToast("Delete this chat?", async () => {
      try {
        await chatService.deleteSession(sessionId);
 
        setSessions(prev =>
          prev.filter(s => s.session_id !== sessionId)
        );
 
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([]);
        }
 
        toast.success("Chat deleted");
      } catch (err) {
        console.error("Delete failed", err);
        toast.error("Unable to delete chat");
      }
    });
  };
 
  return (
    <div className="flex h-screen overflow-hidden">
 
      <Sidebar
        chats={sessions.map(s => ({
          id: s.session_id,
          title: s.session_title,
        }))}
        currentChatId={currentSessionId}
        // onSelectChat={(id) => setCurrentSessionId(id)}
        onSelectChat={(id) => {
          setIsRestoringSession(true);   // 🔥 ADD THIS
          setCurrentSessionId(id);
          localStorage.setItem("active_session_id", id); //
          //SAVE
        }}
 
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onLogout={onLogout}
        user={profileUser} // changes
        onEditProfile={() => setShowEditProfile(true)} // changes1
      />
 
 
      {/* <ChatWindow
        chat={{
          id: currentSessionId ?? 'new',
          messages,
        }}
        onSendMessage={handleSendMessage}
        isTyping={isTyping}
        isSidebarOpen={isSidebarOpen}
        hasMore={hasMore}                 // 👈 MUST
        onLoadMore={loadMoreMessages}     // 👈 MUST
      /> */}
 
      {showEditProfile ? (
        <EditProfileUI
          onClose={() => setShowEditProfile(false)}
          onProfileUpdated={(updatedUser) => setProfileUser(updatedUser)}
        />
      ) : isRestoringSession ? (
        // 🖤 BLANK SCREEN DURING RESTORE (NO HOME FLASH)
        <div className="flex-1 bg-[#0f0f0f]" />
      // ) : (
      //   <ChatWindow
      //     key={currentSessionId ?? 'new-chat'}
      //     chat={
      //       currentSessionId
      //         ? { id: currentSessionId, messages }
      //         : undefined
      //     }
      //     onSendMessage={handleSendMessage}
      //     isTyping={isTyping}
      //     isSidebarOpen={isSidebarOpen}
      //   />
      // )
    ) : (() => {
      const shouldShowChat =
        currentSessionId !== null || messages.length > 0;
 
      return (
        <ChatWindow
          key={currentSessionId ?? 'new-chat'}
          chat={
            shouldShowChat
              ? { id: currentSessionId ?? 'new', messages }
              : undefined
          }
          onSendMessage={handleSendMessage}
          isTyping={isTyping}
          isSidebarOpen={isSidebarOpen}
        />
      );
  })()
 
    }
 
 
      {/* {showEditProfile ? (
  <EditProfileUI
  onClose={() => setShowEditProfile(false)}
  onProfileUpdated={(updatedUser) => setProfileUser(updatedUser)}
   />
) : (
//   <ChatWindow
//   key={currentSessionId ?? 'new-chat'} // 🔥 MAGIC LINE
//   chat={{
//     id: currentSessionId ?? 'new',
//     messages,
//   }}
//   onSendMessage={handleSendMessage}
//   isTyping={isTyping}
//   isSidebarOpen={isSidebarOpen}
// />
<ChatWindow
  key={currentSessionId ?? 'new-chat'}
  chat={
    currentSessionId
      ? { id: currentSessionId, messages }
      : undefined
  }
  onSendMessage={handleSendMessage}
  isTyping={isTyping}
  isSidebarOpen={isSidebarOpen}
/>
 
 
 
 
)} */}
 
 
 
 
    </div>
  );
};
 