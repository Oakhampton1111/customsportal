# ⚠️ Critical Constraints & Limitations for Claude Auto-Fix - Customs Broker Portal

## 📋 Overview
This document defines the critical constraints, limitations, and "DO NOT TOUCH" areas that Claude must absolutely respect when making code fixes for the Customs Broker Portal. This is a **reference and research portal** providing synthesized insights from government data sources. Violating these constraints could break data accuracy, compromise calculation integrity, or provide incorrect regulatory information.

## 🚨 CRITICAL - DO NOT MODIFY

### **Reference Data & Calculation Logic**
- **Tariff classification algorithms** - HS code lookup and classification logic
- **Duty calculation formulas** - All financial calculation algorithms must remain exact
- **FTA rate calculations** - Free trade agreement rate application logic
- **TCO calculation logic** - Tariff Concession Order duty calculations
- **GST calculation engines** - Goods and Services Tax calculation formulas
- **Schedule 3 tariff data** - Import tariff reference data structure
- **Export tariff data** - Export classification and rate data

### **Government Data Integrity**
- **Official rate tables** - Government-sourced duty and tax rates
- **HS code databases** - Official tariff classification data
- **Trade agreement data** - FTA rates and eligibility rules
- **TCO databases** - Tariff concession order information
- **Regulatory data sync** - Government data synchronization logic
- **Data validation rules** - Accuracy checks for government data

### **Research Portal Functionality**
- **Calculation engines** - Comprehensive duty and cost calculators
- **Comparison algorithms** - Rate comparison and optimization logic
- **Search and lookup systems** - Fast tariff and regulation search
- **Data synthesis logic** - Combining insights from multiple sources
- **Reference data caching** - Performance optimization for lookups

## 🔒 Security Constraints

### **Customs Data Protection**
```typescript
// NEVER MODIFY: Client data isolation
function enforceClientIsolation(query: any, user: User): any {
  // Always filter by user's client - CRITICAL for customs data security
  return { ...query, clientId: user.clientId }
}

// NEVER BYPASS: Customs compliance validation
function validateCustomsCompliance(declaration: CustomsDeclaration): boolean {
  // This validation ensures regulatory compliance
  return validateHSCode(declaration.hsCode) &&
         validateOrigin(declaration.origin) &&
         validateDocuments(declaration.documents) &&
         validateRestrictions(declaration.commodity)
}

// NEVER CHANGE: Duty calculation precision
function calculateDuty(customsValue: number, dutyRate: number): number {
  // Financial precision is legally required - DO NOT MODIFY
  return Math.round((customsValue * dutyRate / 100) * 100) / 100
}
```

### **Trade Data Security**
- **Commercial invoice data** - Sensitive business information protection
- **Customs declarations** - Official government document integrity
- **Trade certificates** - Certificate of origin and compliance documents
- **Client credentials** - Customs broker license and authorization data
- **Government API keys** - Customs authority system access tokens

## 💾 Data Integrity Constraints

### **Customs Database Operations**
```sql
-- NEVER MODIFY: Critical customs database constraints
ALTER TABLE customs_declarations ADD CONSTRAINT valid_hs_code 
  CHECK (hs_code ~ '^\d{4}\.\d{2}(\.\d{2})?$');

-- NEVER REMOVE: Client data isolation
ALTER TABLE customs_declarations ADD CONSTRAINT fk_client_isolation 
  FOREIGN KEY (client_id) REFERENCES clients(id);

-- NEVER CHANGE: Audit trail triggers
CREATE TRIGGER audit_customs_changes 
  BEFORE UPDATE ON customs_declarations 
  FOR EACH ROW EXECUTE FUNCTION log_customs_audit();

-- NEVER MODIFY: Duty calculation precision
ALTER TABLE duty_calculations ADD CONSTRAINT duty_precision 
  CHECK (duty_amount = ROUND(duty_amount, 2));
```

### **Trade Data Validation**
- **HS code format validation** - International standard format enforcement
- **Country code validation** - ISO country code compliance
- **Currency code validation** - ISO currency code standards
- **Document type validation** - Customs document type standards
- **Compliance status validation** - Regulatory status requirements

## 🔄 Business Logic Constraints

