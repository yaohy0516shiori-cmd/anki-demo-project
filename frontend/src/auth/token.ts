// token.ts用于保存和获取token，判断是否登录
// token指的是后端返回的JWT token，前端要保存，用户登录后每次请求都要带上token相当于登录凭证（一个临时密码，这样在前端发送请求的时候后端不用每次都校验密码）
// localStorage 里保存 token 的 key
const TOKEN_KEY = "access_token"; // 后端查找token的key，把key固定在硬盘固定位置上

// 保存 token
export function saveToken(token: string): void {
  // 把 token 存到浏览器本地，用于后续请求
  localStorage.setItem(TOKEN_KEY, token);
}

// 读取 token
export function getToken(): string | null {
  // 如果已经登录，返回 token
  // 如果没登录，返回 null
  return localStorage.getItem(TOKEN_KEY);
}

// 删除 token
export function removeToken(): void {
  // 退出登录时删除 token
  localStorage.removeItem(TOKEN_KEY);
}

// 判断是否登录
export function isLoggedIn(): boolean {
  // Boolean(...) 把 token 转成 true/false
  return Boolean(getToken());
}
