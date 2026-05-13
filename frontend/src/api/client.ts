// src/api/client.ts

// 引入读取 token 的函数
import { getToken } from "../auth/token";

// 后端 API 基础地址
// 优先读取 frontend/.env 里的 VITE_API_BASE_URL
// 如果没配置，就默认使用 http://localhost:8000
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// 通用 API 请求函数
export async function apiRequest<T>(
  path: string, // API 路径，例如 "/users/login"
  options: RequestInit = {}, // fetch 的配置，例如 method/body
): Promise<T> {
  // 读取当前保存的 token
  const token = getToken();

  // 统一设置请求头
  const headers: HeadersInit = {
    "Content-Type": "application/json", // 告诉后端：请求体是 JSON
    ...(options.headers ?? {}), // 合并调用者额外传入的 headers
  };

  // 如果有 token，就自动放进 Authorization
  if (token) {
    (headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }

  // 发起请求
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options, // 保留 method/body 等参数
    headers, // 使用统一处理后的 headers
  });

  // 如果状态码不是 2xx，说明请求失败
  if (!response.ok) {
    // 读取错误信息
    const errorText = await response.text();

    // 抛出错误，页面可以 catch 后显示
    throw new Error(errorText || `API request failed: ${response.status}`);
  }

  // 如果后端没有返回内容，避免 response.json() 报错
  if (response.status === 204) {
    return undefined as T;
  }

  // 把 JSON 转成调用者指定的类型 T
  return response.json() as Promise<T>;
}
