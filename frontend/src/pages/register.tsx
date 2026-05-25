import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser, registerUser, sendRegisterCode } from "../api/authApi";
import { saveToken } from "../auth/token";

export function RegisterPage() {
  const navigate = useNavigate();
  const [verificationCode, setVerificationCode] = useState("");
  const [devCode, setDevCode] = useState<string | null>(null);
  const [codeExpiresAt, setCodeExpiresAt] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSendCode() {
    setError(null);

    try {
      const result = await sendRegisterCode({ email });
      setDevCode(result.dev_code);
      setVerificationCode(result.dev_code);
      setCodeExpiresAt(Date.now() + 5 * 60 * 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send code");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setLoading(true);
    if (!codeExpiresAt || Date.now() > codeExpiresAt) {
      setError("Verification code expired. Please request a new code.");
      setLoading(false);
      return;
    }
    try {
      await registerUser({
        email,
        username,
        password,
        verification_code: verificationCode,
      });
      const token = await loginUser({ email, password });
      saveToken(token.access_token);
      navigate("/decks");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Register failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="card auth-card">
        <h1>Register</h1>
        <p className="muted">
          Create a user first. The backend will also prepare user-scoped data.
        </p>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              autoComplete="email"
              required
            />
          </label>

          <label>
            Username
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              type="text"
              autoComplete="username"
              required
            />
          </label>

          <label>
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete="new-password"
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="muted">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </section>
    </main>
  );
}
