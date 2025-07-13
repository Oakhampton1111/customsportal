import React, { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { authService, type AuthState } from '../../../services/portal/authService';

interface AuthContextType extends AuthState {
  login: (email: string, password: string, rememberMe?: boolean) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (data: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
    company: string;
    phone?: string;
  }) => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
  updateProfile: (data: {
    firstName?: string;
    lastName?: string;
    company?: string;
    phone?: string;
  }) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>(authService.getAuthState());
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Subscribe to auth state changes
    const unsubscribe = authService.subscribe((newState) => {
      setAuthState(newState);
    });

    // Validate session on mount
    const initializeAuth = async () => {
      try {
        if (authState.token) {
          await authService.validateSession();
        }
      } catch (error) {
        // Session validation failed - handled silently
      } finally {
        setIsInitialized(true);
      }
    };

    initializeAuth();

    return unsubscribe;
  }, []);

  const login = async (email: string, password: string, rememberMe?: boolean): Promise<boolean> => {
    try {
      const response = await authService.login({ email, password, rememberMe });
      return response.success;
    } catch (error) {
      // Login failed - handled silently
      return false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      // Logout failed - handled silently
    }
  };

  const register = async (data: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
    company: string;
    phone?: string;
  }): Promise<boolean> => {
    try {
      const response = await authService.register(data);
      return response.success;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await authService.refreshToken();
      return response.success;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const updateProfile = async (data: {
    firstName?: string;
    lastName?: string;
    company?: string;
    phone?: string;
  }): Promise<boolean> => {
    try {
      const response = await authService.updateProfile(data);
      return response.success;
    } catch (error) {
      console.error('Profile update failed:', error);
      return false;
    }
  };

  const contextValue: AuthContextType = {
    ...authState,
    login,
    logout,
    register,
    refreshToken,
    updateProfile,
  };

  // Show loading spinner while initializing
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Initializing...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthProvider;