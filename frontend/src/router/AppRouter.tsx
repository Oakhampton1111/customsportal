import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import LoginForm from '../components/auth/LoginForm';
import RegisterForm from '../components/auth/RegisterForm';
import CustomerDashboard from '../components/dashboard/CustomerDashboard';
import DocumentUpload from '../components/documents/DocumentUpload';
import LOACreator from '../components/loa/LOACreator';
import EDIJobRegistration from '../components/edi/EDIJobRegistration';

// Page components
import DocumentsPage from '../pages/DocumentsPage';
import DocumentDetailPage from '../pages/DocumentDetailPage';
import LOAPage from '../pages/LOAPage';
import LOADetailPage from '../pages/LOADetailPage';
import EDIPage from '../pages/EDIPage';
import EDIDetailPage from '../pages/EDIDetailPage';
import CompliancePage from '../pages/CompliancePage';
import SettingsPage from '../pages/SettingsPage';
import HelpPage from '../pages/HelpPage';
import NotFoundPage from '../pages/NotFoundPage';
import BrokerReviewPage from '../pages/BrokerReviewPage';

// Auth guard component
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = localStorage.getItem('auth_token');
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Public route component (redirects to dashboard if authenticated)
const PublicRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = localStorage.getItem('auth_token');
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <>{children}</>;
};

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={
          <PublicRoute>
            <LoginForm />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <RegisterForm />
          </PublicRoute>
        } />

        {/* Protected routes with layout */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          {/* Dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<CustomerDashboard />} />

          {/* Documents */}
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="documents/upload" element={<DocumentUpload />} />
          <Route path="documents/:id" element={<DocumentDetailPage />} />

          {/* Letter of Authority */}
          <Route path="loa" element={<LOAPage />} />
          <Route path="loa/create" element={<LOACreator />} />
          <Route path="loa/:id" element={<LOADetailPage />} />

          {/* EDI Jobs */}
          <Route path="edi" element={<EDIPage />} />
          <Route path="edi/register" element={<EDIJobRegistration />} />
          <Route path="edi/:id" element={<EDIDetailPage />} />

          {/* Broker Review */}
          <Route path="broker-review" element={<BrokerReviewPage />} />

          {/* Compliance */}
          <Route path="compliance" element={<CompliancePage />} />
          <Route path="compliance/requirements" element={<CompliancePage />} />
          <Route path="compliance/audits" element={<CompliancePage />} />
          <Route path="compliance/reports" element={<CompliancePage />} />

          {/* Settings */}
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<SettingsPage />} />

          {/* Help & Support */}
          <Route path="help" element={<HelpPage />} />
          <Route path="help/*" element={<HelpPage />} />
          <Route path="contact" element={<HelpPage />} />
          <Route path="status" element={<HelpPage />} />

          {/* Legal pages */}
          <Route path="privacy" element={<HelpPage />} />
          <Route path="terms" element={<HelpPage />} />
          <Route path="security" element={<HelpPage />} />
        </Route>

        {/* 404 page */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;