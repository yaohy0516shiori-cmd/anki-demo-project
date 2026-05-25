import { apiRequest } from "./client";
import type {
  EmailCodeRequest,
  TokenResponse,
  UserOut,
  DevEmailCodeOut,
  MessageOut,
  PasswordResetConfirm,
} from "../types/api";

// register user
// 输入：邮箱、用户名、密码
// 输出：用户信息
export function registerUser(input: {
  email: string;
  username: string;
  password: string;
  verification_code: string; // 注册验证码
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

export function sendRegisterCode(
  input: EmailCodeRequest,
): Promise<DevEmailCodeOut> {
  return apiRequest<DevEmailCodeOut>("/users/register/send-code", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function resetPassword(
  input: PasswordResetConfirm,
): Promise<MessageOut> {
  return apiRequest<MessageOut>("/users/password/reset", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function sendForgetCode(input: EmailCodeRequest): Promise<MessageOut> {
  return apiRequest<MessageOut>("/users/password/forgot/send-code", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateMyPassword(input: {
  old_password: string;
  new_password: string;
}): Promise<MessageOut> {
  return apiRequest<MessageOut>("/users/me/password", {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}
