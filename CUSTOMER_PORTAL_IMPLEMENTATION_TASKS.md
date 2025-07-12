# Customer Portal Implementation Tasks

## Overview

This document provides a comprehensive, step-by-step task list for implementing the customer portal based on the specifications in the following guardrail documents:

- **CUSTOMER_PORTAL_SPECIFICATION.md** - Overall requirements and architecture
- **COMPONENT_REFACTORING_PLAN.md** - Component structure and refactoring strategy  
- **FILE_PRUNING_GUIDE_UPDATED.md** - File management and cleanup strategy
- **REAL_DATA_INTEGRATION_REQUIREMENTS.md** - API and data integration requirements

## Phase 1: Project Setup and File Management

### Task 1.1: Create Backup and Setup Branch
```powershell
# Create backup of current state
git add .
git commit -m "Backup before customer portal implementation"
git branch customer-portal-backup

# Create new feature branch
git checkout -b feature/customer-portal-implementation
```

### Task 1.2: Remove Customer Portal Incompatible Files
**Guardrail Reference**: FILE_PRUNING_GUIDE_UPDATED.md - Section 3

```powershell
# Remove LOA and EDI components (replace with Jobs System)
Remove-Item "frontend/src/components/loa/LOACreator.tsx" -Force
Remove-Item "frontend/src/components/edi/EDIJobRegistration.tsx" -Force

# Remove customer portal incompatible pages
Remove-Item "frontend/src/pages/DocumentDetailPage.tsx" -Force
Remove-Item "frontend/src/pages/EDIDetailPage.tsx" -Force
Remove-Item "frontend/src/pages/EDIPage.tsx" -Force
Remove-Item "frontend/src/pages/LOADetailPage.tsx" -Force
Remove-Item "frontend/src/pages/LOAPage.tsx" -Force
Remove-Item "frontend/src/pages/SettingsPage.tsx" -Force

# Remove customer portal incompatible types
Remove-Item "frontend/src/types/compliance.ts" -Force
Remove-Item "frontend/src/types/edi.ts" -Force
Remove-Item "frontend/src/types/loa.ts" -Force

# Remove old test files that need replacement
Remove-Item "frontend/src/__tests__/integration/user-workflows.test.tsx" -Force
```

### Task 1.3: Create Portal Directory Structure
**Guardrail Reference**: COMPONENT_REFACTORING_PLAN.md - Section 3

```powershell
# Create portal component directories
New-Item -ItemType Directory -Path "frontend/src/components/portal" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/layout" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/dashboard" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/jobs" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/booking" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/documents" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/payments" -Force
New-Item -ItemType Directory -Path "frontend/src/components/portal/support" -Force

# Create portal pages directory
New-Item -ItemType Directory -Path "frontend/src/pages/portal" -Force

# Create portal services directory
New-Item -ItemType Directory -Path "frontend/src/services/portal" -Force

# Create portal types directory
New-Item -ItemType Directory -Path "frontend/src/types/portal" -Force

# Create portal styles directory
New-Item -ItemType Directory -Path "frontend/src/styles/portal" -Force
```

