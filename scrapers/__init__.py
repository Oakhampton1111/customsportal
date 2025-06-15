# =====================================================
# Customs Broker Portal - Scrapers Package
# =====================================================
# 
# Core infrastructure package for the Australian Customs Broker Portal
# data scraping and ETL systems.
# 
# This package provides:
# - Configuration management for different environments
# - Utilities for error handling, logging, and retry logic
# - Base scraper class with common functionality
# - Database connection management
# - Rate limiting and respectful scraping practices
# 
# Usage:
#   from scrapers import get_settings, BaseScraper, db_manager
#   from scrapers.config import get_abf_config
#   from scrapers.utils import logger, validate_hs_code
# =====================================================

__version__ = "1.0.0"
__author__ = "Customs Broker Portal Team"
__description__ = "Australian Customs Data Scraping Infrastructure"

# =====================================================
# CORE IMPORTS
# =====================================================

# Configuration management
from .config import (
    get_settings,
    get_database_config,
    get_rate_limit_config,
    get_abf_config,
    get_fta_config,
    get_anti_dumping_config,
    get_legislation_config,
    get_logging_config,
    validate_all_configurations,
    ConfigurationManager,
    ScraperSettings,
    DatabaseConfig,
    RateLimitConfig,
    ABFScraperConfig,
    FTAScraperConfig,
    AntiDumpingScraperConfig,
    LegislationScraperConfig,
    LoggingConfig
)

# Utilities and helpers
from .utils import (
    logger,
    db_manager,
    http_client,
    rate_limiter,
    setup_logging,
    ScrapingError,
    RateLimitError,
    DataValidationError,
    ScrapingMetrics,
    DatabaseManager,
    HTTPClient,
    RateLimiter,
    HealthChecker,
    retry_with_exponential_backoff,
    exponential_backoff_with_jitter,
    validate_hs_code,
    validate_duty_rate,
    validate_date,
    validate_country_code,
    generate_content_hash,
    check_duplicate_record,
    cleanup_resources
)

# Base scraper and record classes
from .base_scraper import (
    BaseScraper,
    ScrapedRecord,
    TariffRecord,
    FTARecord,
    AntiDumpingRecord,
    TCORecord,
    ScraperFactory
)

# =====================================================
# PACKAGE LEVEL FUNCTIONS
# =====================================================

def initialize_scrapers(config_file: str = None) -> None:
    """Initialize the scrapers package with optional configuration file."""
    try:
        # Load configuration
        if config_file:
            from .config import config_manager
            config_manager.load_from_file(config_file)
        
        # Validate configuration
        validate_all_configurations()
        
        # Setup logging
        setup_logging()
        
        logger.info("Scrapers package initialized successfully")
        logger.info(f"Environment: {get_settings().environment}")
        logger.info(f"Database: {get_database_config().host}:{get_database_config().port}")
        
    except Exception as e:
        print(f"Failed to initialize scrapers package: {e}")
        raise

def get_package_info() -> dict:
    """Get package information."""
    return {
        'name': 'customs-broker-scrapers',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'environment': get_settings().environment,
        'database_host': get_database_config().host,
        'rate_limit': f"{get_rate_limit_config().requests_per_minute} req/min"
    }

