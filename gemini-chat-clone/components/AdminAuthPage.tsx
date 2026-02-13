import { adminAuthService } from "../services/adminAuthService";
import eyeOpen from "../assets/eye-open.svg";
import eyeClosed from "../assets/eye-closed.svg";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export const AdminAuthPage: React.FC = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const data = await adminAuthService.login(email, password);
      localStorage.setItem("admin_token", data.access_token);
      navigate("/admin");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-[#0d0d0d]">
      <div className="w-full max-w-md bg-[#171717] rounded-2xl p-8 shadow-2xl border border-[#303030]">

        <h1 className="text-3xl font-bold text-center mb-2">
          Admin Login
        </h1>

        <p className="text-[#b4b4b4] text-center mb-6">
          Login to access the Admin Dashboard
        </p>

        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-500 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">

          {/* Email */}
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

          {/* Password */}
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
            {isLoading ? "Processing..." : "Login"}
          </button>
        </form>

      </div>
    </div>
  );
};
