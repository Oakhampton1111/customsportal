# File Pruning Guide - Customer Portal Implementation

## Overview

This document provides a comprehensive list of files to remove, keep, or refactor when implementing the customer portal. The goal is to eliminate broker-specific functionality and focus on customer-facing features.

## 1. Files to DELETE (Complete Removal)

### A. AI Assistant Components (Not Customer-Facing)
```
frontend/src/components/ai-assistant/
├── ConversationalInterface.tsx          ❌ DELETE
├── DocumentAnalysisPanel.tsx            ❌ DELETE
└── index.ts                             ❌ DELETE
```

### B. Broker Review Components (Internal Broker Tools)
```
frontend/src/components/broker-review/
├── BrokerReviewDashboard.tsx            ❌ DELETE
├── ComplianceChecker.tsx                ❌ DELETE
├── DocumentProcessingQueue.tsx          ❌ DELETE
├── DutyCalculationPanel.tsx             ❌ DELETE
├── EntryCompiler.tsx                    ❌ DELETE
├── index.ts                             ❌ DELETE
└── OCRReviewPanel.tsx                   ❌ DELETE
```

### C. Export Tariffs Components (Not Customer Portal Feature)
```
frontend/src/components/export-tariffs/
├── AHECCTreeBrowser.tsx                 ❌ DELETE
├── ExportRequirementsPanel.tsx          ❌ DELETE
└── MarketAccessDashboard.tsx            ❌ DELETE
```

### D. Tariff Navigation Components (Too Technical for Customers)
```
frontend/src/components/tariff/
├── index.ts                             ❌ DELETE
├── TariffDisplay.tsx                    ❌ DELETE
└── TariffTreeView.tsx                   ❌ DELETE

frontend/src/components/tariff-tree/
├── InteractiveTariffTree.tsx            ❌ DELETE
├── TariffComparisonPanel.tsx            ❌ DELETE
├── TariffDetailPanel.tsx                ❌ DELETE
└── TreeNavigation.tsx                   ❌ DELETE
```

### E. Duty Calculator Components (Internal Tool)
```
frontend/src/components/duty/
├── CountrySelector.tsx                  ❌ DELETE
├── DutyCalculator.tsx                   ❌ DELETE
├── DutyCalculatorForm.tsx               ❌ DELETE
├── DutyResults.tsx                      ❌ DELETE
├── DutyResultsDisplay.tsx               ❌ DELETE
├── HsCodeLookup.tsx                     ❌ DELETE
├── index.ts                             ❌ DELETE
└── __tests__/                           ❌ DELETE
    └── DutyCalculator.test.tsx          ❌ DELETE
```

### F. Search Components (Replace with Simple Search)
```
frontend/src/components/search/
├── index.ts                             ❌ DELETE
├── SearchForm.tsx                       ❌ DELETE
├── SearchResults.tsx                    ❌ DELETE
└── __tests__/                           ❌ DELETE
    └── SearchForm.test.tsx              ❌ DELETE
```

### G. LOA and EDI Components (Replace with Jobs System)
```
frontend/src/components/loa/
└── LOACreator.tsx                       ❌ DELETE

frontend/src/components/edi/
└── EDIJobRegistration.tsx               ❌ DELETE
```

### H. News Components (Not Customer Portal Feature)
```
frontend/src/components/news/
├── NewsApi.ts                           ❌ DELETE
└── NewsFeed.tsx                         ❌ DELETE
```

### I. Dashboard Components (Replace with Portal Dashboard)
```
frontend/src/components/dashboard/
├── NewsIntelligenceCenter.tsx           ❌ DELETE
├── RecentRulingsPanel.tsx               ❌ DELETE
└── TradeStatsSidebar.tsx                ❌ DELETE
```

### J. Page Components (Broker-Specific)
```
frontend/src/pages/
├── AIAssistant.tsx                      ❌ DELETE
├── BrokerReviewPage.tsx                 ❌ DELETE
├── Compliance.tsx                       ❌ DELETE
├── CompliancePage.tsx                   ❌ DELETE
├── DocumentDetailPage.tsx               ❌ DELETE
├── EDIDetailPage.tsx                    ❌ DELETE
├── EDIPage.tsx                          ❌ DELETE
├── ExportTariffs.tsx                    ❌ DELETE
├── LOADetailPage.tsx                    ❌ DELETE
├── LOAPage.tsx                          ❌ DELETE
├── Reports.tsx                          ❌ DELETE
├── SettingsPage.tsx                     ❌ DELETE (Replace with Profile)
└── TariffTree.tsx                       ❌ DELETE
```

### K. Service Files (Broker-Specific APIs)
```
frontend/src/services/
├── aiApi.ts                             ❌ DELETE
├── complianceApi.ts                     ❌ DELETE
├── dutyCalculatorApi.ts                 ❌ DELETE
├── exportApi.ts                         ❌ DELETE
├── newsApi.ts                           ❌ DELETE
├── reportsApi.ts                        ❌ DELETE
├── rulingsApi.ts                        ❌ DELETE
├── searchApi.ts                         ❌ DELETE
└── tariffApi.ts                         ❌ DELETE
```

