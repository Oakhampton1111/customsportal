// Authentication Service for Portal
// Handles user authentication, session management, and user data

import { portalApi } from './api';
import type { User, ApiResponse } from '../../types/portal';

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  company: string;
  phone?: string;
}

export interface ResetPasswordData {
  email: string;
}

export interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface UpdateProfileData {
  firstName?: string;
  lastName?: string;
  company?: string;
  phone?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
}

export class AuthService {
  private authState: AuthState = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    token: null,
  };

  private listeners: Array<(state: AuthState) => void> = [];

  constructor() {
    // Initialize auth state from localStorage on service creation
    this.initializeAuth();
  }

  /**
   * Initialize authentication state from stored data
   */
  private initializeAuth(): void {
    const token = localStorage.getItem('portal_auth_token');
    const userStr = localStorage.getItem('portal_user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.authState = {
          user,
          isAuthenticated: true,
          isLoading: false,
          token,
        };
        portalApi.setAuthToken(token);
      } catch (error) {
        // Clear invalid stored data
        this.clearStoredAuth();
      }
    }
  }

  /**
   * Subscribe to auth state changes
   */
  subscribe(listener: (state: AuthState) => void): () => void {
    this.listeners.push(listener);
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * Notify all listeners of state changes
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.authState));
  }

  /**
   * Update auth state and notify listeners
   */
  private updateAuthState(updates: Partial<AuthState>): void {
    this.authState = { ...this.authState, ...updates };
    this.notifyListeners();
  }

  /**
   * Get current auth state
   */
  getAuthState(): AuthState {
    return { ...this.authState };
  }

  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<ApiResponse<{
    user: User;
    token: string;
    expiresAt: string;
  }>> {
    try {
      this.updateAuthState({ isLoading: true });

      const response = await portalApi.post<{
        user: User;
        token: string;
        expiresAt: string;
      }>('/auth/login', credentials);

      if (response.success && response.data) {
        const { user, token } = response.data;
        
        // Store auth data
        localStorage.setItem('portal_auth_token', token);
        localStorage.setItem('portal_user', JSON.stringify(user));
        
        if (credentials.rememberMe) {
          localStorage.setItem('portal_remember_me', 'true');
        }

        // Update API service with token
        portalApi.setAuthToken(token);

        // Update auth state
        this.updateAuthState({
          user,
          isAuthenticated: true,
          isLoading: false,
          token,
        });
      } else {
        this.updateAuthState({ isLoading: false });
      }

      return response;
    } catch (error) {
      this.updateAuthState({ isLoading: false });
      throw error;
    }
  }

  /**
   * Register new user account
   */
  async register(data: RegisterData): Promise<ApiResponse<{
    user: User;
    token: string;
    message: string;
  }>> {
    try {
      this.updateAuthState({ isLoading: true });

      const response = await portalApi.post<{
        user: User;
        token: string;
        message: string;
      }>('/auth/register', data);

      if (response.success && response.data) {
        const { user, token } = response.data;
        
        // Store auth data
        localStorage.setItem('portal_auth_token', token);
        localStorage.setItem('portal_user', JSON.stringify(user));

        // Update API service with token
        portalApi.setAuthToken(token);

        // Update auth state
        this.updateAuthState({
          user,
          isAuthenticated: true,
          isLoading: false,
          token,
        });
      } else {
        this.updateAuthState({ isLoading: false });
      }

      return response;
    } catch (error) {
      this.updateAuthState({ isLoading: false });
      throw error;
    }
  }

  /**
   * Logout user and clear session
   */
  async logout(): Promise<void> {
    try {
      // Call logout endpoint to invalidate token on server
      await portalApi.post('/auth/logout');
    } catch (error) {
      // Continue with logout even if server call fails
      console.error('Logout API call failed:', error);
    } finally {
      this.clearStoredAuth();
      portalApi.clearAuthToken();
      
      this.updateAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        token: null,
      });
    }
  }

  /**
   * Clear stored authentication data
   */
  private clearStoredAuth(): void {
    localStorage.removeItem('portal_auth_token');
    localStorage.removeItem('portal_user');
    localStorage.removeItem('portal_remember_me');
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(data: ResetPasswordData): Promise<ApiResponse<{
    message: string;
    resetToken?: string; // For development/testing
  }>> {
    return portalApi.post('/auth/forgot-password', data);
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<ApiResponse<{
    message: string;
  }>> {
    return portalApi.post('/auth/reset-password', {
      token,
      password: newPassword,
    });
  }

  /**
   * Change user password
   */
  async changePassword(data: ChangePasswordData): Promise<ApiResponse<{
    message: string;
  }>> {
    return portalApi.post('/auth/change-password', data);
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<ApiResponse<User>> {
    const response = await portalApi.get<User>('/auth/profile');
    
    if (response.success && response.data) {
      // Update stored user data
      localStorage.setItem('portal_user', JSON.stringify(response.data));
      this.updateAuthState({ user: response.data });
    }
    
    return response;
  }

  /**
   * Update user profile
   */
  async updateProfile(data: UpdateProfileData): Promise<ApiResponse<User>> {
    const response = await portalApi.patch<User>('/auth/profile', data);
    
    if (response.success && response.data) {
      // Update stored user data
      localStorage.setItem('portal_user', JSON.stringify(response.data));
      this.updateAuthState({ user: response.data });
    }
    
    return response;
  }

  /**
   * Verify email address
   */
  async verifyEmail(token: string): Promise<ApiResponse<{
    message: string;
    user: User;
  }>> {
    const response = await portalApi.post<{
      message: string;
      user: User;
    }>('/auth/verify-email', { token });
    
    if (response.success && response.data) {
      // Update stored user data
      localStorage.setItem('portal_user', JSON.stringify(response.data.user));
      this.updateAuthState({ user: response.data.user });
    }
    
    return response;
  }

  /**
   * Resend email verification
   */
  async resendEmailVerification(): Promise<ApiResponse<{
    message: string;
  }>> {
    return portalApi.post('/auth/resend-verification');
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<ApiResponse<{
    token: string;
    expiresAt: string;
  }>> {
    try {
      const response = await portalApi.post<{
        token: string;
        expiresAt: string;
      }>('/auth/refresh');

      if (response.success && response.data) {
        const { token } = response.data;
        
        // Update stored token
        localStorage.setItem('portal_auth_token', token);
        portalApi.setAuthToken(token);
        
        this.updateAuthState({ token });
      }

      return response;
    } catch (error) {
      // If refresh fails, logout user
      await this.logout();
      throw error;
    }
  }

  /**
   * Check if user session is valid
   */
  async validateSession(): Promise<boolean> {
    try {
      if (!this.authState.token) {
        return false;
      }

      const response = await portalApi.get('/auth/validate');
      
      if (!response.success) {
        await this.logout();
        return false;
      }

      return true;
    } catch (error) {
      await this.logout();
      return false;
    }
  }

  /**
   * Get user permissions
   */
  async getUserPermissions(): Promise<ApiResponse<{
    permissions: string[];
    roles: string[];
  }>> {
    return portalApi.get('/auth/permissions');
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(permission: string): boolean {
    // This would be implemented based on user roles/permissions
    // For now, return true for authenticated users
    return this.authState.isAuthenticated;
  }

  /**
   * Enable two-factor authentication
   */
  async enableTwoFactor(): Promise<ApiResponse<{
    qrCode: string;
    secret: string;
    backupCodes: string[];
  }>> {
    return portalApi.post('/auth/2fa/enable');
  }

  /**
   * Verify two-factor authentication setup
   */
  async verifyTwoFactor(code: string): Promise<ApiResponse<{
    message: string;
    backupCodes: string[];
  }>> {
    return portalApi.post('/auth/2fa/verify', { code });
  }

  /**
   * Disable two-factor authentication
   */
  async disableTwoFactor(password: string): Promise<ApiResponse<{
    message: string;
  }>> {
    return portalApi.post('/auth/2fa/disable', { password });
  }

  /**
   * Get user sessions
   */
  async getUserSessions(): Promise<ApiResponse<Array<{
    id: string;
    device: string;
    location: string;
    lastActive: string;
    current: boolean;
  }>>> {
    return portalApi.get('/auth/sessions');
  }

  /**
   * Revoke user session
   */
  async revokeSession(sessionId: string): Promise<ApiResponse<{
    message: string;
  }>> {
    return portalApi.delete(`/auth/sessions/${sessionId}`);
  }

  /**
   * Revoke all other sessions
   */
  async revokeAllOtherSessions(): Promise<ApiResponse<{
    message: string;
    revokedCount: number;
  }>> {
    return portalApi.post('/auth/sessions/revoke-all');
  }
}

// Create and export default instance
export const authService = new AuthService();
export default AuthService;