### Task 1.4: Create Index Files for New Directories
```powershell
# Create index files for portal components
@"
// Portal Layout Components
export { default as PortalLayout } from './PortalLayout';
export { default as PortalHeader } from './PortalHeader';
export { default as PortalNavigation } from './PortalNavigation';
export { default as PortalSidebar } from './PortalSidebar';
"@ | Out-File -FilePath "frontend/src/components/portal/layout/index.ts" -Encoding UTF8

@"
// Portal Dashboard Components
export { default as CustomerPortalDashboard } from './CustomerPortalDashboard';
export { default as StatCard } from './StatCard';
export { default as RecentActivityFeed } from './RecentActivityFeed';
export { default as QuickActionsSidebar } from './QuickActionsSidebar';
"@ | Out-File -FilePath "frontend/src/components/portal/dashboard/index.ts" -Encoding UTF8

@"
// Portal Jobs Components
export { default as JobsListView } from './JobsListView';
export { default as JobCard } from './JobCard';
export { default as JobStatusBadge } from './JobStatusBadge';
export { default as JobDetailsModal } from './JobDetailsModal';
export { default as CustomsDeclarationView } from './CustomsDeclarationView';
export { default as LineItemsTable } from './LineItemsTable';
export { default as JobFilters } from './JobFilters';
"@ | Out-File -FilePath "frontend/src/components/portal/jobs/index.ts" -Encoding UTF8

@"
// Portal Services
export * from './customerJobsApi';
export * from './customerPaymentsApi';
export * from './customerSupportApi';
export * from './customerDashboardApi';
"@ | Out-File -FilePath "frontend/src/services/portal/index.ts" -Encoding UTF8

@"
// Portal Types
export * from './jobs';
export * from './payments';
export * from './dashboard';
export * from './support';
"@ | Out-File -FilePath "frontend/src/types/portal/index.ts" -Encoding UTF8
```

## Phase 2: Portal Styling and Theme Setup

### Task 2.1: Create Portal CSS Variables and Base Styles
**Guardrail Reference**: CUSTOMER_PORTAL_SPECIFICATION.md - Section 1, COMPONENT_REFACTORING_PLAN.md - Section 4

```powershell
# Create portal theme CSS
@"
/* Portal Theme Variables */
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
"@ | Out-File -FilePath "frontend/src/styles/portal/theme.css" -Encoding UTF8

# Create portal base styles
@"
/* Portal Base Styles */
.portal-layout {
  min-height: 100vh;
  background: var(--portal-background);
  font-family: Arial, sans-serif;
}

.portal-header {
  background: var(--portal-primary);
  color: white;
  height: var(--portal-header-height);
  box-shadow: var(--portal-shadow);
}

.portal-navigation {
  background: #2c5282;
  height: var(--portal-nav-height);
}

.portal-main {
  display: grid;
  grid-template-columns: var(--portal-sidebar-width) 1fr;
  gap: 25px;
  max-width: 1400px;
  margin: 20px auto;
  padding: 0 20px;
}

.portal-sidebar {
  background: white;
  border-radius: 12px;
  box-shadow: var(--portal-shadow);
  height: fit-content;
  position: sticky;
  top: 20px;
}

.portal-content {
  background: white;
  border-radius: 12px;
  box-shadow: var(--portal-shadow);
  overflow: hidden;
}

@media (max-width: 1024px) {
  .portal-main {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .portal-sidebar {
    position: static;
  }
}
"@ | Out-File -FilePath "frontend/src/styles/portal/layout.css" -Encoding UTF8

# Create main portal CSS file
@"
/* Portal Main Stylesheet */
@import './theme.css';
@import './layout.css';
@import './components.css';
@import './responsive.css';
"@ | Out-File -FilePath "frontend/src/styles/portal/portal.css" -Encoding UTF8
```

### Task 2.2: Create Component-Specific Styles
```powershell
# Create component styles
@"
/* Portal Component Styles */

/* Stat Cards */
.stat-card {
  color: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.orange {
  background: linear-gradient(135deg, #ff6b35 0%, #e55a2b 100%);
}

.stat-card.blue {
  background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
}

.stat-card.green {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
}

.stat-card.purple {
  background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
}

/* Job Status Badges */
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-processing {
  background: #fff3cd;
  color: #856404;
}

.status-cleared {
  background: #d4edda;
  color: #155724;
}

.status-pending {
  background: #f8d7da;
  color: #721c24;
}

.status-documents {
  background: #d1ecf1;
  color: #0c5460;
}

/* Navigation */
.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 15px 20px;
  display: block;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.nav-link:hover,
.nav-link.active {
  background: var(--portal-secondary);
  border-bottom-color: #e55a2b;
}

/* Buttons */
.btn-portal {
  background: var(--portal-secondary);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-portal:hover {
  background: #e55a2b;
  transform: translateY(-1px);
}
"@ | Out-File -FilePath "frontend/src/styles/portal/components.css" -Encoding UTF8

# Create responsive styles
@"
/* Portal Responsive Styles */
@media (max-width: 768px) {
  .portal-header .container {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .portal-navigation .nav-links {
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .portal-content .content-header,
  .portal-content .content-body {
    padding: 20px;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .portal-main {
    padding: 0 10px;
  }
}
"@ | Out-File -FilePath "frontend/src/styles/portal/responsive.css" -Encoding UTF8
```