### L. Type Definitions (Unused in Customer Portal)
```
frontend/src/types/
├── compliance.ts                        ❌ DELETE
├── edi.ts                               ❌ DELETE
└── loa.ts                               ❌ DELETE
```

### M. Test Files (For Deleted Components)
```
frontend/src/__tests__/integration/
└── user-workflows.test.tsx              ❌ DELETE (Replace with customer workflows)

frontend/src/pages/__tests__/integration/
├── api-integration.test.tsx             ❌ DELETE (Update for customer APIs)
└── routing.test.tsx                     ❌ DELETE (Update for customer routes)
```

## 2. Files to KEEP and REFACTOR

### A. Core Application Files
```
frontend/src/
├── App.tsx                              🔄 MAJOR REFACTOR
├── main.tsx                             ✅ KEEP (Minor updates)
├── index.css                            🔄 UPDATE (Add portal styles)
└── vite-env.d.ts                        ✅ KEEP
```

### B. Authentication Components
```
frontend/src/components/auth/
├── LoginForm.tsx                        🔄 REFACTOR (Update styling)
└── RegisterForm.tsx                     🔄 REFACTOR (Update styling)
```

### C. Common Components (Reusable)
```
frontend/src/components/common/
├── Button.tsx                           ✅ KEEP
├── index.ts                             🔄 UPDATE
├── Input.tsx                            ✅ KEEP
└── __tests__/                           ✅ KEEP
    ├── Button.test.tsx                  ✅ KEEP
    └── Input.test.tsx                   ✅ KEEP
```

### D. Document Components
```
frontend/src/components/documents/
└── DocumentUpload.tsx                   🔄 MAJOR REFACTOR (Transform to DocumentManagement)
```

### E. Layout Components
```
frontend/src/components/layout/
├── AppLayout.tsx                        🔄 MAJOR REFACTOR (Portal layout)
├── Footer.tsx                           🔄 REFACTOR (Portal footer)
├── Header.tsx                           🔄 MAJOR REFACTOR (Portal header)
├── index.ts                             🔄 UPDATE
├── Layout.tsx                           🔄 MAJOR REFACTOR
└── Navigation.tsx                       🔄 MAJOR REFACTOR (Portal navigation)
```

### F. UI Components (Reusable)
```
frontend/src/components/ui/
├── ActionToolbar.tsx                    ✅ KEEP
├── Alert.tsx                            ✅ KEEP
├── badge.tsx                            ✅ KEEP
├── Button.tsx                           ✅ KEEP
├── Card.tsx                             ✅ KEEP
├── EnhancedCard.tsx                     ✅ KEEP
├── index.ts                             🔄 UPDATE
├── input.tsx                            ✅ KEEP
├── KPICard.tsx                          ✅ KEEP (Use for dashboard stats)
├── LoadingSpinner.tsx                   ✅ KEEP
├── ProfessionalCard.tsx                 ✅ KEEP
├── ProfessionalForm.tsx                 ✅ KEEP
├── ProfessionalLayouts.tsx              ✅ KEEP
├── ProfessionalModal.tsx                ✅ KEEP
├── ProfessionalTable.tsx                ✅ KEEP
├── scroll-area.tsx                      ✅ KEEP
└── SearchInput.tsx                      ✅ KEEP
```

### G. Dashboard Components
```
frontend/src/components/dashboard/
└── CustomerDashboard.tsx                🔄 MAJOR REFACTOR (Portal dashboard)
```

### H. Router Components
```
frontend/src/router/
└── AppRouter.tsx                        🔄 MAJOR REFACTOR (Customer routes only)
```

### I. Service Files (Core APIs)
```
frontend/src/services/
├── api.ts                               🔄 REFACTOR (Update for customer APIs)
├── documentsApi.ts                      🔄 REFACTOR (Add job association)
└── index.ts                             🔄 UPDATE
```

### J. Type Definitions (Core Types)
```
frontend/src/types/
├── customer.ts                          ✅ KEEP
├── documents.ts                         🔄 REFACTOR (Add job association)
├── index.ts                             🔄 UPDATE
└── test.d.ts                            ✅ KEEP
```

### K. Utility Files
```
frontend/src/lib/
└── utils.ts                             ✅ KEEP

frontend/src/utils/
└── index.ts                             ✅ KEEP
```

### L. Page Components (Keep and Refactor)
```
frontend/src/pages/
├── Dashboard.tsx                        🔄 MAJOR REFACTOR (Portal dashboard)
├── Documents.tsx                        🔄 REFACTOR (Document management)
├── DocumentsPage.tsx                    🔄 REFACTOR (Document management)
├── HelpPage.tsx                         🔄 REFACTOR (Support center)
├── index.ts                             🔄 UPDATE
└── NotFoundPage.tsx                     ✅ KEEP
```

## 3. Files to CREATE (New Components)

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

## 4. File Cleanup Script

