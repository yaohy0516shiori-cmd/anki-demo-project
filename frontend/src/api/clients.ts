// 统一后端地址
// 统一 Content-Type
// 自动带 token
// 统一处理错误
// 统一返回 JSON
// 从 token.ts 里面引入 getToken 函数
// 作用：每次请求后端前，读取当前保存的 token
import { getToken } from "../auth/token";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
  return response.json();
}
