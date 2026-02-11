
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminAuthService } from "../services/adminAuthService";
import eyeOpen from "../assets/eye-open.svg";
import eyeClosed from "../assets/eye-closed.svg";

type Mode = "login" | "signup";

export const AdminAuthPage: React.FC = () => {
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      if (mode === "login") {
        const data = await adminAuthService.login(email, password);
        localStorage.setItem("admin_token", data.access_token);
        navigate("/admin"); // 👉 later admin dashboard
      } else {
        await adminAuthService.signup(username, email, password);
        setSuccessMessage("Admin account created. Please log in.");
        setTimeout(() => {
          setMode("login");
          setSuccessMessage(null);
        }, 1500);
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const getTitle = () =>
    mode === "login" ? "Admin Login" : "Create Admin Account";

  const getSubtitle = () =>
    mode === "login"
      ? "Login to manage the Knowledge Base"
      : "Create an admin account for system control";

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

        <h1 className="text-3xl font-bold text-center mb-2">{getTitle()}</h1>
        <p className="text-[#b4b4b4] text-center mb-6">{getSubtitle()}</p>

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
          {mode === "signup" && (
            <div>
              <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">
                Admin Username
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 focus:ring-2 focus:ring-white outline-none transition"
                placeholder="Enter admin username"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">
              Admin Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#212121] border border-[#424242] rounded-lg px-4 py-2 focus:ring-2 focus:ring-white outline-none transition"
              placeholder="admin@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-[#e5e5e5]">
              Password
            </label>
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
                className="absolute right-3 top-1/2 -translate-y-1/2"
              >
                <img src={showPassword ? eyeClosed : eyeOpen} className="w-5 h-5" />
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-white text-black font-semibold py-3 rounded-lg hover:bg-[#d1d1d1] transition mt-4"
          >
            {isLoading ? "Processing..." : mode === "login" ? "Login" : "Create Admin Account"}
          </button>
        </form>

        <div className="mt-8 text-center text-sm">
          <span className="text-[#b4b4b4]">
            {mode === "login" ? "Need an admin account?" : "Already an admin?"}
          </span>
          <button
            onClick={() => {
              setMode(mode === "login" ? "signup" : "login");
              setError(null);
              setSuccessMessage(null);
            }}
            className="ml-2 text-white font-medium hover:underline"
          >
            {mode === "login" ? "Sign up" : "Log in"}
          </button>
        </div>
      </div>
    </div>
  );
};
