# File Pruning Guide - Customer Portal Implementation (Updated)

## Overview

This document provides a comprehensive list of files to remove, keep, or refactor when implementing the customer portal. **IMPORTANT**: We are keeping all broker-specific components as they will be part of a separate broker portal. This guide focuses only on customer portal-specific changes.

## 1. Files to KEEP (Broker Portal Components)

### A. AI Assistant Components (Broker Portal)
```
frontend/src/components/ai-assistant/
├── ConversationalInterface.tsx          ✅ KEEP (Broker Portal)
├── DocumentAnalysisPanel.tsx            ✅ KEEP (Broker Portal)
└── index.ts                             ✅ KEEP (Broker Portal)
```

### B. Broker Review Components (Broker Portal)
```
frontend/src/components/broker-review/
├── BrokerReviewDashboard.tsx            ✅ KEEP (Broker Portal)
├── ComplianceChecker.tsx                ✅ KEEP (Broker Portal)
├── DocumentProcessingQueue.tsx          ✅ KEEP (Broker Portal)
├── DutyCalculationPanel.tsx             ✅ KEEP (Broker Portal)
├── EntryCompiler.tsx                    ✅ KEEP (Broker Portal)
├── index.ts                             ✅ KEEP (Broker Portal)
└── OCRReviewPanel.tsx                   ✅ KEEP (Broker Portal)
```

### C. Export Tariffs Components (Broker Portal)
```
frontend/src/components/export-tariffs/
├── AHECCTreeBrowser.tsx                 ✅ KEEP (Broker Portal)
├── ExportRequirementsPanel.tsx          ✅ KEEP (Broker Portal)
└── MarketAccessDashboard.tsx            ✅ KEEP (Broker Portal)
```

### D. Tariff Navigation Components (Broker Portal)
```
frontend/src/components/tariff/
├── index.ts                             ✅ KEEP (Broker Portal)
├── TariffDisplay.tsx                    ✅ KEEP (Broker Portal)
└── TariffTreeView.tsx                   ✅ KEEP (Broker Portal)

frontend/src/components/tariff-tree/
├── InteractiveTariffTree.tsx            ✅ KEEP (Broker Portal)
├── TariffComparisonPanel.tsx            ✅ KEEP (Broker Portal)
├── TariffDetailPanel.tsx                ✅ KEEP (Broker Portal)
└── TreeNavigation.tsx                   ✅ KEEP (Broker Portal)
```

### E. Duty Calculator Components (Broker Portal)
```
frontend/src/components/duty/
├── CountrySelector.tsx                  ✅ KEEP (Broker Portal)
├── DutyCalculator.tsx                   ✅ KEEP (Broker Portal)
├── DutyCalculatorForm.tsx               ✅ KEEP (Broker Portal)
├── DutyResults.tsx                      ✅ KEEP (Broker Portal)
├── DutyResultsDisplay.tsx               ✅ KEEP (Broker Portal)
├── HsCodeLookup.tsx                     ✅ KEEP (Broker Portal)
├── index.ts                             ✅ KEEP (Broker Portal)
└── __tests__/                           ✅ KEEP (Broker Portal)
    └── DutyCalculator.test.tsx          ✅ KEEP (Broker Portal)
```

### F. Search Components (Broker Portal)
```
frontend/src/components/search/
├── index.ts                             ✅ KEEP (Broker Portal)
├── SearchForm.tsx                       ✅ KEEP (Broker Portal)
├── SearchResults.tsx                    ✅ KEEP (Broker Portal)
└── __tests__/                           ✅ KEEP (Broker Portal)
    └── SearchForm.test.tsx              ✅ KEEP (Broker Portal)
```

### G. News Components (Broker Portal)
```
frontend/src/components/news/
├── NewsApi.ts                           ✅ KEEP (Broker Portal)
└── NewsFeed.tsx                         ✅ KEEP (Broker Portal)
```

### H. Broker-Specific Pages (Broker Portal)
```
frontend/src/pages/
├── AIAssistant.tsx                      ✅ KEEP (Broker Portal)
├── BrokerReviewPage.tsx                 ✅ KEEP (Broker Portal)
├── Compliance.tsx                       ✅ KEEP (Broker Portal)
├── CompliancePage.tsx                   ✅ KEEP (Broker Portal)
├── ExportTariffs.tsx                    ✅ KEEP (Broker Portal)
├── Reports.tsx                          ✅ KEEP (Broker Portal)
└── TariffTree.tsx                       ✅ KEEP (Broker Portal)
```

