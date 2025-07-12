import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import PortalLayout from './layout/PortalLayout';
import DashboardPage from '../../pages/portal/DashboardPage';
import JobsPage from '../../pages/portal/JobsPage';
import JobDetailPage from '../../pages/portal/JobDetailPage';
import DocumentsPage from '../../pages/portal/DocumentsPage';
import PaymentsPage from '../../pages/portal/PaymentsPage';
import SupportPage from '../../pages/portal/SupportPage';
import ProtectedRoute from './auth/ProtectedRoute';
import { useAuth } from './auth/AuthProvider';

// Temporary placeholder component for unimplemented pages
const PlaceholderPage: React.FC<{ title: string; description: string }> = ({ title, description }) => (
  <div className="portal-card">
    <div className="portal-card-header">
      <h1 className="portal-card-title">{title}</h1>
    </div>
    <div className="portal-card-content">
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🚧</div>
        <h2 className="text-xl font-medium text-gray-900 mb-2">Coming Soon</h2>
        <p className="text-gray-600 mb-4">{description}</p>
        <p className="text-sm text-gray-500">This page is currently under development.</p>
      </div>
    </div>
  </div>
);

const PortalRoutes: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <Routes>
      <Route path="/" element={
        <ProtectedRoute>
          <PortalLayout user={user || undefined} onLogout={logout} />
        </ProtectedRoute>
      }>
        {/* Default redirect to dashboard */}
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* Dashboard */}
        <Route path="dashboard" element={<DashboardPage />} />
        
        {/* Jobs */}
        <Route path="jobs" element={<JobsPage />} />
        <Route path="jobs/:jobId" element={<JobDetailPage />} />
        
        {/* Documents */}
        <Route path="documents" element={<DocumentsPage />} />
        
        {/* Payments */}
        <Route path="payments" element={<PaymentsPage />} />
        
        {/* Activity */}
        <Route 
          path="activity" 
          element={
            <PlaceholderPage 
              title="Activity Feed" 
              description="Stay updated with real-time notifications and activity logs for all your shipments and account." 
            />
          } 
        />
        
        {/* Support */}
        <Route path="support" element={<SupportPage />} />
        
        {/* Profile & Settings */}
        <Route 
          path="profile" 
          element={
            <PlaceholderPage 
              title="Profile Settings" 
              description="Manage your account information, company details, and contact preferences." 
            />
          } 
        />
        <Route 
          path="preferences" 
          element={
            <PlaceholderPage 
              title="Preferences" 
              description="Customize your portal experience, notification settings, and display preferences." 
            />
          } 
        />
        <Route 
          path="help" 
          element={
            <PlaceholderPage 
              title="Help & Support" 
              description="Find answers to common questions, access user guides, and learn how to use the portal effectively." 
            />
          } 
        />
        
        {/* Catch-all route for 404 within portal */}
        <Route 
          path="*" 
          element={
            <div className="portal-card">
              <div className="portal-card-content">
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">❓</div>
                  <h2 className="text-xl font-medium text-gray-900 mb-2">Page Not Found</h2>
                  <p className="text-gray-600 mb-4">
                    The page you're looking for doesn't exist or has been moved.
                  </p>
                  <div className="space-x-4">
                    <button 
                      onClick={() => window.history.back()}
                      className="portal-btn portal-btn-outline"
                    >
                      Go Back
                    </button>
                    <a href="/dashboard" className="portal-btn portal-btn-primary">
                      Go to Dashboard
                    </a>
                  </div>
                </div>
              </div>
            </div>
          } 
        />
      </Route>
    </Routes>
  );
};

export default PortalRoutes;