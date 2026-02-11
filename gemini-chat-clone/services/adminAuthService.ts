// // Admin authentication service (separate from normal users)

// const API_BASE_URL = 'http://localhost:8000';

// export interface AdminLoginResponse {
//   access_token: string;
//   token_type: string;
// }

// /**
//  * adminAuthService handles admin signup and login
//  * using FastAPI /admin routes.
//  */
// export const adminAuthService = {
//   /**
//    * Admin Login
//    * Calls: POST /admin/login
//    * Stores admin JWT token in localStorage
//    */
//   async login(email: string, password: string): Promise<AdminLoginResponse> {
//     const response = await fetch(`${API_BASE_URL}/admin/login`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ email, password }),
//     });

//     const data = await response.json();

//     console.log("ADMIN LOGIN RESPONSE:", data);

//     if (!response.ok) {
//       throw new Error(data.detail || 'Admin login failed');
//     }

//     // 🔐 Store admin token separately from user token
//     localStorage.setItem("admin_token", data.access_token);

//     return data;
//   },

//   /**
//    * Admin Signup
//    * Calls: POST /admin/signup
//    * Requires secret key for security
//    */
//   async signup(email: string, password: string, secret: string): Promise<{ message: string }> {
//     const response = await fetch(`${API_BASE_URL}/admin/signup`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         email,
//         password,
//         admin_secret: secret, // required by backend
//       }),
//     });

//     const data = await response.json();

//     if (!response.ok) {
//       throw new Error(data.detail || 'Admin signup failed');
//     }

//     return data;
//   },

//   /**
//    * Get stored admin token
//    */
//   getToken(): string | null {
//     return localStorage.getItem("admin_token");
//   },

//   /**
//    * Logout admin
//    */
//   logout(): void {
//     localStorage.removeItem("admin_token");
//   }
// };
// Admin authentication service (separate from normal users)

const API_BASE_URL = 'http://localhost:8000';

export interface AdminLoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * adminAuthService handles admin signup and login
 * using FastAPI /admin routes.
 */
export const adminAuthService = {
  /**
   * Admin Login
   * Calls: POST /admin/login
   */
  async login(email: string, password: string): Promise<AdminLoginResponse> {
    const response = await fetch(`${API_BASE_URL}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    console.log("ADMIN LOGIN RESPONSE:", data);

    if (!response.ok) {
      throw new Error(data.detail || 'Admin login failed');
    }

    // 🔐 Store admin token separately
    localStorage.setItem("admin_token", data.access_token);

    return data;
  },

  /**
   * Admin Signup
   * Calls: POST /admin/signup
   * No secret key (dev mode)
   */
  async signup(username: string,email: string, password: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/admin/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Admin signup failed');
    }

    return data;
  },

  /** Get stored admin token */
  getToken(): string | null {
    return localStorage.getItem("admin_token");
  },

  /** Logout admin */
  logout(): void {
    localStorage.removeItem("admin_token");
  }
};

