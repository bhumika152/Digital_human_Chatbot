import React, { useState, useEffect } from 'react'; // useEffect add
import { chatService } from './services/chatService'; //
// import { Routes, Route, Navigate } from "react-router-dom"; // change
import AdminDashboard from "./components/AdminDashboard";

import { AuthPage } from './components/AuthPage';
import { ChatPage } from './components/ChatPage';
import { AdminAuthPage } from "./components/AdminAuthPage";
import { User, AppView } from './types';
import { useLocation ,useNavigate} from "react-router-dom";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

 
/**
 * App component manages the global state: Authentication and App View.
 */
const App: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

// const hasToken = new URLSearchParams(location.search).has('token');

 
  // const [currentUser, setCurrentUser] = useState<User | null>(() => {
  //   const savedUser = localStorage.getItem('chat_clone_user');
  //   try {
  //     return savedUser ? JSON.parse(savedUser) : null;
  //   } catch (e) {
  //     return null;
  //   }
  // });
 
  const [currentUser, setCurrentUser] = useState<User | null>(null);
 
 
  // const [view, setView] = useState<AppView>(() => {
  //   if (hasToken) return 'auth';
  //   const savedUser = localStorage.getItem('chat_clone_user');
  //   return savedUser ? 'chat' : 'auth';
  // });
 
  const [view, setView] = useState<'loading' | AppView>('loading');
 
  useEffect(() => {
    const initUser = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setView('auth');
        return;
      }
 
      try {
        const me = await chatService.getMe(); // always fresh user
        setCurrentUser(me);
        localStorage.setItem('chat_clone_user', JSON.stringify(me));
        setView('chat');
      } catch (err) {
        console.error("Auto login failed", err);
        localStorage.clear();
        setCurrentUser(null);
        setView('auth');
      }
    };
 
    initUser();
  }, []);
 
 // changes 
 useEffect(() => {
  if (view === 'loading') return;

  const token = localStorage.getItem("access_token");

  // 🟢 If logged in → always allow home to be chat
  if (token && location.pathname === "/login") {
    navigate("/", { replace: true });
  }

  // 🔴 If not logged in → block chat access
  if (!token && location.pathname === "/") {
    navigate("/login", { replace: true });
  }

}, [view, location.pathname]);

  const handleLogin = (data: any) => {
    console.log("Login data received:", data);
   
    // DATA NORMALIZATION:
    // If backend returns { "user": {...}, "token": "..." }, flatten it.
    let normalizedUser: User = {};
   
    if (data.user && typeof data.user === 'object') {
      normalizedUser = { ...data.user };
      // Keep the token if it's there
      if (data.access_token) normalizedUser.access_token = data.access_token;
      if (data.token) normalizedUser.token = data.token;
    } else {
      normalizedUser = { ...data };
    }
 
    // Ensure we have an ID mapped consistently
    if (normalizedUser.id && !normalizedUser.user_id) {
      normalizedUser.user_id = normalizedUser.id;
    }
 
    setCurrentUser(normalizedUser);
    localStorage.setItem('chat_clone_user', JSON.stringify(normalizedUser));
    setView('chat');
   
    // window.history.replaceState({}, document.title, window.location.pathname);
    //navigate(location.pathname, { replace: true });
    navigate("/", { replace: true });


  };
 
  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.clear(); // Complete wipe to prevent stale 'User' display
    setView('auth');
    navigate('/login',{replace: true}); // for URL update
  };

  if (view === 'loading') {
    return null;
}

 
//    return (
//     <div className="min-h-screen bg-[#0d0d0d] text-[#ececec]">
//       {view === 'auth' ? (
//         // <AuthPage
//         //   onAuthSuccess={handleLogin}
//         //   initialMode="login"
//         // />
//         <AuthPage
//   onAuthSuccess={handleLogin}
//   initialMode={getAuthModeFromPath()}
// />

//       ) : (
//         <ChatPage user={currentUser} onLogout={handleLogout} />
//       )}
 
//       <ToastContainer position="top-right" autoClose={2500} />
//     </div>
//   );
//   return (
//   <div className="min-h-screen bg-[#0d0d0d] text-[#ececec]">
//     <AdminAuthPage />
//     <ToastContainer position="top-right" autoClose={2500} />
//   </div>
// );

const isAdminRoute =
  location.pathname === "/admin-login" ;

const isAdminDashboard = location.pathname === "/admin";
const isAdminLoggedIn = !!localStorage.getItem("admin_token");

return (
  <div className="min-h-screen bg-[#0d0d0d] text-[#ececec]">

    {/* 🟣 ADMIN DASHBOARD */}
    {isAdminDashboard ? (
      isAdminLoggedIn ? (
        <AdminDashboard />
      ) : (
        <AdminAuthPage />
      )
    ) : isAdminRoute ? (

      /* 🟣 ADMIN LOGIN / SIGNUP */
      <AdminAuthPage
      />

    ) : view === "auth" ? (

      /* 🔵 USER LOGIN / SIGNUP */
      <AuthPage
        onAuthSuccess={handleLogin}
        initialMode="login"

      />

    ) : (

      /* 🟢 USER CHAT */
      <ChatPage user={currentUser} onLogout={handleLogout} />

    )}

    <ToastContainer position="top-right" autoClose={2500} />
  </div>
);


 
 
 
};
 
export default App;
 