import React, { useState } from "react";
import { authService } from "../services/authService";

type Props = {
  token: string;
  onSuccess: () => void;
};

const ResetPassword: React.FC<Props> = ({ token, onSuccess }) => {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReset = async () => {
    try {
      setError("");
      setLoading(true);

      if (!token) {
        throw new Error("Invalid or missing reset token");
      }

      if (password.length < 6) {
        throw new Error("Password must be at least 6 characters");
      }

      if (password !== confirmPassword) {
        throw new Error("Passwords do not match");
      }

      const response = await authService.resetPassword(token, password);

      setSuccess(
        response?.message || "Password reset successful. Redirecting to login..."
      );

      // redirect to login after success
      setTimeout(() => {
        onSuccess();
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-box">
      <h2 className="auth-title">Reset Password</h2>

      <input
        type="password"
        placeholder="New password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <input
        type="password"
        placeholder="Confirm new password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
      />

      <button onClick={handleReset} disabled={loading}>
        {loading ? "Resetting..." : "Reset Password"}
      </button>

      {error && <p className="auth-error">{error}</p>}
      {success && <p className="auth-success">{success}</p>}
    </div>
  );
};

export default ResetPassword;
