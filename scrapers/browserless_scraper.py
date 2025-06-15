# =====================================================
# Customs Broker Portal - Browserless API Scraper
# =====================================================
# 
# Enhanced scraper base class that uses the Browserless API for more robust
# and reliable scraping of Australian government websites. This class extends
# the existing BaseScraper with Browserless-specific functionality including:
# - BrowserQL query execution for simplified data extraction
# - Built-in anti-detection and bot protection bypass
# - Managed browser sessions with automatic scaling
# - Professional-grade proxy rotation and fingerprint management
# 
# This implementation maintains full compatibility with existing database
# schemas and data validation while providing superior reliability for
# scraping protected government websites.
# =====================================================

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from abc import abstractmethod

import aiohttp
from .base_scraper import BaseScraper, ScrapedRecord
from .config import get_settings
from .utils import ScrapingError, retry_with_exponential_backoff


class BrowserlessError(ScrapingError):
    """Browserless-specific error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}


class BrowserlessScraper(BaseScraper):
    """Enhanced scraper using Browserless API for robust data extraction."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Browserless scraper with API configuration."""
        super().__init__(name, config)
        
        # Get Browserless configuration
        self.settings = get_settings()
        self.browserless_config = self.settings.browserless
        
        # Validate configuration
        if not self.browserless_config.api_url:
            raise ValueError("Browserless API URL is required")
        if not self.browserless_config.api_key:
            raise ValueError("Browserless API key is required")
        
        # Initialize session tracking
        self._active_sessions = 0
        self._session_lock = asyncio.Lock()
        
        self.logger.info(f"Initialized Browserless scraper: {name}")
        self.logger.info(f"API URL: {self.browserless_config.api_url}")
        self.logger.info(f"Max sessions: {self.browserless_config.max_sessions}")
    
    # =====================================================
    # BROWSERLESS API METHODS
    # =====================================================
    
    async def _acquire_session(self) -> None:
        """Acquire a Browserless session slot."""
        async with self._session_lock:
            while self._active_sessions >= self.browserless_config.max_sessions:
                self.logger.debug("Waiting for available Browserless session...")
                await asyncio.sleep(1)
            self._active_sessions += 1
            self.logger.debug(f"Acquired session ({self._active_sessions}/{self.browserless_config.max_sessions})")
    
    async def _release_session(self) -> None:
        """Release a Browserless session slot."""
        async with self._session_lock:
            if self._active_sessions > 0:
                self._active_sessions -= 1
                self.logger.debug(f"Released session ({self._active_sessions}/{self.browserless_config.max_sessions})")
    
    @retry_with_exponential_backoff(max_attempts=3)
    async def execute_browserql(self, query: str, url: str, **options) -> Dict[str, Any]:
        """Execute a BrowserQL query using the Browserless API."""
        await self._acquire_session()
        
        try:
            # Prepare request payload
            payload = {
                "url": url,
                "query": query,
                **self.browserless_config.get_launch_options(),
                **options
            }
            
            # Add custom headers for Australian government sites
            if "abf.gov.au" in url or "dfat.gov.au" in url or "austrade.gov.au" in url:
                payload.setdefault("headers", {}).update({
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-AU,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                })
            
            # Execute request
            endpoint = f"{self.browserless_config.api_url}/query"
            headers = {"Authorization": f"Bearer {self.browserless_config.api_key}"}
            
            self.logger.debug(f"Executing BrowserQL query for: {url}")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(
                total=self.browserless_config.timeout
            )) as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    # Update metrics
                    self.metrics.total_requests += 1
                    
                    if response.status == 200:
                        result = await response.json()
                        self.metrics.successful_requests += 1
                        self.logger.debug(f"BrowserQL query successful for: {url}")
                        return result
                    else:
                        error_text = await response.text()
                        self.metrics.failed_requests += 1
                        raise BrowserlessError(
                            f"Browserless API error: {response.status}",
                            status_code=response.status,
                            response_data={"error": error_text},
                            source_url=url
                        )
        
        except asyncio.TimeoutError:
            self.metrics.failed_requests += 1
            raise BrowserlessError(f"Browserless API timeout for: {url}", source_url=url)
        except Exception as e:
            self.metrics.failed_requests += 1
            if not isinstance(e, BrowserlessError):
                raise BrowserlessError(f"Unexpected Browserless error: {e}", source_url=url)
            raise
        finally:
            await self._release_session()
    
    async def execute_screenshot(self, url: str, **options) -> bytes:
        """Take a screenshot using Browserless API."""
        await self._acquire_session()
        
        try:
            payload = {
                "url": url,
                **self.browserless_config.get_launch_options(),
                **options
            }
            
            endpoint = f"{self.browserless_config.api_url}/screenshot"
            headers = {"Authorization": f"Bearer {self.browserless_config.api_key}"}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(
                total=self.browserless_config.timeout
            )) as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        raise BrowserlessError(
                            f"Screenshot API error: {response.status}",
                            status_code=response.status,
                            response_data={"error": error_text},
                            source_url=url
                        )
        finally:
            await self._release_session()
    
    async def execute_pdf(self, url: str, **options) -> bytes:
        """Generate PDF using Browserless API."""
        await self._acquire_session()
        
        try:
            payload = {
                "url": url,
                **self.browserless_config.get_launch_options(),
                **options
            }
            
            endpoint = f"{self.browserless_config.api_url}/pdf"
            headers = {"Authorization": f"Bearer {self.browserless_config.api_key}"}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(
                total=self.browserless_config.timeout
            )) as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        raise BrowserlessError(
                            f"PDF API error: {response.status}",
                            status_code=response.status,
                            response_data={"error": error_text},
                            source_url=url
                        )
        finally:
            await self._release_session()
    
    # =====================================================
    # ENHANCED SCRAPING METHODS
    # =====================================================
    
    async def fetch_page_data(self, url: str, query: str, **options) -> Dict[str, Any]:
        """Fetch and extract data from a page using BrowserQL."""
        if url in self.processed_urls:
            self.logger.debug(f"Skipping already processed URL: {url}")
            return {}
        
        self.logger.info(f"Fetching data from: {url}")
        
        try:
            result = await self.execute_browserql(query, url, **options)
            self.processed_urls.add(url)
            return result
        except BrowserlessError as e:
            self.logger.error(f"Browserless error for {url}: {e}")
            self.metrics.errors.append(f"{url}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            self.metrics.errors.append(f"{url}: {e}")
            raise BrowserlessError(f"Unexpected error: {e}", source_url=url)
    
    async def fetch_multiple_pages_data(self, url_queries: List[Dict[str, str]], 
                                       max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Fetch data from multiple pages concurrently using BrowserQL."""
        # Limit concurrency to respect Browserless session limits
        max_concurrent = min(max_concurrent, self.browserless_config.max_sessions)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url_query: Dict[str, str]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    url = url_query["url"]
                    query = url_query["query"]
                    options = url_query.get("options", {})
                    return await self.fetch_page_data(url, query, **options)
                except Exception as e:
                    self.logger.error(f"Failed to fetch {url_query.get('url', 'unknown')}: {e}")
                    return {}
        
        self.logger.info(f"Fetching {len(url_queries)} pages with max {max_concurrent} concurrent requests")
        
        tasks = [fetch_with_semaphore(uq) for uq in url_queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and empty results
        valid_results = [r for r in results if isinstance(r, dict) and r]
        
        self.logger.info(f"Successfully fetched {len(valid_results)} out of {len(url_queries)} pages")
        return valid_results
    
    # =====================================================
    # BROWSERQL QUERY HELPERS
    # =====================================================
    
    def build_table_query(self, table_selector: str, columns: Optional[List[str]] = None) -> str:
        """Build BrowserQL query for extracting table data."""
        if columns:
            column_selectors = ", ".join([f'"{col}": text' for col in columns])
            return f"""
            {{
                "tables": {{
                    "selector": "{table_selector}",
                    "extract": {{
                        {column_selectors}
                    }}
                }}
            }}
            """
        else:
            return f"""
            {{
                "tables": {{
                    "selector": "{table_selector}",
                    "extract": "all"
                }}
            }}
            """
    
    def build_link_query(self, link_selector: str, base_url: str = "") -> str:
        """Build BrowserQL query for extracting links."""
        return f"""
        {{
            "links": {{
                "selector": "{link_selector}",
                "extract": {{
                    "href": "href",
                    "text": "text"
                }}
            }}
        }}
        """
    
    def build_content_query(self, selectors: Dict[str, str]) -> str:
        """Build BrowserQL query for extracting specific content."""
        extract_parts = []
        for key, selector in selectors.items():
            extract_parts.append(f'"{key}": {{ "selector": "{selector}", "extract": "text" }}')
        
        return f"""
        {{
            "content": {{
                {", ".join(extract_parts)}
            }}
        }}
        """
    
    # =====================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # =====================================================
    
    @abstractmethod
    async def scrape_data(self) -> List[ScrapedRecord]:
        """Main scraping method using Browserless API - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_base_urls(self) -> List[str]:
        """Get list of base URLs to scrape - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def build_extraction_queries(self) -> Dict[str, str]:
        """Build BrowserQL queries for data extraction - must be implemented by subclasses."""
        pass
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    async def cleanup(self) -> None:
        """Cleanup Browserless scraper resources."""
        await super().cleanup()
        # Reset session tracking
        async with self._session_lock:
            self._active_sessions = 0
        self.logger.info(f"Cleaned up Browserless scraper: {self.name}")
    
    def get_browserless_stats(self) -> Dict[str, Any]:
        """Get Browserless-specific statistics."""
        return {
            "active_sessions": self._active_sessions,
            "max_sessions": self.browserless_config.max_sessions,
            "api_url": self.browserless_config.api_url,
            "timeout": self.browserless_config.timeout
        }
