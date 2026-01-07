/**
 * Authentication API functions.
 */
import apiClient from './client';
import type { LoginCredentials, RegisterData, AuthToken, User } from '../types/auth';

export const authApi = {
  /**
   * Login with email and password.
   */
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const response = await apiClient.post<AuthToken>('/api/v1/auth/login', credentials);
    return response.data;
  },

  /**
   * Register a new user.
   */
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/api/v1/auth/register', data);
    return response.data;
  },

  /**
   * Get the current authenticated user.
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },

  /**
   * Logout the current user.
   */
  async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout');
  },
};

export default authApi;
