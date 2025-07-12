# 🏢 Business Rules & Logic for Claude Auto-Fix - Customs Broker Portal

## 📋 Overview
This document defines the core business rules, domain logic, and workflow constraints that Claude must preserve when making code fixes for the Customs Broker Portal. This is a **reference and research portal** - a live library for customs brokers to access synthesized insights on import/export regulations, tariffs, and duty calculations.

## 🎯 Core Business Principles

### **Reference Data Integrity & Accuracy**
- **Tariff Classification**: HS code classification algorithms must remain intact
- **Duty Calculations**: All duty rate formulas must preserve mathematical accuracy
- **Trade Agreements**: FTA rates and preference calculations cannot be modified
- **Government Data**: Official tariff and regulatory data must remain unaltered
- **Calculation Precision**: All financial calculations must maintain exact precision

### **Research Portal Functionality**
- **Data Synthesis**: Combining insights from multiple government sources
- **Real-time Accuracy**: Ensuring all reference data reflects current regulations
- **Comprehensive Coverage**: Schedule 3 tariffs, exports, TCOs, FTA rates, GST
- **User Research Tools**: Fast lookup, comparison, and calculation capabilities

## 🔄 Reference Portal Workflows

### **Core Research Process**
```
1. Product/Commodity Research
   ↓
2. HS Code Classification Lookup
   ↓
3. Tariff Rate Research (Schedule 3)
   ↓
4. FTA Rate Comparison
   ↓
5. TCO Eligibility Check
   ↓
6. Comprehensive Duty Calculation
   ↓
7. Synthesized Insights & Recommendations
```

### **Critical Research Functions**
- **Classification Accuracy**: HS code lookup must provide precise results
- **Rate Comparison**: Side-by-side comparison of standard vs FTA vs TCO rates
- **Calculation Precision**: All duty calculations must be mathematically exact
- **Data Currency**: All reference data must reflect current government rates
- **Comprehensive Coverage**: Include all relevant taxes, duties, and concessions

## 🏗️ Domain Models

### **Core Reference Data Entities**
```typescript
// Example: Core reference portal entities
interface TariffItem {
  hsCode: string            // 6-10 digit HS code
  description: string       // Product description
  schedule3Rate: number     // Standard Australian duty rate
  ftaRates: FTARate[]      // Free trade agreement rates
  tcoRates: TCORate[]      // Tariff Concession Order rates
  gstRate: number          // GST rate
  restrictions: string[]    // Import/export restrictions
  lastUpdated: Date        // Government data sync timestamp
}

interface DutyCalculator {
  customsValue: number      // FOB value
  hsCode: string           // Tariff classification
  origin: string           // Country of origin
  calculatedDuty: number   // Standard duty
  ftaDuty?: number         // FTA preferential duty
  tcoDuty?: number         // TCO concessional duty
  gstAmount: number        // GST calculation
  totalLandedCost: number  // Comprehensive cost
}

interface ReferenceData {
  tariffSchedule: TariffItem[]     // Schedule 3 import tariffs
  exportTariffs: ExportTariff[]    // Export classification data
  ftas: TradeAgreement[]           // Free trade agreements
  tcos: TariffConcession[]         // Tariff concession orders
  lastSyncDate: Date               // Government data currency
}

// Business rule: All data must reflect current government rates
```

### **Reference Portal Constraints**
- **Data Accuracy**: All rates must match current government sources
- **Calculation Precision**: Financial calculations must be exact
- **Comprehensive Coverage**: Include all relevant duties, taxes, and concessions
- **Real-time Currency**: Data must be current and regularly synchronized

## 📊 Customs Data Validation Rules

### **Tariff Classification Validation**
```typescript
// Example: Customs validation rules
interface CustomsValidationRules {
  hsCodeFormat: RegExp      // HS code format validation
  dutyRateRange: [number, number]  // Valid duty rate ranges
  originCountry: string[]   // Valid country codes
  tradeAgreements: Record<string, FTARate[]>  // FTA rate mappings
}

// Critical validation rules
const CUSTOMS_RULES = {
  HS_CODE_PATTERN: /^\d{4}\.\d{2}(\.\d{2})?$/,  // HS code format
  MAX_DUTY_RATE: 100,                           // Maximum duty rate %
  MIN_DUTY_RATE: 0,                            // Minimum duty rate %
  REQUIRED_DOCUMENTS: ['commercial_invoice', 'bill_of_lading'],
  COMPLIANCE_CHECKS: ['restricted_goods', 'prohibited_items', 'licensing']
}
```

### **Business Logic Validation**
- **Duty Calculation Rules**: Precise calculation based on value, quantity, and rates
- **Trade Agreement Rules**: Correct application of preferential rates
- **Compliance Rules**: Validation against customs regulations and restrictions
- **Document Rules**: Required documentation for different commodity types

## 🔐 Customs Security & Compliance

### **Regulatory Compliance**
```typescript
// Example: Compliance requirements
enum ComplianceStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  UNDER_REVIEW = 'under_review'
}

interface ComplianceCheck {
  checkType: string         // Type of compliance check
  status: ComplianceStatus  // Check result
  details: string          // Check details
  performedBy: string      // Who performed the check
  timestamp: Date          // When check was performed
}
```

