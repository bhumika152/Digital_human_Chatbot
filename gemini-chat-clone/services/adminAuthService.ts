// 🔐 Admin Authentication Service

const API_BASE = "http://localhost:8000/auth/admin"; 
// Make sure backend route matches this:
// POST   /auth/admin/login
// GET    /auth/admin/me

export interface AdminAuthResponse {
  access_token: string;
  token_type: string;
}

export interface AdminInfo {
  user_id: number;
  email: string;
  username: string;
  role: string;
}

export const adminAuthService = {

  // 🔐 ADMIN LOGIN
  login: async (
    email: string,
    password: string
  ): Promise<AdminAuthResponse> => {
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Invalid admin credentials");
    }

    // ✅ Store token
    localStorage.setItem("admin_token", data.access_token);

    return data;
  },

  // 👤 GET CURRENT ADMIN INFO
  getMe: async (): Promise<AdminInfo> => {
    const token = localStorage.getItem("admin_token");

    if (!token) {
      throw new Error("No admin token found");
    }

    const res = await fetch(`${API_BASE}/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Admin not authenticated");
    }

    return data;
  },

  // 🔍 CHECK IF ADMIN LOGGED IN
  isLoggedIn: (): boolean => {
    return !!localStorage.getItem("admin_token");
  },

  // 🚪 LOGOUT ADMIN
  logout: (): void => {
    localStorage.removeItem("admin_token");
  },
};