### I. Broker-Specific Services (Broker Portal)
```
frontend/src/services/
├── aiApi.ts                             ✅ KEEP (Broker Portal)
├── complianceApi.ts                     ✅ KEEP (Broker Portal)
├── dutyCalculatorApi.ts                 ✅ KEEP (Broker Portal)
├── exportApi.ts                         ✅ KEEP (Broker Portal)
├── newsApi.ts                           ✅ KEEP (Broker Portal)
├── reportsApi.ts                        ✅ KEEP (Broker Portal)
├── rulingsApi.ts                        ✅ KEEP (Broker Portal)
├── searchApi.ts                         ✅ KEEP (Broker Portal)
└── tariffApi.ts                         ✅ KEEP (Broker Portal)
```

## 2. Files to REFACTOR for Customer Portal

### A. Core Application Files
```
frontend/src/
├── App.tsx                              🔄 MAJOR REFACTOR (Add portal routing)
├── main.tsx                             🔄 MINOR UPDATE (Portal-specific setup)
├── index.css                            🔄 UPDATE (Add portal styles)
└── vite-env.d.ts                        ✅ KEEP
```

### B. Authentication Components (Shared but Styled for Portal)
```
frontend/src/components/auth/
├── LoginForm.tsx                        🔄 REFACTOR (Portal styling)
└── RegisterForm.tsx                     🔄 REFACTOR (Portal styling)
```

### C. Layout Components (Portal-Specific)
```
frontend/src/components/layout/
├── AppLayout.tsx                        🔄 MAJOR REFACTOR (Portal layout)
├── Footer.tsx                           🔄 REFACTOR (Portal footer)
├── Header.tsx                           🔄 MAJOR REFACTOR (Portal header)
├── index.ts                             🔄 UPDATE
├── Layout.tsx                           🔄 MAJOR REFACTOR
└── Navigation.tsx                       🔄 MAJOR REFACTOR (Portal navigation)
```

### D. Dashboard Components (Customer-Specific)
```
frontend/src/components/dashboard/
├── CustomerDashboard.tsx                🔄 MAJOR REFACTOR (Portal dashboard)
├── NewsIntelligenceCenter.tsx           🔄 REFACTOR (Customer news)
├── RecentRulingsPanel.tsx               🔄 REFACTOR (Customer rulings)
└── TradeStatsSidebar.tsx                🔄 REFACTOR (Customer stats)
```

### E. Document Components (Customer-Focused)
```
frontend/src/components/documents/
└── DocumentUpload.tsx                   🔄 MAJOR REFACTOR (Job association)
```

### F. Router Components (Customer Routes)
```
frontend/src/router/
└── AppRouter.tsx                        🔄 MAJOR REFACTOR (Customer routes)
```

### G. Service Files (Customer APIs)
```
frontend/src/services/
├── api.ts                               🔄 REFACTOR (Customer endpoints)
├── documentsApi.ts                      🔄 REFACTOR (Job association)
└── index.ts                             🔄 UPDATE
```

## 3. Files to REMOVE/REPLACE (Customer Portal Specific)

### A. LOA and EDI Components (Replace with Jobs System)
```
frontend/src/components/loa/
└── LOACreator.tsx                       ❌ REMOVE (Replace with Jobs)

frontend/src/components/edi/
└── EDIJobRegistration.tsx               ❌ REMOVE (Replace with Jobs)
```

### B. Customer Portal Incompatible Pages
```
frontend/src/pages/
├── DocumentDetailPage.tsx               ❌ REMOVE (Integrate into jobs)
├── EDIDetailPage.tsx                    ❌ REMOVE (Replace with jobs)
├── EDIPage.tsx                          ❌ REMOVE (Replace with jobs)
├── LOADetailPage.tsx                    ❌ REMOVE (Replace with jobs)
├── LOAPage.tsx                          ❌ REMOVE (Replace with jobs)
└── SettingsPage.tsx                     ❌ REMOVE (Replace with Profile)
```

### C. Customer Portal Incompatible Types
```
frontend/src/types/
├── compliance.ts                        ❌ REMOVE (Not customer-facing)
├── edi.ts                               ❌ REMOVE (Replace with jobs)
└── loa.ts                               ❌ REMOVE (Replace with jobs)
```

### D. Test Files (Update for Customer Portal)
```
frontend/src/__tests__/integration/
└── user-workflows.test.tsx              🔄 REPLACE (Customer workflows)

frontend/src/pages/__tests__/integration/
├── api-integration.test.tsx             🔄 UPDATE (Customer APIs)
└── routing.test.tsx                     🔄 UPDATE (Customer routes)
```

## 4. Files to CREATE (Customer Portal Specific)

### A. Portal Layout Components
```
frontend/src/components/portal/layout/
├── PortalLayout.tsx                     ➕ CREATE
├── PortalHeader.tsx                     ➕ CREATE
├── PortalNavigation.tsx                 ➕ CREATE
├── PortalSidebar.tsx                    ➕ CREATE
└── index.ts                             ➕ CREATE
```

