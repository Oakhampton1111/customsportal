# 🔌 API Contracts & Specifications for Claude Auto-Fix - Customs Broker Portal

## 📋 Overview
This document defines the API contracts, data models, and service specifications that Claude must preserve when making code fixes for the Customs Broker Portal. This is a **reference and research portal** providing synthesized insights from government data sources. These contracts ensure API compatibility and reference data integrity.

## 🎯 API Design Principles

### **Reference Portal Standards**
- **RESTful Design**: Standard HTTP methods for research and lookup operations
- **Data Accuracy**: Precise representation of government reference data
- **Performance Optimized**: Fast lookup and comparison operations
- **Financial Precision**: Exact decimal precision for duty calculations
- **Government Data Sync**: Compatible with official data sources

### **API Versioning**
- **Version Strategy**: Semantic versioning (v1, v2, etc.)
- **Backward Compatibility**: Maintain existing customs integrations
- **Deprecation Policy**: Gradual deprecation with customs broker notice
- **Migration Paths**: Clear upgrade paths for customs system integrations

## 🔗 Core Customs API Endpoints

### **Authentication & Multi-Tenant Access**
```typescript
// POST /api/v1/auth/login
interface CustomsLoginRequest {
  email: string
  password: string
  clientId?: string     // Optional client context
  remember?: boolean
}

interface CustomsLoginResponse {
  token: string
  refreshToken: string
  user: CustomsUser
  availableClients: Client[]  // Multi-tenant client access
  permissions: CustomsPermission[]
  expiresIn: number
}

// POST /api/v1/auth/switch-client
interface ClientSwitchRequest {
  clientId: string
  token: string
}

interface ClientSwitchResponse {
  token: string         // New token with client context
  client: Client
  permissions: CustomsPermission[]
}
```

### **Customs Declaration Management**
```typescript
// GET /api/v1/declarations
interface DeclarationsListResponse {
  data: CustomsDeclaration[]
  pagination: PaginationMeta
  filters: DeclarationFilters
  summary: DeclarationSummary
}

// POST /api/v1/declarations
interface CreateDeclarationRequest {
  clientId: string
  declarationType: 'import' | 'export'
  commodities: CommodityItem[]
  valuation: CustomsValuation
  documents: DocumentReference[]
}

// GET /api/v1/declarations/:id
interface DeclarationDetailResponse {
  data: CustomsDeclaration
  dutyCalculation: DutyBreakdown
  complianceStatus: ComplianceCheck[]
  auditTrail: AuditEntry[]
  relatedDocuments: Document[]
}
```

### **Tariff Classification & HS Codes**
```typescript
// GET /api/v1/tariff/search
interface HSCodeSearchRequest {
  query: string         // Product description
  chapter?: string      // HS chapter filter
  country?: string      // Country-specific codes
  limit?: number
}

interface HSCodeSearchResponse {
  data: HSCodeResult[]
  suggestions: string[]
  totalResults: number
}

// GET /api/v1/tariff/classify/:hsCode
interface HSCodeDetailResponse {
  hsCode: string
  description: string
  dutyRate: number
  ftaRates: FTARate[]
  restrictions: TradeRestriction[]
  relatedCodes: string[]
}
```

### **Duty & Tax Calculations**
```typescript
// POST /api/v1/calculations/duty
interface DutyCalculationRequest {
  customsValue: number
  currency: string
  hsCode: string
  origin: string
  destination: string
  tradeAgreement?: string
}

interface DutyCalculationResponse {
  customsValue: number
  dutyRate: number
  dutyAmount: number      // Precise to 2 decimal places
  gstAmount: number
  totalTaxes: number
  ftaEligible: boolean
  ftaRate?: number
  breakdown: TaxBreakdown[]
}
```

## 📊 Customs Data Models

### **Core Customs Entities**
```typescript
interface CustomsDeclaration {
  id: string
  clientId: string           // Multi-tenant isolation
  declarationNumber: string  // Government-assigned number
  declarationType: 'import' | 'export'
  status: DeclarationStatus
  commodities: CommodityItem[]
  totalValue: number
  totalDuty: number
  totalTaxes: number
  submittedAt?: string
  clearedAt?: string
  createdAt: string
  updatedAt: string
}

interface CommodityItem {
  id: string
  hsCode: string            // Tariff classification
  description: string       // Product description
  quantity: number
  unitOfMeasure: string
  unitValue: number
  totalValue: number
  dutyRate: number
  dutyAmount: number
  origin: string           // Country of origin
  restrictions: string[]   // Import/export restrictions
}

interface Client {
  id: string
  companyName: string
  customsLicense: string    // Customs broker license
  clientCode: string        // Unique client identifier
  contactInfo: ContactInfo
  settings: ClientSettings
  isActive: boolean
  createdAt: string
}
```

