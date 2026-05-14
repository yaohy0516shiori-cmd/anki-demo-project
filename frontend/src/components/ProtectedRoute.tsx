import { isLoggedIn } from "../auth/token";
import { Navigate } from "react-router-dom"; // React 官方提供的浏览器端路由库，用于导航到其他页面
import type { ReactNode } from "react"; //ReactNode 类型就表示一切可以被放在 JSX 标签之间的东西。

type ProtectedRouteProps = {
  children: ReactNode; //ReactNode，也就是任何合法的 React 可渲染内容。
};

// 前端登录访问保护，没有登录的情况下不能接收到token，跳转到login页面
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" />;
  }
  return children;
}
