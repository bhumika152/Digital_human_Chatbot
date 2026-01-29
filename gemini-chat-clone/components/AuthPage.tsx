
import React, { useState, useEffect } from 'react';
import { AuthMode, User } from '../types';
import { authService } from '../services/authService';

interface AuthPageProps {
  onAuthSuccess: (user: User) => void;
  initialMode?: AuthMode;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess, initialMode = 'login' }) => {
  // Capture token from URL immediately
  const [token] = useState<string | null>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('token');
  });

  // Initialize mode: If token exists, force 'reset-password' mode immediately
  const [mode, setMode] = useState<AuthMode>(() => {
    if (token) return 'reset-password';
    return initialMode;
  });

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);


  // Sync mode only if initialMode prop changes (e.g. user manually toggles login/signup elsewhere)
  useEffect(() => {
    if (!token) {
      setMode(initialMode);
    }
  }, [initialMode, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (mode === 'login') {
        const user = await authService.login(email, password);
        onAuthSuccess(user);
      } else if (mode === 'signup') {
        const user = await authService.signup(username, email, password);
        setSuccessMessage("Signup successful. Please login.");
  
  // 🔥 IMPORTANT: switch to login mode
  setTimeout(() => {
    setMode('login');
    setSuccessMessage(null);
  }, 1500);

      } else if (mode === 'forgot-password') {
        const response = await authService.forgotPassword(email);
        setSuccessMessage(response.message || 'Check your email for reset instructions.');
      } else if (mode === 'reset-password') {
        if (!token) throw new Error("Invalid or missing reset token.");
        if (password.length < 6) throw new Error("Password must be at least 6 characters.");
        if (password !== confirmPassword) throw new Error("Passwords do not match.");
        
        const response = await authService.resetPassword(token, password);
        setSuccessMessage(response.message || 'Password reset successfully! Redirecting to login...');
        
        // After success, switch to login mode after 2 seconds
        setTimeout(() => {
          setMode('login');
          setSuccessMessage(null);
          // Clean up the URL token
          window.history.replaceState({}, document.title, window.location.pathname);
        }, 2000);
      }
    } catch (err: any) {
      setError(err.message || 'Action failed');
    } finally {
      setIsLoading(false);
    }
  };

  const getTitle = () => {
    if (mode === 'login') return 'Welcome back';
    if (mode === 'signup') return 'Create an account';
    if (mode === 'forgot-password') return 'Reset password';
    return 'Create new password';
  };

  const getSubtitle = () => {
    if (mode === 'login') return 'Log in with your details to continue';
    if (mode === 'signup') return 'Sign up to start chatting with Gemini';
    if (mode === 'forgot-password') return 'Enter your email to receive a reset link';
    return 'Enter a strong password for your account';
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
          {getTitle()}
        </h1>
        <p className="text-[#b4b4b4] text-center mb-6">
          {getSubtitle()}
        </p>

        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-500 text-sm text-center">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-3 bg-emerald-500/10 border border-emerald-500/50 rounded-lg text-emerald-500 text-sm text-center">
            {successMessage}
          </div>
        )}

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
          
          {(mode === 'login' || mode === 'signup' || mode === 'forgot-password') && (
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
          )}

          {mode !== 'forgot-password' && (
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-sm font-medium text-[#e5e5e5]">
                  {mode === 'reset-password' ? 'New Password' : 'Password'}
                </label>
                {mode === 'login' && (
                  <button
                    type="button"
                    onClick={() => {
                      setMode('forgot-password');
                      setError(null);
                      setSuccessMessage(null);
                    }}
                    className="text-xs text-[#b4b4b4] hover:text-white transition"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
                        <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 pr-10 focus:ring-2 focus:ring-white outline-none transition"
                placeholder="Enter password"
              />

              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#b4b4b4] hover:text-white"
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>

            </div>
          )}

          {mode === 'reset-password' && (
            <div>
              <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">Confirm New Password</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 focus:ring-2 focus:ring-white outline-none transition"
                placeholder="Confirm new password"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-white text-black font-semibold py-3 rounded-lg hover:bg-[#d1d1d1] transition mt-4 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin"></div>
            ) : mode === 'login' ? 'Continue' : mode === 'signup' ? 'Sign up' : mode === 'forgot-password' ? 'Send reset link' : 'Reset password'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm">
          {(mode === 'forgot-password' || mode === 'reset-password') ? (
            <button
              onClick={() => {
                setMode('login');
                setError(null);
                setSuccessMessage(null);
              }}
              className="text-white font-medium hover:underline"
            >
              Back to log in
            </button>
          ) : (
            <>
              <span className="text-[#b4b4b4]">
                {mode === 'login' ? "Don't have an account?" : "Already have an account?"}
              </span>
              <button
                onClick={() => {
                  setMode(mode === 'login' ? 'signup' : 'login');
                  setError(null);
                  setSuccessMessage(null);
                }}
                className="ml-2 text-white font-medium hover:underline"
              >
                {mode === 'login' ? 'Sign up' : 'Log in'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
