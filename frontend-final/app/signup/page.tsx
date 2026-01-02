// "use client";

// import { useState } from "react";
// import { signup } from "@/lib/api";
// import { useRouter } from "next/navigation";

// export default function SignupPage() {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const router = useRouter();

//   const handleSignup = async () => {
//     await signup(email, password);
//     router.push("/login");
//   };

//   return (
//     <div className="container">
//       <h2>Signup</h2>

//       <input
//         type="email"
//         placeholder="Email"
//         value={email}
//         onChange={(e) => setEmail(e.target.value)}
//       />

//       <input
//         type="password"
//         placeholder="Password"
//         value={password}
//         onChange={(e) => setPassword(e.target.value)}
//       />

//       <button onClick={handleSignup}>Create Account</button>
//     </div>
//   );
// }

// import AuthTabs from "../../components/auth/AuthTabs";
// import Input from "../../components/auth/Input";
// import GoogleButton from "../../components/auth/GoogleButton";

// export default function SignupPage() {
//   return (
//     <div className="auth-container">
//       <AuthTabs />

//       <h2>Create Your Account</h2>

//       <GoogleButton />

//       <div className="divider">OR</div>

//       <Input label="Username" placeholder="Username" />
//       <Input label="Email" placeholder="Email" />
//       <Input label="Password" type="password" placeholder="Password" />

//       <label className="checkbox">
//         <input type="checkbox" /> I agree to the Terms and Privacy Policy
//       </label>

//       <button className="primary-btn">REGISTER</button>
//     </div>
//   );
// }
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import AuthTabs from "../../components/auth/AuthTabs";
import Input from "../../components/auth/Input";
import GoogleButton from "../../components/auth/GoogleButton";

type UserConfig = {
  rag: boolean;
  memory: boolean;
  tools: boolean;
  multichat: boolean;
  chat_history: boolean;
  max_sessions: string;
  max_tokens: string;
};

export default function SignupPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

const [config, setConfig] = useState({
  memory: false,
  history: false,
  rag: false,
  tools: false,
  max_sessions: "",
  max_tokens: "",
});


  const handleSignup = async () => {
    try {
      const res = await fetch("http://localhost:8000/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, config }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("Signup successful");
        router.push("/login");
      } else {
        alert(data.detail || "Signup failed");
      }
    } catch {
      alert("Network error");
    }
  };

  return (
    <div className="auth-container">
      <AuthTabs />

      <h2>Create Your Account</h2>

      <GoogleButton />

      <div className="divider">OR</div>

      {/* EMAIL */}
      <Input
        label="Email"
        placeholder="Email"
        value={email}
        onChange={(e: any) => setEmail(e.target.value)}
      />

      {/* PASSWORD */}
      <Input
        label="Password"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e: any) => setPassword(e.target.value)}
      />

      {/* ================= CONFIGURATION ================= */}
<div className="config-section">
  <p className="config-title">Configuration</p>

  {/* CHECKBOXES */}
  <label className="config-item">
    <input
      type="checkbox"
      checked={config.memory}
      onChange={(e) =>
        setConfig({ ...config, memory: e.target.checked })
      }
    />
    Let the chatbot remember my preferences and habits
  </label>

  <label className="config-item">
    <input
      type="checkbox"
      checked={config.history}
      onChange={(e) =>
        setConfig({ ...config, history: e.target.checked })
      }
    />
    Save my conversation history
  </label>

  <label className="config-item">
    <input
      type="checkbox"
      checked={config.rag}
      onChange={(e) =>
        setConfig({ ...config, rag: e.target.checked })
      }
    />
    Allow the chatbot to learn from my documents
  </label>

  <label className="config-item">
    <input
      type="checkbox"
      checked={config.tools}
      onChange={(e) =>
        setConfig({ ...config, tools: e.target.checked })
      }
    />
    Enable smart assistant features
  </label>

  {/* INPUTS */}
  <div className="config-input-row">
    <div className="config-input-col">
      <label>Maximum chat sessions</label>
      <input
        type="number"
        placeholder="5"
        value={config.max_sessions}
        onChange={(e) =>
          setConfig({ ...config, max_sessions: e.target.value })
        }
      />
    </div>

    <div className="config-input-col">
      <label>Response length limit</label>
      <input
        type="number"
        placeholder="4096"
        value={config.max_tokens}
        onChange={(e) =>
          setConfig({ ...config, max_tokens: e.target.value })
        }
      />
    </div>
  </div>
</div>


      {/* TERMS */}
      <label className="checkbox">
        <input type="checkbox" /> I agree to the Terms and Privacy Policy
      </label>

      <button className="primary-btn" onClick={handleSignup}>
        REGISTER
      </button>
    </div>
  );
}
