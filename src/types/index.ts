// 用户相关类型定义
export interface User {
  id: number;
  username: string;
  role: string;
  token?: string;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  password: string;
  role: string;
}

export interface ApiResponse<T> {
  code: number;
  msg: string;
  data: T;
}