### B. Portal Dashboard Components
```
frontend/src/components/portal/dashboard/
├── CustomerPortalDashboard.tsx          ➕ CREATE
├── StatCard.tsx                         ➕ CREATE
├── RecentActivityFeed.tsx               ➕ CREATE
├── QuickActionsSidebar.tsx              ➕ CREATE
└── index.ts                             ➕ CREATE
```

### C. Jobs Management Components
```
frontend/src/components/portal/jobs/
├── JobsListView.tsx                     ➕ CREATE
├── JobCard.tsx                          ➕ CREATE
├── JobStatusBadge.tsx                   ➕ CREATE
├── JobDetailsModal.tsx                  ➕ CREATE
├── CustomsDeclarationView.tsx           ➕ CREATE
├── LineItemsTable.tsx                   ➕ CREATE
├── JobFilters.tsx                       ➕ CREATE
└── index.ts                             ➕ CREATE
```

### D. Booking Components
```
frontend/src/components/portal/booking/
├── NewBookingSection.tsx                ➕ CREATE
├── BookingServiceSelector.tsx           ➕ CREATE
├── ClearanceBookingForm.tsx             ➕ CREATE
├── ConsultationBookingForm.tsx          ➕ CREATE
├── ServiceFeatureCards.tsx              ➕ CREATE
└── index.ts                             ➕ CREATE
```

### E. Document Management Components
```
frontend/src/components/portal/documents/
├── DocumentManagement.tsx               ➕ CREATE
├── DocumentUploadZone.tsx               ➕ CREATE
├── DocumentTable.tsx                    ➕ CREATE
├── DocumentViewer.tsx                   ➕ CREATE
├── DocumentCategories.tsx               ➕ CREATE
└── index.ts                             ➕ CREATE
```

### F. Payment Components
```
frontend/src/components/portal/payments/
├── PaymentsDashboard.tsx                ➕ CREATE
├── OutstandingPayments.tsx              ➕ CREATE
├── PaymentHistory.tsx                   ➕ CREATE
├── PaymentBreakdown.tsx                 ➕ CREATE
├── PaymentModal.tsx                     ➕ CREATE
└── index.ts                             ➕ CREATE
```

### G. Support Components
```
frontend/src/components/portal/support/
├── SupportCenter.tsx                    ➕ CREATE
├── ContactOptions.tsx                   ➕ CREATE
├── SupportTickets.tsx                   ➕ CREATE
├── LiveChat.tsx                         ➕ CREATE
└── index.ts                             ➕ CREATE
```

### H. New Page Components
```
frontend/src/pages/portal/
├── PortalDashboard.tsx                  ➕ CREATE
├── JobsPage.tsx                         ➕ CREATE
├── BookingPage.tsx                      ➕ CREATE
├── PaymentsPage.tsx                     ➕ CREATE
├── SupportPage.tsx                      ➕ CREATE
├── ProfilePage.tsx                      ➕ CREATE
└── index.ts                             ➕ CREATE
```

### I. New Service Files
```
frontend/src/services/portal/
├── customerJobsApi.ts                   ➕ CREATE
├── customerPaymentsApi.ts               ➕ CREATE
├── customerSupportApi.ts                ➕ CREATE
├── customerDashboardApi.ts              ➕ CREATE
└── index.ts                             ➕ CREATE
```

### J. New Type Definitions
```
frontend/src/types/portal/
├── jobs.ts                              ➕ CREATE
├── payments.ts                          ➕ CREATE
├── dashboard.ts                         ➕ CREATE
├── support.ts                           ➕ CREATE
└── index.ts                             ➕ CREATE
```

### K. Portal Styling
```
frontend/src/styles/portal/
├── base.css                             ➕ CREATE
├── components.css                       ➕ CREATE
├── layout.css                           ➕ CREATE
├── theme.css                            ➕ CREATE
├── responsive.css                       ➕ CREATE
└── portal.css                           ➕ CREATE
```

## 5. Shared Components Strategy

