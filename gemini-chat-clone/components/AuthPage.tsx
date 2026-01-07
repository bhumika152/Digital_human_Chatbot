
import React, { useState } from 'react';
import { AuthMode, User } from '../types';

interface AuthPageProps {
  onAuthSuccess: (user: User) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulated auth delay
    setTimeout(() => {
      const mockUser: User = {
        id: Math.random().toString(36).substr(2, 9),
        email,
        username: username || email.split('@')[0],
      };
      onAuthSuccess(mockUser);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-[#0d0d0d]">
      <div className="w-full max-w-md bg-[#171717] rounded-2xl p-8 shadow-2xl border border-[#303030]">
        <div className="flex justify-center mb-8">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-black" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-center mb-2">
          {mode === 'login' ? 'Welcome back' : 'Create an account'}
        </h1>
        <p className="text-[#b4b4b4] text-center mb-8">
          {mode === 'login' ? 'Log in with your details to continue' : 'Sign up to start chatting with Gemini'}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'signup' && (
            <div>
              <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">Username</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 focus:ring-2 focus:ring-white outline-none transition"
                placeholder="Enter your username"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 focus:ring-2 focus:ring-white outline-none transition"
              placeholder="Email address"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 focus:ring-2 focus:ring-white outline-none transition"
              placeholder="Password"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-white text-black font-semibold py-3 rounded-lg hover:bg-[#d1d1d1] transition mt-4 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin"></div>
            ) : mode === 'login' ? 'Continue' : 'Sign up'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm">
          <span className="text-[#b4b4b4]">
            {mode === 'login' ? "Don't have an account?" : "Already have an account?"}
          </span>
          <button
            onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
            className="ml-2 text-white font-medium hover:underline"
          >
            {mode === 'login' ? 'Sign up' : 'Log in'}
          </button>
        </div>
      </div>
    </div>
  );
};
