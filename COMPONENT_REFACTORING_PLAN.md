# Component Refactoring Plan - Customer Portal Implementation

## Overview

This document outlines the detailed plan for refactoring existing React components and creating new ones to implement the customer portal based on the HTML specification.

## 1. Files to Remove (Not Needed in Customer Portal)

### Complete Directories to Remove:
```
frontend/src/components/ai-assistant/
├── ConversationalInterface.tsx
├── DocumentAnalysisPanel.tsx

frontend/src/components/broker-review/
├── BrokerReviewDashboard.tsx
├── ComplianceChecker.tsx
├── DocumentProcessingQueue.tsx
├── DutyCalculationPanel.tsx
├── EntryCompiler.tsx
├── index.ts
├── OCRReviewPanel.tsx

frontend/src/components/export-tariffs/
├── AHECCTreeBrowser.tsx
├── ExportRequirementsPanel.tsx
├── MarketAccessDashboard.tsx

frontend/src/components/tariff/
├── index.ts
├── TariffDisplay.tsx
├── TariffTreeView.tsx

frontend/src/components/tariff-tree/
├── InteractiveTariffTree.tsx
├── TariffComparisonPanel.tsx
├── TariffDetailPanel.tsx
├── TreeNavigation.tsx

frontend/src/components/duty/
├── CountrySelector.tsx
├── DutyCalculator.tsx
├── DutyCalculatorForm.tsx
├── DutyResults.tsx
├── DutyResultsDisplay.tsx
├── HsCodeLookup.tsx
├── index.ts
├── __tests__/
```

### Individual Files to Remove:
```
frontend/src/components/loa/LOACreator.tsx
frontend/src/components/edi/EDIJobRegistration.tsx
frontend/src/components/search/SearchForm.tsx
frontend/src/components/search/SearchResults.tsx
frontend/src/components/search/index.ts
frontend/src/components/search/__tests__/

frontend/src/pages/TariffTree.tsx
frontend/src/pages/ExportTariffs.tsx
frontend/src/pages/BrokerReviewPage.tsx
frontend/src/pages/AIAssistant.tsx
frontend/src/pages/Compliance.tsx
frontend/src/pages/CompliancePage.tsx
frontend/src/pages/Reports.tsx
frontend/src/pages/LOAPage.tsx
frontend/src/pages/LOADetailPage.tsx
frontend/src/pages/EDIPage.tsx
frontend/src/pages/EDIDetailPage.tsx

frontend/src/services/aiApi.ts
frontend/src/services/complianceApi.ts
frontend/src/services/dutyCalculatorApi.ts
frontend/src/services/exportApi.ts
frontend/src/services/newsApi.ts
frontend/src/services/reportsApi.ts
frontend/src/services/rulingsApi.ts
frontend/src/services/searchApi.ts
frontend/src/services/tariffApi.ts

frontend/src/types/compliance.ts
frontend/src/types/edi.ts
frontend/src/types/loa.ts
```

## 2. Files to Refactor (Major Changes)

### A. Core Application Files

#### `frontend/src/App.tsx`
**Current State**: Basic view switching with mock authentication
**Refactor Plan**:
- Remove all existing view logic
- Implement proper React Router integration
- Add portal layout wrapper
- Implement authentication guard
- Add error boundary

**New Structure**:
```typescript
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ErrorBoundary>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/*" element={
              <ProtectedRoute>
                <PortalLayout />
              </ProtectedRoute>
            } />
          </Routes>
        </ErrorBoundary>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

#### `frontend/src/router/AppRouter.tsx`
**Current State**: Complex routing with many broker-specific routes
**Refactor Plan**:
- Simplify to customer portal routes only
- Remove all broker/admin routes
- Update route structure to match portal navigation

**New Routes**:
```typescript
const customerRoutes = [
  { path: '/', element: <Navigate to="/dashboard" /> },
  { path: '/dashboard', element: <CustomerPortalDashboard /> },
  { path: '/jobs', element: <JobsListView /> },
  { path: '/jobs/:id', element: <JobDetailsView /> },
  { path: '/booking', element: <NewBookingSection /> },
  { path: '/documents', element: <DocumentManagement /> },
  { path: '/payments', element: <PaymentsDashboard /> },
  { path: '/support', element: <SupportCenter /> },
  { path: '/profile', element: <ProfileSettings /> },
];
```

### B. Authentication Components

#### `frontend/src/components/auth/LoginForm.tsx`
**Current State**: Basic styling with SSO options
**Refactor Plan**:
- Update styling to match portal theme (navy/orange)
- Simplify SSO options (keep only Google, Microsoft)
- Add Cargoclear branding
- Improve responsive design

**Key Changes**:
```typescript
// Update color scheme
const portalTheme = {
  primary: '#1e3a5f',
  secondary: '#ff6b35',
  background: '#f8f9fa'
};

