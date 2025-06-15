# =====================================================
# Customs Broker Portal - Base Scraper Class
# =====================================================
# 
# Abstract base class for all scrapers with common functionality including:
# - Rate limiting and respectful scraping practices
# - Error handling and retry logic with exponential backoff
# - Database operations and connection management
# - Comprehensive logging and monitoring
# - Data validation and deduplication
# 
# This class follows the patterns specified in PRD sections 3.3.1-3.3.4
# =====================================================

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import text

from .config import (
    get_settings, get_database_config, get_rate_limit_config,
    ABFScraperConfig, FTAScraperConfig, AntiDumpingScraperConfig, LegislationScraperConfig
)
from .utils import (
    logger, db_manager, http_client, rate_limiter,
    ScrapingMetrics, ScrapingError, RateLimitError, DataValidationError,
    retry_with_exponential_backoff, validate_hs_code, validate_duty_rate,
    validate_date, validate_country_code, generate_content_hash,
    check_duplicate_record, cleanup_resources
)

# =====================================================
# SCRAPER RESULT CLASSES
# =====================================================

@dataclass
class ScrapedRecord:
    """Base class for scraped data records."""
    source_url: str
    scraped_at: datetime = field(default_factory=datetime.now)
    content_hash: Optional[str] = None
    
    def __post_init__(self):
        """Generate content hash after initialization."""
        if self.content_hash is None:
            self.content_hash = generate_content_hash(self.__dict__)

class TariffRecord(ScrapedRecord):
    """Tariff code record from ABF scraping."""
    
    def __init__(self, source_url: str, hs_code: str, description: str, **kwargs):
        super().__init__(source_url=source_url)
        self.hs_code = hs_code
        self.description = description
        self.unit_description = kwargs.get('unit_description')
        self.parent_code = kwargs.get('parent_code')
        self.level = kwargs.get('level', 0)
        self.chapter_notes = kwargs.get('chapter_notes')
        self.general_rate = kwargs.get('general_rate')
        self.rate_text = kwargs.get('rate_text')
        self.statistical_code = kwargs.get('statistical_code')

class FTARecord(ScrapedRecord):
    """FTA rate record from DFAT scraping."""
    
    def __init__(self, source_url: str, hs_code: str, fta_code: str, country_code: str, **kwargs):
        super().__init__(source_url=source_url)
        self.hs_code = hs_code
        self.fta_code = fta_code
        self.country_code = country_code
        self.preferential_rate = kwargs.get('preferential_rate')
        self.staging_category = kwargs.get('staging_category')
        self.effective_date = kwargs.get('effective_date')
        self.elimination_date = kwargs.get('elimination_date')
        self.rule_of_origin = kwargs.get('rule_of_origin')

class AntiDumpingRecord(ScrapedRecord):
    """Anti-dumping duty record."""
    
    def __init__(self, source_url: str, hs_code: str, country_code: str, **kwargs):
        super().__init__(source_url=source_url)
        self.hs_code = hs_code
        self.country_code = country_code
        self.exporter_name = kwargs.get('exporter_name')
        self.duty_type = kwargs.get('duty_type', 'dumping')
        self.duty_rate = kwargs.get('duty_rate')
        self.duty_amount = kwargs.get('duty_amount')
        self.unit = kwargs.get('unit')
        self.effective_date = kwargs.get('effective_date')
        self.expiry_date = kwargs.get('expiry_date')
        self.case_number = kwargs.get('case_number')

class TCORecord(ScrapedRecord):
    """Tariff Concession Order record."""
    
    def __init__(self, source_url: str, tco_number: str, hs_code: str, description: str, **kwargs):
        super().__init__(source_url=source_url)
        self.tco_number = tco_number
        self.hs_code = hs_code
        self.description = description
        self.applicant_name = kwargs.get('applicant_name')
        self.effective_date = kwargs.get('effective_date')
        self.expiry_date = kwargs.get('expiry_date')
        self.gazette_date = kwargs.get('gazette_date')
        self.gazette_number = kwargs.get('gazette_number')

# =====================================================
# BASE SCRAPER CLASS
# =====================================================

