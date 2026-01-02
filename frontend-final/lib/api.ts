const API_URL = "http://localhost:8000";

export async function signup(email: string, password: string) {
  try {
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Signup failed: ${res.status} ${text}`);
    }

    return await res.json();
  } catch (err) {
    // Re-throw so caller can show an error message; provide clearer message for network errors
    throw new Error(err instanceof Error ? err.message : String(err));
  }
}

export async function login(email: string, password: string) {
  try {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Login failed: ${res.status} ${text}`);
    }

    return await res.json();
  } catch (err) {
    throw new Error(err instanceof Error ? err.message : String(err));
  }
}