// Add Cargoclear logo and branding
const LoginHeader = () => (
  <div className="text-center mb-8">
    <div className="text-3xl font-bold text-portal-primary">
      <span className="text-portal-secondary">Cargo</span>clear International
    </div>
    <p className="text-portal-text-light mt-2">Customer Portal</p>
  </div>
);
```

#### `frontend/src/components/auth/RegisterForm.tsx`
**Current State**: Basic registration form
**Refactor Plan**:
- Match LoginForm styling updates
- Add company information fields
- Add terms and conditions acceptance
- Improve validation

### C. Dashboard Component

#### `frontend/src/components/dashboard/CustomerDashboard.tsx`
**Current State**: Generic dashboard with mock stats
**Refactor Plan**: Complete rewrite to match HTML portal design

**New Component Structure**:
```typescript
interface CustomerPortalDashboardProps {
  customer: Customer;
}

const CustomerPortalDashboard: React.FC<CustomerPortalDashboardProps> = ({ customer }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  
  return (
    <div className="portal-dashboard">
      <DashboardHeader customer={customer} />
      <StatsGrid stats={stats} />
      <div className="dashboard-content">
        <RecentActivityFeed activities={recentActivity} />
        <QuickActionsSidebar />
      </div>
    </div>
  );
};
```

### D. Document Components

#### `frontend/src/components/documents/DocumentUpload.tsx`
**Current State**: Basic file upload
**Refactor Plan**: Transform into comprehensive document management

**New Features**:
- Job association for documents
- Document categorization
- Drag & drop upload zone
- Document preview
- Bulk operations

## 3. New Components to Create

### A. Layout Components

#### `frontend/src/components/portal/layout/PortalLayout.tsx`
```typescript
interface PortalLayoutProps {
  children: React.ReactNode;
}

