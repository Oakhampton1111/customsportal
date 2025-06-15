# =====================================================
# Customs Broker Portal - ABF Browserless Scraper
# =====================================================
# 
# Browserless API implementation for scraping the Australian Border Force
# Working Tariff. This scraper replaces the traditional approach with
# BrowserQL queries for more reliable data extraction from the ABF website.
# 
# Key improvements over traditional scraping:
# - Built-in anti-detection for government site protection
# - Simplified query-based data extraction
# - Better handling of dynamic content and JavaScript
# - Reduced maintenance overhead from selector changes
# 
# This implementation maintains full compatibility with existing database
# schemas and produces identical TariffRecord objects.
# =====================================================

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from .browserless_scraper import BrowserlessScraper, BrowserlessError
from .base_scraper import TariffRecord, ScrapedRecord
from .utils import validate_hs_code, logger


class ABFBrowserlessScraper(BrowserlessScraper):
    """ABF Working Tariff scraper using Browserless API."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ABF Browserless scraper."""
        super().__init__("ABF_Browserless", config)
        
        # ABF-specific configuration
        self.base_url = "https://www.abf.gov.au/importing-exporting-and-manufacturing/tariff-classification/current-tariff/schedule-3"
        self.section_urls = []
        
        # Tariff structure tracking
        self.current_chapter = None
        self.current_heading = None
        self.current_subheading = None
        
        self.logger.info("Initialized ABF Browserless scraper")
    
    def get_base_urls(self) -> List[str]:
        """Get ABF Working Tariff base URLs."""
        return [self.base_url]
    
    def build_extraction_queries(self) -> Dict[str, str]:
        """Build BrowserQL queries for ABF data extraction."""
        return {
            "section_links": self.build_link_query("a[href*='section-']"),
            "chapter_links": self.build_link_query("a[href*='chapter-']"),
            "tariff_table": self.build_table_query("table.tariff-table, table[class*='tariff'], .table-responsive table"),
            "chapter_notes": self.build_content_query({
                "notes": ".chapter-notes, .notes, [class*='note']"
            }),
            "page_title": self.build_content_query({
                "title": "h1, .page-title, .chapter-title"
            })
        }
    
    async def scrape_data(self) -> List[ScrapedRecord]:
        """Main scraping method for ABF Working Tariff."""
        self.logger.info("Starting ABF Working Tariff scraping with Browserless API")
        
        try:
            # Step 1: Get section links from main page
            section_urls = await self._get_section_urls()
            self.logger.info(f"Found {len(section_urls)} sections to scrape")
            
            # Step 2: For proof-of-concept, scrape only first section
            if section_urls:
                test_section_url = section_urls[0]
                self.logger.info(f"Scraping test section: {test_section_url}")
                records = await self._scrape_section(test_section_url)
                
                self.logger.info(f"Extracted {len(records)} records from test section")
                return records
            else:
                self.logger.warning("No section URLs found")
                return []
                
        except Exception as e:
            self.logger.error(f"ABF scraping failed: {e}")
            raise
    
    async def _get_section_urls(self) -> List[str]:
        """Extract section URLs from the main ABF tariff page."""
        queries = self.build_extraction_queries()
        
        try:
            result = await self.fetch_page_data(
                self.base_url, 
                queries["section_links"],
                waitUntil="networkidle0",
                timeout=30000
            )
            
            section_urls = []
            if "links" in result:
                for link in result["links"]:
                    href = link.get("href", "")
                    if href and ("section-" in href or "chapter-" in href):
                        # Convert relative URLs to absolute
                        if href.startswith("/"):
                            full_url = urljoin(self.base_url, href)
                        elif not href.startswith("http"):
                            full_url = urljoin(self.base_url, href)
                        else:
                            full_url = href
                        
                        section_urls.append(full_url)
            
            # Remove duplicates while preserving order
            unique_urls = list(dict.fromkeys(section_urls))
            
            self.logger.info(f"Found {len(unique_urls)} unique section URLs")
            return unique_urls
            
        except Exception as e:
            self.logger.error(f"Failed to extract section URLs: {e}")
            return []
    
    async def _scrape_section(self, section_url: str) -> List[TariffRecord]:
        """Scrape a specific section of the ABF tariff."""
        self.logger.info(f"Scraping section: {section_url}")
        
        records = []
        queries = self.build_extraction_queries()
        
        try:
            # Get page content and structure
            result = await self.fetch_page_data(
                section_url,
                queries["tariff_table"],
                waitUntil="networkidle0",
                timeout=30000
            )
            
            # Extract chapter information
            chapter_info = await self._extract_chapter_info(section_url)
            
            # Process tariff tables
            if "tables" in result:
                for table_data in result["tables"]:
                    table_records = await self._process_tariff_table(
                        table_data, section_url, chapter_info
                    )
                    records.extend(table_records)
            
            self.logger.info(f"Extracted {len(records)} records from section")
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to scrape section {section_url}: {e}")
            return []
    
    async def _extract_chapter_info(self, url: str) -> Dict[str, Any]:
        """Extract chapter information from the page."""
        queries = self.build_extraction_queries()
        
        try:
            # Get page title and notes
            title_result = await self.fetch_page_data(url, queries["page_title"])
            notes_result = await self.fetch_page_data(url, queries["chapter_notes"])
            
            chapter_info = {
                "title": "",
                "notes": "",
                "chapter_number": None
            }
            
            # Extract title
            if "content" in title_result and "title" in title_result["content"]:
                title = title_result["content"]["title"]
                chapter_info["title"] = title
                
                # Extract chapter number from title
                chapter_match = re.search(r'chapter\s+(\d+)', title.lower())
                if chapter_match:
                    chapter_info["chapter_number"] = int(chapter_match.group(1))
            
            # Extract notes
            if "content" in notes_result and "notes" in notes_result["content"]:
                chapter_info["notes"] = notes_result["content"]["notes"]
            
            return chapter_info
            
        except Exception as e:
            self.logger.warning(f"Failed to extract chapter info from {url}: {e}")
            return {"title": "", "notes": "", "chapter_number": None}
    
    async def _process_tariff_table(self, table_data: Dict, source_url: str, 
                                   chapter_info: Dict[str, Any]) -> List[TariffRecord]:
        """Process tariff table data and create TariffRecord objects."""
        records = []
        
        if not isinstance(table_data, dict) or "rows" not in table_data:
            self.logger.warning("Invalid table data structure")
            return records
        
        rows = table_data.get("rows", [])
        headers = table_data.get("headers", [])
        
        self.logger.debug(f"Processing table with {len(rows)} rows and headers: {headers}")
        
        for row_idx, row in enumerate(rows):
            try:
                record = await self._parse_tariff_row(row, headers, source_url, chapter_info)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.warning(f"Failed to parse row {row_idx}: {e}")
                continue
        
        return records
    
    async def _parse_tariff_row(self, row: Dict, headers: List[str], source_url: str,
                               chapter_info: Dict[str, Any]) -> Optional[TariffRecord]:
        """Parse a single tariff table row into a TariffRecord."""
        try:
            # Map common column names to our expected fields
            column_mapping = {
                "hs code": "hs_code",
                "tariff code": "hs_code", 
                "code": "hs_code",
                "description": "description",
                "item description": "description",
                "unit": "unit_description",
                "unit description": "unit_description",
                "general rate": "general_rate",
                "rate": "general_rate",
                "duty rate": "general_rate",
                "statistical code": "statistical_code",
                "stat code": "statistical_code"
            }
            
            # Extract data from row
            extracted_data = {}
            for header, value in row.items():
                normalized_header = header.lower().strip()
                if normalized_header in column_mapping:
                    field_name = column_mapping[normalized_header]
                    extracted_data[field_name] = str(value).strip() if value else ""
            
            # Validate required fields
            if "hs_code" not in extracted_data or not extracted_data["hs_code"]:
                return None
            
            if "description" not in extracted_data or not extracted_data["description"]:
                return None
            
            # Clean and validate HS code
            hs_code = self._clean_hs_code(extracted_data["hs_code"])
            if not hs_code:
                return None
            
            # Determine tariff level and parent code
            level, parent_code = self._determine_tariff_level(hs_code)
            
            # Parse duty rate
            general_rate = None
            rate_text = extracted_data.get("general_rate", "")
            if rate_text:
                general_rate = self._parse_duty_rate(rate_text)
            
            # Create TariffRecord
            record = TariffRecord(
                source_url=source_url,
                hs_code=hs_code,
                description=extracted_data["description"],
                unit_description=extracted_data.get("unit_description"),
                parent_code=parent_code,
                level=level,
                chapter_notes=chapter_info.get("notes"),
                general_rate=general_rate,
                rate_text=rate_text,
                statistical_code=extracted_data.get("statistical_code")
            )
            
            return record
            
        except Exception as e:
            self.logger.warning(f"Failed to parse tariff row: {e}")
            return None
    
    def _clean_hs_code(self, hs_code: str) -> Optional[str]:
        """Clean and validate HS code."""
        if not hs_code:
            return None
        
        # Remove common prefixes and clean
        cleaned = re.sub(r'^(hs\s*code:?\s*|tariff\s*code:?\s*)', '', hs_code.lower())
        cleaned = re.sub(r'[^\d.]', '', cleaned)
        
        # Validate format
        if len(cleaned) >= 4 and cleaned.replace('.', '').isdigit():
            return cleaned
        
        return None
    
    def _determine_tariff_level(self, hs_code: str) -> Tuple[int, Optional[str]]:
        """Determine tariff hierarchy level and parent code."""
        # Remove dots for analysis
        clean_code = hs_code.replace('.', '')
        
        if len(clean_code) >= 10:
            # Statistical level (10+ digits)
            parent_code = clean_code[:8]
            return 4, parent_code
        elif len(clean_code) >= 8:
            # Subheading level (8 digits)
            parent_code = clean_code[:6]
            return 3, parent_code
        elif len(clean_code) >= 6:
            # Heading level (6 digits)
            parent_code = clean_code[:4]
            return 2, parent_code
        elif len(clean_code) >= 4:
            # Chapter level (4 digits)
            parent_code = clean_code[:2]
            return 1, parent_code
        else:
            # Section level (2 digits)
            return 0, None
    
    def _parse_duty_rate(self, rate_text: str) -> Optional[float]:
        """Parse duty rate from text."""
        if not rate_text:
            return None
        
        # Look for percentage rates
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', rate_text)
        if percent_match:
            return float(percent_match.group(1))
        
        # Look for "Free" or "Nil"
        if re.search(r'\b(free|nil|0)\b', rate_text.lower()):
            return 0.0
        
        # Look for dollar amounts (convert to percentage if needed)
        dollar_match = re.search(r'\$(\d+(?:\.\d+)?)', rate_text)
        if dollar_match:
            # For now, return as-is (may need conversion logic)
            return float(dollar_match.group(1))
        
        return None
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """Get ABF scraper-specific statistics."""
        stats = self.get_browserless_stats()
        stats.update({
            "scraper_type": "ABF_Browserless",
            "base_url": self.base_url,
            "processed_urls_count": len(self.processed_urls),
            "current_chapter": self.current_chapter,
            "current_heading": self.current_heading
        })
        return stats