### A. Automated Deletion Script
```bash
#!/bin/bash
# File cleanup script for customer portal implementation

echo "Starting customer portal file cleanup..."

# Remove AI Assistant components
rm -rf frontend/src/components/ai-assistant/

# Remove Broker Review components
rm -rf frontend/src/components/broker-review/

# Remove Export Tariffs components
rm -rf frontend/src/components/export-tariffs/

# Remove Tariff components
rm -rf frontend/src/components/tariff/
rm -rf frontend/src/components/tariff-tree/

# Remove Duty Calculator components
rm -rf frontend/src/components/duty/

# Remove Search components
rm -rf frontend/src/components/search/

# Remove LOA and EDI components
rm -f frontend/src/components/loa/LOACreator.tsx
rm -f frontend/src/components/edi/EDIJobRegistration.tsx

# Remove News components
rm -rf frontend/src/components/news/

# Remove specific dashboard components
rm -f frontend/src/components/dashboard/NewsIntelligenceCenter.tsx
rm -f frontend/src/components/dashboard/RecentRulingsPanel.tsx
rm -f frontend/src/components/dashboard/TradeStatsSidebar.tsx

# Remove broker-specific pages
rm -f frontend/src/pages/AIAssistant.tsx
rm -f frontend/src/pages/BrokerReviewPage.tsx
rm -f frontend/src/pages/Compliance.tsx
rm -f frontend/src/pages/CompliancePage.tsx
rm -f frontend/src/pages/DocumentDetailPage.tsx
rm -f frontend/src/pages/EDIDetailPage.tsx
rm -f frontend/src/pages/EDIPage.tsx
rm -f frontend/src/pages/ExportTariffs.tsx
rm -f frontend/src/pages/LOADetailPage.tsx
rm -f frontend/src/pages/LOAPage.tsx
rm -f frontend/src/pages/Reports.tsx
rm -f frontend/src/pages/SettingsPage.tsx
rm -f frontend/src/pages/TariffTree.tsx

# Remove broker-specific services
rm -f frontend/src/services/aiApi.ts
rm -f frontend/src/services/complianceApi.ts
rm -f frontend/src/services/dutyCalculatorApi.ts
rm -f frontend/src/services/exportApi.ts
rm -f frontend/src/services/newsApi.ts
rm -f frontend/src/services/reportsApi.ts
rm -f frontend/src/services/rulingsApi.ts
rm -f frontend/src/services/searchApi.ts
rm -f frontend/src/services/tariffApi.ts

# Remove unused type definitions
rm -f frontend/src/types/compliance.ts
rm -f frontend/src/types/edi.ts
rm -f frontend/src/types/loa.ts

echo "File cleanup completed!"
echo "Next steps:"
echo "1. Create new portal components"
echo "2. Refactor existing components"
echo "3. Update routing and navigation"
echo "4. Implement new styling"
```

## 5. Directory Structure After Cleanup

```
frontend/src/
├── components/
│   ├── auth/                            # Authentication components
│   ├── common/                          # Reusable common components
│   ├── documents/                       # Document management (refactored)
│   ├── layout/                          # Layout components (refactored)
│   ├── portal/                          # New portal-specific components
│   │   ├── dashboard/
│   │   ├── jobs/
│   │   ├── booking/
│   │   ├── documents/
│   │   ├── payments/
│   │   ├── support/
│   │   └── layout/
│   └── ui/                              # UI components library
├── pages/
│   ├── portal/                          # New portal pages
│   ├── Dashboard.tsx                    # Refactored
│   ├── Documents.tsx                    # Refactored
│   ├── DocumentsPage.tsx               # Refactored
│   ├── HelpPage.tsx                     # Refactored
│   ├── index.ts                         # Updated
│   └── NotFoundPage.tsx                 # Keep
├── router/
│   └── AppRouter.tsx                    # Major refactor
├── services/
│   ├── portal/                          # New customer APIs
│   ├── api.ts                           # Refactored
│   ├── documentsApi.ts                  # Refactored
│   └── index.ts                         # Updated
├── styles/
│   ├── portal/                          # New portal styles
│   ├── modern-enterprise.css            # Keep
│   └── pages/                           # Keep
├── types/
│   ├── portal/                          # New portal types
│   ├── customer.ts                      # Keep
│   ├── documents.ts                     # Refactored
│   ├── index.ts                         # Updated
│   └── test.d.ts                        # Keep
├── utils/
│   └── index.ts                         # Keep
├── lib/
│   └── utils.ts                         # Keep
├── App.tsx                              # Major refactor
├── main.tsx                             # Minor updates
├── index.css                            # Updated
└── vite-env.d.ts                        # Keep
```

## 6. Impact Analysis

### A. Bundle Size Reduction
- **Estimated reduction**: 40-50% of current bundle size
- **Removed dependencies**: AI libraries, complex tariff navigation, broker tools
- **Performance improvement**: Faster load times, smaller JavaScript bundles

### B. Maintenance Benefits
- **Simplified codebase**: Focus on customer-specific functionality
- **Reduced complexity**: Fewer components to maintain
- **Clear separation**: Customer portal vs broker portal

### C. Development Benefits
- **Faster development**: Less code to navigate and understand
- **Focused testing**: Test only customer-facing features
- **Easier deployment**: Smaller, more focused application

This file pruning guide ensures a clean, focused customer portal implementation while maintaining code quality and performance standards.