import React from 'react';
import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
  permissions?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  redirectTo = '/login',
  permissions = [],
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    // Save the attempted location for redirect after login
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location.pathname }} 
        replace 
      />
    );
  }

  // If user is authenticated but doesn't have required permissions
  if (requireAuth && isAuthenticated && permissions.length > 0) {
    const hasRequiredPermissions = permissions.every(permission => {
      // This would check against user's actual permissions
      // For now, we'll assume all authenticated users have access
      return true;
    });

    if (!hasRequiredPermissions) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="text-6xl mb-4">🚫</div>
            <h2 className="text-xl font-medium text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600 mb-4">
              You don't have permission to access this page.
            </p>
            <button
              onClick={() => window.history.back()}
              className="portal-btn portal-btn-primary"
            >
              Go Back
            </button>
          </div>
        </div>
      );
    }
  }

  // If user is authenticated but account is not active
  if (requireAuth && isAuthenticated && user && !user.isActive) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">⏳</div>
          <h2 className="text-xl font-medium text-gray-900 mb-2">Account Pending</h2>
          <p className="text-gray-600 mb-4">
            Your account is currently being reviewed. You'll receive an email once it's activated.
          </p>
          <div className="space-x-4">
            <button
              onClick={() => window.location.reload()}
              className="portal-btn portal-btn-outline"
            >
              Refresh
            </button>
            <button
              onClick={() => {
                // This would trigger logout
                window.location.href = '/login';
              }}
              className="portal-btn portal-btn-primary"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render children if all checks pass
  return <>{children}</>;
};

export default ProtectedRoute;