### **Financial & Calculation Models**
```typescript
interface DutyBreakdown {
  customsValue: number      // Base value for calculations
  dutyRate: number         // Applied duty rate percentage
  dutyAmount: number       // Calculated duty (2 decimal precision)
  gstRate: number          // GST/VAT rate
  gstAmount: number        // Calculated GST/VAT
  otherTaxes: TaxItem[]    // Additional taxes and fees
  totalAmount: number      // Total duties and taxes
  currency: string         // Currency code (ISO 4217)
  exchangeRate?: number    // If currency conversion applied
}

interface FTARate {
  agreement: string        // Trade agreement name
  rate: number            // Preferential duty rate
  eligible: boolean       // Eligibility for preference
  requirements: string[]  // Certificate requirements
  originRules: string[]   // Rules of origin
}
```

## 🔐 Authentication & Authorization

### **JWT Token Structure for Customs**
```typescript
interface CustomsJWTPayload {
  sub: string              // User ID
  email: string            // User email
  role: CustomsRole        // Customs-specific role
  clientId: string         // Current client context
  permissions: string[]    // Customs permissions
  customsLicense: string   // Customs broker license
  iat: number             // Issued at
  exp: number             // Expires at
}

enum CustomsRole {
  CUSTOMS_BROKER = 'customs_broker',
  SENIOR_CLERK = 'senior_clerk',
  CUSTOMS_CLERK = 'customs_clerk',
  CLIENT_USER = 'client_user',
  VIEWER = 'viewer'
}
```

### **Customs-Specific Security Headers**
```typescript
interface CustomsSecurityHeaders {
  'Authorization': 'Bearer <jwt-token>'
  'Content-Type': 'application/json'
  'X-API-Version': 'v1'
  'X-Request-ID': string      // For audit tracing
  'X-Client-ID': string       // Multi-tenant context
  'X-Customs-License': string // Customs broker license
}
```

## 📝 Customs Request Validation

### **Customs-Specific Validation Rules**
```typescript
interface CustomsValidationRules {
  // HS Code validation
  hsCode: {
    required: true
    pattern: /^\d{4}\.\d{2}(\.\d{2})?$/  // HS code format
    length: { min: 7, max: 10 }
  }
  
  // Financial validation
  customsValue: {
    required: true
    type: 'number'
    min: 0
    precision: 2              // 2 decimal places
  }
  
  // Country code validation
  origin: {
    required: true
    enum: ISO_COUNTRY_CODES   // Valid country codes
    length: 2
  }
  
  // Currency validation
  currency: {
    required: true
    enum: ISO_CURRENCY_CODES  // Valid currency codes
    length: 3
  }
}
```

### **Business Rule Validations**
```typescript
interface CustomsBusinessValidation {
  // Multi-tenant validation
  clientAccess: (userId: string, clientId: string) => Promise<boolean>
  
  // Customs compliance validation
  hsCodeCompliance: (hsCode: string, origin: string) => Promise<boolean>
  
  // Financial validation
  dutyCalculationAccuracy: (calculation: DutyCalculation) => boolean
  
  // Document validation
  requiredDocuments: (declarationType: string, hsCode: string) => string[]
}
```

## 🔄 Customs API Response Patterns

### **Success Responses**
```typescript
// Customs declaration list
interface CustomsListResponse<T> {
  success: true
  data: T[]
  pagination: PaginationMeta
  summary: {
    totalDeclarations: number
    pendingDeclarations: number
    totalValue: number
    totalDuties: number
  }
}

// Duty calculation response
interface DutyCalculationResponse {
  success: true
  data: DutyBreakdown
  ftaOptions: FTARate[]
  warnings: string[]        // Compliance warnings
  recommendations: string[] // Cost optimization suggestions
}
```

