import http from './http';
import type { User, LoginForm, RegisterForm } from '../types';

/**
 * 认证服务
 */
export const authService = {
  /**
   * 用户注册
   * @param form 注册表单数据
   * @returns 注册成功的用户信息
   */
  async register(form: RegisterForm): Promise<User> {
    const response = await http.post('/auth/register', form);
    return response.data;
  },

  /**
   * 用户登录
   * @param form 登录表单数据
   * @returns 登录成功的用户信息
   */
  async login(form: LoginForm): Promise<User> {
    const response = await http.post('/auth/login', form);
    return response.data;
  },

  /**
   * 获取当前用户信息
   * @returns 当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response = await http.get('/auth/me');
    return response.data;
  },

  /**
   * 保存用户信息到本地存储
   * @param user 用户信息
   */
  saveUserToLocalStorage(user: User): void {
    localStorage.setItem('user', JSON.stringify(user));
  },

  /**
   * 从本地存储获取用户信息
   * @returns 用户信息或null
   */
  getUserFromLocalStorage(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error('解析用户信息失败:', error);
      return null;
    }
  },

  /**
   * 从本地存储移除用户信息
   */
  removeUserFromLocalStorage(): void {
    localStorage.removeItem('user');
  },

  /**
   * 获取认证令牌
   * @returns 令牌或null
   */
  getToken(): string | null {
    const user = this.getUserFromLocalStorage();
    return user?.token || null;
  },
};
