import type { FormEvent } from "react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { updateMyPassword } from "../api/authApi";

export function UpdatePasswordPage() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setMessage(null);

    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await updateMyPassword({
        old_password: oldPassword,
        new_password: newPassword,
      });

      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMessage("Password updated successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Password update failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card auth-card">
      <h1>Update Password</h1>
      <p className="muted">
        Enter your current password before setting a new one.
      </p>

      <form className="form" onSubmit={handleSubmit}>
        <label>
          Current password
          <input
            value={oldPassword}
            onChange={(event) => setOldPassword(event.target.value)}
            type="password"
            autoComplete="current-password"
            required
          />
        </label>

        <label>
          New password
          <input
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            type="password"
            autoComplete="new-password"
            minLength={6}
            required
          />
        </label>

        <label>
          Confirm new password
          <input
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            type="password"
            autoComplete="new-password"
            minLength={6}
            required
          />
        </label>

        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Updating..." : "Update password"}
        </button>
      </form>

      <p className="muted">
        <Link to="/decks">Back to decks</Link>
      </p>
    </section>
  );
}
