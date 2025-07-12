# Real Data Integration Requirements - Customer Portal

## Overview

This document outlines the comprehensive requirements for integrating real data into the customer portal, replacing all mock data with live backend connections. The integration focuses on customer-specific data flows, API endpoints, and real-time updates.

## 1. Current Mock Data Analysis

### A. Existing Mock Data in Components

#### Dashboard Mock Data
```typescript
// Current mock data in CustomerDashboard.tsx
const mockStats: DashboardStats = {
  documents: {
    total_documents: 45,
    total_size_bytes: 125000000,
    // ... more mock data
  },
  compliance: {
    total_requirements: 12,
    pending_requirements: 3,
    // ... more mock data
  },
  recentActivity: [
    {
      id: '1',
      type: 'document',
      title: 'Invoice uploaded',
      // ... mock activity items
    }
  ]
};
```

#### Authentication Mock Data
```typescript
// Current mock data in App.tsx
const mockTokenResponse: TokenResponse = {
  access_token: 'mock_access_token_' + Date.now(),
  refresh_token: 'mock_refresh_token_' + Date.now(),
  customer: {
    id: 'cust_001',
    email: credentials.email,
    first_name: 'John',
    last_name: 'Doe',
    // ... more mock customer data
  }
};
```

## 2. Required Backend API Endpoints

### A. Customer Authentication APIs

#### Existing APIs (Update Required)
```typescript
// Update existing authApi in services/api.ts
export const authApi = {
  // ✅ Already exists - update for customer portal branding
  async login(credentials: CustomerLogin): Promise<TokenResponse>,
  async register(data: CustomerRegistration): Promise<TokenResponse>,
  async logout(): Promise<void>,
  async refreshToken(): Promise<TokenResponse>,
  
  // ➕ New endpoints needed
  async getCustomerProfile(): Promise<Customer>,
  async updateCustomerProfile(data: Partial<Customer>): Promise<Customer>,
  async changePassword(data: PasswordChangeRequest): Promise<void>,
  async requestPasswordReset(email: string): Promise<void>,
  async resetPassword(token: string, newPassword: string): Promise<void>
};
```

### B. Customer Jobs/Clearances APIs

#### New API Endpoints Required
```typescript
// New customerJobsApi in services/portal/customerJobsApi.ts
export const customerJobsApi = {
  // Get all jobs for authenticated customer
  async getJobs(filters?: JobFilters): Promise<CustomsJob[]> {
    // GET /api/customer/jobs?status=active&serviceType=clearance
  },
  
  // Get specific job details
  async getJob(jobId: string): Promise<CustomsJob> {
    // GET /api/customer/jobs/{jobId}
  },
  
  // Create new job/booking
  async createJob(data: JobCreateRequest): Promise<CustomsJob> {
    // POST /api/customer/jobs
  },
  
  // Get customs declaration for job
  async getJobDeclaration(jobId: string): Promise<CustomsDeclaration> {
    // GET /api/customer/jobs/{jobId}/declaration
  },
  
  // Get job line items with tariff details
  async getJobLineItems(jobId: string): Promise<LineItem[]> {
    // GET /api/customer/jobs/{jobId}/line-items
  },
  
  // Update job status (limited customer actions)
  async updateJobStatus(jobId: string, action: CustomerJobAction): Promise<CustomsJob> {
    // PUT /api/customer/jobs/{jobId}/status
  },
  
  // Upload documents for job
  async uploadJobDocuments(jobId: string, files: File[]): Promise<Document[]> {
    // POST /api/customer/jobs/{jobId}/documents
  },
  
  // Get job documents
  async getJobDocuments(jobId: string): Promise<Document[]> {
    // GET /api/customer/jobs/{jobId}/documents
  }
};
```

### C. Customer Dashboard APIs

#### New Dashboard Endpoints
```typescript
// New customerDashboardApi in services/portal/customerDashboardApi.ts
export const customerDashboardApi = {
  // Get dashboard statistics
  async getDashboardStats(): Promise<DashboardStats> {
    // GET /api/customer/dashboard/stats
    return {
      activeJobs: number,
      awaitingClearance: number,
      completedThisYear: number,
      pendingPayments: string // formatted currency
    };
  },
  
  // Get recent activity feed
  async getRecentActivity(limit?: number): Promise<ActivityItem[]> {
    // GET /api/customer/dashboard/activity?limit=10
  },
  
  // Get customer notifications
  async getNotifications(): Promise<CustomerNotification[]> {
    // GET /api/customer/notifications
  },
  
  // Mark notification as read
  async markNotificationRead(notificationId: string): Promise<void> {
    // PUT /api/customer/notifications/{notificationId}/read
  }
};
```

