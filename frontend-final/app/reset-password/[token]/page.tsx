// "use client";

// import { useParams, useRouter } from "next/navigation";
// import { useState } from "react";

// export default function ResetPasswordPage() {
//   const { token } = useParams();
//   const router = useRouter();

//   const [password, setPassword] = useState("");
//   const [confirmPassword, setConfirmPassword] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [message, setMessage] = useState("");

//   const handleReset = async () => {
//     if (!password || password !== confirmPassword) {
//       setMessage("Passwords do not match");
//       return;
//     }

//     setLoading(true);
//     setMessage("");

//     try {
//       const res = await fetch("http://localhost:8000/auth/reset-password", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           token,
//           new_password: password,
//         }),
//       });

//       const data = await res.json();

//       if (!res.ok) {
//         setMessage(data.detail || "Reset failed");
//         return;
//       }

//       setMessage("Password reset successful 🎉");

//       setTimeout(() => {
//         router.push("/login");
//       }, 1500);
//     } catch (err) {
//       setMessage("Something went wrong");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gray-100">
//       <div className="bg-white p-8 rounded-lg shadow-md w-[400px]">
//         <h2 className="text-2xl font-bold mb-4 text-center">
//           Create new password
//         </h2>

//         <input
//           type="password"
//           placeholder="New password"
//           className="w-full border px-3 py-2 rounded mb-3"
//           value={password}
//           onChange={(e) => setPassword(e.target.value)}
//         />

//         <input
//           type="password"
//           placeholder="Confirm password"
//           className="w-full border px-3 py-2 rounded mb-4"
//           value={confirmPassword}
//           onChange={(e) => setConfirmPassword(e.target.value)}
//         />

//         <button
//           onClick={handleReset}
//           disabled={loading}
//           className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
//         >
//           {loading ? "Resetting..." : "Reset Password"}
//         </button>

//         {message && (
//           <p className="text-center text-sm mt-4 text-red-600">
//             {message}
//           </p>
//         )}
//       </div>
//     </div>
//   );
// }


"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

export default function ResetPasswordPage() {
  const { token } = useParams();
  const router = useRouter();

  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReset = async () => {
    if (!password) {
      setMessage("Password is required");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessage(data.detail || "Reset failed");
        return;
      }

      setMessage("Password reset successful 🎉");

      setTimeout(() => {
        router.push("/login");
      }, 1500);
    } catch {
      setMessage("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Create New Password</h2>

      <input
        type="password"
        placeholder="New password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button className="primary-btn" onClick={handleReset} disabled={loading}>
        {loading ? "Resetting..." : "Reset Password"}
      </button>

      {message && <p>{message}</p>}
    </div>
  );
}
