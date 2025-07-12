# Customer Portal Specification - React Frontend Update

## Executive Summary

This document outlines the comprehensive plan to transform the current React frontend into a customer portal that matches the HTML design specification provided. The new portal will focus on customs clearance job management, document handling, payments, and customer support while integrating with real backend data.

## Current State Analysis

### Existing React Frontend
- **Architecture**: Single-page application with basic routing
- **Components**: Generic dashboard, document upload, LOA creator, EDI registration
- **Navigation**: Simple tab-based navigation
- **Styling**: Tailwind CSS with basic styling
- **Data**: Mock data throughout the application
- **Authentication**: Basic login/register forms

### HTML Design Requirements
- **Brand Identity**: Cargoclear International with orange (#ff6b35) and navy (#1e3a5f) theme
- **Layout**: Professional sidebar + main content layout
- **Features**: Job management, document handling, payments, support
- **User Experience**: Modern, responsive design with clear information hierarchy

## New Customer Portal Requirements

### 1. Visual Design & Branding

#### Color Scheme
- **Primary**: Navy Blue (#1e3a5f)
- **Secondary**: Orange (#ff6b35) 
- **Background**: Light Gray (#f8f9fa)
- **Success**: Green (#28a745)
- **Warning**: Yellow (#ffc107)
- **Error**: Red (#dc3545)

#### Typography
- **Font Family**: Arial, sans-serif
- **Headers**: Bold, navy blue
- **Body**: Regular, dark gray (#333)
- **Small Text**: Light gray (#6c757d)

#### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│ Header (Logo, User Info, Logout)                       │
├─────────────────────────────────────────────────────────┤
│ Navigation Bar (Dashboard, Jobs, Booking, etc.)        │
├──────────────┬──────────────────────────────────────────┤
│ Sidebar      │ Main Content Area                        │
│ (280px)      │                                          │
│ - Quick      │ - Content Header                         │
│   Actions    │ - Content Body                           │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### 2. Core Features Implementation

#### A. Dashboard Section
**Components to Create/Update:**
- `CustomerPortalDashboard.tsx` (replace existing)
- `StatCard.tsx` (new)
- `RecentActivityFeed.tsx` (new)
- `QuickActionsSidebar.tsx` (new)

**Features:**
- Welcome message with customer name
- Statistics cards (Active Jobs, Awaiting Clearance, Completed, Pending Payments)
- Recent activity feed with job updates
- Quick actions sidebar

**Data Integration:**
```typescript
interface DashboardStats {
  activeJobs: number;
  awaitingClearance: number;
  completedThisYear: number;
  pendingPayments: string; // formatted currency
}

interface ActivityItem {
  id: string;
  type: 'clearance' | 'consultation' | 'payment' | 'document';
  title: string;
  description: string;
  date: string;
  status: 'processing' | 'cleared' | 'pending' | 'documents';
}
```

#### B. Jobs Management Section
**Components to Create:**
- `JobsListView.tsx`
- `JobCard.tsx`
- `JobStatusBadge.tsx`
- `JobDetailsModal.tsx`
- `CustomsDeclarationView.tsx`

**Features:**
- Comprehensive job listing with filtering
- Job status tracking (ICS Processing, Completed, Payment Required, etc.)
- Detailed customs declaration view
- Line items with HS codes and duty calculations
- Payment integration

**Data Models:**
```typescript
interface CustomsJob {
  id: string;
  reference: string; // CC-2025-001234
  serviceType: 'Import Clearance' | 'Export Clearance' | 'Consultation';
  description: string;
  icsStatus: string;
  dateCreated: string;
  customsValue: number;
  dutyAmount: number;
  gstAmount: number;
  totalAmount: number;
  lineItems: LineItem[];
  documents: Document[];
}

interface LineItem {
  lineNumber: number;
  hsCode: string;
  description: string;
  quantity: number;
  value: number;
  dutyRate: string;
  dutyAmount: number;
  concessions: string[];
}
```

#### C. New Booking Section
**Components to Create:**
- `BookingServiceSelector.tsx`
- `ClearanceBookingForm.tsx`
- `ConsultationBookingForm.tsx`
- `ServiceFeatureCards.tsx`

**Features:**
- Service selection (Customs Clearance vs Consultation)
- Pricing display
- Service features showcase
- Booking form integration

#### D. Documents Section
**Components to Update:**
- `DocumentManagement.tsx` (replace DocumentUpload)
- `DocumentUploadZone.tsx`
- `DocumentTable.tsx`
- `DocumentViewer.tsx`

**Features:**
- Drag & drop file upload
- Document categorization (Commercial Invoice, Packing List, etc.)
- Document association with jobs
- Download and delete functionality

#### E. Payments Section
**Components to Create:**
- `PaymentsDashboard.tsx`
- `OutstandingPayments.tsx`
- `PaymentHistory.tsx`
- `PaymentBreakdown.tsx`

**Features:**
- Outstanding duties summary
- Payment breakdown (Customs Duty, GST, Processing Fees)
- Payment history with receipts
- Bulk payment functionality

#### F. Support Section
**Components to Create:**
- `SupportCenter.tsx`
- `ContactOptions.tsx`
- `SupportTickets.tsx` (future)

**Features:**
- Multiple contact methods (Email, Phone, Live Chat)
- Knowledge base links
- Support ticket system (future enhancement)

### 3. Navigation & Routing Updates

#### New Route Structure
```typescript
// Replace current App.tsx routing with:
const routes = [
  { path: '/', component: CustomerPortalDashboard },
  { path: '/dashboard', component: CustomerPortalDashboard },
  { path: '/jobs', component: JobsListView },
  { path: '/jobs/:id', component: JobDetailsModal },
  { path: '/booking', component: NewBookingSection },
  { path: '/documents', component: DocumentManagement },
  { path: '/payments', component: PaymentsDashboard },
  { path: '/support', component: SupportCenter },
];
```

#### Navigation Components
- `PortalHeader.tsx` - Logo, user info, logout
- `PortalNavigation.tsx` - Main navigation tabs
- `PortalSidebar.tsx` - Quick actions sidebar
- `PortalLayout.tsx` - Overall layout wrapper

### 4. API Integration Requirements

#### New API Endpoints Needed

**Jobs/Clearances API:**
```typescript
// GET /api/customer/jobs
// GET /api/customer/jobs/{id}
// POST /api/customer/jobs (new booking)
// GET /api/customer/jobs/{id}/declaration
// POST /api/customer/jobs/{id}/payment
```

**Customer Dashboard API:**
```typescript
// GET /api/customer/dashboard/stats
// GET /api/customer/dashboard/activity
```

**Payments API:**
```typescript
// GET /api/customer/payments/outstanding
// GET /api/customer/payments/history
// POST /api/customer/payments/process
```

#### Backend Schema Updates Required

**New Tables:**
```sql
-- Customer Jobs/Clearances
CREATE TABLE customer_jobs (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    reference VARCHAR(50) UNIQUE,
    service_type VARCHAR(50),
    description TEXT,
    ics_status VARCHAR(50),
    customs_value DECIMAL(12,2),
    duty_amount DECIMAL(12,2),
    gst_amount DECIMAL(12,2),
    total_amount DECIMAL(12,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Job Line Items
CREATE TABLE job_line_items (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES customer_jobs(id),
    line_number INTEGER,
    hs_code VARCHAR(10),
    description TEXT,
    quantity INTEGER,
    value DECIMAL(12,2),
    duty_rate VARCHAR(20),
    duty_amount DECIMAL(12,2),
    concessions TEXT[]
);

-- Customer Payments
CREATE TABLE customer_payments (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    job_id UUID REFERENCES customer_jobs(id),
    amount DECIMAL(12,2),
    payment_type VARCHAR(50),
    status VARCHAR(20),
    payment_date TIMESTAMP,
    receipt_url VARCHAR(255)
);

-- Customer Documents (extend existing)
ALTER TABLE documents ADD COLUMN job_id UUID REFERENCES customer_jobs(id);
ALTER TABLE documents ADD COLUMN document_category VARCHAR(50);
```

### 5. Component Architecture

#### Shared Components
```
src/components/
├── portal/
│   ├── layout/
│   │   ├── PortalLayout.tsx
│   │   ├── PortalHeader.tsx
│   │   ├── PortalNavigation.tsx
│   │   └── PortalSidebar.tsx
│   ├── dashboard/
│   │   ├── CustomerPortalDashboard.tsx
│   │   ├── StatCard.tsx
│   │   ├── RecentActivityFeed.tsx
│   │   └── QuickActionsSidebar.tsx
│   ├── jobs/
│   │   ├── JobsListView.tsx
│   │   ├── JobCard.tsx
│   │   ├── JobStatusBadge.tsx
│   │   ├── JobDetailsModal.tsx
│   │   └── CustomsDeclarationView.tsx
│   ├── booking/
│   │   ├── NewBookingSection.tsx
│   │   ├── BookingServiceSelector.tsx
│   │   ├── ClearanceBookingForm.tsx
│   │   └── ConsultationBookingForm.tsx
│   ├── documents/
│   │   ├── DocumentManagement.tsx
│   │   ├── DocumentUploadZone.tsx
│   │   ├── DocumentTable.tsx
│   │   └── DocumentViewer.tsx
│   ├── payments/
│   │   ├── PaymentsDashboard.tsx
│   │   ├── OutstandingPayments.tsx
│   │   ├── PaymentHistory.tsx
│   │   └── PaymentBreakdown.tsx
│   └── support/
│       ├── SupportCenter.tsx
│       ├── ContactOptions.tsx
│       └── SupportTickets.tsx
```

### 6. Files to Remove/Refactor

#### Files to Remove:
- `src/components/loa/LOACreator.tsx` (not needed in customer portal)
- `src/components/edi/EDIJobRegistration.tsx` (replace with jobs system)
- `src/components/broker-review/` (entire directory - not customer-facing)
- `src/components/ai-assistant/` (not needed in customer portal)
- `src/components/export-tariffs/` (not customer-facing)
- `src/components/tariff/` (not customer-facing)
- `src/components/tariff-tree/` (not customer-facing)
- `src/pages/TariffTree.tsx`
- `src/pages/ExportTariffs.tsx`
- `src/pages/BrokerReviewPage.tsx`
- `src/pages/AIAssistant.tsx`

#### Files to Refactor:
- `src/App.tsx` - Complete rewrite for portal layout
- `src/components/dashboard/CustomerDashboard.tsx` - Transform to portal dashboard
- `src/components/documents/DocumentUpload.tsx` - Enhance for job association
- `src/components/auth/LoginForm.tsx` - Update styling to match portal theme
- `src/components/auth/RegisterForm.tsx` - Update styling to match portal theme

### 7. Styling Updates

#### New CSS Variables
```css
:root {
  --portal-primary: #1e3a5f;
  --portal-secondary: #ff6b35;
  --portal-background: #f8f9fa;
  --portal-success: #28a745;
  --portal-warning: #ffc107;
  --portal-error: #dc3545;
  --portal-text: #333;
  --portal-text-light: #6c757d;
  --portal-border: #e9ecef;
  --portal-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
```

#### Component-Specific Styles
- Create `portal.css` for portal-specific styling
- Update existing Tailwind classes to use portal color scheme
- Implement responsive design for mobile/tablet

### 8. Data Integration Plan

#### Phase 1: Mock Data Replacement
1. Replace all mock data with API calls
2. Implement proper error handling
3. Add loading states for all components

#### Phase 2: Real-time Updates
1. Implement WebSocket connections for job status updates
2. Add notification system for important events
3. Implement auto-refresh for critical data

#### Phase 3: Advanced Features
1. Document preview functionality
2. Payment processing integration
3. Support ticket system
4. Mobile app considerations

### 9. Implementation Timeline

#### Week 1: Foundation
- [ ] Create new portal layout components
- [ ] Implement portal routing structure
- [ ] Update authentication components styling
- [ ] Create base portal CSS

#### Week 2: Core Features
- [ ] Implement dashboard with real data
- [ ] Create jobs listing and details views
- [ ] Implement document management
- [ ] Create payment dashboard

#### Week 3: Advanced Features
- [ ] Implement booking system
- [ ] Create support center
- [ ] Add modal components for job details
- [ ] Implement file upload functionality

#### Week 4: Integration & Testing
- [ ] Connect all components to real APIs
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Test responsive design
- [ ] Performance optimization

### 10. API Mapping to Portal Features

#### Existing APIs that can be leveraged:
- `documentsApi` - For document management
- `customerApi` - For profile and dashboard stats
- `authApi` - For authentication

#### New APIs needed:
```typescript
// Customer Jobs API
export const customerJobsApi = {
  async getJobs(): Promise<CustomsJob[]>,
  async getJob(id: string): Promise<CustomsJob>,
  async createJob(data: JobCreateRequest): Promise<CustomsJob>,
  async updateJobStatus(id: string, status: string): Promise<CustomsJob>,
  async getJobDeclaration(id: string): Promise<CustomsDeclaration>,
  async payJobDuties(id: string, paymentData: PaymentRequest): Promise<Payment>
};

// Customer Payments API
export const customerPaymentsApi = {
  async getOutstandingPayments(): Promise<OutstandingPayment[]>,
  async getPaymentHistory(): Promise<Payment[]>,
  async processPayment(data: PaymentRequest): Promise<PaymentResult>
};

// Customer Support API
export const customerSupportApi = {
  async createTicket(data: SupportTicketRequest): Promise<SupportTicket>,
  async getTickets(): Promise<SupportTicket[]>,
  async updateTicket(id: string, data: TicketUpdate): Promise<SupportTicket>
};
```

### 11. Database Schema Extensions

#### Customer Management
```sql
-- Extend customers table
ALTER TABLE customers ADD COLUMN customer_reference VARCHAR(20) UNIQUE;
ALTER TABLE customers ADD COLUMN company_abn VARCHAR(11);
ALTER TABLE customers ADD COLUMN billing_address JSONB;
ALTER TABLE customers ADD COLUMN shipping_address JSONB;
```

#### Jobs and Clearances
```sql
-- Main jobs table
CREATE TABLE customer_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    reference VARCHAR(50) UNIQUE NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    description TEXT,
    ics_reference VARCHAR(100),
    ics_status VARCHAR(50) DEFAULT 'pending',
    port_of_entry VARCHAR(10),
    country_of_origin VARCHAR(3),
    supplier_name VARCHAR(255),
    consignee_name VARCHAR(255),
    customs_value DECIMAL(12,2),
    freight_insurance DECIMAL(12,2),
    cif_value DECIMAL(12,2),
    duty_amount DECIMAL(12,2),
    gst_amount DECIMAL(12,2),
    processing_fee DECIMAL(12,2),
    total_amount DECIMAL(12,2),
    exchange_rate DECIMAL(8,4),
    declaration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job line items with tariff details
CREATE TABLE job_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES customer_jobs(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    hs_code VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_of_measure VARCHAR(20),
    unit_value DECIMAL(12,2),
    total_value DECIMAL(12,2),
    duty_rate VARCHAR(20),
    duty_amount DECIMAL(12,2),
    concessions TEXT[],
    treatment_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payment tracking
CREATE TABLE customer_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    job_id UUID REFERENCES customer_jobs(id),
    payment_reference VARCHAR(100) UNIQUE,
    amount DECIMAL(12,2) NOT NULL,
    payment_type VARCHAR(50) NOT NULL, -- 'duty', 'service_fee', 'consultation'
    payment_method VARCHAR(50), -- 'credit_card', 'bank_transfer', 'eft'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    payment_date TIMESTAMP,
    receipt_url VARCHAR(255),
    gateway_transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support tickets
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'closed'
    assigned_to VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity tracking
CREATE TABLE customer_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    job_id UUID REFERENCES customer_jobs(id),
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 12. Security Considerations

#### Authentication & Authorization
- Implement proper JWT token validation
- Add role-based access control (customer vs broker vs admin)
- Secure file upload with virus scanning
- Implement rate limiting on API endpoints

#### Data Protection
- Encrypt sensitive customer data
- Implement audit logging for all customer actions
- Secure document storage with access controls
- GDPR compliance for customer data

### 13. Performance Optimization

#### Frontend Optimization
- Implement lazy loading for components
- Use React.memo for expensive components
- Implement virtual scrolling for large job lists
- Optimize bundle size with code splitting

#### Backend Optimization
- Add database indexing for customer queries
- Implement caching for frequently accessed data
- Use pagination for large datasets
- Optimize file upload handling

### 14. Testing Strategy

#### Unit Testing
- Test all new portal components
- Test API integration functions
- Test utility functions and helpers

#### Integration Testing
- Test complete user workflows
- Test payment processing
- Test document upload/download
- Test job creation and management

#### E2E Testing
- Test complete customer journey
- Test responsive design on different devices
- Test browser compatibility

### 15. Deployment Considerations

#### Environment Configuration
- Separate customer portal from broker portal
- Configure different API endpoints for customer vs broker
- Set up proper SSL certificates
- Configure CDN for static assets

#### Monitoring & Analytics
- Implement customer usage analytics
- Set up error tracking and monitoring
- Add performance monitoring
- Implement customer feedback collection

## Conclusion

This specification provides a comprehensive roadmap for transforming the current React frontend into a professional customer portal that matches the HTML design requirements. The implementation will focus on real data integration, modern UX/UI design, and robust functionality for customs clearance management.

The portal will significantly improve the customer experience by providing:
- Clear visibility into job status and progress
- Easy document management and upload
- Transparent payment processing
- Professional support channels
- Mobile-responsive design

Implementation should follow the phased approach outlined above, with careful attention to data security, performance, and user experience throughout the development process.