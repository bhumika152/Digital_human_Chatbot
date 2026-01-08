import React, { useState, useEffect, useCallback } from 'react';
import { AuthPage } from './components/AuthPage';
import { ChatPage } from './components/ChatPage';
// Fix: Removed non-existent 'Chat' export from './types'
import { User, AppView } from './types';

/**
 * App component manages the global state: Authentication and App View.
 * It simulates basic authentication persistence using localStorage.
 */
const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [view, setView] = useState<AppView>('auth');

  // Check for existing session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('chat_clone_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
      setView('chat');
    }
  }, []);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('chat_clone_user', JSON.stringify(user));
    setView('chat');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('chat_clone_user');
    setView('auth');
  };

  return (
    <div className="min-h-screen bg-[#0d0d0d] text-[#ececec]">
      {view === 'auth' ? (
        <AuthPage onAuthSuccess={handleLogin} />
      ) : (
        <ChatPage user={currentUser} onLogout={handleLogout} />
      )}
    </div>
  );
};

export default App;