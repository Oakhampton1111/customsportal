-- =====================================================
-- Customs Broker Portal - Master Database Initialization Script
-- =====================================================
-- 
-- This script serves as the master initialization script for the complete
-- Customs Broker Portal database setup. It provides a comprehensive,
-- production-ready database initialization with proper error handling,
-- transaction management, and validation.
-- 
-- Features:
-- - Idempotent execution (can be run multiple times safely)
-- - Comprehensive error handling and rollback capabilities
-- - Database configuration optimizations for Australian customs data
-- - Full-text search and trigram matching setup
-- - Performance optimizations and memory settings
-- - Validation and integrity checks
-- - Progress logging and status reporting
-- 
-- Prerequisites:
-- - PostgreSQL 15+ server running
-- - Sufficient privileges to create databases and extensions
-- - schema.sql and sample_data.sql files in the same directory
-- 
-- Usage:
-- psql -U postgres -f init.sql
-- 
-- PostgreSQL Version: 15+
-- Encoding: UTF-8
-- Timezone: Australia/Sydney
-- =====================================================

-- Set client encoding and timezone for Australian operations
SET client_encoding = 'UTF8';
SET timezone = 'Australia/Sydney';

-- Enable detailed error reporting
\set ON_ERROR_STOP on
\set VERBOSITY verbose

-- Display initialization start message
\echo ''
\echo '======================================================='
\echo 'Customs Broker Portal - Database Initialization'
\echo '======================================================='
\echo 'Starting database initialization process...'
\echo ''

-- =====================================================
-- PHASE 1: DATABASE SETUP AND CONFIGURATION
-- =====================================================

\echo 'PHASE 1: Database Setup and Configuration'
\echo '-----------------------------------------'

-- Begin main transaction for database setup
BEGIN;

-- Create database if it doesn't exist (this will be run outside transaction)
-- Note: Database creation cannot be done within a transaction block
COMMIT;

-- Check if database exists, create if needed
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'customs_broker_portal') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE customs_broker_portal 
            WITH ENCODING = ''UTF8'' 
            LC_COLLATE = ''en_AU.UTF-8'' 
            LC_CTYPE = ''en_AU.UTF-8'' 
            TEMPLATE = template0');
        RAISE NOTICE 'Database customs_broker_portal created successfully';
    ELSE
        RAISE NOTICE 'Database customs_broker_portal already exists';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- If dblink is not available, assume database exists or will be created manually
        RAISE NOTICE 'Database creation skipped - ensure customs_broker_portal database exists';
END $$;

-- Connect to the target database
\c customs_broker_portal

-- Begin main initialization transaction
BEGIN;

\echo 'Connected to customs_broker_portal database'

-- =====================================================
-- PHASE 2: POSTGRESQL EXTENSIONS AND CONFIGURATION
-- =====================================================

\echo ''
\echo 'PHASE 2: PostgreSQL Extensions and Configuration'
\echo '------------------------------------------------'

-- Enable required PostgreSQL extensions for full functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\echo 'Extension uuid-ossp enabled for UUID generation'

CREATE EXTENSION IF NOT EXISTS "pg_trgm";
\echo 'Extension pg_trgm enabled for trigram similarity search'

CREATE EXTENSION IF NOT EXISTS "btree_gin";
\echo 'Extension btree_gin enabled for optimized GIN indexes'

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
\echo 'Extension pg_stat_statements enabled for query performance monitoring'

-- Configure PostgreSQL settings for optimal performance with Australian customs data
-- These settings are optimized for tariff data processing and search operations

-- Memory settings for large dataset processing
SET shared_buffers = '256MB';
SET effective_cache_size = '1GB';
SET work_mem = '16MB';
SET maintenance_work_mem = '64MB';

-- Query planner settings for complex hierarchical queries
SET random_page_cost = 1.1;
SET effective_io_concurrency = 200;

-- Full-text search configuration
SET default_text_search_config = 'english';

-- Logging configuration for monitoring
SET log_statement = 'mod';
SET log_min_duration_statement = 1000;

\echo 'PostgreSQL configuration optimized for customs data processing'

-- =====================================================
-- PHASE 3: SCHEMA CREATION AND VALIDATION
-- =====================================================

\echo ''
\echo 'PHASE 3: Schema Creation and Validation'
\echo '---------------------------------------'

-- Check if schema.sql file exists and execute it
\echo 'Executing schema.sql to create database structure...'