const PortalLayout: React.FC<PortalLayoutProps> = ({ children }) => {
  return (
    <div className="portal-layout">
      <PortalHeader />
      <PortalNavigation />
      <div className="portal-main">
        <PortalSidebar />
        <main className="portal-content">
          {children}
        </main>
      </div>
    </div>
  );
};
```

#### `frontend/src/components/portal/layout/PortalHeader.tsx`
```typescript
const PortalHeader: React.FC = () => {
  const { customer, logout } = useAuth();
  
  return (
    <header className="portal-header">
      <div className="portal-header-container">
        <PortalLogo />
        <UserInfo customer={customer} onLogout={logout} />
      </div>
    </header>
  );
};
```

#### `frontend/src/components/portal/layout/PortalNavigation.tsx`
```typescript
const PortalNavigation: React.FC = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/jobs', label: 'My Jobs', icon: '📋' },
    { path: '/booking', label: 'New Booking', icon: '➕' },
    { path: '/documents', label: 'Documents', icon: '📄' },
    { path: '/payments', label: 'Payments', icon: '💳' },
    { path: '/support', label: 'Support', icon: '🎧' },
  ];
  
  return (
    <nav className="portal-navigation">
      <div className="nav-container">
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};
```

#### `frontend/src/components/portal/layout/PortalSidebar.tsx`
```typescript
const PortalSidebar: React.FC = () => {
  const quickActions = [
    { label: 'New Clearance', icon: '📋', action: 'booking' },
    { label: 'Book Consultation', icon: '💬', action: 'consultation' },
    { label: 'Upload Documents', icon: '📄', action: 'upload' },
    { label: 'Track Shipment', icon: '📍', action: 'track' },
    { label: 'Pay Duties', icon: '💳', action: 'payment' },
    { label: 'Contact Support', icon: '📧', action: 'support' },
  ];
  
  return (
    <aside className="portal-sidebar">
      <div className="sidebar-header">
        <h3>Quick Actions</h3>
      </div>
      <ul className="sidebar-menu">
        {quickActions.map(action => (
          <QuickActionItem key={action.action} {...action} />
        ))}
      </ul>
    </aside>
  );
};
```

### B. Dashboard Components

#### `frontend/src/components/portal/dashboard/StatCard.tsx`
```typescript
interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: 'orange' | 'blue' | 'green' | 'purple';
  onClick?: () => void;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, onClick }) => {
  const colorClasses = {
    orange: 'bg-gradient-to-br from-orange-500 to-orange-600',
    blue: 'bg-gradient-to-br from-blue-600 to-blue-700',
    green: 'bg-gradient-to-br from-green-500 to-green-600',
    purple: 'bg-gradient-to-br from-purple-500 to-purple-600',
  };
  
  return (
    <div 
      className={`stat-card ${colorClasses[color]} ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-title">{title}</div>
    </div>
  );
};
```

#### `frontend/src/components/portal/dashboard/RecentActivityFeed.tsx`
```typescript
interface RecentActivityFeedProps {
  activities: ActivityItem[];
}

const RecentActivityFeed: React.FC<RecentActivityFeedProps> = ({ activities }) => {
  return (
    <div className="activity-feed">
      <div className="activity-header">
        <h3>Recent Activity</h3>
      </div>
      <div className="activity-list">
        {activities.map(activity => (
          <ActivityItem key={activity.id} activity={activity} />
        ))}
      </div>
    </div>
  );
};
```

### C. Jobs Components

#### `frontend/src/components/portal/jobs/JobsListView.tsx`
```typescript
const JobsListView: React.FC = () => {
  const [jobs, setJobs] = useState<CustomsJob[]>([]);
  const [filters, setFilters] = useState<JobFilters>({});
  const [loading, setLoading] = useState(true);
  
  return (
    <div className="jobs-list-view">
      <JobsHeader onNewJob={() => navigate('/booking')} />
      <JobsFilters filters={filters} onChange={setFilters} />
      <JobsTable jobs={jobs} loading={loading} />
    </div>
  );
};
```

#### `frontend/src/components/portal/jobs/JobDetailsModal.tsx`
```typescript
interface JobDetailsModalProps {
  jobId: string;
  isOpen: boolean;
  onClose: () => void;
}

const JobDetailsModal: React.FC<JobDetailsModalProps> = ({ jobId, isOpen, onClose }) => {
  const [job, setJob] = useState<CustomsJob | null>(null);
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalHeader>
        <h2>Customs Declaration - Job {job?.reference}</h2>
        <JobStatusBadge status={job?.icsStatus} />
      </ModalHeader>
      <ModalBody>
        <CustomsDeclarationView job={job} />
        <LineItemsTable items={job?.lineItems} />
        <DutyCalculationBreakdown job={job} />
        <PaymentSection job={job} />
      </ModalBody>
    </Modal>
  );
};
```

### D. Booking Components

#### `frontend/src/components/portal/booking/NewBookingSection.tsx`
```typescript
const NewBookingSection: React.FC = () => {
  const [selectedService, setSelectedService] = useState<'clearance' | 'consultation' | null>(null);
  
  return (
    <div className="booking-section">
      <BookingHeader />
      <ServiceSelector 
        selected={selectedService} 
        onSelect={setSelectedService} 
      />
      <ServiceFeatures />
      {selectedService && (
        <BookingForm serviceType={selectedService} />
      )}
    </div>
  );
};
```

### E. Payment Components

#### `frontend/src/components/portal/payments/PaymentsDashboard.tsx`
```typescript
const PaymentsDashboard: React.FC = () => {
  const [outstandingPayments, setOutstandingPayments] = useState<OutstandingPayment[]>([]);
  const [paymentHistory, setPaymentHistory] = useState<Payment[]>([]);
  
  return (
    <div className="payments-dashboard">
      <PaymentsHeader />
      <OutstandingPaymentsSection payments={outstandingPayments} />
      <PaymentHistorySection history={paymentHistory} />
    </div>
  );
};
```

## 4. Styling Strategy

### A. CSS Architecture
```
frontend/src/styles/
├── portal/
│   ├── base.css          # Portal-specific base styles
│   ├── components.css    # Component-specific styles
│   ├── layout.css        # Layout and grid styles
│   ├── theme.css         # Color scheme and variables
│   └── responsive.css    # Mobile/tablet responsive styles
├── components/
│   ├── dashboard.css
│   ├── jobs.css
│   ├── payments.css
│   └── modals.css
└── portal.css            # Main portal stylesheet
```

### B. CSS Variables
```css
:root {
  /* Portal Colors */
  --portal-primary: #1e3a5f;
  --portal-secondary: #ff6b35;
  --portal-background: #f8f9fa;
  --portal-surface: #ffffff;
  
  /* Status Colors */
  --portal-success: #28a745;
  --portal-warning: #ffc107;
  --portal-error: #dc3545;
  --portal-info: #17a2b8;
  
  /* Text Colors */
  --portal-text: #333333;
  --portal-text-light: #6c757d;
  --portal-text-muted: #adb5bd;
  
  /* Border and Shadow */
  --portal-border: #e9ecef;
  --portal-border-light: #f1f3f4;
  --portal-shadow: 0 2px 10px rgba(0,0,0,0.1);
  --portal-shadow-lg: 0 4px 20px rgba(0,0,0,0.15);
  
  /* Layout */
  --portal-sidebar-width: 280px;
  --portal-header-height: 70px;
  --portal-nav-height: 60px;
}
```

## 5. Type Definitions

### A. New Type Files to Create

#### `frontend/src/types/portal.ts`
```typescript
export interface DashboardStats {
  activeJobs: number;
  awaitingClearance: number;
  completedThisYear: number;
  pendingPayments: string;
}

export interface ActivityItem {
  id: string;
  type: 'clearance' | 'consultation' | 'payment' | 'document';
  title: string;
  description: string;
  date: string;
  status: 'processing' | 'cleared' | 'pending' | 'documents';
}

export interface CustomsJob {
  id: string;
  reference: string;
  serviceType: 'Import Clearance' | 'Export Clearance' | 'Consultation';
  description: string;
  icsStatus: string;
  dateCreated: string;
  customsValue: number;
  dutyAmount: number;
  gstAmount: number;
  totalAmount: number;
  lineItems: LineItem[];
  documents: JobDocument[];
}

export interface LineItem {
  lineNumber: number;
  hsCode: string;
  description: string;
  quantity: number;
  value: number;
  dutyRate: string;
  dutyAmount: number;
  concessions: string[];
}

export interface OutstandingPayment {
  id: string;
  jobId: string;
  jobReference: string;
  customsDuty: number;
  gst: number;
  processingFee: number;
  totalAmount: number;
  dueDate: string;
}

export interface Payment {
  id: string;
  jobReference: string;
  amount: number;
  paymentType: string;
  status: 'completed' | 'pending' | 'failed';
  paymentDate: string;
  receiptUrl?: string;
}
```

#### `frontend/src/types/jobs.ts`
```typescript
export interface JobFilters {
  status?: string;
  serviceType?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface JobCreateRequest {
  serviceType: 'clearance' | 'consultation';
  description: string;
  documents?: File[];
  urgency?: 'standard' | 'urgent';
  specialInstructions?: string;
}

export interface CustomsDeclaration {
  idn: string;
  icsReference: string;
  abfAssessment: string;
  declarationDate: string;
  portOfEntry: string;
  countryOfOrigin: string;
  supplier: string;
  consignee: string;
  customsValue: number;
  freightInsurance: number;
  cifValue: number;
  exchangeRate: number;
  treatmentCode: string;
  appliedConcessions: string[];
}
```

## 6. API Service Updates

### A. New Service Files

#### `frontend/src/services/customerJobsApi.ts`
```typescript
export const customerJobsApi = {
  async getJobs(filters?: JobFilters): Promise<CustomsJob[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, String(value));
      });
    }
    return httpClient.get(`/customer/jobs?${params.toString()}`);
  },

  async getJob(id: string): Promise<CustomsJob> {
    return httpClient.get(`/customer/jobs/${id}`);
  },

  async createJob(data: JobCreateRequest): Promise<CustomsJob> {
    return httpClient.post('/customer/jobs', data);
  },

  async getJobDeclaration(id: string): Promise<CustomsDeclaration> {
    return httpClient.get(`/customer/jobs/${id}/declaration`);
  },

  async payJobDuties(id: string, paymentData: PaymentRequest): Promise<Payment> {
    return httpClient.post(`/customer/jobs/${id}/payment`, paymentData);
  }
};
```

#### `frontend/src/services/customerPaymentsApi.ts`
```typescript
export const customerPaymentsApi = {
  async getOutstandingPayments(): Promise<OutstandingPayment[]> {
    return httpClient.get('/customer/payments/outstanding');
  },

  async getPaymentHistory(): Promise<Payment[]> {
    return httpClient.get('/customer/payments/history');
  },

  async processPayment(data: PaymentRequest): Promise<PaymentResult> {
    return httpClient.post('/customer/payments/process', data);
  },

  async downloadReceipt(paymentId: string): Promise<Blob> {
    return httpClient.getBlob(`/customer/payments/${paymentId}/receipt`);
  }
};
```

## 7. Implementation Priority

### Phase 1: Foundation (Week 1)
1. Remove unnecessary files and directories
2. Create portal layout components
3. Update authentication components styling
4. Set up new routing structure

### Phase 2: Core Features (Week 2)
1. Implement dashboard with real data integration
2. Create jobs listing and details components
3. Update document management components
4. Create payment dashboard

### Phase 3: Advanced Features (Week 3)
1. Implement booking system
2. Create support center
3. Add modal components for detailed views
4. Implement file upload enhancements

### Phase 4: Polish & Testing (Week 4)
1. Add loading states and error handling
2. Implement responsive design
3. Add animations and transitions
4. Comprehensive testing

## 8. Testing Strategy

### A. Component Testing
- Test all new portal components
- Test refactored components
- Test responsive behavior
- Test accessibility compliance

### B. Integration Testing
- Test complete user workflows
- Test API integration
- Test error scenarios
- Test performance under load

### C. E2E Testing
- Test complete customer journey
- Test payment processing
- Test document upload/download
- Test cross-browser compatibility

This refactoring plan provides a comprehensive roadmap for transforming the current React frontend into a professional customer portal that matches the HTML specification while maintaining code quality and user experience standards.