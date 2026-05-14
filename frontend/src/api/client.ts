// src/api/client.ts

// 引入读取 token 的函数
import { getToken } from "../auth/token";

// 后端 API 基础地址
// 优先读取 frontend/.env 里的 VITE_API_BASE_URL
// 声明变量读取环境变量（存储配置信息）
// 如果没有，浏览器访问http://localhost:8000？为什么？
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// 通用 API 请求函数，async是异步函数，返回Promise<T>，
//同步：代码一行一行执行，当前任务没完成，后面的代码必须等着。
// 异步：当前任务（比如网络请求）太慢，代码先把它挂起，先去执行后面的，等结果回来了再处理。
export async function apiRequest<T>(
  path: string, // API 路径，例如 "/users/login"，后端访问函数的路径？
  options: RequestInit = {}, // fetch 的配置，例如 method/body，什么是fetch？fetch是什么？fetch和ajax有什么区别？
): Promise<T> {
  // 读取当前保存的 token，判断是否登录
  const token = getToken();

  // 统一设置请求头
  const headers: HeadersInit = {
    "Content-Type": "application/json", // 告诉后端：请求体是 JSON
    ...(options.headers ?? {}), // 合并调用者额外传入的 headers
  };

  // 如果有 token，就自动放进 Authorization
  //  HTTP 请求头，用来向服务器证明“我是登录过的用户”。
  // Authorization：告诉服务器“我带着凭证来了”。
  // Bearer：凭证类型，意思是“持票人认证”，后面跟着 JWT token。
  // 后端读取这个头，验证 token 是否有效，就知道是谁在请求，从而返回这个用户的数据或拒绝访问。
  if (token) {
    (headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }

  // 发起请求，请求后端API
  // await是什么
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options, // 保留 method/body 等参数，调用者传入的 method、body 等除了 headers 以外的所有东西，原封不动地交给 fetch
    headers, // 使用统一处理后的 headers，这里是你构建的 headers: { 'Content-Type': '...', 'X-Custom': 'abc' }
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
