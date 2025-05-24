// src/utils/auth.js

// 从 localStorage 获取 token
export function getToken() {
    return localStorage.getItem('token');
  }
  
  // 将 token 存入 localStorage
  export function setToken(token) {
    localStorage.setItem('token', token);
  }
  
  // 移除 token
  export function removeToken() {
    localStorage.removeItem('token');
  }
  
  // 检查是否已登录
  export function isLoggedIn() {
    return !!getToken();
  }