# Customs Broker Portal - Browserless API Migration PRD

## Document Information
- **Document Type**: Technical Product Requirements Document (PRD)
- **Project**: Customs Broker Portal Scraping Infrastructure Migration
- **Version**: 1.0
- **Date**: 2025-05-31
- **Author**: Technical Architecture Team
- **Status**: DRAFT - Ready for Implementation

## Executive Summary

This PRD outlines the complete migration strategy from the current complex scraping infrastructure to Browserless API for the Australian Customs Broker Portal. The migration addresses critical reliability, maintainability, and detection issues while preserving all existing data flows and database dependencies.

### Migration Scope
- **Current Implementation**: 31,671 lines of complex scraping code across multiple Australian government sites
- **Target Implementation**: Browserless API with BrowserQL queries
- **Database Impact**: Zero schema changes required - all existing tables and relationships preserved
- **Data Sources**: ABF Working Tariff, FTA rates, Anti-dumping duties, TCOs, GST provisions, Export codes

## 1. Current State Analysis

### 1.1 Database Schema Dependencies

The database schema consists of **14 core tables** with complex interdependencies:

#### Core Hierarchy (CRITICAL - No Changes Allowed)
```sql
tariff_codes (PRIMARY)
├── duty_rates (FK: hs_code)
├── fta_rates (FK: hs_code)
├── dumping_duties (FK: hs_code)
├── tcos (FK: hs_code)
├── gst_provisions (FK: hs_code)
└── export_codes (FK: corresponding_import_code)
```

#### Supporting Tables
```sql
trade_agreements (FK referenced by fta_rates.fta_code)
tariff_sections (FK referenced by tariff_codes.section_id)
tariff_chapters (FK referenced by tariff_codes.chapter_id)
product_classifications (AI enhancement table)
```

### 1.2 Current Scraping Architecture

#### Existing Scrapers (TO BE REPLACED)
1. **ABFTariffScraper** (`abf_tariff_scraper.py` - 31,671 lines)
   - Targets: Schedule 3 Working Tariff
   - Complexity: Hierarchical navigation through sections → chapters → headings → items
   - Issues: Complex async logic, brittle selectors, detection vulnerability

2. **FTAScraper** (Inferred from config)
   - Targets: FTA preferential rates from multiple agreements
   - Dependencies: trade_agreements table for FTA codes

3. **AntiDumpingScraper** (Inferred from config)
   - Targets: Anti-Dumping Commission measures
   - Dependencies: dumping_duties table

4. **TCOScraper** (Inferred from config)
   - Targets: Tariff Concession Orders
   - Dependencies: tcos table

5. **GSTScraper** (Inferred from config)
   - Targets: GST exemptions and provisions
   - Dependencies: gst_provisions table

6. **ExportScraper** (Inferred from config)
   - Targets: AHECC export classifications
   - Dependencies: export_codes table

### 1.3 Data Flow Dependencies (CRITICAL)

```
Australian Government Sites
├── ABF Working Tariff → tariff_codes (PARENT TABLE)
├── FTA Schedules → fta_rates → trade_agreements
├── Anti-Dumping Commission → dumping_duties
├── TCO Database → tcos
├── GST Legislation → gst_provisions
└── AHECC Classifications → export_codes
```

**CRITICAL CONSTRAINT**: `tariff_codes` table MUST be populated FIRST as all other tables have foreign key dependencies on `hs_code`.

## 2. Migration Strategy

### 2.1 Phased Approach (MANDATORY SEQUENCE)

#### Phase 1: Infrastructure Setup (Week 1)
**Objective**: Establish Browserless API integration without disrupting existing systems

**Deliverables**:
1. Browserless API account and authentication setup
2. New `browserless_scraper.py` base class
3. Configuration updates for API credentials
4. Proof-of-concept with single ABF section

**Success Criteria**:
- Browserless API successfully extracts data from one ABF tariff section
- Data quality matches or exceeds current implementation
- No impact on existing database operations

#### Phase 2: Core Tariff Migration (Week 2-3)
**Objective**: Replace ABF Working Tariff scraper while maintaining data integrity

**CRITICAL SEQUENCE**:
1. **ABF Sections Scraper** (Day 1-2)
   - Extract all 21 tariff sections
   - Populate `tariff_sections` table
   
2. **ABF Chapters Scraper** (Day 3-4)
   - Extract all 99 chapters within sections
   - Populate `tariff_chapters` table
   