## Phase 3: Portal Type Definitions

### Task 3.1: Create Portal Type Definitions
**Guardrail Reference**: REAL_DATA_INTEGRATION_REQUIREMENTS.md - Section 2, COMPONENT_REFACTORING_PLAN.md - Section 5

```powershell
# Create dashboard types
@"
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

export interface CustomerNotification {
  id: string;
  type: string;
  title: string;
  message: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  readAt?: string;
  createdAt: string;
}
"@ | Out-File -FilePath "frontend/src/types/portal/dashboard.ts" -Encoding UTF8

# Create jobs types
@"
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

export interface JobDocument {
  id: string;
  filename: string;
  category: string;
  uploadDate: string;
  size: number;
}

export type CustomerJobAction = 'cancel' | 'request_update' | 'add_documents';
"@ | Out-File -FilePath "frontend/src/types/portal/jobs.ts" -Encoding UTF8

# Create payments types
@"
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

export interface PaymentFilters {
  status?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface PaymentRequest {
  paymentMethod: string;
  returnUrl: string;
  cancelUrl: string;
}

export interface PaymentResult {
  success: boolean;
  paymentId?: string;
  redirectUrl?: string;
  error?: string;
}

export interface PaymentBreakdown {
  customsValue: number;
  freightInsurance: number;
  cifValue: number;
  customsDuty: number;
  gst: number;
  processingFee: number;
  totalAmount: number;
  exchangeRate: number;
}
"@ | Out-File -FilePath "frontend/src/types/portal/payments.ts" -Encoding UTF8

# Create support types
@"
export interface SupportTicket {
  id: string;
  ticketNumber: string;
  subject: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  createdAt: string;
  updatedAt: string;
}

export interface SupportTicketRequest {
  subject: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category?: string;
}

export interface TicketMessage {
  id: string;
  ticketId: string;
  message: string;
  sender: string;
  createdAt: string;
}

export interface SupportContactInfo {
  email: string;
  phone: string;
  hours: string;
  address: string;
}
"@ | Out-File -FilePath "frontend/src/types/portal/support.ts" -Encoding UTF8
```

## Phase 4: Portal Layout Components

### Task 4.1: Create Portal Layout Components
**Guardrail Reference**: COMPONENT_REFACTORING_PLAN.md - Section 3.A

