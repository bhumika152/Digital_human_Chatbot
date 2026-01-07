"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function TopProfileMenu() {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    setEmail(localStorage.getItem("user_email"));
  }, []);

  const logout = () => {
    localStorage.clear();
    router.push("/login");
  };

  return (
    <div style={{ position: "relative" }}>
      

      <div
        onClick={() => setOpen(!open)}
        style={{
          width: 36,
          height: 36,
          borderRadius: "50%",
          background: "red", // 🔴 TEMP COLOR (testing)
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
        }}
      >
        {email ? email[0].toUpperCase() : "U"}
      </div>

      {/* DROPDOWN */}
      {open && (
        <div
          style={{
            position: "absolute",
            top: "110%",
            right: 0,
            width: 220,
            background: "#1f1f1f",
            border: "1px solid #444",
            borderRadius: 8,
            zIndex: 2000,
          }}
        >
          <div style={{ padding: 12, color: "#ccc" }}>
            Hello, {email}
          </div>

          <button
            onClick={logout}
            style={{
              width: "100%",
              padding: 12,
              textAlign: "left",
              background: "transparent",
              color: "red",
              border: "none",
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
}