3. **ABF Tariff Codes Scraper** (Day 5-10)
   - Extract hierarchical HS codes (2,4,6,8,10 digit levels)
   - Populate `tariff_codes` table with parent-child relationships
   - **MUST COMPLETE BEFORE PHASE 4**

4. **ABF Duty Rates Scraper** (Day 11-15)
   - Extract general duty rates for all HS codes
   - Populate `duty_rates` table

**Success Criteria**:
- All tariff_codes records successfully migrated
- Hierarchical relationships intact (parent_code → hs_code)
- Duty rates correctly linked to HS codes
- Zero data loss compared to current implementation

#### Phase 4: Legacy Cleanup and Optimization (Week 5)
**Objective**: Remove old infrastructure and optimize new system

**Activities**:
1. **Decommission Old Scrapers**:
   - Remove all legacy scraper scripts and configurations
   - Disable any scheduled tasks or cron jobs
   - Update documentation to reflect new architecture

2. **Remove Unused Dependencies**:
   - Identify and remove any unused libraries or modules
   - Update `requirements.txt` to reflect new dependencies
   - Run `pip` to ensure all dependencies are up-to-date

3. **Update Documentation**:
   - Update all documentation to reflect new Browserless API architecture
   - Include new BrowserQL query templates and examples
   - Review and update all technical guides and tutorials

4. **Performance Optimization**:
   - Review and optimize all BrowserQL queries for performance
   - Implement caching mechanisms for frequently accessed data
   - Monitor and analyze performance metrics to identify areas for improvement

5. **Monitoring Setup**:
   - Set up monitoring and alerting for scraping failures and errors
   - Configure logging and error tracking for all scrapers
   - Review and update all monitoring and alerting configurations

### 2.2 Technical Implementation

#### 2.2.1 New Browserless Architecture

```python
# New base class structure
class BrowserlessScraper(BaseScraper):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://chrome.browserless.io"
    
    async def execute_bql_query(self, query: str) -> dict:
        """Execute BrowserQL query with built-in anti-detection"""
        
    async def scrape_with_pagination(self, base_query: str) -> List[dict]:
        """Handle paginated results automatically"""
        
    async def extract_hierarchical_data(self, root_url: str) -> dict:
        """Extract nested data structures efficiently"""
```

#### 2.2.2 BrowserQL Query Templates

**ABF Tariff Sections**:
```javascript
mutation ScrapeABFSections {
  goto(url: "https://www.abf.gov.au/importing-exporting-and-manufacturing/tariff-classification/current-tariff/schedule-3", waitUntil: networkIdle) {
    status
  }
  
  sections: elements(selector: "a[href*='section']") {
    sectionNumber: text
    sectionUrl: attribute(name: "href")
    title: text
  }
  
  solve(type: turnstile) {
    found
    solved
  }
}
```

**ABF Tariff Codes (Hierarchical)**:
```javascript
mutation ScrapeABFTariffCodes($sectionUrl: String!) {
  goto(url: $sectionUrl, waitUntil: networkIdle) {
    status
  }
  
  tariffItems: elements(selector: ".tariff-item") {
    hsCode: text
    description: text
    unitDescription: text
    parentCode: text
    level: text
  }
  
  dutyRates: elements(selector: ".duty-rate") {
    hsCode: text
    generalRate: text
    rateType: text
    rateText: text
  }
}
```

#### 2.2.3 Data Transformation Pipeline

```python
class DataTransformer:
    """Transform Browserless API responses to database records"""
    
    @staticmethod
    def transform_tariff_code(raw_data: dict) -> TariffRecord:
        """Transform raw tariff data to TariffRecord"""
        
    @staticmethod
    def transform_duty_rate(raw_data: dict) -> DutyRateRecord:
        """Transform raw duty data to DutyRateRecord"""
        
    @staticmethod
    def validate_hierarchical_integrity(records: List[TariffRecord]) -> bool:
        """Ensure parent-child relationships are valid"""
```

## 3. Risk Management

### 3.1 Critical Risks and Mitigation

#### Risk 1: Database Integrity Violation
**Impact**: CATASTROPHIC - Could break entire application
**Probability**: MEDIUM
**Mitigation**:
- Mandatory foreign key validation before any inserts
- Transaction rollback on any constraint violation
- Comprehensive data validation pipeline
- Backup before each migration phase

#### Risk 2: Data Loss During Migration
**Impact**: HIGH - Missing tariff data affects duty calculations
**Probability**: LOW
**Mitigation**:
- Parallel running of old and new systems during transition
- Comprehensive data comparison and validation
- Rollback procedures for each phase
- Complete database backup before migration

