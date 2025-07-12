import React, { useState, useEffect } from 'react';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { CustomerDashboard } from './components/dashboard/CustomerDashboard';
import { DocumentUpload } from './components/documents/DocumentUpload';
import { LOACreator } from './components/loa/LOACreator';
import { EDIJobRegistration } from './components/edi/EDIJobRegistration';
import type { Customer, CustomerLogin, CustomerRegistration, TokenResponse } from './types/customer';
import type { DocumentUploadRequest } from './types/documents';
import type { LOACreateRequest } from './types/loa';
import type { JobRegistrationRequest } from './types/edi';

type AppView = 'login' | 'register' | 'dashboard' | 'upload' | 'loa' | 'edi';

interface AppState {
  currentView: AppView;
  customer: Customer | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

function App() {
  const [state, setState] = useState<AppState>({
    currentView: 'login',
    customer: null,
    token: null,
    loading: false,
    error: null
  });

  // Check for existing session on app load
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    const savedCustomer = localStorage.getItem('customer_data');
    
    if (savedToken && savedCustomer) {
      try {
        const customer = JSON.parse(savedCustomer);
        setState(prev => ({
          ...prev,
          token: savedToken,
          customer,
          currentView: 'dashboard'
        }));
      } catch (error) {
        console.error('Failed to parse saved customer data:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('customer_data');
      }
    }
  }, []);

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  };

  const setView = (view: AppView) => {
    setState(prev => ({ ...prev, currentView: view, error: null }));
  };

  // Mock API functions - these would be replaced with actual API calls
  const handleLogin = async (credentials: CustomerLogin) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful login
      const mockTokenResponse: TokenResponse = {
        access_token: 'mock_access_token_' + Date.now(),
        refresh_token: 'mock_refresh_token_' + Date.now(),
        token_type: 'Bearer',
        expires_in: 3600,
        customer: {
          id: 'cust_001',
          email: credentials.email,
          first_name: 'John',
          last_name: 'Doe',
          phone: '+61 2 1234 5678',
          company_name: 'Acme Import/Export Pty Ltd',
          verification_status: 'verified',
          email_verified: true,
          profile_picture_url: undefined,
          preferred_auth_method: 'email',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T10:30:00Z'
        }
      };

      // Save to localStorage
      localStorage.setItem('auth_token', mockTokenResponse.access_token);
      localStorage.setItem('customer_data', JSON.stringify(mockTokenResponse.customer));

      setState(prev => ({
        ...prev,
        token: mockTokenResponse.access_token,
        customer: mockTokenResponse.customer,
        currentView: 'dashboard'
      }));
    } catch (error) {
      setError('Login failed. Please check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = async (provider: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate SSO redirect
      await new Promise(resolve => setTimeout(resolve, 500));
      setError(`SSO login with ${provider} would redirect to provider's authentication page.`);
    } catch (error) {
      setError(`Failed to initiate SSO login with ${provider}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: CustomerRegistration) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock successful registration
      setError(null);
      alert('Registration successful! Please check your email to verify your account.');
      setView('login');
    } catch (error) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('customer_data');
    setState({
      currentView: 'login',
      customer: null,
      token: null,
      loading: false,
      error: null
    });
  };

  const handleDocumentUpload = async (file: File, metadata: DocumentUploadRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate file upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      alert(`Document "${file.name}" uploaded successfully!`);
      setView('dashboard');
    } catch (error) {
      setError('Failed to upload document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLOA = async (data: LOACreateRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate LOA creation
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      alert('Digital Letter of Authority created successfully!');
      setView('dashboard');
    } catch (error) {
      setError('Failed to create LOA. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterEDIJob = async (data: JobRegistrationRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate EDI job registration
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert('EDI job registered successfully!');
      setView('dashboard');
    } catch (error) {
      setError('Failed to register EDI job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Navigation component
  const Navigation = () => {
    if (!state.customer) return null;

    return (
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex space-x-8">
              <button
                onClick={() => setView('dashboard')}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  state.currentView === 'dashboard'
                    ? 'border-indigo-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setView('upload')}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  state.currentView === 'upload'
                    ? 'border-indigo-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Upload Documents
              </button>
              <button
                onClick={() => setView('loa')}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  state.currentView === 'loa'
                    ? 'border-indigo-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Create LOA
              </button>
              <button
                onClick={() => setView('edi')}
                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                  state.currentView === 'edi'
                    ? 'border-indigo-500 text-gray-900'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                EDI Jobs
              </button>
            </div>
          </div>
        </div>
      </nav>
    );
  };

  // Render current view
  const renderCurrentView = () => {
    switch (state.currentView) {
      case 'login':
        return (
          <LoginForm
            onLogin={handleLogin}
            onSSOLogin={handleSSOLogin}
            loading={state.loading}
            error={state.error || undefined}
          />
        );
      
      case 'register':
        return (
          <RegisterForm
            onRegister={handleRegister}
            loading={state.loading}
            error={state.error || undefined}
          />
        );
      
      case 'dashboard':
        return state.customer ? (
          <CustomerDashboard
            customer={state.customer}
            onLogout={handleLogout}
          />
        ) : null;
      
      case 'upload':
        return (
          <div className="min-h-screen bg-gray-50 py-8">
            <DocumentUpload
              onUpload={handleDocumentUpload}
              loading={state.loading}
              error={state.error || undefined}
            />
          </div>
        );
      
      case 'loa':
        return (
          <div className="min-h-screen bg-gray-50 py-8">
            <LOACreator
              onCreateLOA={handleCreateLOA}
              loading={state.loading}
              error={state.error || undefined}
            />
          </div>
        );
      
      case 'edi':
        return (
          <div className="min-h-screen bg-gray-50 py-8">
            <EDIJobRegistration
              onRegisterJob={handleRegisterEDIJob}
              loading={state.loading}
              error={state.error || undefined}
            />
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="App">
      {/* Show navigation only when logged in and not on auth pages */}
      {state.customer && state.currentView !== 'login' && state.currentView !== 'register' && (
        <Navigation />
      )}
      
      {/* Main content */}
      {renderCurrentView()}
      
      {/* Auth toggle for demo purposes */}
      {(state.currentView === 'login' || state.currentView === 'register') && (
        <div className="fixed bottom-4 right-4">
          <button
            onClick={() => setView(state.currentView === 'login' ? 'register' : 'login')}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm"
          >
            {state.currentView === 'login' ? 'Go to Register' : 'Go to Login'}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