### D. Customer Payments APIs

#### New Payment Endpoints
```typescript
// New customerPaymentsApi in services/portal/customerPaymentsApi.ts
export const customerPaymentsApi = {
  // Get outstanding payments
  async getOutstandingPayments(): Promise<OutstandingPayment[]> {
    // GET /api/customer/payments/outstanding
  },
  
  // Get payment history
  async getPaymentHistory(filters?: PaymentFilters): Promise<Payment[]> {
    // GET /api/customer/payments/history
  },
  
  // Process payment for job
  async processJobPayment(jobId: string, paymentData: PaymentRequest): Promise<PaymentResult> {
    // POST /api/customer/jobs/{jobId}/payment
  },
  
  // Process bulk payment
  async processBulkPayment(jobIds: string[], paymentData: PaymentRequest): Promise<PaymentResult> {
    // POST /api/customer/payments/bulk
  },
  
  // Get payment receipt
  async getPaymentReceipt(paymentId: string): Promise<Blob> {
    // GET /api/customer/payments/{paymentId}/receipt
  },
  
  // Get payment breakdown for job
  async getPaymentBreakdown(jobId: string): Promise<PaymentBreakdown> {
    // GET /api/customer/jobs/{jobId}/payment-breakdown
  }
};
```

### E. Customer Documents APIs

#### Enhanced Document Endpoints
```typescript
// Update existing documentsApi for customer portal
export const customerDocumentsApi = {
  // Get customer documents (with job association)
  async getDocuments(filters?: CustomerDocumentFilters): Promise<Document[]> {
    // GET /api/customer/documents?jobId=123&category=invoice
  },
  
  // Upload document with job association
  async uploadDocument(data: CustomerDocumentUploadRequest, file: File): Promise<Document> {
    // POST /api/customer/documents
    // Include jobId, category, description in metadata
  },
  
  // Get document categories for customer
  async getDocumentCategories(): Promise<DocumentCategory[]> {
    // GET /api/customer/documents/categories
  },
  
  // Delete customer document
  async deleteDocument(documentId: string): Promise<void> {
    // DELETE /api/customer/documents/{documentId}
  },
  
  // Download document
  async downloadDocument(documentId: string): Promise<Blob> {
    // GET /api/customer/documents/{documentId}/download
  }
};
```

### F. Customer Support APIs

#### New Support Endpoints
```typescript
// New customerSupportApi in services/portal/customerSupportApi.ts
export const customerSupportApi = {
  // Create support ticket
  async createTicket(data: SupportTicketRequest): Promise<SupportTicket> {
    // POST /api/customer/support/tickets
  },
  
  // Get customer tickets
  async getTickets(): Promise<SupportTicket[]> {
    // GET /api/customer/support/tickets
  },
  
  // Get specific ticket
  async getTicket(ticketId: string): Promise<SupportTicket> {
    // GET /api/customer/support/tickets/{ticketId}
  },
  
  // Add message to ticket
  async addTicketMessage(ticketId: string, message: string): Promise<TicketMessage> {
    // POST /api/customer/support/tickets/{ticketId}/messages
  },
  
  // Get support contact information
  async getContactInfo(): Promise<SupportContactInfo> {
    // GET /api/customer/support/contact-info
  }
};
```

## 3. Backend Database Schema Requirements

### A. Customer Jobs Table
```sql
CREATE TABLE customer_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    reference VARCHAR(50) UNIQUE NOT NULL, -- CC-2025-001234
    service_type VARCHAR(50) NOT NULL, -- 'Import Clearance', 'Export Clearance', 'Consultation'
    description TEXT NOT NULL,
    
    -- ICS/Customs Information
    ics_reference VARCHAR(100),
    ics_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'cleared', 'payment_required'
    port_of_entry VARCHAR(10), -- AUBNE, AUSYD, etc.
    country_of_origin VARCHAR(3), -- ISO country code
    supplier_name VARCHAR(255),
    consignee_name VARCHAR(255),
    
    -- Financial Information
    customs_value DECIMAL(12,2),
    freight_insurance DECIMAL(12,2),
    cif_value DECIMAL(12,2),
    duty_amount DECIMAL(12,2),
    gst_amount DECIMAL(12,2),
    processing_fee DECIMAL(12,2),
    total_amount DECIMAL(12,2),
    exchange_rate DECIMAL(8,4),
    
    -- Dates
    declaration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for customer queries
    INDEX idx_customer_jobs_customer_id (customer_id),
    INDEX idx_customer_jobs_reference (reference),
    INDEX idx_customer_jobs_status (ics_status),
    INDEX idx_customer_jobs_created (created_at DESC)
);
```