### **Customs Calculations**
```typescript
// NEVER MODIFY: Tariff classification logic
const HS_CODE_RULES = {
  CHAPTER_RANGE: [1, 99],           // Valid HS chapters
  HEADING_DIGITS: 4,                // HS heading length
  SUBHEADING_DIGITS: 6,             // HS subheading length
  TARIFF_ITEM_DIGITS: 8,            // National tariff item length
  STATISTICAL_DIGITS: 10            // Statistical suffix length
}

// NEVER CHANGE: Trade agreement rate application
function applyFTARate(baseRate: number, ftaRate: number, origin: string, destination: string): number {
  // FTA rate application is governed by trade agreements
  if (isEligibleForFTA(origin, destination)) {
    return Math.min(baseRate, ftaRate)  // Apply most favorable rate
  }
  return baseRate
}

// NEVER MODIFY: Customs valuation methods
enum ValuationMethod {
  TRANSACTION_VALUE = 'transaction_value',      // Primary method
  IDENTICAL_GOODS = 'identical_goods',          // Secondary method
  SIMILAR_GOODS = 'similar_goods',              // Tertiary method
  DEDUCTIVE_VALUE = 'deductive_value',          // Quaternary method
  COMPUTED_VALUE = 'computed_value',            // Quinary method
  FALLBACK_METHOD = 'fallback_method'           // Last resort method
}
```

### **Compliance Workflow Rules**
- **Declaration status transitions** - Valid customs status changes
- **Document submission sequences** - Required document order
- **Payment processing flows** - Duty and tax payment procedures
- **Clearance authorization** - Customs release procedures
- **Appeal and review processes** - Dispute resolution workflows

## 🏗️ Architecture Constraints

### **Customs System Architecture**
- **Government API integrations** - Customs authority system connections
- **Trade database synchronization** - Tariff and trade data updates
- **Document management systems** - Electronic document storage and retrieval
- **Payment gateway integrations** - Secure duty and tax payment processing
- **Audit and reporting systems** - Compliance and regulatory reporting

### **Integration Points**
```typescript
// NEVER MODIFY: Government API integration contracts
interface CustomsAuthorityAPI {
  // This structure is mandated by customs authorities
  submitDeclaration(declaration: CustomsDeclaration): Promise<SubmissionResult>
  validateHSCode(hsCode: string): Promise<ValidationResult>
  calculateDuty(request: DutyCalculationRequest): Promise<DutyResult>
  checkCompliance(declaration: CustomsDeclaration): Promise<ComplianceResult>
}

// NEVER CHANGE: Trade data synchronization
interface TradeDataSync {
  // Synchronization with international trade databases
  updateTariffRates(): Promise<void>
  syncTradeAgreements(): Promise<void>
  refreshCurrencyRates(): Promise<void>
  updateRestrictedGoods(): Promise<void>
}
```

## 📊 Performance Constraints

### **Customs Processing Requirements**
- **Tariff lookup performance** - Sub-second HS code classification
- **Duty calculation speed** - Real-time financial calculations
- **Compliance validation time** - Rapid regulatory checks
- **Document generation speed** - Fast customs declaration creation
- **Data synchronization** - Timely trade data updates

### **System Resource Limits**
```typescript
// NEVER MODIFY: Customs system resource limits
const CUSTOMS_LIMITS = {
  MAX_DECLARATIONS_PER_CLIENT: 10000,      // Client declaration limit
  MAX_DOCUMENT_SIZE: 50 * 1024 * 1024,     // 50MB document limit
  MAX_CONCURRENT_VALIDATIONS: 100,         // Compliance check limit
  MAX_DUTY_CALCULATION_TIME: 5000,         // 5 second calculation limit
  MAX_API_REQUESTS_PER_MINUTE: 1000,       // Government API rate limit
  MAX_AUDIT_LOG_RETENTION: 2555            // 7 years audit retention
}
```

## 🔧 Technical Constraints

### **Customs Technology Stack**
- **Python FastAPI version** - Maintain API compatibility
- **React TypeScript version** - Keep frontend framework stable
- **PostgreSQL version** - Database version for customs data
- **Docker configurations** - Container deployment settings
- **Government API versions** - Customs authority API compatibility

### **Configuration Management**
```yaml
# NEVER MODIFY: Production customs environment
production:
  customs_api:
    base_url: ${CUSTOMS_API_URL}        # Government API endpoint
    timeout: 30000                      # 30 second timeout
    retry_attempts: 3                   # Retry for reliability
  
  trade_database:
    sync_interval: 3600                 # Hourly synchronization
    backup_retention: 2555              # 7 years retention
  
  compliance:
    audit_level: "full"                 # Complete audit logging
    retention_period: 2555              # Legal requirement
```

## 🚫 Forbidden Operations

### **NEVER DO THESE**
- **Bypass customs validation** - Could cause regulatory violations
- **Modify duty calculations** - Could cause financial discrepancies
- **Remove audit logging** - Could violate compliance requirements
- **Change client isolation** - Could cause data breaches
- **Alter trade agreement rules** - Could violate international agreements
- **Disable compliance checks** - Could cause regulatory penalties
- **Modify government API calls** - Could break customs integration
- **Change financial precision** - Could cause calculation errors

