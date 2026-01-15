
import React, { useState } from 'react';
import { Routes, Route, Navigate } from "react-router-dom"; // change
import { AuthPage } from './components/AuthPage';
import { ChatPage } from './components/ChatPage';
import { User, AppView } from './types';

/**
 * App component manages the global state: Authentication and App View.
 */
const App: React.FC = () => {
  const hasToken = new URLSearchParams(window.location.search).has('token');
  
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('chat_clone_user');
    try {
      return savedUser ? JSON.parse(savedUser) : null;
    } catch (e) {
      return null;
    }
  });

  const [view, setView] = useState<AppView>(() => {
    if (hasToken) return 'auth';
    const savedUser = localStorage.getItem('chat_clone_user');
    return savedUser ? 'chat' : 'auth';
  });

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
    
    window.history.replaceState({}, document.title, window.location.pathname);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.clear(); // Complete wipe to prevent stale 'User' display
    setView('auth');
  };

   return (
    <div className="min-h-screen bg-[#0d0d0d] text-[#ececec]">
      {view === 'auth' ? (
        <AuthPage 
          onAuthSuccess={handleLogin} 
          initialMode="login" 
        />
      ) : (
        <ChatPage user={currentUser} onLogout={handleLogout} />
      )}
    </div>
  );

  

};

export default App;
