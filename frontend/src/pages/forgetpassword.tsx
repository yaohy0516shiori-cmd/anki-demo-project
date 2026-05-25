import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { resetPassword, sendPasswordResetCode } from "../api/authApi";

const CODE_TTL_MS = 5 * 60 * 1000;
const RESEND_COOLDOWN_MS = 60 * 1000;

export function ForgotPasswordPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [devCode, setDevCode] = useState<string | null>(null);
  const [codeExpiresAt, setCodeExpiresAt] = useState<number | null>(null);
  const [resendAvailableAt, setResendAvailableAt] = useState<number | null>(
    null,
  );
  const [now, setNow] = useState(Date.now());
  const [sendingCode, setSendingCode] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

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
    setMessage(null);

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

    setSendingCode(true);

    try {
      const result = await sendPasswordResetCode({ email });

      setDevCode(result.dev_code);
      setVerificationCode(result.dev_code);
      setCodeExpiresAt(Date.now() + CODE_TTL_MS);
      setResendAvailableAt(Date.now() + RESEND_COOLDOWN_MS);
      setMessage("Password reset code sent.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send code");
    } finally {
      setSendingCode(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setMessage(null);

    if (!codeExpiresAt || Date.now() > codeExpiresAt) {
      setError("Verification code expired. Please request a new code.");
      return;
    }

    setResetting(true);

    try {
      await resetPassword({
        email,
        verification_code: verificationCode,
        new_password: newPassword,
      });

      setMessage("Password reset successful. Please login again.");
      navigate("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Password reset failed");
    } finally {
      setResetting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="card auth-card">
        <h1>Forgot Password</h1>
        <p className="muted">
          Enter your email, get a verification code, then set a new password.
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

          <button
            type="button"
            className="button-secondary"
            onClick={() => void handleSendCode()}
            disabled={!canSendCode || sendingCode}
          >
            {sendingCode
              ? "Sending..."
              : resendSecondsLeft > 0
                ? `Send again in ${resendSecondsLeft}s`
                : "Send reset code"}
          </button>

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
              DEV reset code: <strong>{devCode}</strong>. Expires in{" "}
              {codeSecondsLeft}s.
            </p>
          )}

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

          {error && <p className="error">{error}</p>}
          {message && <p className="success">{message}</p>}

          <button type="submit" disabled={resetting}>
            {resetting ? "Resetting..." : "Reset password"}
          </button>
        </form>

        <p className="muted">
          Remember your password? <Link to="/login">Back to login</Link>
        </p>
      </section>
    </main>
  );
}