### **Data Protection**
- **Trade Data Security**: Sensitive commercial information must be encrypted
- **Client Confidentiality**: Each client's trade data is confidential
- **Audit Logging**: All access and modifications must be logged
- **Regulatory Reporting**: Compliance with customs reporting requirements

## 💰 Financial & Duty Calculation Rules

### **Duty & Tax Calculations**
```typescript
// CRITICAL: These calculation formulas must NEVER be modified
interface DutyCalculation {
  customsValue: number      // Declared value for customs
  dutyRate: number         // Applicable duty rate
  dutyAmount: number       // Calculated duty
  gstAmount: number        // Goods and Services Tax
  totalTaxes: number       // Total taxes and duties
}

// Example calculation (DO NOT MODIFY)
function calculateDuty(customsValue: number, dutyRate: number): number {
  // This calculation is audited and must remain exact
  return Math.round((customsValue * dutyRate / 100) * 100) / 100
}

function calculateGST(customsValue: number, dutyAmount: number, gstRate: number): number {
  // GST calculated on customs value plus duty
  const gstBase = customsValue + dutyAmount
  return Math.round((gstBase * gstRate / 100) * 100) / 100
}
```

### **Trade Agreement Rates**
- **FTA Preferences**: Correct application of free trade agreement rates
- **Origin Rules**: Validation of country of origin for preferential rates
- **Certificate Requirements**: Required certificates for preferential treatment
- **Rate Calculations**: Precise calculation of preferential duty rates

## 📅 Customs Timing & Workflow Rules

### **Processing Deadlines**
- **Declaration Timing**: Import declarations must be lodged within specified timeframes
- **Payment Deadlines**: Duties and taxes must be paid by due dates
- **Document Submission**: Required documents must be provided within deadlines
- **Compliance Response**: Response to customs queries within regulatory timeframes

### **Workflow Timing**
- **Classification Review**: HS code classification review and approval
- **Duty Assessment**: Duty calculation and verification
- **Compliance Clearance**: Regulatory compliance validation
- **Release Authorization**: Customs clearance and cargo release

## 🚨 Critical Customs Constraints

### **DO NOT CHANGE**
- **Duty calculation formulas** - Financial accuracy is legally required
- **HS code classification logic** - Tariff classification must be precise
- **Trade agreement rules** - FTA rate application is regulated
- **Compliance validation** - Regulatory checks cannot be bypassed
- **Audit logging** - Complete audit trail is mandatory
- **Client data isolation** - Multi-tenant separation is critical

### **PRESERVE ALWAYS**
- **Customs compliance checks** - All regulatory validations
- **Financial calculation accuracy** - Duty and tax precision
- **Trade data integrity** - Commercial information accuracy
- **Client confidentiality** - Data separation and privacy
- **Regulatory reporting** - Compliance and audit requirements

## 🔍 Testing Requirements

### **Customs Business Logic Validation**
- [ ] All duty calculations produce correct results to 2 decimal places
- [ ] HS code classification follows international standards
- [ ] Trade agreement rates are correctly applied
- [ ] Compliance checks validate against current regulations
- [ ] Audit logs capture all required information
- [ ] Client data isolation is maintained
- [ ] Financial calculations are accurate and auditable

## 📈 Performance Requirements

### **Customs Process Performance**
- **Tariff Lookup**: < 500ms for HS code classification
- **Duty Calculation**: < 200ms for standard calculations
- **Compliance Validation**: < 2 seconds for regulatory checks
- **Document Generation**: < 5 seconds for customs declarations

## 📝 Integration Rules

### **Customs System Integration**
- **Government APIs**: Integration with customs authority systems
- **Trade Data**: Synchronization with international trade databases
- **Banking Systems**: Integration for duty and tax payments
- **Document Management**: Electronic document submission and storage

### **Third-party Services**
- **Customs Authorities**: Direct integration with government systems
- **Trade Databases**: Access to tariff and trade agreement data
- **Payment Processors**: Secure payment for duties and taxes
- **Document Verification**: Certificate and document validation services

## 🎯 Success Criteria

### **Customs Business KPIs**
- **Classification Accuracy**: 99.9% correct HS code assignments
- **Duty Calculation Accuracy**: 100% financial precision
- **Compliance Rate**: 100% regulatory compliance
- **Processing Time**: < 24 hours for standard declarations
- **Client Satisfaction**: > 95% client approval rating

## 📝 Notes for Claude

When making fixes:
1. **Preserve customs logic** - Never alter tariff classification or duty calculations
2. **Maintain compliance** - Keep all regulatory validation intact
3. **Respect client isolation** - Ensure multi-tenant data separation
4. **Preserve audit trails** - Keep complete logging of all operations
5. **Maintain financial accuracy** - Ensure precise duty and tax calculations
6. **Test thoroughly** - Validate customs business rules after any changes

## 🔗 Related Documentation
- Customs Regulations and Procedures
- Tariff Classification Guidelines
- Trade Agreement Documentation
- Compliance and Audit Requirements
- Multi-tenant Security Policies