// 常量，保存 token 的 key
const TOKEN_KEY = "access_token";

// 保存 token 到 localStorage
// 登录成功后调用
export function saveToken(token: string): void {
  // localStorage浏览器本地存储，保存 token
  // setItem 存数据
  localStorage.setItem(TOKEN_KEY, token);
}

// 从 localStorage 读取 token
// 发送请求调用函数，token放进authorization请求头
export function getToken(): string | null {
  // getItem 取数据
  // 返回 token 字符串或 没登陆返回 null
  return localStorage.getItem(TOKEN_KEY);
}

// 删除 token
// 退出登录后调用
export function deleteToken(): void {
  // removeItem 删数据
  localStorage.removeItem(TOKEN_KEY);
}

// 检查 token 是否存在
// 判断是否登录
export function isLoggedIn(): boolean {
  // Boolean() 将 token 转换为布尔值
  return Boolean(getToken()); // 如果 token 存在，返回 true，否则返回 false
}