### B. Job Line Items Table
```sql
CREATE TABLE job_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES customer_jobs(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    
    -- Product Information
    hs_code VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_of_measure VARCHAR(20),
    unit_value DECIMAL(12,2),
    total_value DECIMAL(12,2),
    
    -- Duty Information
    duty_rate VARCHAR(20), -- '5%', 'Free', '$2.50/kg'
    duty_amount DECIMAL(12,2),
    concessions TEXT[], -- ['FTA - Germany', 'TCO 2504567']
    treatment_code VARCHAR(10), -- N10, N20, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_line_items_job_id (job_id),
    INDEX idx_line_items_hs_code (hs_code)
);
```

### C. Customer Payments Table
```sql
CREATE TABLE customer_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    job_id UUID REFERENCES customer_jobs(id),
    
    -- Payment Information
    payment_reference VARCHAR(100) UNIQUE,
    amount DECIMAL(12,2) NOT NULL,
    payment_type VARCHAR(50) NOT NULL, -- 'duty', 'service_fee', 'consultation'
    payment_method VARCHAR(50), -- 'credit_card', 'bank_transfer', 'eft'
    
    -- Status and Processing
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    payment_date TIMESTAMP,
    receipt_url VARCHAR(255),
    gateway_transaction_id VARCHAR(255),
    
    -- Breakdown
    customs_duty DECIMAL(12,2) DEFAULT 0,
    gst_amount DECIMAL(12,2) DEFAULT 0,
    processing_fee DECIMAL(12,2) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_customer_payments_customer_id (customer_id),
    INDEX idx_customer_payments_job_id (job_id),
    INDEX idx_customer_payments_status (status),
    INDEX idx_customer_payments_date (payment_date DESC)
);
```

### D. Customer Activity Log Table
```sql
CREATE TABLE customer_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    job_id UUID REFERENCES customer_jobs(id),
    
    -- Activity Information
    activity_type VARCHAR(50) NOT NULL, -- 'job_created', 'document_uploaded', 'payment_completed'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50), -- 'success', 'warning', 'error', 'info'
    
    -- Metadata
    metadata JSONB, -- Additional activity-specific data
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_customer_activity_customer_id (customer_id),
    INDEX idx_customer_activity_job_id (job_id),
    INDEX idx_customer_activity_type (activity_type),
    INDEX idx_customer_activity_created (created_at DESC)
);
```

### E. Support Tickets Table
```sql
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    
    -- Ticket Information
    ticket_number VARCHAR(50) UNIQUE NOT NULL, -- ST-2025-001234
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'closed'
    
    -- Assignment
    assigned_to VARCHAR(255), -- Broker/support staff email
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_support_tickets_customer_id (customer_id),
    INDEX idx_support_tickets_status (status),
    INDEX idx_support_tickets_priority (priority),
    INDEX idx_support_tickets_created (created_at DESC)
);
```

### F. Customer Notifications Table
```sql
CREATE TABLE customer_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    job_id UUID REFERENCES customer_jobs(id),
    
    -- Notification Information
    type VARCHAR(50) NOT NULL, -- 'job_update', 'payment_due', 'document_required'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    
    -- Status
    read_at TIMESTAMP NULL,
    dismissed_at TIMESTAMP NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_customer_notifications_customer_id (customer_id),
    INDEX idx_customer_notifications_read (read_at),
    INDEX idx_customer_notifications_created (created_at DESC)
);
```

## 4. Data Integration Implementation Plan

### A. Phase 1: Authentication Integration

#### Replace Mock Authentication
```typescript
// Remove mock data from App.tsx
const handleLogin = async (credentials: CustomerLogin) => {
  setLoading(true);
  setError(null);
  
  try {
    // Replace mock with real API call
    const response = await authApi.login(credentials);
    
    // Store real tokens
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    localStorage.setItem('customer_data', JSON.stringify(response.customer));
    
    setState(prev => ({
      ...prev,
      token: response.access_token,
      customer: response.customer,
      currentView: 'dashboard'
    }));
  } catch (error) {
    setError(error.message || 'Login failed');
  } finally {
    setLoading(false);
  }
};
```

