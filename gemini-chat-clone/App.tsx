
import React, { useState, useEffect } from 'react';
import { AuthPage } from './components/AuthPage';
import { ChatPage } from './components/ChatPage';
import { User, AppView, AuthMode } from './types';

/**
 * App component manages the global state: Authentication and App View.
 */
const App: React.FC = () => {
  // Check for reset token in URL immediately during initialization
  const params = new URLSearchParams(window.location.search);
  const resetToken = params.get('token');
  
  // Determine initial view and auth mode before first render
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('chat_clone_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [view, setView] = useState<AppView>(() => {
    if (resetToken) return 'auth';
    const savedUser = localStorage.getItem('chat_clone_user');
    return savedUser ? 'chat' : 'auth';
  });

  const [initialAuthMode] = useState<AuthMode>(resetToken ? 'reset-password' : 'login');

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('chat_clone_user', JSON.stringify(user));
    setView('chat');
    // Clean up URL if we were on a reset link
    window.history.replaceState({}, document.title, window.location.pathname);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('chat_clone_user');
    setView('auth');
  };

  return (
    <div className="min-h-screen bg-[#0d0d0d] text-[#ececec]">
      {view === 'auth' ? (
        <AuthPage 
          onAuthSuccess={handleLogin} 
          initialMode={initialAuthMode} 
        />
      ) : (
        <ChatPage user={currentUser} onLogout={handleLogout} />
      )}
    </div>
  );
};

export default App;