-- Execute the schema creation script
\i schema.sql

-- Validate schema creation
DO $$
DECLARE
    table_count INTEGER;
    index_count INTEGER;
    view_count INTEGER;
BEGIN
    -- Count created tables
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    -- Count created indexes
    SELECT COUNT(*) INTO index_count 
    FROM pg_indexes 
    WHERE schemaname = 'public';
    
    -- Count created views
    SELECT COUNT(*) INTO view_count 
    FROM information_schema.views 
    WHERE table_schema = 'public';
    
    RAISE NOTICE 'Schema validation: % tables, % indexes, % views created', 
        table_count, index_count, view_count;
    
    -- Verify core tables exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tariff_codes') THEN
        RAISE EXCEPTION 'Critical error: tariff_codes table not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'duty_rates') THEN
        RAISE EXCEPTION 'Critical error: duty_rates table not created';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fta_rates') THEN
        RAISE EXCEPTION 'Critical error: fta_rates table not created';
    END IF;
    
    RAISE NOTICE 'Schema validation completed successfully';
END $$;

-- =====================================================
-- PHASE 4: SAMPLE DATA LOADING AND VALIDATION
-- =====================================================

\echo ''
\echo 'PHASE 4: Sample Data Loading and Validation'
\echo '-------------------------------------------'

-- Execute sample data loading script
\echo 'Executing sample_data.sql to load comprehensive test data...'

\i sample_data.sql

-- Validate data loading
DO $$
DECLARE
    tariff_count INTEGER;
    duty_count INTEGER;
    fta_count INTEGER;
    tco_count INTEGER;
    classification_count INTEGER;
BEGIN
    -- Count loaded data
    SELECT COUNT(*) INTO tariff_count FROM tariff_codes;
    SELECT COUNT(*) INTO duty_count FROM duty_rates;
    SELECT COUNT(*) INTO fta_count FROM fta_rates;
    SELECT COUNT(*) INTO tco_count FROM tcos;
    SELECT COUNT(*) INTO classification_count FROM product_classifications;
    
    RAISE NOTICE 'Data validation: % tariff codes, % duty rates, % FTA rates, % TCOs, % classifications loaded', 
        tariff_count, duty_count, fta_count, tco_count, classification_count;
    
    -- Verify minimum data requirements
    IF tariff_count < 50 THEN
        RAISE EXCEPTION 'Insufficient tariff codes loaded: % (minimum 50 required)', tariff_count;
    END IF;
    
    IF duty_count < 20 THEN
        RAISE EXCEPTION 'Insufficient duty rates loaded: % (minimum 20 required)', duty_count;
    END IF;
    
    RAISE NOTICE 'Sample data validation completed successfully';
END $$;

-- =====================================================
-- PHASE 5: PERFORMANCE OPTIMIZATION
-- =====================================================

\echo ''
\echo 'PHASE 5: Performance Optimization'
\echo '---------------------------------'

-- Update table statistics for optimal query planning
ANALYZE tariff_codes;
ANALYZE duty_rates;
ANALYZE fta_rates;
ANALYZE dumping_duties;
ANALYZE tcos;
ANALYZE gst_provisions;
ANALYZE export_codes;
ANALYZE product_classifications;
ANALYZE tariff_sections;
ANALYZE tariff_chapters;
ANALYZE trade_agreements;

\echo 'Table statistics updated for optimal query planning'

