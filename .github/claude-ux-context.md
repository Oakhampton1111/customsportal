# 🎨 UX Context & Guidelines for Claude Auto-Fix - Customs Broker Portal

## 📋 Overview
This document provides UX guidelines and user experience requirements that Claude must preserve when making code fixes for the Customs Broker Portal. This is a **reference and research portal** - a live library providing synthesized insights for customs brokers to research import/export regulations, tariffs, and duty calculations.

## 🎯 Core UX Principles

### **Research-Focused User Experience**
- **Speed of Research**: Fast lookup and comparison of tariff information
- **Data Accuracy**: Zero tolerance for errors in government reference data
- **Comprehensive Insights**: Synthesized view of all relevant duties, taxes, and concessions
- **Comparison Tools**: Side-by-side rate comparisons (Standard vs FTA vs TCO)
- **Calculator Integration**: Comprehensive duty and landed cost calculators

### **Visual Consistency**
- **Professional Design**: Clean, research-focused interface design
- **Data Density**: Efficient display of complex tariff and regulatory information
- **Rate Indicators**: Clear visual comparison of different duty rates
- **Color Coding**: Consistent scheme for rate types (Standard, FTA, TCO, GST)
- **Typography**: Readable fonts for detailed regulatory and financial data

## 🔄 Reference Portal User Workflows

### **Primary Research Journey**
1. **Product Research** → Search for commodity or product information
2. **HS Code Classification** → Find correct tariff classification
3. **Schedule 3 Lookup** → View standard import duty rates
4. **FTA Rate Comparison** → Compare free trade agreement rates
5. **TCO Investigation** → Check tariff concession order eligibility
6. **Comprehensive Calculation** → Calculate total landed costs
7. **Export Research** → Research export classifications and requirements

### **Critical User Interactions**
- **HS Code Search**: Fast and accurate tariff classification lookup
- **Rate Comparison Tool**: Side-by-side comparison of all applicable rates
- **Duty Calculator**: Comprehensive landed cost calculations
- **Tariff Tree Navigation**: Browse Schedule 3 and export tariff hierarchies
- **Regulation Lookup**: Quick access to trade rules and restrictions

## 🚨 UX Constraints

### **DO NOT CHANGE**
- **Customs workflow sequences** - Established customs procedures must be maintained
- **Data entry forms** - Customs declaration forms follow government standards
- **Calculation displays** - Duty and tax calculation presentation is critical
- **Status indicators** - Compliance and processing status displays
- **Client switching** - Multi-tenant client selection and isolation

### **PRESERVE ALWAYS**
- **Data validation feedback** - Immediate validation of customs data
- **Error handling** - Clear error messages for customs compliance issues
- **Loading states** - Progress indicators for government API calls
- **Confirmation dialogs** - Verification for critical customs operations
- **Audit trail displays** - Complete activity logging visibility

## 🎨 Customs Component Guidelines

### **Customs Declaration Forms**
```typescript
// Example: Customs declaration form structure
interface CustomsDeclarationForm {
  clientInfo: ClientSelector        // Multi-tenant client selection
  declarationType: DeclarationType  // Import/Export selection
  commodities: CommodityList       // HS code and description
  valuation: ValuationSection      // Customs value and currency
  dutyCalculation: DutyDisplay     // Calculated duties and taxes
  documents: DocumentUpload        // Required customs documents
  compliance: ComplianceCheck      // Regulatory validation status
}
```

### **Tariff Classification Interface**
```typescript
// Example: HS code classification component
interface HSCodeLookup {
  searchInput: string              // Product description search
  suggestions: HSCodeSuggestion[]  // Matching HS codes
  selectedCode: string             // Selected HS code
  dutyRate: number                // Associated duty rate
  restrictions: string[]           // Import/export restrictions
  tradeAgreements: FTARate[]      // Available FTA rates
}
```

## 📱 Responsive Behavior for Customs Operations

### **Desktop First (Primary Use)**
- **Multi-panel layout** - Side-by-side customs forms and reference data
- **Data tables** - Comprehensive commodity and calculation displays
- **Document preview** - Full-size document viewing and editing
- **Advanced search** - Complex tariff classification searches

### **Tablet Support**
- **Collapsible panels** - Adaptive layout for customs forms
- **Touch-friendly inputs** - Larger touch targets for data entry
- **Simplified navigation** - Streamlined customs workflow steps

### **Mobile Support (Limited)**
- **Status checking** - View declaration status and tracking
- **Basic data entry** - Simple customs data updates
- **Document capture** - Camera integration for document upload
- **Emergency access** - Critical customs operations only

## 🔍 Customs-Specific UI Patterns

### **HS Code Classification Interface**
```typescript
// Critical UX pattern for tariff classification
interface HSCodeClassifier {
  productDescription: TextArea     // Detailed product description
  hsCodeSearch: SearchInput       // HS code lookup
  classificationTree: TreeView    // Hierarchical HS code navigation
  dutyRateDisplay: RateCard       // Duty rate and FTA options
  complianceIndicators: StatusBadge[]  // Regulatory compliance status
}
```