```powershell
# Create PortalLayout component
@"
import React from 'react';
import { Outlet } from 'react-router-dom';
import PortalHeader from './PortalHeader';
import PortalNavigation from './PortalNavigation';
import PortalSidebar from './PortalSidebar';
import '../../../styles/portal/portal.css';

const PortalLayout: React.FC = () => {
  return (
    <div className="portal-layout">
      <PortalHeader />
      <PortalNavigation />
      <div className="portal-main">
        <PortalSidebar />
        <main className="portal-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default PortalLayout;
"@ | Out-File -FilePath "frontend/src/components/portal/layout/PortalLayout.tsx" -Encoding UTF8

# Create PortalHeader component
@"
import React from 'react';
import { useAuth } from '../../../hooks/useAuth';

const PortalHeader: React.FC = () => {
  const { customer, logout } = useAuth();

  return (
    <header className="portal-header">
      <div className="container mx-auto px-4 flex justify-between items-center h-full">
        <div className="logo text-2xl font-bold">
          <span className="text-orange-500">Cargo</span>clear International
        </div>
        <div className="user-info flex items-center gap-4">
          <div className="text-right">
            <div className="font-semibold">{customer?.first_name} {customer?.last_name}</div>
            <div className="text-sm opacity-75">Customer ID: {customer?.id}</div>
          </div>
          <div className="user-avatar w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center font-bold">
            {customer?.first_name?.[0]}{customer?.last_name?.[0]}
          </div>
          <button 
            onClick={logout}
            className="btn-portal btn-sm"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default PortalHeader;
"@ | Out-File -FilePath "frontend/src/components/portal/layout/PortalHeader.tsx" -Encoding UTF8

# Create PortalNavigation component
@"
import React from 'react';
import { NavLink } from 'react-router-dom';

const PortalNavigation: React.FC = () => {
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
      <div className="container mx-auto px-4">
        <ul className="flex gap-0">
          {navItems.map(item => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => 
                  `nav-link ${isActive ? 'active' : ''}`
                }
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default PortalNavigation;
"@ | Out-File -FilePath "frontend/src/components/portal/layout/PortalNavigation.tsx" -Encoding UTF8

# Create PortalSidebar component
@"
import React from 'react';
import { useNavigate } from 'react-router-dom';

const PortalSidebar: React.FC = () => {
  const navigate = useNavigate();

  const quickActions = [
    { label: 'New Clearance', icon: '📋', action: () => navigate('/booking') },
    { label: 'Book Consultation', icon: '💬', action: () => navigate('/booking?type=consultation') },
    { label: 'Upload Documents', icon: '📄', action: () => navigate('/documents') },
    { label: 'Track Shipment', icon: '📍', action: () => alert('Track shipment functionality') },
    { label: 'Pay Duties', icon: '💳', action: () => navigate('/payments') },
    { label: 'Contact Support', icon: '📧', action: () => navigate('/support') },
  ];

  return (
    <aside className="portal-sidebar">
      <div className="p-5 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">Quick Actions</h3>
      </div>
      <ul className="p-0 m-0 list-none">
        {quickActions.map((action, index) => (
          <li key={index} className="border-b border-gray-100 last:border-b-0">
            <button
              onClick={action.action}
              className="w-full text-left p-4 flex items-center gap-3 hover:bg-orange-50 hover:text-orange-600 transition-colors"
            >
              <span className="text-lg">{action.icon}</span>
              {action.label}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default PortalSidebar;
"@ | Out-File -FilePath "frontend/src/components/portal/layout/PortalSidebar.tsx" -Encoding UTF8
```

## Phase 5: Portal Service APIs

### Task 5.1: Create Customer Portal APIs
**Guardrail Reference**: REAL_DATA_INTEGRATION_REQUIREMENTS.md - Section 2