-- Create additional performance indexes for Australian customs patterns
CREATE INDEX IF NOT EXISTS idx_tariff_codes_description_trgm 
ON tariff_codes USING gin (description gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_product_classifications_desc_trgm 
ON product_classifications USING gin (product_description gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_fta_rates_composite 
ON fta_rates (hs_code, country_code, effective_date, elimination_date);

CREATE INDEX IF NOT EXISTS idx_dumping_duties_composite 
ON dumping_duties (hs_code, country_code, is_active, effective_date, expiry_date);

\echo 'Additional performance indexes created for Australian customs data patterns'

-- =====================================================
-- PHASE 6: FUNCTIONAL VALIDATION AND TESTING
-- =====================================================

\echo ''
\echo 'PHASE 6: Functional Validation and Testing'
\echo '------------------------------------------'

-- Test hierarchical relationships
DO $$
DECLARE
    hierarchy_test INTEGER;
BEGIN
    -- Test parent-child relationships in tariff codes
    SELECT COUNT(*) INTO hierarchy_test 
    FROM tariff_codes tc1 
    JOIN tariff_codes tc2 ON tc1.hs_code = tc2.parent_code 
    WHERE tc1.level < tc2.level;
    
    IF hierarchy_test = 0 THEN
        RAISE WARNING 'No hierarchical relationships found in tariff codes';
    ELSE
        RAISE NOTICE 'Hierarchical relationships validated: % parent-child links found', hierarchy_test;
    END IF;
END $$;

-- Test foreign key constraints
DO $$
DECLARE
    fk_violations INTEGER := 0;
BEGIN
    -- Test duty_rates foreign key
    SELECT COUNT(*) INTO fk_violations 
    FROM duty_rates dr 
    LEFT JOIN tariff_codes tc ON dr.hs_code = tc.hs_code 
    WHERE tc.hs_code IS NULL;
    
    IF fk_violations > 0 THEN
        RAISE EXCEPTION 'Foreign key violations in duty_rates: % orphaned records', fk_violations;
    END IF;
    
    -- Test fta_rates foreign key
    SELECT COUNT(*) INTO fk_violations 
    FROM fta_rates fr 
    LEFT JOIN tariff_codes tc ON fr.hs_code = tc.hs_code 
    WHERE tc.hs_code IS NULL;
    
    IF fk_violations > 0 THEN
        RAISE EXCEPTION 'Foreign key violations in fta_rates: % orphaned records', fk_violations;
    END IF;
    
    RAISE NOTICE 'Foreign key constraints validated successfully';
END $$;

-- Test full-text search functionality
DO $$
DECLARE
    search_results INTEGER;
BEGIN
    -- Test full-text search on tariff descriptions
    SELECT COUNT(*) INTO search_results 
    FROM tariff_codes 
    WHERE to_tsvector('english', description) @@ to_tsquery('english', 'steel | aluminum | cotton');
    
    IF search_results = 0 THEN
        RAISE WARNING 'Full-text search test returned no results';
    ELSE
        RAISE NOTICE 'Full-text search functionality validated: % results for test query', search_results;
    END IF;
END $$;

-- Test trigram similarity search
DO $$
DECLARE
    similarity_results INTEGER;
BEGIN
    -- Test trigram similarity search
    SELECT COUNT(*) INTO similarity_results 
    FROM tariff_codes 
    WHERE description % 'aluminium' OR description % 'steel';
    
    IF similarity_results = 0 THEN
        RAISE WARNING 'Trigram similarity search test returned no results';
    ELSE
        RAISE NOTICE 'Trigram similarity search validated: % results for test query', similarity_results;
    END IF;
END $$;

-- Test view functionality
DO $$
DECLARE
    view_results INTEGER;
BEGIN
    -- Test complete tariff view
    SELECT COUNT(*) INTO view_results FROM v_tariff_complete;
    
    IF view_results = 0 THEN
        RAISE WARNING 'Tariff complete view returned no results';
    ELSE
        RAISE NOTICE 'Database views validated: % records in complete tariff view', view_results;
    END IF;
END $$;

-- =====================================================
-- PHASE 7: SECURITY AND PERMISSIONS SETUP
-- =====================================================

\echo ''
\echo 'PHASE 7: Security and Permissions Setup'
\echo '---------------------------------------'

-- Create application user role (if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'customs_broker_app') THEN
        CREATE ROLE customs_broker_app WITH LOGIN PASSWORD 'secure_password_change_me';
        RAISE NOTICE 'Application role customs_broker_app created';
    ELSE
        RAISE NOTICE 'Application role customs_broker_app already exists';
    END IF;
END $$;

-- Grant appropriate permissions to application role
GRANT CONNECT ON DATABASE customs_broker_portal TO customs_broker_app;
GRANT USAGE ON SCHEMA public TO customs_broker_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO customs_broker_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO customs_broker_app;

-- Grant permissions on views
GRANT SELECT ON v_tariff_complete TO customs_broker_app;
GRANT SELECT ON v_fta_rates_active TO customs_broker_app;
GRANT SELECT ON v_dumping_duties_current TO customs_broker_app;

\echo 'Security permissions configured for application role'

-- =====================================================
-- PHASE 8: FINAL VALIDATION AND CLEANUP
-- =====================================================

\echo ''
\echo 'PHASE 8: Final Validation and Cleanup'
\echo '-------------------------------------'

-- Perform final database integrity check
DO $$
DECLARE
    total_tables INTEGER;
    total_indexes INTEGER;
    total_constraints INTEGER;
    total_records INTEGER;
BEGIN
    -- Count database objects
    SELECT COUNT(*) INTO total_tables 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    
    SELECT COUNT(*) INTO total_indexes 
    FROM pg_indexes 
    WHERE schemaname = 'public';
    
    SELECT COUNT(*) INTO total_constraints 
    FROM information_schema.table_constraints 
    WHERE table_schema = 'public';
    
    -- Count total records across main tables
    SELECT 
        (SELECT COUNT(*) FROM tariff_codes) +
        (SELECT COUNT(*) FROM duty_rates) +
        (SELECT COUNT(*) FROM fta_rates) +
        (SELECT COUNT(*) FROM dumping_duties) +
        (SELECT COUNT(*) FROM tcos) +
        (SELECT COUNT(*) FROM gst_provisions) +
        (SELECT COUNT(*) FROM export_codes) +
        (SELECT COUNT(*) FROM product_classifications)
    INTO total_records;
    
    RAISE NOTICE 'Final validation summary:';
    RAISE NOTICE '  - Tables created: %', total_tables;
    RAISE NOTICE '  - Indexes created: %', total_indexes;
    RAISE NOTICE '  - Constraints created: %', total_constraints;
    RAISE NOTICE '  - Total records loaded: %', total_records;
    
    -- Verify minimum requirements
    IF total_tables < 10 THEN
        RAISE EXCEPTION 'Insufficient tables created: % (minimum 10 required)', total_tables;
    END IF;
    
    IF total_records < 100 THEN
        RAISE EXCEPTION 'Insufficient data loaded: % records (minimum 100 required)', total_records;
    END IF;
    
    RAISE NOTICE 'Database initialization completed successfully!';
END $$;

-- Update database statistics one final time
VACUUM ANALYZE;

\echo 'Final database optimization completed'

-- Commit the main transaction
COMMIT;

-- =====================================================
-- INITIALIZATION COMPLETION
-- =====================================================

\echo ''
\echo '======================================================='
\echo 'Customs Broker Portal Database Initialization Complete'
\echo '======================================================='
\echo ''
\echo 'Database Features Enabled:'
\echo '  ✓ Hierarchical tariff code navigation'
\echo '  ✓ Full-text search with GIN indexes'
\echo '  ✓ Trigram similarity matching'
\echo '  ✓ FTA preferential rate calculations'
\echo '  ✓ Anti-dumping duty tracking'
\echo '  ✓ Tariff Concession Order (TCO) management'
\echo '  ✓ GST provision handling'
\echo '  ✓ Export classification (AHECC) support'
\echo '  ✓ AI-enhanced product classification'
\echo '  ✓ Performance optimization for Australian customs data'
\echo ''
\echo 'Database Statistics:'

-- Display final statistics
SELECT 
    'Tariff Codes' as table_name, 
    COUNT(*) as record_count 
FROM tariff_codes
UNION ALL
SELECT 
    'Duty Rates' as table_name, 
    COUNT(*) as record_count 
FROM duty_rates
UNION ALL
SELECT 
    'FTA Rates' as table_name, 
    COUNT(*) as record_count 
FROM fta_rates
UNION ALL
SELECT 
    'Anti-Dumping Duties' as table_name, 
    COUNT(*) as record_count 
FROM dumping_duties
UNION ALL
SELECT 
    'TCOs' as table_name, 
    COUNT(*) as record_count 
FROM tcos
UNION ALL
SELECT 
    'GST Provisions' as table_name, 
    COUNT(*) as record_count 
FROM gst_provisions
UNION ALL
SELECT 
    'Export Codes' as table_name, 
    COUNT(*) as record_count 
FROM export_codes
UNION ALL
SELECT 
    'Product Classifications' as table_name, 
    COUNT(*) as record_count 
FROM product_classifications
ORDER BY table_name;

\echo ''
\echo 'Next Steps:'
\echo '  1. Update application configuration to connect to customs_broker_portal database'
\echo '  2. Change default password for customs_broker_app role'
\echo '  3. Configure backup and monitoring procedures'
\echo '  4. Review and adjust PostgreSQL configuration for production environment'
\echo '  5. Set up regular data updates from Australian Border Force systems'
\echo ''
\echo 'The Customs Broker Portal database is ready for use!'
\echo ''

-- End of initialization script