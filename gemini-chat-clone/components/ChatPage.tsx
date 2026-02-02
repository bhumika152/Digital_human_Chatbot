import React, { useState, useEffect } from 'react';
import { User, Message, ChatSession } from '../types';
import { Sidebar } from './Sidebar';
import { ChatWindow } from './ChatWindow';
import { chatService } from '../services/chatService';
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

/* ==========================================================
   EDIT PROFILE UI COMPONENT
========================================================== */

const EditProfileUI: React.FC<{
  onClose: () => void;
  onProfileUpdated: (updatedUser: User) => void;
}> = ({ onClose, onProfileUpdated }) => {

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [bio, setBio] = useState("");

  const [errors, setErrors] = useState({
    firstName: "",
    lastName: "",
    username: "",
    phone: "",
    bio: ""
  });

  const [originalData, setOriginalData] = useState({
    firstName: "",
    lastName: "",
    username: "",
    phone: "",
    bio: ""
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const me = await chatService.getMe();
        setFirstName(me.first_name || "");
        setLastName(me.last_name || "");
        setUsername(me.username || "");
        setEmail(me.email || "");
        setPhone(me.phone || "");
        setBio(me.bio || "");

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

  const hasErrors = Object.values(errors).some(e => e !== "");

  const validateField = (name: string, value: string) => {
    let message = "";

    if (value.trim() === "") {
      setErrors(prev => ({ ...prev, [name]: "" }));
      return;
    }

    if ((name === "firstName" || name === "lastName") && /[^A-Za-z]/.test(value)) {
      message = "Only letters allowed.";
    }

    if (name === "username" && /[^A-Za-z0-9_]/.test(value)) {
      message = "Only letters, numbers, underscore allowed.";
    }

    if (name === "phone" && !/^\d{10}$/.test(value)) {
      message = "Phone must be 10 digits.";
    }

    if (name === "bio" && value.length > 500) {
      message = "Max 500 characters.";
    }

    setErrors(prev => ({ ...prev, [name]: message }));
  };

  const handleSave = async () => {
    if (hasErrors) return;

    if (
      firstName === originalData.firstName &&
      lastName === originalData.lastName &&
      username === originalData.username &&
      phone === originalData.phone &&
      bio === originalData.bio
    ) {
      toast.info("No changes");
      return;
    }

    try {
      const payload: any = {};
      if (firstName) payload.first_name = firstName;
      if (lastName) payload.last_name = lastName;
      if (username) payload.username = username;
      if (phone) payload.phone = phone;
      if (bio) payload.bio = bio;

      const res = await chatService.updateMe(payload);
      toast.success(res.message || "Profile updated");

      onProfileUpdated(res.user as User);
      localStorage.setItem("user", JSON.stringify(res.user));
      onClose();
    } catch (err: any) {
      toast.error(err?.message || "Update failed");
    }
  };

  return (
    <div className="h-screen bg-[#0f0f0f] text-white flex justify-center p-6">
      <ToastContainer />
      <div className="w-full max-w-2xl bg-[#171717] p-6 rounded-xl">
        <h1 className="text-xl font-bold mb-4">Edit Profile</h1>

        <input value={firstName} onChange={e => { setFirstName(e.target.value); validateField("firstName", e.target.value); }} />
        <input value={lastName} onChange={e => { setLastName(e.target.value); validateField("lastName", e.target.value); }} />
        <input value={username} onChange={e => { setUsername(e.target.value); validateField("username", e.target.value); }} />
        <input value={email} readOnly />
        <input value={phone} onChange={e => { setPhone(e.target.value); validateField("phone", e.target.value); }} />
        <textarea value={bio} onChange={e => { setBio(e.target.value); validateField("bio", e.target.value); }} />

        <button onClick={handleSave} disabled={hasErrors}>Save</button>
        <button onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
};

/* ==========================================================
   CHAT PAGE
========================================================== */

export const ChatPage: React.FC<{ user: User | null; onLogout: () => void }> = ({
  user,
  onLogout
}) => {

  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [profileUser, setProfileUser] = useState<User | null>(user);

  const PAGE_SIZE = 20;

  /* =======================
     LOAD SIDEBAR SESSIONS
  ======================== */
  useEffect(() => {
    if (!user) return;
    chatService.getSessions().then(setSessions);
  }, [user]);

  /* =======================
     LOAD CHAT HISTORY
     (DO NOT overwrite optimistic UI)
  ======================== */
  useEffect(() => {
    if (!currentSessionId) return;
    if (messages.length > 0) return;

    const load = async () => {
      const history = await chatService.getMessages(currentSessionId, PAGE_SIZE, 0);
      setMessages(history);
    };

    load();
  }, [currentSessionId]);

  /* =======================
     SEND MESSAGE
  ======================== */
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return;

    const token = localStorage.getItem("access_token");
    if (!token) return;

    const userMsg: Message = {
      request_id: `user-${Date.now()}`,
      session_id: currentSessionId ?? '',
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    const assistantId = `assistant-${Date.now()}`;
    setMessages(prev => [...prev, {
      request_id: assistantId,
      session_id: currentSessionId ?? '',
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    }]);

    let fullResponse = "";

    try {
      await chatService.sendChatMessageStreaming(
        token,
        currentSessionId,
        content,
        (chunk) => {
          fullResponse += chunk;
          setMessages(prev =>
            prev.map(m =>
              m.request_id === assistantId
                ? { ...m, content: fullResponse }
                : m
            )
          );
        },
        (newSessionId) => {
          setCurrentSessionId(prev => prev ?? newSessionId);
        }
      );

      setSessions(await chatService.getSessions());
    } catch {
      setMessages(prev =>
        prev.map(m =>
          m.request_id === assistantId
            ? { ...m, content: "Error" }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  /* =======================
     DELETE CHAT (🔥 FIX)
  ======================== */
  const handleDeleteChat = async (sessionId: string) => {
    try {
      await chatService.deleteSession(sessionId);

      // remove from sidebar
      setSessions(prev =>
        prev.filter(s => s.session_id !== sessionId)
      );

      // if current chat deleted → reset UI
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }

      toast.success("Chat deleted");
    } catch {
      toast.error("Failed to delete chat");
    }
  };

  return (
    <div className="flex h-screen">
      <ToastContainer />

      <Sidebar
        chats={sessions.map(s => ({
          id: s.session_id,
          title: s.session_title
        }))}
        currentChatId={currentSessionId}
        onSelectChat={setCurrentSessionId}
        onNewChat={() => {
          setCurrentSessionId(null);
          setMessages([]);
        }}
        onDeleteChat={handleDeleteChat}  
        isOpen={true}
        toggleSidebar={() => {}}
        onLogout={onLogout}
        user={profileUser}
        onEditProfile={() => setShowEditProfile(true)}
      />

      {showEditProfile ? (
        <EditProfileUI
          onClose={() => setShowEditProfile(false)}
          onProfileUpdated={setProfileUser}
        />
      ) : (
        <ChatWindow
          chat={{ id: currentSessionId ?? 'new', messages }}
          onSendMessage={handleSendMessage}
          isTyping={isTyping}
          isSidebarOpen={true}
        />
      )}
    </div>
  );
};