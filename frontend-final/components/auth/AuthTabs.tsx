"use client";

import { usePathname, useRouter } from "next/navigation";

export default function AuthTabs() {
  const router = useRouter();
  const path = usePathname();

  return (
    <div className="auth-tabs">
      <span
        className={path === "/signup" ? "active" : ""}
        onClick={() => router.push("/signup")}
      >
        SIGN UP
      </span>
      <span
        className={path === "/login" ? "active" : ""}
        onClick={() => router.push("/login")}
      >
        LOGIN
      </span>
    </div>
  );
}