```powershell
# Create customer jobs API
@"
import { httpClient } from '../api';
import type { CustomsJob, JobFilters, JobCreateRequest, CustomsDeclaration, LineItem, CustomerJobAction } from '../../types/portal/jobs';
import type { Document } from '../../types/documents';

export const customerJobsApi = {
  async getJobs(filters?: JobFilters): Promise<CustomsJob[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (typeof value === 'object') {
            params.append(key, JSON.stringify(value));
          } else {
            params.append(key, String(value));
          }
        }
      });
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return httpClient.get<CustomsJob[]>(`/customer/jobs${query}`);
  },

  async getJob(jobId: string): Promise<CustomsJob> {
    return httpClient.get<CustomsJob>(`/customer/jobs/${jobId}`);
  },

  async createJob(data: JobCreateRequest): Promise<CustomsJob> {
    return httpClient.post<CustomsJob>('/customer/jobs', data);
  },

  async getJobDeclaration(jobId: string): Promise<CustomsDeclaration> {
    return httpClient.get<CustomsDeclaration>(`/customer/jobs/${jobId}/declaration`);
  },

  async getJobLineItems(jobId: string): Promise<LineItem[]> {
    return httpClient.get<LineItem[]>(`/customer/jobs/${jobId}/line-items`);
  },

  async updateJobStatus(jobId: string, action: CustomerJobAction): Promise<CustomsJob> {
    return httpClient.put<CustomsJob>(`/customer/jobs/${jobId}/status`, { action });
  },

  async uploadJobDocuments(jobId: string, files: File[]): Promise<Document[]> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('jobId', jobId);
    return httpClient.upload<Document[]>(`/customer/jobs/${jobId}/documents`, formData);
  },

  async getJobDocuments(jobId: string): Promise<Document[]> {
    return httpClient.get<Document[]>(`/customer/jobs/${jobId}/documents`);
  }
};
"@ | Out-File -FilePath "frontend/src/services/portal/customerJobsApi.ts" -Encoding UTF8

# Create customer dashboard API
@"
import { httpClient } from '../api';
import type { DashboardStats, ActivityItem, CustomerNotification } from '../../types/portal/dashboard';

export const customerDashboardApi = {
  async getDashboardStats(): Promise<DashboardStats> {
    return httpClient.get<DashboardStats>('/customer/dashboard/stats');
  },

  async getRecentActivity(limit?: number): Promise<ActivityItem[]> {
    const params = limit ? `?limit=${limit}` : '';
    return httpClient.get<ActivityItem[]>(`/customer/dashboard/activity${params}`);
  },

  async getNotifications(): Promise<CustomerNotification[]> {
    return httpClient.get<CustomerNotification[]>('/customer/notifications');
  },

  async markNotificationRead(notificationId: string): Promise<void> {
    return httpClient.put<void>(`/customer/notifications/${notificationId}/read`);
  }
};
"@ | Out-File -FilePath "frontend/src/services/portal/customerDashboardApi.ts" -Encoding UTF8

# Create customer payments API
@"
import { httpClient } from '../api';
import type { 
  OutstandingPayment, 
  Payment, 
  PaymentFilters, 
  PaymentRequest, 
  PaymentResult, 
  PaymentBreakdown 
} from '../../types/portal/payments';

export const customerPaymentsApi = {
  async getOutstandingPayments(): Promise<OutstandingPayment[]> {
    return httpClient.get<OutstandingPayment[]>('/customer/payments/outstanding');
  },

  async getPaymentHistory(filters?: PaymentFilters): Promise<Payment[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (typeof value === 'object') {
            params.append(key, JSON.stringify(value));
          } else {
            params.append(key, String(value));
          }
        }
      });
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return httpClient.get<Payment[]>(`/customer/payments/history${query}`);
  },

  async processJobPayment(jobId: string, paymentData: PaymentRequest): Promise<PaymentResult> {
    return httpClient.post<PaymentResult>(`/customer/jobs/${jobId}/payment`, paymentData);
  },

  async processBulkPayment(jobIds: string[], paymentData: PaymentRequest): Promise<PaymentResult> {
    return httpClient.post<PaymentResult>('/customer/payments/bulk', {
      jobIds,
      ...paymentData
    });
  },

  async getPaymentReceipt(paymentId: string): Promise<Blob> {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customer/payments/${paymentId}/receipt`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to download receipt');
    }
    
    return response.blob();
  },

  async getPaymentBreakdown(jobId: string): Promise<PaymentBreakdown> {
    return httpClient.get<PaymentBreakdown>(`/customer/jobs/${jobId}/payment-breakdown`);
  }
};
"@ | Out-File -FilePath "frontend/src/services/portal/customerPaymentsApi.ts" -Encoding UTF8

# Create customer support API
@"
import { httpClient } from '../api';
import type { 
  SupportTicket, 
  SupportTicketRequest, 
  TicketMessage, 
  SupportContactInfo 
} from '../../types/portal/support';

export const customerSupportApi = {
  async createTicket(data: SupportTicketRequest): Promise<SupportTicket> {
    return httpClient.post<SupportTicket>('/customer/support/tickets', data);
  },

  async getTickets(): Promise<SupportTicket[]> {
    return httpClient.get<SupportTicket[]>('/customer/support/tickets');
  },

  async getTicket(ticketId: string): Promise<SupportTicket> {
    return httpClient.get<SupportTicket>(`/customer/support/tickets/${