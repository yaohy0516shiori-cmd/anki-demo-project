import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { removeToken } from "./auth/token";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/login";
import { RegisterPage } from "./pages/register";
import { DeckListPage } from "./pages/decklist";
import { CreateNotePage } from "./pages/createnote";
import { StudyPage } from "./pages/study";
import "./App.css";
import { CardListPage } from "./pages/cardlist";
import { ReviewLogsPage } from "./pages/reviewlogs";
/*
Layout 组件是应用的布局组件，包含导航和应用主体。
1. 导航栏
品牌名 Memory Anki Demo 点击回到 /decks。
两个导航链接：/decks（卡组列表）和 /notes/new（创建笔记）。
退出登录按钮：调用 removeToken() 清除 token，然后用 window.location.href 强制跳转到 /login（刷新页面，清空内存状态）。
2. 内层路由（<main> 里的 Routes）
这些路由都是在已登录的基础上才能访问，因为他们被 ProtectedRoute 包裹。
/decks → DeckListPage：卡组列表页。
/notes/new → CreateNotePage：新建笔记页。
/study/:deckId → StudyPage：学习某个卡组，:deckId 是动态参数，例如 /study/5。
* → 如果以上都不匹配（比如用户随便输入一个路径），重定向到 /decks，避免出现空白页。
*/
function Layout() {
  const navigate = useNavigate();
  function handleLogout() {
    //     removeToken()：清除 localStorage 里的 JWT
    // navigate("/login")：回到登录页
    // replace: true：用户不能用浏览器返回键回到登录后的页面
    removeToken();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link className="brand" to="/decks">
          Memory Flashcards
        </Link>

        <nav className="nav-links">
          <Link to="/decks">Decks</Link>
          <Link to="/notes/new">Create Note</Link>
          <Link to="/reviewlogs">Review Logs</Link>
          <button type="button" className="link-button" onClick={handleLogout}>
            Logout
          </button>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/decks" element={<DeckListPage />} />
          <Route path="/notes/new" element={<CreateNotePage />} />
          <Route path="/study/:deckId" element={<StudyPage />} />
          <Route path="*" element={<Navigate to="/decks" replace />} />
          <Route path="/decks/:deckId/cards" element={<CardListPage />} />
          <Route path="/reviewlogs" element={<ReviewLogsPage />} />
        </Routes>
      </main>
    </div>
  );
}
/*
/login → 渲染 LoginPage，无需登录。
/register → 渲染 RegisterPage，无需登录。
/* → 匹配所有其他路径，但需要登录保护：
已登录 → 渲染 Layout 组件（包含导航和应用主体）。
未登录 → 重定向到 /login（由 ProtectedRoute 实现）。
注意：/* 是一个通配符，表示 / 及任何子路径都会进入这个分支，但 /login 和 /register 在上面已经精确匹配，不会被拦截。
*/
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