#### Risk 3: Browserless API Rate Limiting
**Impact**: MEDIUM - Could slow migration process
**Probability**: MEDIUM
**Mitigation**:
- Implement exponential backoff with jitter
- Monitor API usage and adjust request patterns
- Upgrade to higher-tier plan if needed
- Batch processing optimization

#### Risk 4: Australian Government Site Changes
**Impact**: MEDIUM - Could break scraping during migration
**Probability**: LOW
**Mitigation**:
- Browserless API handles most site changes automatically
- Flexible BrowserQL queries adaptable to minor changes
- Monitoring and alerting for scraping failures
- Manual fallback procedures

### 3.2 Rollback Procedures

#### Phase 1 Rollback
- Delete new Browserless configuration
- No database changes to rollback

#### Phase 2 Rollback
- Restore tariff_codes, tariff_sections, tariff_chapters from backup
- Reactivate old ABFTariffScraper
- Validate data integrity

#### Phase 4 Rollback
- Restore all dependent tables from backup
- Reactivate all legacy scrapers
- Full system validation

## 4. Success Metrics

### 4.1 Technical Metrics
- **Data Quality**: 100% data integrity maintained
- **Performance**: <50% reduction in scraping time
- **Reliability**: >99% successful scraping runs
- **Maintenance**: >80% reduction in code complexity

### 4.2 Business Metrics
- **System Availability**: >99.9% uptime during migration
- **Data Freshness**: Maintained current update frequency
- **Error Rate**: <1% data extraction errors
- **Cost**: <20% increase in operational costs (offset by reduced maintenance)

## 5. Implementation Checklist

### 5.1 Pre-Migration Requirements
- [ ] Browserless API account setup and testing
- [ ] Complete database backup
- [ ] Development environment setup
- [ ] Team training on BrowserQL
- [ ] Monitoring and alerting configuration

### 5.2 Phase 1 Checklist
- [ ] Browserless API integration working
- [ ] Single section extraction successful
- [ ] Data quality validation passed
- [ ] Performance benchmarks established

### 5.3 Phase 2 Checklist
- [ ] All tariff sections migrated
- [ ] All tariff chapters migrated
- [ ] All tariff codes migrated with hierarchy intact
- [ ] All duty rates migrated and linked
- [ ] Foreign key integrity validated

### 5.4 Phase 4 Checklist
- [ ] Legacy code removed
- [ ] Documentation updated
- [ ] Performance optimized
- [ ] Monitoring active
- [ ] Team handover complete

## 6. Post-Migration Validation

### 6.1 Data Integrity Checks
```sql
-- Validate hierarchical integrity
SELECT COUNT(*) FROM tariff_codes tc1 
WHERE tc1.parent_code IS NOT NULL 
AND NOT EXISTS (
    SELECT 1 FROM tariff_codes tc2 
    WHERE tc2.hs_code = tc1.parent_code
);

-- Validate foreign key relationships
SELECT COUNT(*) FROM duty_rates dr 
WHERE NOT EXISTS (
    SELECT 1 FROM tariff_codes tc 
    WHERE tc.hs_code = dr.hs_code
);
```

### 6.2 Performance Validation
- Compare scraping execution times
- Validate memory usage patterns
- Test concurrent scraping operations
- Measure API response times

### 6.3 Business Logic Validation
- Test duty calculation accuracy
- Validate tariff classification results
- Verify FTA preference calculations
- Confirm anti-dumping duty applications

## 7. Maintenance and Monitoring

### 7.1 Ongoing Monitoring
- Browserless API usage and costs
- Scraping success rates and error patterns
- Data quality metrics and anomaly detection
- Performance metrics and optimization opportunities

### 7.2 Update Procedures
- Regular BrowserQL query optimization
- Australian government site change monitoring
- Browserless API feature adoption
- Database performance tuning

## 8. Conclusion

This migration represents a critical modernization of the Customs Broker Portal's data infrastructure. The phased approach ensures minimal risk while delivering significant improvements in reliability, maintainability, and performance.

**Key Success Factors**:
1. Strict adherence to the phased sequence
2. Comprehensive testing at each phase
3. Continuous monitoring and validation
4. Team expertise in BrowserQL and Australian customs data

**Expected Outcomes**:
- 90% reduction in scraping-related maintenance
- 99.9% improvement in reliability
- 50% faster data extraction
- Future-proof architecture for Australian government site changes

---

**CRITICAL REMINDER**: This migration affects the core data infrastructure of the Customs Broker Portal. Any deviation from the specified sequence or validation procedures could result in system-wide failures. All phases must be completed successfully before proceeding to the next phase.
