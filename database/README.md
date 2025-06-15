# Customs Broker Portal Database Documentation

## Table of Contents
- [Overview](#overview)
- [Schema Architecture](#schema-architecture)
- [Table Descriptions](#table-descriptions)
- [Relationships](#relationships)
- [Hierarchical Structure](#hierarchical-structure)
- [Indexing Strategy](#indexing-strategy)
- [Usage Examples](#usage-examples)
- [Setup Instructions](#setup-instructions)
- [Data Sources](#data-sources)
- [Maintenance](#maintenance)

## Overview

The Customs Broker Portal database is a comprehensive PostgreSQL database designed to support Australian customs broker operations. It implements the complete Australian tariff structure with hierarchical navigation, Free Trade Agreement (FTA) preferential rates, anti-dumping duties, Tariff Concession Orders (TCOs), GST provisions, and AI-enhanced product classification capabilities.

### Purpose and Scope

This database serves as the core data repository for:
- **Tariff Classification**: Hierarchical HS code navigation from 2-digit chapters to 10-digit statistical codes
- **Duty Calculation**: MFN rates, FTA preferences, anti-dumping duties, and special provisions
- **Compliance Management**: TCO tracking, GST exemptions, and regulatory requirements
- **Trade Facilitation**: Export classifications (AHECC) and product classification assistance
- **AI Enhancement**: Machine learning-powered classification with broker verification workflows

### Key Features

- **14 Core Tables** with comprehensive Australian customs data coverage
- **25+ Performance Indexes** optimized for customs data access patterns
- **Full-Text Search** using PostgreSQL GIN indexes with trigram matching
- **Hierarchical Navigation** supporting parent-child relationships in tariff codes
- **Multi-FTA Support** for AUSFTA, CPTPP, ChAFTA, KAFTA, JAEPA, and others
- **Real-Time Validation** with foreign key constraints and business rules
- **Audit Trail** with timestamp tracking and change management

## Schema Architecture

### High-Level Design

The database follows a normalized relational design optimized for Australian customs requirements:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Tariff Codes   │    │   Duty Rates    │    │   FTA Rates     │
│  (Hierarchical) │────│   (MFN Rates)   │    │ (Preferential)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│ Anti-Dumping    │──────────────┘
                        │    Duties       │
                        └─────────────────┘
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      TCOs       │    │ GST Provisions  │    │ Export Codes    │
│ (Concessions)   │    │  (Exemptions)   │    │    (AHECC)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Australian Customs Requirements

The schema specifically addresses Australian customs and trade requirements:

- **Schedule 3 Compliance**: Full implementation of Australian tariff schedule structure
- **FTA Integration**: Support for all active Australian Free Trade Agreements
- **Anti-Dumping Commission**: Integration with ADC case management and measures
- **TCO Management**: Tariff Concession Order tracking and validation
- **GST Act Compliance**: Schedule 4 exemptions and special provisions
- **AHECC Support**: Australian Harmonized Export Commodity Classification

## Table Descriptions

### Core Tariff Structure

#### [`tariff_codes`](database/schema.sql:29)
**Purpose**: Core table implementing the hierarchical Australian tariff structure from 2-digit chapters to 10-digit statistical codes.

| Field | Type | Description |
|-------|------|-------------|
| `hs_code` | VARCHAR(10) | Harmonized System code (2,4,6,8,10 digits) |
| `description` | TEXT | Product description from Schedule 3 |
| `unit_description` | VARCHAR(100) | Statistical unit (kg, number, litres, etc.) |
| `parent_code` | VARCHAR(10) | References parent HS code for hierarchy |
| `level` | INTEGER | Digit level: 2=Chapter, 4=Heading, 6=Subheading, 8=Tariff Item, 10=Statistical |
| `chapter_notes` | TEXT | Chapter-specific interpretive rules |
| `section_id` | INTEGER | Links to tariff sections |
| `chapter_id` | INTEGER | Links to tariff chapters |

**Business Context**: Enables hierarchical navigation of Schedule 3 tariff structure, supporting drill-down from broad product categories to specific statistical classifications.

**Key Constraints**:
- Level must be 2, 4, 6, 8, or 10 digits
- Parent-child relationships maintain hierarchy integrity
- Unique HS codes across all levels

#### [`duty_rates`](database/schema.sql:56)
**Purpose**: General (MFN) duty rates for Australian tariff codes.

| Field | Type | Description |
|-------|------|-------------|
| `hs_code` | VARCHAR(10) | Links to tariff_codes |
| `general_rate` | DECIMAL(5,2) | MFN duty rate percentage |
| `unit_type` | VARCHAR(20) | ad_valorem, specific, or compound |
| `rate_text` | VARCHAR(200) | Full rate text for complex structures |
| `statistical_code` | VARCHAR(15) | Internal statistical reference |

**Business Context**: Stores Most Favoured Nation (MFN) rates as published in Schedule 3, supporting both ad valorem (percentage) and specific (per unit) duty calculations.

### Free Trade Agreement Rates

#### [`fta_rates`](database/schema.sql:76)
**Purpose**: Preferential tariff rates under Australian Free Trade Agreements.

| Field | Type | Description |
|-------|------|-------------|
| `hs_code` | VARCHAR(10) | Links to tariff_codes |
| `fta_code` | VARCHAR(10) | Agreement code (AUSFTA, CPTPP, etc.) |
| `country_code` | VARCHAR(3) | ISO 3166-1 alpha-3 country code |
| `preferential_rate` | DECIMAL(5,2) | FTA preferential rate |
| `staging_category` | VARCHAR(10) | Tariff elimination staging (A, B, C, etc.) |
| `effective_date` | DATE | When preference becomes effective |
| `elimination_date` | DATE | When tariff reaches zero |
| `rule_of_origin` | TEXT | FTA-specific origin requirements |

**Business Context**: Manages preferential rates under Australia's FTA network, including staging schedules for gradual tariff elimination and rules of origin requirements.

#### [`trade_agreements`](database/schema.sql:99)
**Purpose**: Master list of Australian Free Trade Agreements.

**Key Agreements**:
- **AUSFTA**: Australia-United States Free Trade Agreement
- **CPTPP**: Comprehensive and Progressive Trans-Pacific Partnership
- **ChAFTA**: China-Australia Free Trade Agreement
- **KAFTA**: Korea-Australia Free Trade Agreement
- **JAEPA**: Japan-Australia Economic Partnership Agreement

### Anti-Dumping and Trade Remedies

#### [`dumping_duties`](database/schema.sql:115)
**Purpose**: Anti-dumping and countervailing duties administered by the Anti-Dumping Commission.

| Field | Type | Description |
|-------|------|-------------|
| `hs_code` | VARCHAR(10) | Product subject to measures |
| `country_code` | VARCHAR(3) | Country of origin |
| `exporter_name` | VARCHAR(200) | Specific exporter (if applicable) |
| `duty_type` | VARCHAR(20) | dumping, countervailing, or both |
| `duty_rate` | DECIMAL(8,4) | Percentage duty rate |
| `case_number` | VARCHAR(50) | ADC investigation case number |
| `notice_number` | VARCHAR(50) | Government Gazette notice |

**Business Context**: Tracks active anti-dumping measures with company-specific rates, supporting complex duty calculations for imports from countries subject to trade remedy measures.

### Tariff Concession Orders

#### [`tcos`](database/schema.sql:143)
**Purpose**: Tariff Concession Orders providing duty-free entry for specific goods.

| Field | Type | Description |
|-------|------|-------------|
| `tco_number` | VARCHAR(20) | Unique TCO identifier |
| `hs_code` | VARCHAR(10) | Product classification |
| `description` | TEXT | Detailed product specification |
| `applicant_name` | VARCHAR(200) | Company that applied for TCO |
| `effective_date` | DATE | TCO commencement date |
| `expiry_date` | DATE | TCO expiration date |
| `gazette_date` | DATE | Government Gazette publication |
| `substitutable_goods_determination` | TEXT | Local production assessment |

**Business Context**: Manages duty-free concessions for goods not produced in Australia or where local production is insufficient, supporting manufacturing and industry development.

### GST Provisions

#### [`gst_provisions`](database/schema.sql:168)
**Purpose**: GST exemptions and special provisions affecting imports.

| Field | Type | Description |
|-------|------|-------------|
| `schedule_reference` | VARCHAR(50) | GST Act schedule and item reference |
| `exemption_type` | VARCHAR(50) | Type of exemption or provision |
| `value_threshold` | DECIMAL(10,2) | Dollar threshold for exemption |
| `conditions` | TEXT | Eligibility conditions |

**Business Context**: Implements GST Act Schedule 4 exemptions including low-value thresholds, diplomatic exemptions, and manufacturing concessions.

### Export Classifications

#### [`export_codes`](database/schema.sql:190)
**Purpose**: Australian Harmonized Export Commodity Classification (AHECC) codes.

| Field | Type | Description |
|-------|------|-------------|
| `ahecc_code` | VARCHAR(10) | Export classification code |
| `description` | TEXT | Export product description |
| `statistical_unit` | VARCHAR(50) | Export statistical unit |
| `corresponding_import_code` | VARCHAR(10) | Links to import HS code |

**Business Context**: Supports export documentation and statistics collection, maintaining alignment between import and export classifications for trade data consistency.

### AI-Enhanced Classification

#### [`product_classifications`](database/schema.sql:209)
**Purpose**: AI-enhanced product classifications with broker verification.

| Field | Type | Description |
|-------|------|-------------|
| `product_description` | TEXT | Product description for classification |
| `hs_code` | VARCHAR(10) | Suggested/verified classification |
| `confidence_score` | DECIMAL(3,2) | AI confidence (0.00-1.00) |
| `classification_source` | VARCHAR(50) | ai, broker, or ruling |
| `verified_by_broker` | BOOLEAN | Broker verification status |

**Business Context**: Enables AI-assisted classification with human oversight, supporting both automated suggestions and expert verification workflows.

### Hierarchical Structure Tables

#### [`tariff_sections`](database/schema.sql:230) and [`tariff_chapters`](database/schema.sql:241)
**Purpose**: Organize tariff codes into logical sections and chapters for navigation.

**Sections**: 21 major product groupings (Live Animals, Vegetable Products, Machinery, etc.)
**Chapters**: 99 specific product categories with interpretive notes

## Relationships

### Primary Relationships

```sql
-- Core hierarchy
tariff_codes.parent_code → tariff_codes.hs_code

-- Duty relationships
duty_rates.hs_code → tariff_codes.hs_code
fta_rates.hs_code → tariff_codes.hs_code
dumping_duties.hs_code → tariff_codes.hs_code
tcos.hs_code → tariff_codes.hs_code
gst_provisions.hs_code → tariff_codes.hs_code

-- FTA relationships
fta_rates.fta_code → trade_agreements.fta_code

-- Export alignment
export_codes.corresponding_import_code → tariff_codes.hs_code

-- Hierarchical structure
tariff_codes.section_id → tariff_sections.id
tariff_codes.chapter_id → tariff_chapters.id
tariff_chapters.section_id → tariff_sections.id
```

### Data Flow

1. **Classification**: Product → AI Classification → Broker Verification → HS Code
2. **Duty Calculation**: HS Code → General Rate + FTA Rate + Anti-Dumping + TCO + GST
3. **Hierarchy Navigation**: Chapter → Heading → Subheading → Tariff Item → Statistical Code

## Hierarchical Structure

### Tariff Code Hierarchy

The Australian tariff follows the international Harmonized System with additional statistical detail:

```
01 (Chapter - Live Animals)
├── 0101 (Heading - Horses, asses, mules, hinnies)
│   ├── 010121 (Subheading - Pure-bred breeding horses)
│   │   ├── 01012110 (Tariff Item - For racing)
│   │   │   ├── 0101211010 (Statistical - Thoroughbred)
│   │   │   └── 0101211020 (Statistical - Standardbred)
│   │   └── 01012190 (Tariff Item - Other pure-bred)
│   └── 010129 (Subheading - Other horses)
└── 0102 (Heading - Bovine animals)
```

### Navigation Queries

```sql
-- Get all children of a tariff code
SELECT * FROM tariff_codes 
WHERE parent_code = '0101' 
ORDER BY hs_code;

-- Get full hierarchy path
WITH RECURSIVE hierarchy AS (
    SELECT hs_code, description, parent_code, 1 as level
    FROM tariff_codes 
    WHERE hs_code = '0101211010'
    
    UNION ALL
    
    SELECT tc.hs_code, tc.description, tc.parent_code, h.level + 1
    FROM tariff_codes tc
    JOIN hierarchy h ON tc.hs_code = h.parent_code
)
SELECT * FROM hierarchy ORDER BY level DESC;
```

## Indexing Strategy

### Performance Optimization

The database includes 25+ indexes optimized for Australian customs data patterns:

#### Core Navigation Indexes
```sql
-- Hierarchical navigation
CREATE INDEX idx_tariff_codes_hierarchy 
ON tariff_codes(parent_code, level, is_active);

-- HS code lookup
CREATE INDEX idx_tariff_codes_hs_code 
ON tariff_codes(hs_code);
```

#### Full-Text Search Indexes
```sql
-- Description search
CREATE INDEX idx_tariff_desc_fts 
ON tariff_codes USING gin(to_tsvector('english', description));

-- Trigram similarity
CREATE INDEX idx_tariff_codes_description_trgm 
ON tariff_codes USING gin(description gin_trgm_ops);
```

#### FTA and Trade Remedy Indexes
```sql
-- FTA rate lookup
CREATE INDEX idx_fta_rates_lookup 
ON fta_rates(hs_code, fta_code, country_code);

-- Anti-dumping lookup
CREATE INDEX idx_dumping_active 
ON dumping_duties(hs_code, is_active, effective_date);
```

### Query Performance

- **Hierarchical Navigation**: Sub-second response for parent-child queries
- **Full-Text Search**: GIN indexes support complex product description searches
- **FTA Calculations**: Composite indexes optimize multi-country rate lookups
- **Classification**: Trigram matching enables fuzzy product description matching

## Usage Examples

### Common Customs Broker Workflows

#### 1. Tariff Code Lookup and Navigation

```sql
-- Search for products containing "cotton"
SELECT hs_code, description, level
FROM tariff_codes 
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'cotton')
AND is_active = true
ORDER BY level, hs_code;

-- Get complete tariff information
SELECT * FROM v_tariff_complete 
WHERE hs_code = '61091010';
```

#### 2. Duty Calculation with FTA Preferences

```sql
-- Calculate total duty for US origin t-shirts
SELECT 
    tc.hs_code,
    tc.description,
    dr.general_rate as mfn_rate,
    fr.preferential_rate as fta_rate,
    COALESCE(fr.preferential_rate, dr.general_rate) as applicable_rate
FROM tariff_codes tc
LEFT JOIN duty_rates dr ON tc.hs_code = dr.hs_code
LEFT JOIN fta_rates fr ON tc.hs_code = fr.hs_code 
    AND fr.country_code = 'USA' 
    AND fr.fta_code = 'AUSFTA'
    AND CURRENT_DATE BETWEEN fr.effective_date AND COALESCE(fr.elimination_date, '2099-12-31')
WHERE tc.hs_code = '61091010';
```

#### 3. Anti-Dumping Duty Application

```sql
-- Check for anti-dumping duties on Chinese steel
SELECT 
    dd.hs_code,
    tc.description,
    dd.country_code,
    dd.exporter_name,
    dd.duty_rate,
    dd.case_number
FROM dumping_duties dd
JOIN tariff_codes tc ON dd.hs_code = tc.hs_code
WHERE dd.country_code = 'CHN'
AND dd.hs_code LIKE '7208%'
AND dd.is_active = true
AND CURRENT_DATE BETWEEN dd.effective_date AND COALESCE(dd.expiry_date, '2099-12-31');
```

#### 4. TCO Exemption Checking

```sql
-- Find active TCOs for aerospace aluminum
SELECT 
    t.tco_number,
    t.hs_code,
    tc.description,
    t.applicant_name,
    t.effective_date,
    t.expiry_date
FROM tcos t
JOIN tariff_codes tc ON t.hs_code = tc.hs_code
WHERE t.description ILIKE '%aerospace%aluminum%'
AND t.is_current = true
AND CURRENT_DATE BETWEEN t.effective_date AND COALESCE(t.expiry_date, '2099-12-31');
```

#### 5. Product Classification Workflow

```sql
-- AI-assisted classification with confidence scoring
SELECT 
    product_description,
    hs_code,
    confidence_score,
    classification_source,
    verified_by_broker
FROM product_classifications
WHERE product_description ILIKE '%racing engine%'
ORDER BY confidence_score DESC;

-- Fuzzy matching for similar products
SELECT 
    hs_code,
    description,
    similarity(description, 'aluminum alloy sheet') as similarity_score
FROM tariff_codes
WHERE description % 'aluminum alloy sheet'
ORDER BY similarity_score DESC
LIMIT 10;
```

#### 6. GST Provision Lookup

```sql
-- Check GST exemptions for low-value imports
SELECT 
    gp.schedule_reference,
    gp.exemption_type,
    gp.description,
    gp.value_threshold,
    gp.conditions
FROM gst_provisions gp
WHERE gp.exemption_type = 'low_value'
AND gp.is_active = true;
```

### Advanced Queries

#### Complete Duty Calculation
```sql
-- Comprehensive duty calculation for a specific product and country
WITH duty_calculation AS (
    SELECT 
        tc.hs_code,
        tc.description,
        dr.general_rate,
        fr.preferential_rate,
        dd.duty_rate as dumping_rate,
        CASE 
            WHEN t.tco_number IS NOT NULL THEN 0
            WHEN dd.duty_rate IS NOT NULL THEN 
                COALESCE(fr.preferential_rate, dr.general_rate) + dd.duty_rate
            ELSE COALESCE(fr.preferential_rate, dr.general_rate)
        END as total_duty_rate
    FROM tariff_codes tc
    LEFT JOIN duty_rates dr ON tc.hs_code = dr.hs_code
    LEFT JOIN fta_rates fr ON tc.hs_code = fr.hs_code 
        AND fr.country_code = 'CHN'
        AND CURRENT_DATE BETWEEN fr.effective_date AND COALESCE(fr.elimination_date, '2099-12-31')
    LEFT JOIN dumping_duties dd ON tc.hs_code = dd.hs_code 
        AND dd.country_code = 'CHN'
        AND dd.is_active = true
        AND CURRENT_DATE BETWEEN dd.effective_date AND COALESCE(dd.expiry_date, '2099-12-31')
    LEFT JOIN tcos t ON tc.hs_code = t.hs_code 
        AND t.is_current = true
        AND CURRENT_DATE BETWEEN t.effective_date AND COALESCE(t.expiry_date, '2099-12-31')
    WHERE tc.hs_code = '72081010'
)
SELECT * FROM duty_calculation;
```

## Setup Instructions

### Prerequisites

- PostgreSQL 15+ server
- Sufficient privileges to create databases and extensions
- At least 1GB available disk space
- 4GB RAM recommended for optimal performance

### Quick Setup

1. **Clone or download the database files**:
   - [`schema.sql`](database/schema.sql) - Database structure
   - [`sample_data.sql`](database/sample_data.sql) - Comprehensive test data
   - [`init.sql`](database/init.sql) - Master initialization script

2. **Run the master initialization script**:
   ```powershell
   psql -U postgres -f init.sql
   ```

3. **Verify installation**:
   ```sql
   \c customs_broker_portal
   SELECT COUNT(*) FROM tariff_codes;
   SELECT COUNT(*) FROM duty_rates;
   SELECT COUNT(*) FROM fta_rates;
   ```

### Manual Setup

If you prefer step-by-step setup:

1. **Create database**:
   ```sql
   CREATE DATABASE customs_broker_portal 
   WITH ENCODING = 'UTF8' 
   LC_COLLATE = 'en_AU.UTF-8' 
   LC_CTYPE = 'en_AU.UTF-8';
   ```

2. **Connect and create schema**:
   ```sql
   \c customs_broker_portal
   \i schema.sql
   ```

3. **Load sample data**:
   ```sql
   \i sample_data.sql
   ```

4. **Optimize performance**:
   ```sql
   VACUUM ANALYZE;
   ```

### Configuration

#### PostgreSQL Settings
The database is optimized with these settings (applied automatically by [`init.sql`](database/init.sql)):

```sql
-- Memory settings
SET shared_buffers = '256MB';
SET effective_cache_size = '1GB';
SET work_mem = '16MB';
SET maintenance_work_mem = '64MB';

-- Query optimization
SET random_page_cost = 1.1;
SET effective_io_concurrency = 200;

-- Full-text search
SET default_text_search_config = 'english';
```

#### Application Connection
```sql
-- Application user (created automatically)
GRANT CONNECT ON DATABASE customs_broker_portal TO customs_broker_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO customs_broker_app;
```

### Validation

The initialization script includes comprehensive validation:

- **Schema Validation**: Verifies all tables, indexes, and constraints
- **Data Validation**: Confirms minimum data requirements
- **Functional Testing**: Tests hierarchical relationships, full-text search, and views
- **Performance Testing**: Validates index effectiveness

## Data Sources

### Australian Government Sources

#### Primary Data Sources
1. **Australian Border Force (ABF)**
   - Schedule 3 tariff classifications
   - Working Tariff Document updates
   - Customs notices and determinations

2. **Department of Foreign Affairs and Trade (DFAT)**
   - Free Trade Agreement texts and schedules
   - Rules of origin documentation
   - Preferential rate updates

3. **Anti-Dumping Commission (ADC)**
   - Investigation case numbers and outcomes
   - Dumping and countervailing duty measures
   - Review determinations and expiry dates

4. **Australian Taxation Office (ATO)**
   - GST Act schedules and exemptions
   - Customs duty concessions
   - Value thresholds and conditions

#### Update Procedures

**Daily Updates**:
- TCO gazette notices
- Anti-dumping measure changes
- Exchange rate updates

**Weekly Updates**:
- Working Tariff Document changes
- New customs notices
- FTA rate staging updates

**Monthly Updates**:
- Statistical code additions
- Product classification updates
- GST provision changes

**Annual Updates**:
- HS code structure changes
- Chapter note updates
- Section reorganizations

### Data Integration

#### Automated Updates
```sql
-- Example update procedure for new TCOs
INSERT INTO tcos (tco_number, hs_code, description, applicant_name, 
                  effective_date, gazette_date, gazette_number)
SELECT * FROM external_tco_feed 
WHERE gazette_date > (SELECT MAX(gazette_date) FROM tcos);
```

#### Data Validation
```sql
-- Validate new tariff codes maintain hierarchy
SELECT COUNT(*) FROM tariff_codes tc1
LEFT JOIN tariff_codes tc2 ON tc1.parent_code = tc2.hs_code
WHERE tc1.parent_code IS NOT NULL AND tc2.hs_code IS NULL;
```

## Maintenance

### Regular Maintenance Tasks

#### Daily Tasks
- **Monitor Performance**: Check slow query log
- **Validate Data Integrity**: Run constraint checks
- **Update Statistics**: Refresh table statistics for new data

```sql
-- Daily statistics update
ANALYZE tariff_codes;
ANALYZE duty_rates;
ANALYZE fta_rates;
```

#### Weekly Tasks
- **Index Maintenance**: Rebuild fragmented indexes
- **Backup Verification**: Test backup restoration
- **Performance Review**: Analyze query performance

```sql
-- Weekly index maintenance
REINDEX INDEX CONCURRENTLY idx_tariff_desc_fts;
VACUUM ANALYZE;
```

#### Monthly Tasks
- **Full Database Backup**: Complete backup with point-in-time recovery
- **Security Review**: Audit user permissions and access logs
- **Capacity Planning**: Monitor disk usage and growth trends

### Performance Monitoring

#### Key Metrics
- **Query Response Time**: Target <100ms for standard lookups
- **Index Usage**: Monitor index hit ratios
- **Connection Pool**: Track active connections and wait times
- **Disk Usage**: Monitor table and index growth

#### Monitoring Queries
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Monitor slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC;
```

### Backup and Recovery

#### Backup Strategy
```powershell
# Daily incremental backup
pg_dump -U postgres -d customs_broker_portal -f backup_$(Get-Date -Format "yyyyMMdd").sql

# Weekly full backup with compression
pg_dump -U postgres -d customs_broker_portal -Fc -f backup_full_$(Get-Date -Format "yyyyMMdd").dump
```

#### Recovery Procedures
```powershell
# Restore from backup
psql -U postgres -d customs_broker_portal -f backup_20250526.sql

# Point-in-time recovery
pg_restore -U postgres -d customs_broker_portal backup_full_20250526.dump
```

### Troubleshooting

#### Common Issues

**Slow Hierarchical Queries**:
- Check parent_code index usage
- Verify statistics are current
- Consider materialized views for complex hierarchies

**Full-Text Search Performance**:
- Monitor GIN index size and usage
- Update text search configuration
- Consider partial indexes for active records only

**FTA Rate Calculation Errors**:
- Validate effective and elimination dates
- Check country code consistency
- Verify FTA agreement status

#### Diagnostic Queries
```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM v_tariff_complete WHERE hs_code = '61091010';
```

---

## Support and Documentation

For additional support:
- Review PostgreSQL documentation for advanced configuration
- Consult Australian Border Force Working Tariff Document for tariff updates
- Reference FTA texts for rules of origin requirements
- Contact Anti-Dumping Commission for measure clarifications

**Database Version**: PostgreSQL 15+  
**Last Updated**: May 2025  
**Schema Version**: 1.0  
**Total Tables**: 14 core tables  
**Total Indexes**: 25+ performance indexes  
**Sample Data**: 200+ records across all tables