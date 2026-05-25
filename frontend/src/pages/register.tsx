import type { FormEvent } from "react";
import { useEffect, useState } from "react";
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
  const CODE_TTL_MS = 5 * 60 * 1000;
  const RESEND_COOLDOWN_MS = 60 * 1000;
  const [resendAvailableAt, setResendAvailableAt] = useState<number | null>(
    null,
  );
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => {
      setNow(Date.now());
    }, 1000);

    return () => {
      window.clearInterval(timer);
    };
  }, []);

  const codeSecondsLeft =
    codeExpiresAt === null
      ? 0
      : Math.max(0, Math.ceil((codeExpiresAt - now) / 1000));

  const resendSecondsLeft =
    resendAvailableAt === null
      ? 0
      : Math.max(0, Math.ceil((resendAvailableAt - now) / 1000));

  const canSendCode = email.trim().length > 0 && resendSecondsLeft === 0;

  async function handleSendCode() {
    setError(null);

    if (!email.trim()) {
      setError("Please enter your email first.");
      return;
    }

    if (resendSecondsLeft > 0) {
      setError(
        `Please wait ${resendSecondsLeft}s before sending another code.`,
      );
      return;
    }

    try {
      const result = await sendRegisterCode({ email });

      setDevCode(result.dev_code);
      setVerificationCode(result.dev_code);
      setCodeExpiresAt(Date.now() + CODE_TTL_MS);
      setResendAvailableAt(Date.now() + RESEND_COOLDOWN_MS);
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
            <button
              type="button"
              className="button-secondary"
              onClick={() => void handleSendCode()}
              disabled={!canSendCode}
            >
              {resendSecondsLeft > 0
                ? `Send again in ${resendSecondsLeft}s`
                : "Send verification code"}
            </button>
          </label>
          <label>
            Verification code
            <input
              value={verificationCode}
              onChange={(event) => setVerificationCode(event.target.value)}
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="6-digit code"
              required
            />
          </label>

          {devCode && (
            <p className="muted">
              DEV verification code: <strong>{devCode}</strong>. Expires in{" "}
              {codeSecondsLeft}s.
            </p>
          )}
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