### A. Keep Shared Components
```
frontend/src/components/common/
├── Button.tsx                           ✅ KEEP (Shared)
├── index.ts                             ✅ KEEP (Shared)
├── Input.tsx                            ✅ KEEP (Shared)
└── __tests__/                           ✅ KEEP (Shared)

frontend/src/components/ui/
├── ActionToolbar.tsx                    ✅ KEEP (Shared)
├── Alert.tsx                            ✅ KEEP (Shared)
├── badge.tsx                            ✅ KEEP (Shared)
├── Button.tsx                           ✅ KEEP (Shared)
├── Card.tsx                             ✅ KEEP (Shared)
├── EnhancedCard.tsx                     ✅ KEEP (Shared)
├── index.ts                             ✅ KEEP (Shared)
├── input.tsx                            ✅ KEEP (Shared)
├── KPICard.tsx                          ✅ KEEP (Shared)
├── LoadingSpinner.tsx                   ✅ KEEP (Shared)
├── ProfessionalCard.tsx                 ✅ KEEP (Shared)
├── ProfessionalForm.tsx                 ✅ KEEP (Shared)
├── ProfessionalLayouts.tsx              ✅ KEEP (Shared)
├── ProfessionalModal.tsx                ✅ KEEP (Shared)
├── ProfessionalTable.tsx                ✅ KEEP (Shared)
├── scroll-area.tsx                      ✅ KEEP (Shared)
└── SearchInput.tsx                      ✅ KEEP (Shared)
```

## 6. Implementation Strategy

### A. Portal Separation Approach
1. **Keep all broker components intact** - They will be used in the separate broker portal
2. **Create new customer portal components** - Focus on customer-specific functionality
3. **Share common UI components** - Maintain consistency between portals
4. **Separate routing and navigation** - Customer portal has different navigation needs

### B. Development Phases

#### Phase 1: Portal Foundation
- Create portal layout components
- Set up customer-specific routing
- Update authentication for portal branding
- Create portal-specific styling

#### Phase 2: Core Customer Features
- Implement jobs management system
- Create booking functionality
- Build document management for customers
- Develop payment dashboard

#### Phase 3: Enhanced Features
- Add support center
- Implement real-time notifications
- Create customer profile management
- Add mobile responsiveness

#### Phase 4: Integration & Testing
- Connect to real backend APIs
- Implement error handling
- Add comprehensive testing
- Performance optimization

## 7. Directory Structure After Implementation

```
frontend/src/
├── components/
│   ├── ai-assistant/                    # Broker Portal
│   ├── auth/                            # Shared (styled for portal)
│   ├── broker-review/                   # Broker Portal
│   ├── common/                          # Shared
│   ├── dashboard/                       # Refactored for customers
│   ├── documents/                       # Refactored for customers
│   ├── duty/                            # Broker Portal
│   ├── edi/                             # Remove EDIJobRegistration only
│   ├── export-tariffs/                  # Broker Portal
│   ├── layout/                          # Refactored for portal
│   ├── loa/                             # Remove LOACreator only
│   ├── news/                            # Broker Portal
│   ├── portal/                          # New customer portal components
│   │   ├── dashboard/
│   │   ├── jobs/
│   │   ├── booking/
│   │   ├── documents/
│   │   ├── payments/
│   │   ├── support/
│   │   └── layout/
│   ├── search/                          # Broker Portal
│   ├── tariff/                          # Broker Portal
│   ├── tariff-tree/                     # Broker Portal
│   └── ui/                              # Shared
├── pages/
│   ├── portal/                          # New customer portal pages
│   ├── Dashboard.tsx                    # Refactored for customers
│   ├── Documents.tsx                    # Refactored for customers
│   ├── DocumentsPage.tsx               # Refactored for customers
│   ├── HelpPage.tsx                     # Refactored for support
│   ├── NotFoundPage.tsx                 # Shared
│   └── [broker-specific pages]          # Keep for broker portal
├── router/
│   └── AppRouter.tsx                    # Refactored for customer routes
├── services/
│   ├── portal/                          # New customer APIs
│   ├── api.ts                           # Refactored for customers
│   ├── documentsApi.ts                  # Refactored for customers
│   ├── [broker-specific APIs]           # Keep for broker portal
│   └── index.ts                         # Updated
├── styles/
│   ├── portal/                          # New portal styles
│   ├── modern-enterprise.css            # Shared
│   └── pages/                           # Shared
├── types/
│   ├── portal/                          # New customer portal types
│   ├── customer.ts                      # Shared
│   ├── documents.ts                     # Refactored for customers
│   ├── [broker-specific types]          # Keep for broker portal
│   └── index.ts                         # Updated
└── [other shared directories]           # Keep as-is
```

## 8. Benefits of This Approach

### A. Code Reusability
- Broker portal components remain intact and functional
- Shared UI components reduce duplication
- Common utilities and services can be shared

### B. Maintainability
- Clear separation between customer and broker functionality
- Easier to maintain and update each portal independently
- Reduced risk of breaking changes affecting both portals

### C. Development Efficiency
- Parallel development of customer and broker features
- Focused testing for each portal type
- Easier deployment and versioning

This updated approach ensures we maintain all existing broker functionality while creating a focused, professional customer portal experience.