class BaseScraper(ABC):
    """Abstract base class for all Australian customs data scrapers."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize base scraper with configuration."""
        self.name = name
        self.config = config or {}
        self.settings = get_settings()
        self.rate_config = get_rate_limit_config()
        
        # Initialize metrics
        self.metrics = ScrapingMetrics(start_time=datetime.now())
        
        # Track processed URLs to avoid duplicates
        self.processed_urls: Set[str] = set()
        
        # Cache for session data
        self._session_cache: Dict[str, Any] = {}
        
        # Setup scraper-specific logger
        self.logger = logging.getLogger(f"customs_scraper.{name}")
        
        self.logger.info(f"Initialized {name} scraper")
    
    # =====================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # =====================================================
    
    @abstractmethod
    async def scrape_data(self) -> List[ScrapedRecord]:
        """Main scraping method - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_base_urls(self) -> List[str]:
        """Get list of base URLs to scrape - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def parse_page_content(self, content: str, url: str) -> List[ScrapedRecord]:
        """Parse page content and extract records - must be implemented by subclasses."""
        pass
    
    # =====================================================
    # HTTP REQUEST METHODS
    # =====================================================
    
    @retry_with_exponential_backoff(max_attempts=3)
    async def fetch_page(self, url: str, **kwargs) -> str:
        """Fetch page content with rate limiting and error handling."""
        if url in self.processed_urls:
            self.logger.debug(f"Skipping already processed URL: {url}")
            return ""
        
        self.logger.info(f"Fetching: {url}")
        
        try:
            # Apply rate limiting
            await rate_limiter.acquire()
            
            # Add delay between requests
            delay = self.rate_config.get_delay()
            await asyncio.sleep(delay)
            
            # Make request
            response = await http_client.get(url, **kwargs)
            
            # Update metrics
            self.metrics.total_requests += 1
            
            # Read content
            content = await response.text()
            
            # Mark URL as processed
            self.processed_urls.add(url)
            
            # Update success metrics
            self.metrics.successful_requests += 1
            
            self.logger.debug(f"Successfully fetched {len(content)} characters from {url}")
            return content
            
        except RateLimitError as e:
            self.logger.warning(f"Rate limited for {url}: {e}")
            # Wait for retry-after period
            if e.retry_after:
                await asyncio.sleep(e.retry_after)
            raise
            
        except ScrapingError as e:
            self.logger.error(f"Scraping error for {url}: {e}")
            self.metrics.failed_requests += 1
            self.metrics.errors.append(f"{url}: {e}")
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            self.metrics.failed_requests += 1
            self.metrics.errors.append(f"{url}: {e}")
            raise ScrapingError(f"Unexpected error: {e}", source_url=url)
    
    async def fetch_multiple_pages(self, urls: List[str], max_concurrent: int = 5) -> List[str]:
        """Fetch multiple pages concurrently with rate limiting."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url: str) -> str:
            async with semaphore:
                try:
                    return await self.fetch_page(url)
                except Exception as e:
                    self.logger.error(f"Failed to fetch {url}: {e}")
                    return ""
        
        self.logger.info(f"Fetching {len(urls)} pages with max {max_concurrent} concurrent requests")
        
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and empty results
        valid_results = [r for r in results if isinstance(r, str) and r]
        
        self.logger.info(f"Successfully fetched {len(valid_results)} out of {len(urls)} pages")
        return valid_results
    
    # =====================================================
    # CONTENT PARSING METHODS
    # =====================================================
    
    def parse_html_content(self, content: str, parser: str = 'html.parser') -> BeautifulSoup:
        """Parse HTML content using BeautifulSoup."""
        try:
            soup = BeautifulSoup(content, parser)
            return soup
        except Exception as e:
            raise ScrapingError(f"Failed to parse HTML content: {e}")
    
    def extract_table_data(self, soup: BeautifulSoup, table_selector: str) -> List[Dict[str, str]]:
        """Extract data from HTML tables."""
        tables = soup.select(table_selector)
        if not tables:
            self.logger.warning(f"No tables found with selector: {table_selector}")
            return []
        
        all_data = []
        
        for table in tables:
            # Find header row
            header_row = table.find('tr')
            if not header_row:
                continue
            
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            if not headers:
                continue
            
            # Extract data rows
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= len(headers):
                    row_data = {}
                    for i, cell in enumerate(cells[:len(headers)]):
                        if i < len(headers):
                            row_data[headers[i]] = cell.get_text(strip=True)
                    all_data.append(row_data)
        
        self.logger.debug(f"Extracted {len(all_data)} rows from {len(tables)} tables")
        return all_data
    
    def extract_links(self, soup: BeautifulSoup, link_selector: str, base_url: str = "") -> List[str]:
        """Extract links from page content."""
        links = soup.select(link_selector)
        urls = []
        
        for link in links:
            href = link.get('href')
            if href:
                # Handle relative URLs
                if href.startswith('/') and base_url:
                    href = base_url.rstrip('/') + href
                elif not href.startswith('http') and base_url:
                    href = base_url.rstrip('/') + '/' + href.lstrip('/')
                
                urls.append(href)
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(urls))
        
        self.logger.debug(f"Extracted {len(unique_urls)} unique links")
        return unique_urls
    
    # =====================================================
    # DATA VALIDATION AND PROCESSING
    # =====================================================
    
    def validate_record(self, record: ScrapedRecord) -> bool:
        """Validate scraped record data."""
        try:
            if isinstance(record, TariffRecord):
                record.hs_code = validate_hs_code(record.hs_code)
                if record.general_rate is not None:
                    record.general_rate = validate_duty_rate(record.general_rate)
                
            elif isinstance(record, FTARecord):
                record.hs_code = validate_hs_code(record.hs_code)
                record.country_code = validate_country_code(record.country_code)
                if record.preferential_rate is not None:
                    record.preferential_rate = validate_duty_rate(record.preferential_rate)
                if record.effective_date:
                    record.effective_date = validate_date(record.effective_date)
                
            elif isinstance(record, AntiDumpingRecord):
                record.hs_code = validate_hs_code(record.hs_code)
                record.country_code = validate_country_code(record.country_code)
                if record.duty_rate is not None:
                    record.duty_rate = validate_duty_rate(record.duty_rate)
                if record.effective_date:
                    record.effective_date = validate_date(record.effective_date)
                
            elif isinstance(record, TCORecord):
                record.hs_code = validate_hs_code(record.hs_code)
                if record.effective_date:
                    record.effective_date = validate_date(record.effective_date)
                if record.expiry_date:
                    record.expiry_date = validate_date(record.expiry_date)
            
            return True
            
        except DataValidationError as e:
            self.logger.warning(f"Validation failed for record: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected validation error: {e}")
            return False
    
    def deduplicate_records(self, records: List[ScrapedRecord]) -> List[ScrapedRecord]:
        """Remove duplicate records based on content hash."""
        seen_hashes = set()
        unique_records = []
        
        for record in records:
            if record.content_hash not in seen_hashes:
                seen_hashes.add(record.content_hash)
                unique_records.append(record)
        
        removed_count = len(records) - len(unique_records)
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} duplicate records")
        
        return unique_records
    
    # =====================================================
    # DATABASE OPERATIONS
    # =====================================================
    
    async def save_records(self, records: List[ScrapedRecord]) -> Dict[str, int]:
        """Save scraped records to database."""
        if not records:
            return {'inserted': 0, 'updated': 0, 'skipped': 0}
        
        # Group records by type
        record_groups = {}
        for record in records:
            record_type = type(record).__name__
            if record_type not in record_groups:
                record_groups[record_type] = []
            record_groups[record_type].append(record)
        
        results = {'inserted': 0, 'updated': 0, 'skipped': 0}
        
        # Process each record type
        for record_type, type_records in record_groups.items():
            type_results = await self._save_records_by_type(record_type, type_records)
            for key, value in type_results.items():
                results[key] += value
        
        # Update metrics
        self.metrics.records_processed += len(records)
        self.metrics.records_inserted += results['inserted']
        self.metrics.records_updated += results['updated']
        
        self.logger.info(f"Saved records: {results}")
        return results
    
    async def _save_records_by_type(self, record_type: str, records: List[ScrapedRecord]) -> Dict[str, int]:
        """Save records of a specific type to appropriate database table."""
        results = {'inserted': 0, 'updated': 0, 'skipped': 0}
        
        # Map record types to database tables and operations
        type_mapping = {
            'TariffRecord': ('tariff_codes', self._save_tariff_record),
            'FTARecord': ('fta_rates', self._save_fta_record),
            'AntiDumpingRecord': ('dumping_duties', self._save_dumping_record),
            'TCORecord': ('tcos', self._save_tco_record)
        }
        
        if record_type not in type_mapping:
            self.logger.warning(f"Unknown record type: {record_type}")
            return results
        
        table_name, save_func = type_mapping[record_type]
        
        for record in records:
            try:
                result = await save_func(record)
                results[result] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to save {record_type}: {e}")
                results['skipped'] += 1
        
        return results
    
    async def _save_tariff_record(self, record: TariffRecord) -> str:
        """Save tariff record to database."""
        # Check for existing record
        existing_id = await check_duplicate_record('tariff_codes', {'hs_code': record.hs_code}, ['hs_code'])
        
        data = {
            'hs_code': record.hs_code,
            'description': record.description,
            'unit_description': record.unit_description,
            'parent_code': record.parent_code,
            'level': record.level,
            'chapter_notes': record.chapter_notes,
            'updated_at': datetime.now()
        }
        
        if existing_id:
            # Update existing record
            await db_manager.execute_query(
                "UPDATE tariff_codes SET description = :description, unit_description = :unit_description, "
                "chapter_notes = :chapter_notes, updated_at = :updated_at WHERE id = :id",
                {**data, 'id': existing_id}
            )
            
            # Update duty rates if provided
            if record.general_rate is not None or record.rate_text:
                await self._save_duty_rate(record.hs_code, record.general_rate, record.rate_text, record.statistical_code)
            
            return 'updated'
        else:
            # Insert new record
            await db_manager.execute_insert('tariff_codes', data)
            
            # Insert duty rates if provided
            if record.general_rate is not None or record.rate_text:
                await self._save_duty_rate(record.hs_code, record.general_rate, record.rate_text, record.statistical_code)
            
            return 'inserted'
    
    async def _save_duty_rate(self, hs_code: str, general_rate: Optional[float], 
                             rate_text: Optional[str], statistical_code: Optional[str]) -> None:
        """Save duty rate information."""
        duty_data = {
            'hs_code': hs_code,
            'general_rate': general_rate,
            'rate_text': rate_text,
            'statistical_code': statistical_code
        }
        
        await db_manager.execute_upsert('duty_rates', duty_data, ['hs_code'])
    
    async def _save_fta_record(self, record: FTARecord) -> str:
        """Save FTA record to database."""
        data = {
            'hs_code': record.hs_code,
            'fta_code': record.fta_code,
            'country_code': record.country_code,
            'preferential_rate': record.preferential_rate,
            'staging_category': record.staging_category,
            'effective_date': record.effective_date,
            'elimination_date': record.elimination_date,
            'rule_of_origin': record.rule_of_origin
        }
        
        existing_id = await check_duplicate_record(
            'fta_rates', 
            {'hs_code': record.hs_code, 'fta_code': record.fta_code, 'country_code': record.country_code},
            ['hs_code', 'fta_code', 'country_code']
        )
        
        if existing_id:
            await db_manager.execute_query(
                "UPDATE fta_rates SET preferential_rate = :preferential_rate, staging_category = :staging_category, "
                "effective_date = :effective_date, elimination_date = :elimination_date, "
                "rule_of_origin = :rule_of_origin WHERE id = :id",
                {**data, 'id': existing_id}
            )
            return 'updated'
        else:
            await db_manager.execute_insert('fta_rates', data)
            return 'inserted'
    
    async def _save_dumping_record(self, record: AntiDumpingRecord) -> str:
        """Save anti-dumping record to database."""
        data = {
            'hs_code': record.hs_code,
            'country_code': record.country_code,
            'exporter_name': record.exporter_name,
            'duty_type': record.duty_type,
            'duty_rate': record.duty_rate,
            'duty_amount': record.duty_amount,
            'unit': record.unit,
            'effective_date': record.effective_date,
            'expiry_date': record.expiry_date,
            'case_number': record.case_number
        }
        
        # Check for existing record based on HS code, country, and exporter
        unique_fields = ['hs_code', 'country_code']
        if record.exporter_name:
            unique_fields.append('exporter_name')
        
        existing_id = await check_duplicate_record('dumping_duties', data, unique_fields)
        
        if existing_id:
            await db_manager.execute_query(
                "UPDATE dumping_duties SET duty_rate = :duty_rate, duty_amount = :duty_amount, "
                "effective_date = :effective_date, expiry_date = :expiry_date, "
                "case_number = :case_number WHERE id = :id",
                {**data, 'id': existing_id}
            )
            return 'updated'
        else:
            await db_manager.execute_insert('dumping_duties', data)
            return 'inserted'
    
    async def _save_tco_record(self, record: TCORecord) -> str:
        """Save TCO record to database."""
        data = {
            'tco_number': record.tco_number,
            'hs_code': record.hs_code,
            'description': record.description,
            'applicant_name': record.applicant_name,
            'effective_date': record.effective_date,
            'expiry_date': record.expiry_date,
            'gazette_date': record.gazette_date,
            'gazette_number': record.gazette_number
        }
        
        existing_id = await check_duplicate_record('tcos', {'tco_number': record.tco_number}, ['tco_number'])
        
        if existing_id:
            await db_manager.execute_query(
                "UPDATE tcos SET description = :description, applicant_name = :applicant_name, "
                "effective_date = :effective_date, expiry_date = :expiry_date, "
                "gazette_date = :gazette_date, gazette_number = :gazette_number WHERE id = :id",
                {**data, 'id': existing_id}
            )
            return 'updated'
        else:
            await db_manager.execute_insert('tcos', data)
            return 'inserted'
    
    # =====================================================
    # MAIN EXECUTION METHODS
    # =====================================================
    
    async def run(self) -> ScrapingMetrics:
        """Main execution method for the scraper."""
        self.logger.info(f"Starting {self.name} scraper")
        
        try:
            # Reset metrics
            self.metrics = ScrapingMetrics(start_time=datetime.now())
            
            # Execute main scraping logic
            records = await self.scrape_data()
            
            # Validate records
            valid_records = [record for record in records if self.validate_record(record)]
            invalid_count = len(records) - len(valid_records)
            
            if invalid_count > 0:
                self.logger.warning(f"Filtered out {invalid_count} invalid records")
            
            # Deduplicate records
            unique_records = self.deduplicate_records(valid_records)
            
            # Save to database
            save_results = await self.save_records(unique_records)
            
            # Finalize metrics
            self.metrics.end_time = datetime.now()
            
            self.logger.info(f"Completed {self.name} scraper: {self.metrics.to_dict()}")
            
            return self.metrics
            
        except Exception as e:
            self.metrics.end_time = datetime.now()
            self.metrics.errors.append(f"Fatal error: {e}")
            self.logger.error(f"Scraper {self.name} failed: {e}")
            raise
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    def get_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        return f"{self.name}:" + ":".join(str(arg) for arg in args)
    
    def cache_get(self, key: str) -> Any:
        """Get value from session cache."""
        return self._session_cache.get(key)
    
    def cache_set(self, key: str, value: Any) -> None:
        """Set value in session cache."""
        self._session_cache[key] = value
    
    async def cleanup(self) -> None:
        """Cleanup scraper resources."""
        self.logger.info(f"Cleaning up {self.name} scraper")
        self.processed_urls.clear()
        self._session_cache.clear()

# =====================================================
# SCRAPER FACTORY
# =====================================================

class ScraperFactory:
    """Factory for creating scraper instances."""
    
    @staticmethod
    def create_scraper(scraper_type: str, **kwargs) -> BaseScraper:
        """Create scraper instance based on type."""
        # Import specific scrapers here to avoid circular imports
        scraper_map = {
            'abf': 'ABFScraper',
            'fta': 'FTAScraper', 
            'anti_dumping': 'AntiDumpingScraper',
            'tco': 'TCOScraper',
            'legislation': 'LegislationScraper'
        }
        
        if scraper_type not in scraper_map:
            raise ValueError(f"Unknown scraper type: {scraper_type}")
        
        # This would import and instantiate the specific scraper class
        # For now, return a placeholder
        raise NotImplementedError(f"Scraper {scraper_type} not yet implemented")

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    # Example of how to use the base scraper
    class ExampleScraper(BaseScraper):
        """Example scraper implementation."""
        
        def __init__(self):
            super().__init__("example")
        
        async def scrape_data(self) -> List[ScrapedRecord]:
            """Example scraping implementation."""
            urls = self.get_base_urls()
            records = []
            
            for url in urls:
                try:
                    content = await self.fetch_page(url)
                    page_records = self.parse_page_content(content, url)
                    records.extend(page_records)
                except Exception as e:
                    self.logger.error(f"Failed to scrape {url}: {e}")
            
            return records
        
        def get_base_urls(self) -> List[str]:
            """Example URLs."""
            return ["https://httpbin.org/get"]
        
        def parse_page_content(self, content: str, url: str) -> List[ScrapedRecord]:
            """Example parsing."""
            return [TariffRecord(
                source_url=url,
                hs_code="8471300000",
                description="Example tariff item"
            )]
    
    async def test_base_scraper():
        """Test the base scraper functionality."""
        scraper = ExampleScraper()
        
        try:
            metrics = await scraper.run()
            print(f"Scraper completed: {metrics.to_dict()}")
        except Exception as e:
            print(f"Scraper failed: {e}")
        finally:
            await scraper.cleanup()
            await cleanup_resources()
    
    # Run test
    asyncio.run(test_base_scraper())