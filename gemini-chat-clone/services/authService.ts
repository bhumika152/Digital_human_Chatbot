
// import { User } from '../types';

// // FastAPI default port is 8000. Update this to your production URL later.
// const API_BASE_URL = 'http://localhost:8000'; 

// /**
//  * AuthService handles login and registration with a FastAPI backend.
//  */
// export const authService = {
//   async login(email: string, password: string): Promise<User> {
//     const response = await fetch(`${API_BASE_URL}/auth/login`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ email, password }),
//     });

//     if (!response.ok) {
//       const errorData = await response.json();
//       // FastAPI usually returns errors in a { "detail": "message" } format
//       throw new Error(errorData.detail || 'Login failed');
//     }

//     return response.json();
//   },

//   async signup(username: string, email: string, password: string): Promise<User> {
//     const response = await fetch(`${API_BASE_URL}/auth/signup`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ username, email, password }),
//     });

//     if (!response.ok) {
//       const errorData = await response.json();
//       throw new Error(errorData.detail || 'Signup failed');
//     }

//     return response.json();
//   }
// };
import { User } from '../types';

// FastAPI backend URL
const API_BASE_URL = 'http://localhost:8000'; 

/**
 * AuthService handles login and registration with FastAPI backend.
 */
export const authService = {

  // 🔐 LOGIN
  async login(email: string, password: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Login failed');
  }

  const data = await response.json();

  // 🔑 SAVE TOKEN
  localStorage.setItem('access_token', data.access_token);
},


  // 📝 SIGNUP
  async signup(username: string, email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Signup failed');
    }

    // ❌ Signup me token save NAHI karna
    return response.json();
  }
};