#### Add Token Refresh Logic
```typescript
// Add automatic token refresh
const setupTokenRefresh = () => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    // Decode JWT to get expiry
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiryTime = payload.exp * 1000;
    const refreshTime = expiryTime - (5 * 60 * 1000); // 5 minutes before expiry
    
    setTimeout(async () => {
      try {
        const response = await authApi.refreshToken();
        localStorage.setItem('auth_token', response.access_token);
      } catch (error) {
        // Redirect to login if refresh fails
        handleLogout();
      }
    }, refreshTime - Date.now());
  }
};
```

### B. Phase 2: Dashboard Data Integration

#### Replace Mock Dashboard Stats
```typescript
// Update CustomerPortalDashboard.tsx
const CustomerPortalDashboard: React.FC<CustomerPortalDashboardProps> = ({ customer }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        
        // Replace mock with real API calls
        const [statsData, activityData] = await Promise.all([
          customerDashboardApi.getDashboardStats(),
          customerDashboardApi.getRecentActivity(10)
        ]);
        
        setStats(statsData);
        setRecentActivity(activityData);
      } catch (error) {
        setError('Failed to load dashboard data');
        console.error('Dashboard data error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadDashboardData();
  }, []);
  
  // Add real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Refresh dashboard data every 5 minutes
      loadDashboardData();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);
};
```

### C. Phase 3: Jobs Data Integration