### **Duty Calculator Display**
```typescript
// Essential UX for financial calculations
interface DutyCalculatorUI {
  customsValue: CurrencyInput     // Declared value input
  dutyRate: PercentageDisplay     // Applied duty rate
  dutyAmount: CurrencyDisplay     // Calculated duty
  taxBreakdown: TaxSummary       // Detailed tax calculations
  totalAmount: TotalDisplay       // Total duties and taxes
  ftaOptions: FTASelector        // Trade agreement options
}
```

### **Compliance Status Dashboard**
```typescript
// Critical compliance monitoring interface
interface ComplianceDashboard {
  overallStatus: StatusIndicator   // Overall compliance status
  validationChecks: CheckList     // Individual compliance checks
  requiredDocuments: DocumentList // Missing or required documents
  restrictionAlerts: AlertList    // Import/export restrictions
  deadlineTracker: DeadlineList   // Important customs deadlines
}
```

## 📊 Data Visualization for Customs

### **Customs Declaration Status Flow**
- **Visual workflow** - Clear progression through customs stages
- **Status indicators** - Color-coded status for each stage
- **Timeline view** - Historical progression of declarations
- **Alert notifications** - Immediate alerts for issues or deadlines

### **Duty and Tax Breakdown**
- **Calculation transparency** - Clear breakdown of all charges
- **Rate comparisons** - Standard vs. FTA rate comparisons
- **Historical trends** - Duty rate changes over time
- **Cost analysis** - Total landed cost calculations

## 🔍 Testing Requirements

### **Customs UX Validation Checklist**
- [ ] All customs forms are accessible via keyboard navigation
- [ ] HS code lookup provides accurate and fast results
- [ ] Duty calculations display with proper precision (2 decimal places)
- [ ] Compliance status is clearly visible and actionable
- [ ] Client switching maintains data isolation
- [ ] Document upload supports required customs document types
- [ ] Error messages provide clear guidance for customs compliance
- [ ] Mobile interface supports essential customs operations

## 🎯 Success Metrics for Customs UX

### **User Experience KPIs**
- **Declaration Completion Time**: < 15 minutes for standard declarations
- **HS Code Classification Accuracy**: > 95% first-time accuracy
- **Duty Calculation Speed**: < 2 seconds for calculations
- **Compliance Error Rate**: < 1% compliance validation errors
- **User Task Success Rate**: > 98% for core customs operations

### **Performance Standards**
- **Page Load Time**: < 2 seconds for customs forms
- **Search Response Time**: < 500ms for HS code lookup
- **Calculation Response**: < 1 second for duty calculations
- **Document Upload**: < 30 seconds for standard documents

## 🚨 Critical UX Constraints

### **Customs Workflow Integrity**
- **Sequential validation** - Each step must validate before proceeding
- **Data persistence** - Form data must be saved automatically
- **Error recovery** - Clear path to resolve validation errors
- **Confirmation steps** - Critical operations require confirmation
- **Audit visibility** - All changes must be visible and traceable

### **Multi-Tenant UX Requirements**
- **Client identification** - Always show current client context
- **Data isolation** - No cross-client data visibility
- **Client switching** - Secure and clear client selection process
- **Permission-based UI** - Interface adapts to user permissions
- **Branding support** - Client-specific branding where appropriate

## 📝 Accessibility for Customs Professionals

### **WCAG 2.1 AA Compliance**
- **Keyboard navigation** - Full keyboard access to all customs functions
- **Screen reader support** - Proper ARIA labels for customs data
- **Color contrast** - High contrast for detailed customs information
- **Text scaling** - Support for enlarged text in customs forms
- **Focus indicators** - Clear focus states for form navigation

### **Professional Accessibility Features**
- **Keyboard shortcuts** - Quick access to common customs operations
- **Bulk operations** - Efficient handling of multiple declarations
- **Data export** - Accessible export of customs data and reports
- **Print optimization** - Proper formatting for customs documents

## 📝 Notes for Claude

When making fixes:
1. **Preserve customs workflows** - Don't break established customs procedures
2. **Maintain data accuracy** - Ensure all customs data displays correctly
3. **Keep validation feedback** - Preserve immediate validation responses
4. **Preserve client isolation** - Maintain multi-tenant UI separation
5. **Test calculations** - Verify duty and tax calculations display properly
6. **Maintain compliance indicators** - Keep regulatory status displays intact

## 🔗 Related Documentation
- Customs Broker User Manual
- Government Customs System Integration Guide
- Tariff Classification Guidelines
- Multi-Tenant Security Requirements
- Accessibility Standards for Government Systems

## 🎨 Design System Components

### **Customs-Specific Components**
- **HSCodeSelector** - Tariff classification component
- **DutyCalculator** - Financial calculation display
- **ComplianceIndicator** - Regulatory status component
- **ClientSelector** - Multi-tenant client switching
- **DocumentUploader** - Customs document management
- **DeclarationForm** - Structured customs declaration input
- **StatusTracker** - Declaration processing status
- **AuditTrail** - Activity logging display

### **Color Coding Standards**
- **Green**: Compliant, approved, cleared
- **Yellow**: Pending, under review, warnings
- **Red**: Non-compliant, rejected, errors
- **Blue**: Information, neutral status
- **Gray**: Inactive, disabled, archived

Remember: The customs broker interface must be professional, accurate, and efficient. Any UX changes must support the critical nature of customs compliance and international trade operations.