async def health_check() -> dict:
    """Perform comprehensive health check of all scraper components."""
    health_results = {
        'package_version': __version__,
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy',
        'components': {}
    }
    
    try:
        # Check database connectivity
        db_health = await HealthChecker.check_database()
        health_results['components']['database'] = db_health
        
        # Check configuration
        try:
            validate_all_configurations()
            health_results['components']['configuration'] = {
                'status': 'healthy',
                'environment': get_settings().environment
            }
        except Exception as e:
            health_results['components']['configuration'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Check external URLs (sample)
        test_urls = [
            'https://www.abf.gov.au',
            'https://www.dfat.gov.au',
            'https://www.legislation.gov.au'
        ]
        
        url_results = []
        for url in test_urls:
            try:
                url_health = await HealthChecker.check_external_url(url)
                url_results.append(url_health)
            except Exception as e:
                url_results.append({
                    'status': 'unhealthy',
                    'url': url,
                    'error': str(e)
                })
        
        health_results['components']['external_urls'] = url_results
        
        # Determine overall status
        unhealthy_components = [
            comp for comp in health_results['components'].values()
            if (isinstance(comp, dict) and comp.get('status') == 'unhealthy') or
               (isinstance(comp, list) and any(item.get('status') == 'unhealthy' for item in comp))
        ]
        
        if unhealthy_components:
            health_results['overall_status'] = 'degraded'
        
    except Exception as e:
        health_results['overall_status'] = 'unhealthy'
        health_results['error'] = str(e)
    
    return health_results

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def create_scraper(scraper_type: str, **kwargs) -> BaseScraper:
    """Create a scraper instance of the specified type."""
    return ScraperFactory.create_scraper(scraper_type, **kwargs)

async def run_scraper(scraper_type: str, **kwargs) -> ScrapingMetrics:
    """Create and run a scraper, returning metrics."""
    scraper = create_scraper(scraper_type, **kwargs)
    
    try:
        metrics = await scraper.run()
        return metrics
    finally:
        await scraper.cleanup()

# =====================================================
# PACKAGE LEVEL CONSTANTS
# =====================================================

# Supported scraper types
SCRAPER_TYPES = [
    'abf',           # Australian Border Force tariff scraper
    'fta',           # Free Trade Agreement rates scraper
    'anti_dumping',  # Anti-dumping duties scraper
    'tco',           # Tariff Concession Orders scraper
    'legislation'    # Federal legislation monitor
]

# Australian government data sources
DATA_SOURCES = {
    'ABF': {
        'name': 'Australian Border Force',
        'base_url': 'https://www.abf.gov.au',
        'data_types': ['tariff_codes', 'duty_rates', 'tcos']
    },
    'DFAT': {
        'name': 'Department of Foreign Affairs and Trade',
        'base_url': 'https://www.dfat.gov.au',
        'data_types': ['fta_rates', 'trade_agreements']
    },
    'INDUSTRY': {
        'name': 'Department of Industry, Science and Resources',
        'base_url': 'https://www.industry.gov.au',
        'data_types': ['dumping_duties', 'anti_dumping_measures']
    },
    'LEGISLATION': {
        'name': 'Federal Register of Legislation',
        'base_url': 'https://www.legislation.gov.au',
        'data_types': ['acts', 'regulations', 'amendments']
    }
}

# Database table mappings
TABLE_MAPPINGS = {
    'TariffRecord': 'tariff_codes',
    'FTARecord': 'fta_rates',
    'AntiDumpingRecord': 'dumping_duties',
    'TCORecord': 'tcos'
}

# =====================================================
# PACKAGE INITIALIZATION
# =====================================================

# Import datetime for health check
from datetime import datetime

# Auto-initialize with default settings
try:
    # Only initialize if not already done
    if not hasattr(get_settings, '_initialized'):
        initialize_scrapers()
        get_settings._initialized = True
except Exception as e:
    # Log error but don't fail import
    print(f"Warning: Failed to auto-initialize scrapers package: {e}")

# =====================================================
# EXPORT CONTROL
# =====================================================

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__description__',
    
    # Configuration
    'get_settings',
    'get_database_config',
    'get_rate_limit_config',
    'get_abf_config',
    'get_fta_config',
    'get_anti_dumping_config',
    'get_legislation_config',
    'get_logging_config',
    'validate_all_configurations',
    'ConfigurationManager',
    'ScraperSettings',
    'DatabaseConfig',
    'RateLimitConfig',
    'ABFScraperConfig',
    'FTAScraperConfig',
    'AntiDumpingScraperConfig',
    'LegislationScraperConfig',
    'LoggingConfig',
    
    # Utilities
    'logger',
    'db_manager',
    'http_client',
    'rate_limiter',
    'setup_logging',
    'ScrapingError',
    'RateLimitError',
    'DataValidationError',
    'ScrapingMetrics',
    'DatabaseManager',
    'HTTPClient',
    'RateLimiter',
    'HealthChecker',
    'retry_with_exponential_backoff',
    'exponential_backoff_with_jitter',
    'validate_hs_code',
    'validate_duty_rate',
    'validate_date',
    'validate_country_code',
    'generate_content_hash',
    'check_duplicate_record',
    'cleanup_resources',
    
    # Base classes
    'BaseScraper',
    'ScrapedRecord',
    'TariffRecord',
    'FTARecord',
    'AntiDumpingRecord',
    'TCORecord',
    'ScraperFactory',
    
    # Package functions
    'initialize_scrapers',
    'get_package_info',
    'health_check',
    'create_scraper',
    'run_scraper',
    
    # Constants
    'SCRAPER_TYPES',
    'DATA_SOURCES',
    'TABLE_MAPPINGS'
]