#### Implement Real Jobs API
```typescript
// Create JobsListView.tsx with real data
const JobsListView: React.FC = () => {
  const [jobs, setJobs] = useState<CustomsJob[]>([]);
  const [filters, setFilters] = useState<JobFilters>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const loadJobs = useCallback(async () => {
    try {
      setLoading(true);
      const jobsData = await customerJobsApi.getJobs(filters);
      setJobs(jobsData);
    } catch (error) {
      setError('Failed to load jobs');
      console.error('Jobs loading error:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);
  
  useEffect(() => {
    loadJobs();
  }, [loadJobs]);
  
  // Real-time job status updates via WebSocket
  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE_URL}/customer/jobs`);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type === 'job_status_update') {
        setJobs(prevJobs => 
          prevJobs.map(job => 
            job.id === update.jobId 
              ? { ...job, icsStatus: update.status }
              : job
          )
        );
      }
    };
    
    return () => ws.close();
  }, []);
};
```

### D. Phase 4: Document Integration

#### Real Document Management
```typescript
// Update DocumentManagement.tsx
const DocumentManagement: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<DocumentCategory[]>([]);
  const [uploading, setUploading] = useState(false);
  
  const handleFileUpload = async (files: File[], jobId?: string, category?: string) => {
    setUploading(true);
    
    try {
      const uploadPromises = files.map(file => 
        customerDocumentsApi.uploadDocument({
          jobId,
          category,
          description: file.name
        }, file)
      );
      
      const uploadedDocs = await Promise.all(uploadPromises);
      setDocuments(prev => [...prev, ...uploadedDocs]);
      
      // Show success notification
      showNotification('Documents uploaded successfully', 'success');
    } catch (error) {
      showNotification('Failed to upload documents', 'error');
    } finally {
      setUploading(false);
    }
  };
};
```

### E. Phase 5: Payment Integration

#### Real Payment Processing
```typescript
// Implement PaymentsDashboard.tsx
const PaymentsDashboard: React.FC = () => {
  const [outstandingPayments, setOutstandingPayments] = useState<OutstandingPayment[]>([]);
  const [paymentHistory, setPaymentHistory] = useState<Payment[]>([]);
  const [processing, setProcessing] = useState(false);
  
  const processPayment = async (jobIds: string[], paymentMethod: string) => {
    setProcessing(true);
    
    try {
      const result = await customerPaymentsApi.processBulkPayment(jobIds, {
        paymentMethod,
        returnUrl: `${window.location.origin}/payments/success`,
        cancelUrl: `${window.location.origin}/payments/cancel`
      });
      
      if (result.redirectUrl) {
        // Redirect to payment gateway
        window.location.href = result.redirectUrl;
      }
    } catch (error) {
      showNotification('Payment processing failed', 'error');
    } finally {
      setProcessing(false);
    }
  };
};
```

## 5. Error Handling and Loading States

### A. Global Error Handling
```typescript
// Create ErrorBoundary component
class CustomerPortalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('Customer Portal Error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>We're sorry, but something unexpected happened.</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### B. Loading States
```typescript
// Create consistent loading components
const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => (
  <div className={`loading-spinner loading-spinner-${size}`}>
    <div className="spinner"></div>
  </div>
);

const LoadingCard: React.FC = () => (
  <div className="loading-card">
    <div className="loading-skeleton loading-skeleton-title"></div>
    <div className="loading-skeleton loading-skeleton-text"></div>
    <div className="loading-skeleton loading-skeleton-text"></div>
  </div>
);
```

## 6. Real-time Updates Implementation

### A. WebSocket Integration
```typescript
// Create WebSocket service
class CustomerPortalWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(customerId: string) {
    const token = localStorage.getItem('auth_token');
    this.ws = new WebSocket(`${WS_BASE_URL}/customer/${customerId}?token=${token}`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onclose = () => {
      this.handleReconnect();
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  private handleMessage(message: any) {
    switch (message.type) {
      case 'job_status_update':
        // Emit event for job status updates
        window.dispatchEvent(new CustomEvent('jobStatusUpdate', { detail: message }));
        break;
      case 'payment_completed':
        // Emit event for payment updates
        window.dispatchEvent(new CustomEvent('paymentUpdate', { detail: message }));
        break;
      case 'document_processed':
        // Emit event for document updates
        window.dispatchEvent(new CustomEvent('documentUpdate', { detail: message }));
        break;
    }
  }
  
  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, Math.pow(2, this.reconnectAttempts) * 1000);
    }
  }
}
```

## 7. Performance Optimization

### A. Data Caching Strategy
```typescript
// Implement React Query for data caching
import { useQuery, useMutation, useQueryClient } from 'react-query';

// Cache dashboard data
const useDashboardStats = () => {
  return useQuery(
    'dashboardStats',
    customerDashboardApi.getDashboardStats,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false
    }
  );
};

// Cache jobs data with filters
const useCustomerJobs = (filters: JobFilters) => {
  return useQuery(
    ['customerJobs', filters],
    () => customerJobsApi.getJobs(filters),
    {
      staleTime: 2 * 60 * 1000, // 2 minutes
      keepPreviousData: true
    }
  );
};
```

### B. Pagination Implementation
```typescript
// Implement cursor-based pagination
const useInfiniteJobs = (filters: JobFilters) => {
  return useInfiniteQuery(
    ['customerJobs', filters],
    ({ pageParam = null }) => 
      customerJobsApi.getJobs({ ...filters, cursor: pageParam, limit: 20 }),
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
      staleTime: 2 * 60 * 1000
    }
  );
};
```

## 8. Security Considerations

### A. API Security
```typescript
// Implement request interceptors for security
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
});

// Request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await authApi.refreshToken();
          localStorage.setItem('auth_token', response.access_token);
          // Retry original request
          return apiClient.request(error.config);
        }
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

## 9. Testing Strategy for Real Data

### A. API Integration Tests
```typescript
// Test real API endpoints
describe('Customer Jobs API', () => {
  beforeEach(() => {
    // Set up test authentication
    localStorage.setItem('auth_token', 'test_token');
  });
  
  it('should fetch customer jobs', async () => {
    const jobs = await customerJobsApi.getJobs();
    expect(jobs).toBeInstanceOf(Array);
    expect(jobs[0]).toHaveProperty('reference');
    expect(jobs[0]).toHaveProperty('icsStatus');
  });
  
  it('should handle API errors gracefully', async () => {
    // Mock API error
    jest.spyOn(customerJobsApi, 'getJobs').mockRejectedValue(new Error('API Error'));
    
    await expect(customerJobsApi.getJobs()).rejects.toThrow('API Error');
  });
});
```

### B. Component Integration Tests
```typescript
// Test components with real data
describe('CustomerPortalDashboard', () => {
  it('should display real dashboard data', async () => {
    const mockStats = {
      activeJobs: 5,
      awaitingClearance: 2,
      completedThisYear: 15,
      pendingPayments: '$1,250.00'
    };
    
    jest.spyOn(customerDashboardApi, 'getDashboardStats').mockResolvedValue(mockStats);
    
    render(<CustomerPortalDashboard customer={mockCustomer} />);
    
    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('Active Jobs')).toBeInTheDocument();
    });
  });
});
```

This comprehensive real data integration plan ensures the customer portal will function with live backend data, providing customers with accurate, real-time information about their customs clearance jobs, payments, and documents.