### **Customs Error Responses**
```typescript
// Compliance validation error
interface ComplianceErrorResponse {
  success: false
  error: {
    code: 'COMPLIANCE_VIOLATION'
    message: 'Customs compliance validation failed'
    details: {
      hsCode: string
      violations: string[]
      requiredDocuments: string[]
      restrictions: string[]
    }
  }
}

// Financial calculation error
interface CalculationErrorResponse {
  success: false
  error: {
    code: 'CALCULATION_ERROR'
    message: 'Duty calculation failed'
    details: {
      field: string
      expectedRange: [number, number]
      actualValue: number
    }
  }
}
```

## 🔍 Customs Query Parameters

### **Declaration Filtering**
```typescript
interface DeclarationQueryParams {
  // Pagination
  page?: number
  limit?: number
  
  // Filtering
  status?: DeclarationStatus
  dateFrom?: string         // ISO date
  dateTo?: string          // ISO date
  clientId?: string        // Multi-tenant filter
  declarationType?: 'import' | 'export'
  
  // Searching
  search?: string          // Text search
  hsCode?: string         // Tariff classification filter
  
  // Sorting
  sort?: string           // Sort field
  order?: 'asc' | 'desc'  // Sort direction
}
```

### **Tariff Search Parameters**
```typescript
interface TariffSearchParams {
  q: string               // Product description
  chapter?: string        // HS chapter (01-99)
  country?: string        // Country-specific codes
  tradeAgreement?: string // FTA filter
  includeRestrictions?: boolean
  includeFTARates?: boolean
  limit?: number
  offset?: number
}
```

## 🔄 Government API Integration

### **Customs Authority API Contracts**
```typescript
// Government customs submission
interface GovernmentSubmissionRequest {
  declarationNumber: string
  declarationType: 'import' | 'export'
  commodities: GovernmentCommodity[]
  totalValue: number
  submitterLicense: string  // Customs broker license
  clientReference: string
}

interface GovernmentSubmissionResponse {
  submissionId: string
  status: 'accepted' | 'rejected' | 'pending'
  referenceNumber: string
  estimatedProcessingTime: number
  requiredActions: string[]
}
```

## 🚨 API Constraints

### **DO NOT CHANGE**
- **Endpoint URLs** - Maintain existing customs API paths
- **Response schemas** - Keep customs data structure intact
- **Financial precision** - Preserve 2-decimal place accuracy
- **Multi-tenant isolation** - Maintain client data separation
- **Government API contracts** - Keep customs authority integration

### **PRESERVE ALWAYS**
- **Audit trail data** - Complete activity logging in responses
- **Compliance validation** - Regulatory check results
- **Financial calculations** - Exact duty and tax calculations
- **Client isolation** - Multi-tenant data security
- **Error handling** - Customs-specific error responses

## 📊 Performance Requirements

### **Customs API Performance Standards**
- **HS Code Lookup**: < 500ms for tariff classification
- **Duty Calculation**: < 200ms for financial calculations
- **Declaration Submission**: < 2s for government API calls
- **Compliance Validation**: < 1s for regulatory checks
- **Document Upload**: < 30s for customs documents

## 🔍 Testing Requirements

### **Customs API Testing Checklist**
- [ ] All endpoints maintain multi-tenant isolation
- [ ] Financial calculations return exact precision
- [ ] HS code validation follows international standards
- [ ] Compliance checks validate against current regulations
- [ ] Government API integration handles all response scenarios
- [ ] Audit trails capture all required information
- [ ] Error responses provide actionable guidance

## 📝 Notes for Claude

When making fixes:
1. **Preserve API contracts** - Don't change customs endpoint signatures
2. **Maintain financial precision** - Keep exact decimal calculations
3. **Respect multi-tenancy** - Ensure client data isolation
4. **Keep compliance validation** - Preserve regulatory checks
5. **Maintain audit trails** - Ensure complete activity logging
6. **Test government integration** - Verify customs authority API compatibility

## 🔗 Related Documentation
- Government Customs API Documentation
- Multi-Tenant Security Specifications
- Financial Calculation Standards
- Customs Compliance Requirements
- International Trade Data Standards

## 🎯 API Success Metrics

### **Customs API KPIs**
- **Response Time**: < 500ms for 95% of requests
- **Accuracy**: 100% for financial calculations
- **Availability**: 99.9% uptime for customs operations
- **Compliance**: 100% regulatory validation accuracy
- **Security**: Zero data breaches or cross-client access

Remember: Customs APIs must maintain absolute accuracy, complete audit trails, and strict multi-tenant isolation. Any changes must preserve customs compliance and financial precision.