import type { FormEvent } from "react"; //SubmitEventHandler是React的事件处理函数类型，用于处理表单提交事件。
import { useState } from "react"; //useState是React Hooks中的一个函数，用于在函数组件中管理状态。
import { loginUser } from "../api/authApi";
import { saveToken } from "../auth/token";
import { Link, useNavigate } from "react-router-dom";

export function LoginPage() {
  const navigate = useNavigate(); // hook, 返回函数用于控制页面跳转，之后写 navigate("/decks") 就能跳转到 /decks 页面，无需用户点击链接
  // 表单状态管理
  const [email, setEmail] = useState(""); // 表单状态，email 和 password 是用户输入的值，error 是错误信息，loading 是按钮状态。
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null); // 错误信息，用于显示错误信息。
  const [loading, setLoading] = useState(false); // 按钮状态，用于显示按钮状态。
  /*
  这四行里的 setEmail、setPassword、setError、setLoading 本质行为完全相同：
  它们都是 React 内部的更新函数，作用就是：
  接收新的值。
  把对应的状态（email、password、error、loading）更新为新值。
  通知 React 重新渲染这个组件。 
  */
  //表单提交处理（handleSubmit）
  // 阻止默认表单提交行为。
  // 调用 loginUser API，把邮箱密码发给后端。成功后拿到 token → 存入 localStorage → 跳转到 /decks 页面。
  // 失败则显示错误信息。最终恢复按钮状态。
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); // 阻止表单默认提交行为，防止页面刷新。
    setError(null); // 清除错误信息。
    setLoading(true); // 设置按钮状态为加载中。

    try {
      const token = await loginUser({ email, password }); // 调用 loginUser API，把邮箱密码发给后端。成功后拿到 token → 存入 localStorage → 跳转到 /decks 页面。
      saveToken(token.access_token);
      navigate("/dashboard"); // 跳转到 /dashboard 页面。
    } catch (error) {
      setError(error instanceof Error ? error.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="card auth-card">
        <h1>Login</h1>
        <p className="muted">
          Use your account to load your own decks and cards.
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
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete="current-password"
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="muted">
          <Link to="/forgot-password">Forgot password?</Link> No account?{" "}
          <Link to="/register">Register here</Link>
        </p>
      </section>
    </main>
  );
}
