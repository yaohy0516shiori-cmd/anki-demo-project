import { apiRequest } from "./client";
import type { TokenResponse, UserOut } from "../types/api";

// register user
// 输入：邮箱、用户名、密码
// 输出：用户信息
export function registerUser(input: {
  email: string;
  username: string;
  password: string;
}): Promise<UserOut> {
  return apiRequest<UserOut>("/users/register", {
    //这个path是通过http://localhost:8000发送请求到后端，读到fastapi暴露接口/users/register访问的函数
    method: "POST", // POST请求，请求体是JSON
    body: JSON.stringify(input), // 把输入转换成JSON字符串
  });
}

// login user
// 输入：邮箱、密码
// 输出：token
export function loginUser(input: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/users/login", {
    method: "POST", // POST请求，请求体是JSON
    body: JSON.stringify(input), // 把输入转换成JSON字符串
  });
}

// get current user
// 输入：无
// 输出：用户信息
export function getCurrentUser(): Promise<UserOut> {
  return apiRequest<UserOut>("/users/me", {
    method: "GET",
  });
}
