"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthTabs from "../../components/auth/AuthTabs";
import Input from "../../components/auth/Input";
import GoogleButton from "../../components/auth/GoogleButton";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      alert("Please fill all fields");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        throw new Error("Invalid credentials");
      }

      const data = await res.json();

      // ✅ SAVE TOKEN (CRITICAL)
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_email", email);


      // ✅ REDIRECT AFTER TOKEN SAVE
      router.replace("/chat");
    } catch (err) {
      alert("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <AuthTabs />

      <h2>Already have an account?</h2>

      <GoogleButton />

      <div className="divider">OR</div>

      <Input
        label="Email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <Input
        label="Password"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <Link href="/forgot-password" className="forgot">
        Forgot Password?
      </Link>

      <button
        className="primary-btn"
        onClick={handleLogin}
        disabled={loading}
      >
        {loading ? "Logging in..." : "LOGIN"}
      </button>
    </div>
  );
}