### **Code Patterns to Avoid**
```typescript
// NEVER DO: Bypass client isolation
if (user.role === 'admin') {
  // Don't allow admin to access all client data
  return getAllClientsData()  // FORBIDDEN
}

// NEVER DO: Skip customs validation
if (process.env.NODE_ENV === 'development') {
  // Don't skip validation in any environment
  return true  // FORBIDDEN
}

// NEVER DO: Modify duty calculations
function quickDutyCalc(value: number, rate: number): number {
  // Don't create shortcuts for financial calculations
  return value * rate  // FORBIDDEN - lacks precision
}

// NEVER DO: Expose sensitive customs data
console.log('Customs declaration:', declaration)  // FORBIDDEN
console.log('Client trade data:', clientData)     // FORBIDDEN
```

## 🔍 Monitoring & Alerting

### **Customs Compliance Monitoring**
- **Regulatory compliance checks** - Continuous compliance validation
- **Financial calculation accuracy** - Duty and tax calculation monitoring
- **Data integrity validation** - Trade data consistency checks
- **Client isolation verification** - Multi-tenant security monitoring
- **Audit trail completeness** - Complete activity logging verification

### **Alert Thresholds**
```typescript
// NEVER MODIFY: Critical customs alert thresholds
const CUSTOMS_ALERT_THRESHOLDS = {
  DUTY_CALCULATION_ERROR_RATE: 0.001,    // 0.1% error rate triggers alert
  COMPLIANCE_FAILURE_RATE: 0.005,        // 0.5% compliance failure alert
  CLIENT_DATA_BREACH_ATTEMPTS: 1,        // Any breach attempt alerts
  GOVERNMENT_API_FAILURE_RATE: 0.01,     // 1% API failure rate alert
  FINANCIAL_DISCREPANCY_AMOUNT: 0.01,    // $0.01 discrepancy alert
  AUDIT_LOG_GAPS: 0                      // Any audit gap triggers alert
}
```

## 📝 Compliance & Legal

### **Customs Regulatory Requirements**
- **WTO compliance** - World Trade Organization standards
- **Customs union rules** - Regional customs union requirements
- **Trade agreement compliance** - Bilateral and multilateral trade agreements
- **Anti-dumping regulations** - Trade remedy compliance
- **Customs valuation rules** - International valuation standards

### **Data Governance**
- **Trade data classification** - Sensitive commercial information protection
- **Customs document retention** - Legal document retention requirements
- **Cross-border data transfer** - International data transfer compliance
- **Audit trail preservation** - Complete activity logging requirements
- **Regulatory reporting** - Mandatory customs authority reporting

## 🎯 Testing Constraints

### **Critical Customs Test Coverage**
- **Duty calculation tests** - Never remove financial calculation tests
- **Compliance validation tests** - Preserve regulatory requirement tests
- **Client isolation tests** - Maintain multi-tenant security tests
- **Government API tests** - Keep customs authority integration tests
- **Audit logging tests** - Preserve compliance logging tests

## 📝 Notes for Claude

### **Before Making ANY Changes**
1. **Check customs impact** - Ensure no regulatory compliance is affected
2. **Verify financial accuracy** - Confirm duty calculations remain precise
3. **Validate client isolation** - Ensure multi-tenant security is maintained
4. **Test compliance checks** - Verify regulatory validations still work
5. **Confirm audit trails** - Ensure complete logging is preserved

### **When in Doubt**
- **Don't modify customs logic** - If unsure, leave customs calculations unchanged
- **Preserve compliance checks** - Keep all regulatory validations intact
- **Maintain audit trails** - Never remove or modify logging systems
- **Ask for clarification** - Request customs domain expert review
- **Focus on syntax only** - Fix syntax/import errors rather than business logic

## 🔗 Emergency Contacts

If Claude encounters customs-specific code that seems to violate these constraints:
- **Create detailed issue** - Document the customs compliance conflict
- **Flag for customs expert** - Require customs domain specialist review
- **Preserve existing logic** - Keep current customs implementation intact
- **Suggest manual review** - Recommend human customs expert intervention

## ⚖️ Legal Notice

**Remember: Customs and trade compliance is legally mandated. It's better to leave broken syntax than to break customs compliance, financial calculations, or regulatory requirements.**

**Any modifications to customs logic, duty calculations, or compliance validations could result in:**
- Regulatory penalties and fines
- Customs audit failures
- Financial discrepancies and losses
- Legal liability for customs brokers
- Loss of customs operating licenses