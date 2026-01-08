
import { User } from '../types';

// FastAPI default port is 8000. Update this to your production URL later.
const API_BASE_URL = 'http://localhost:8000'; 

/**
 * AuthService handles login, registration, and password recovery with a FastAPI backend.
 */
export const authService = {
  async login(email: string, password: string){
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();   // 👈 data yahin bana

    console.log("LOGIN RESPONSE:", data); 

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }
        localStorage.setItem("access_token", data.access_token);


    return data;
  
  },

  async signup(username: string, email: string, password: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Signup failed');
    }

    return response.json();
  },

  /**
   * Sends a password reset request to the FastAPI backend.
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send reset request');
    }

    return response.json();
  },

  /**
   * Submits the new password using the token provided in the email link.
   */
  async resetPassword(
  token: string,
  password: string
): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token: token,
      new_password: password, // ✅ FIX
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to reset password');
  }

  return response.json();
}

};
