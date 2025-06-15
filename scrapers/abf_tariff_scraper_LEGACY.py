# =====================================================
# Customs Broker Portal - ABF Working Tariff Scraper
# =====================================================
# 
# Complete implementation of the Australian Border Force Working Tariff scraper
# as specified in PRD section 3.3.1 (lines 222-329).
# 
# Features:
# - Hierarchical scraping of Schedule 3 tariff structure
# - Section → Chapter → Heading → Subheading → Tariff Item navigation
# - Complex duty rate parsing (ad valorem, specific, compound rates)
# - Incremental updates with change detection
# - Chapter notes extraction and storage
# - Integration with existing database schema
# - Comprehensive error handling and logging
# =====================================================

import asyncio
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
import pandas as pd

from .base_scraper import BaseScraper, TariffRecord, ScrapedRecord
from .config import get_abf_config
from .utils import (
    logger, validate_hs_code, validate_duty_rate, 
    ScrapingError, DataValidationError, generate_content_hash
)

# =====================================================
# ABF-SPECIFIC DATA STRUCTURES
# =====================================================

@dataclass
class ABFSection:
    """ABF Schedule 3 section information."""
    section_number: int
    title: str
    description: str
    chapter_range: str
    url: str

@dataclass
class ABFChapter:
    """ABF Schedule 3 chapter information."""
    chapter_number: int
    title: str
    section_id: int
    chapter_notes: Optional[str]
    url: str

@dataclass
class ABFTariffItem:
    """Individual tariff item from ABF Schedule 3."""
    hs_code: str
    description: str
    unit_description: Optional[str]
    general_rate: Optional[float]
    rate_text: str
    statistical_code: Optional[str]
    parent_code: Optional[str]
    level: int
    chapter_number: int
    section_number: int

# =====================================================
# ABF WORKING TARIFF SCRAPER
# =====================================================

class ABFTariffScraper(BaseScraper):
    """
    Australian Border Force Working Tariff scraper for Schedule 3.
    
    Implements comprehensive scraping of the ABF Working Tariff including:
    - Complete hierarchical structure (sections → chapters → tariff items)
    - Complex duty rate parsing for Australian rate structures
    - Chapter notes extraction and storage
    - Incremental updates with change detection
    - Integration with existing database schema
    """
    
    def __init__(self):
        """Initialize ABF tariff scraper with configuration."""
        super().__init__("ABF_Working_Tariff")
        self.config = get_abf_config()
        
        # ABF-specific URLs and patterns
        self.schedule_3_url = f"{self.config.tariff_url}/schedule-3"
        self.base_tariff_url = self.config.tariff_url
        
        # Caching for hierarchical data
        self.sections_cache: Dict[int, ABFSection] = {}
        self.chapters_cache: Dict[int, ABFChapter] = {}
        
        # Track processed items for incremental updates
        self.processed_items: Set[str] = set()
        self.last_update_time: Optional[datetime] = None
        
        # Rate parsing patterns
        self.rate_patterns = {
            'free': re.compile(r'\b(free|nil|n/?a)\b', re.IGNORECASE),
            'percentage': re.compile(r'(\d+(?:\.\d+)?)\s*%', re.IGNORECASE),
            'specific': re.compile(r'\$(\d+(?:\.\d+)?)\s*per\s+(\w+)', re.IGNORECASE),
            'compound': re.compile(r'(\d+(?:\.\d+)?)\s*%\s+or\s+\$(\d+(?:\.\d+)?)\s*per\s+(\w+)', re.IGNORECASE),
            'complex': re.compile(r'(\d+(?:\.\d+)?)\s*%\s+or\s+\$(\d+(?:\.\d+)?)\s*per\s+(\w+),?\s*whichever\s+(greater|higher)', re.IGNORECASE)
        }
        
        self.logger.info("ABF Working Tariff scraper initialized")
    
    # =====================================================
    # MAIN SCRAPING METHODS
    # =====================================================
    
    async def scrape_data(self) -> List[ScrapedRecord]:
        """
        Main scraping method - scrapes complete Schedule 3 tariff data.
        
        Returns:
            List of TariffRecord objects containing all scraped tariff data
        """
        self.logger.info("Starting ABF Working Tariff scraping")
        
        try:
            # Step 1: Get all sections from Schedule 3 main page
            sections = await self._scrape_sections()
            self.logger.info(f"Found {len(sections)} sections in Schedule 3")
            
            all_records = []
            
            # Step 2: Process each section
            for section in sections:
                try:
                    self.logger.info(f"Processing Section {section.section_number}: {section.title}")
                    
                    # Get chapters for this section
                    chapters = await self._scrape_chapters(section)
                    self.logger.info(f"Found {len(chapters)} chapters in Section {section.section_number}")
                    
                    # Process each chapter
                    for chapter in chapters:
                        try:
                            self.logger.info(f"Processing Chapter {chapter.chapter_number}: {chapter.title}")
                            
                            # Scrape tariff items from chapter
                            chapter_records = await self._scrape_chapter_tariff_items(chapter, section)
                            all_records.extend(chapter_records)
                            
                            self.logger.info(f"Extracted {len(chapter_records)} tariff items from Chapter {chapter.chapter_number}")
                            
                            # Rate limiting - respect ABF servers
                            await asyncio.sleep(self.config.timeout / 30)  # 1 second delay
                            
                        except Exception as e:
                            self.logger.error(f"Error processing Chapter {chapter.chapter_number}: {e}")
                            self.metrics.errors.append(f"Chapter {chapter.chapter_number}: {e}")
                            continue
                    
                    # Longer delay between sections
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing Section {section.section_number}: {e}")
                    self.metrics.errors.append(f"Section {section.section_number}: {e}")
                    continue
            
            self.logger.info(f"ABF scraping completed. Total records: {len(all_records)}")
            return all_records
            
        except Exception as e:
            self.logger.error(f"Fatal error in ABF scraping: {e}")
            raise ScrapingError(f"ABF scraping failed: {e}", source_url=self.schedule_3_url)
    
    # =====================================================
    # SECTION SCRAPING
    # =====================================================
    
    async def _scrape_sections(self) -> List[ABFSection]:
        """
        Scrape all sections from Schedule 3 main page.
        
        Returns:
            List of ABFSection objects with section metadata
        """
        try:
            content = await self.fetch_page(self.schedule_3_url)
            soup = self.parse_html_content(content)
            
            sections = []
            
            # Find section links in the Schedule 3 navigation
            section_links = soup.find_all('a', href=lambda x: x and 'section-' in x.lower())
            
            if not section_links:
                # Try alternative selectors for ABF website structure
                section_links = soup.select('a[href*="section"]')
            
            for link in section_links:
                try:
                    section_info = self._parse_section_link(link)
                    if section_info:
                        sections.append(section_info)
                        self.sections_cache[section_info.section_number] = section_info
                        
                except Exception as e:
                    self.logger.warning(f"Error parsing section link {link}: {e}")
                    continue
            
            # Sort sections by number
            sections.sort(key=lambda x: x.section_number)
            
            if not sections:
                raise ScrapingError("No sections found in Schedule 3", source_url=self.schedule_3_url)
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Error scraping sections: {e}")
            raise ScrapingError(f"Failed to scrape sections: {e}", source_url=self.schedule_3_url)
    
    def _parse_section_link(self, link: Tag) -> Optional[ABFSection]:
        """
        Parse individual section link to extract section information.
        
        Args:
            link: BeautifulSoup Tag object for section link
            
        Returns:
            ABFSection object or None if parsing fails
        """
        try:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Extract section number from href or text
            section_match = re.search(r'section[-_]?(\d+)', href, re.IGNORECASE)
            if not section_match:
                section_match = re.search(r'section\s+(\d+)', text, re.IGNORECASE)
            
            if not section_match:
                return None
            
            section_number = int(section_match.group(1))
            
            # Build full URL
            full_url = urljoin(self.base_tariff_url, href)
            
            # Extract title and description from link text
            title_parts = text.split('-', 1)
            title = title_parts[1].strip() if len(title_parts) > 1 else text.strip()
            
            # Extract chapter range if available
            chapter_range = self._extract_chapter_range(text)
            
            return ABFSection(
                section_number=section_number,
                title=title,
                description=text.strip(),
                chapter_range=chapter_range,
                url=full_url
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing section link: {e}")
            return None
    
    # =====================================================
    # CHAPTER SCRAPING
    # =====================================================
    
    async def _scrape_chapters(self, section: ABFSection) -> List[ABFChapter]:
        """
        Scrape all chapters within a section.
        
        Args:
            section: ABFSection object containing section information
            
        Returns:
            List of ABFChapter objects
        """
        try:
            content = await self.fetch_page(section.url)
            soup = self.parse_html_content(content)
            
            chapters = []
            
            # Find chapter links within the section page
            chapter_links = soup.find_all('a', href=lambda x: x and 'chapter-' in x.lower())
            
            if not chapter_links:
                # Try alternative selectors
                chapter_links = soup.select('a[href*="chapter"]')
            
            for link in chapter_links:
                try:
                    chapter_info = self._parse_chapter_link(link, section)
                    if chapter_info:
                        chapters.append(chapter_info)
                        self.chapters_cache[chapter_info.chapter_number] = chapter_info
                        
                except Exception as e:
                    self.logger.warning(f"Error parsing chapter link {link}: {e}")
                    continue
            
            # Sort chapters by number
            chapters.sort(key=lambda x: x.chapter_number)
            
            return chapters
            
        except Exception as e:
            self.logger.error(f"Error scraping chapters for section {section.section_number}: {e}")
            return []
    
    def _parse_chapter_link(self, link: Tag, section: ABFSection) -> Optional[ABFChapter]:
        """
        Parse individual chapter link to extract chapter information.
        
        Args:
            link: BeautifulSoup Tag object for chapter link
            section: Parent section information
            
        Returns:
            ABFChapter object or None if parsing fails
        """
        try:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Extract chapter number
            chapter_match = re.search(r'chapter[-_]?(\d+)', href, re.IGNORECASE)
            if not chapter_match:
                chapter_match = re.search(r'chapter\s+(\d+)', text, re.IGNORECASE)
            
            if not chapter_match:
                return None
            
            chapter_number = int(chapter_match.group(1))
            
            # Build full URL
            full_url = urljoin(self.base_tariff_url, href)
            
            # Extract title
            title_parts = text.split('-', 1)
            title = title_parts[1].strip() if len(title_parts) > 1 else text.strip()
            
            return ABFChapter(
                chapter_number=chapter_number,
                title=title,
                section_id=section.section_number,
                chapter_notes=None,  # Will be extracted when scraping chapter content
                url=full_url
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing chapter link: {e}")
            return None
    
    def _extract_chapter_range(self, text: str) -> str:
        """Extract chapter range from section text (e.g., 'Chapters 01-05')."""
        range_match = re.search(r'chapters?\s+(\d+[-–]\d+)', text, re.IGNORECASE)
        if range_match:
            return range_match.group(1)
        
        # Try single chapter format
        chapter_match = re.search(r'chapter\s+(\d+)', text, re.IGNORECASE)
        if chapter_match:
            return chapter_match.group(1)
        
        return ""
    
    # =====================================================
    # CORE TARIFF ITEM SCRAPING METHODS
    # =====================================================
    
    async def _scrape_chapter_tariff_items(self, chapter: ABFChapter, section: ABFSection) -> List[TariffRecord]:
        """
        Scrape tariff items from a chapter page.
        
        Args:
            chapter: ABFChapter object containing chapter information
            section: ABFSection object containing parent section information
            
        Returns:
            List of TariffRecord objects containing all tariff items from the chapter
        """
        try:
            self.logger.info(f"Scraping tariff items from Chapter {chapter.chapter_number}")
            
            # Fetch chapter page content
            content = await self.fetch_page(chapter.url)
            soup = self.parse_html_content(content)
            
            # Extract chapter notes
            chapter_notes = self._extract_chapter_notes(soup)
            if chapter_notes:
                # Update chapter object with notes
                chapter.chapter_notes = chapter_notes
                self.chapters_cache[chapter.chapter_number] = chapter
            
            # Parse tariff table to extract tariff items
            tariff_records = self._parse_tariff_table(soup, chapter, section)
            
            # Add chapter notes to all records
            for record in tariff_records:
                record.chapter_notes = chapter_notes
            
            self.logger.info(f"Successfully extracted {len(tariff_records)} tariff items from Chapter {chapter.chapter_number}")
            
            # Apply rate limiting between chapter requests
            await asyncio.sleep(1)
            
            return tariff_records
            
        except Exception as e:
            self.logger.error(f"Error scraping tariff items from Chapter {chapter.chapter_number}: {e}")
            raise ScrapingError(f"Failed to scrape chapter {chapter.chapter_number}: {e}", source_url=chapter.url)
    
    def _parse_tariff_table(self, soup: BeautifulSoup, chapter: ABFChapter, section: ABFSection) -> List[TariffRecord]:
        """
        Parse tariff table from chapter page.
        
        Args:
            soup: BeautifulSoup object of the chapter page
            chapter: ABFChapter object containing chapter information
            section: ABFSection object containing parent section information
            
        Returns:
            List of TariffRecord objects extracted from the tariff table
        """
        try:
            tariff_records = []
            
            # Use base scraper's table extraction utility
            # Try multiple table selectors for ABF website structure
            table_selectors = [
                'table.tariff-table',
                'table[class*="tariff"]',
                'table[class*="schedule"]',
                '.tariff-content table',
                'table'  # Fallback to any table
            ]
            
            table_data = []
            for selector in table_selectors:
                table_data = self.extract_table_data(soup, selector)
                if table_data:
                    self.logger.debug(f"Found tariff table using selector: {selector}")
                    break
            
            if not table_data:
                self.logger.warning(f"No tariff tables found in Chapter {chapter.chapter_number}")
                return []
            
            # Process each row in the table
            for row_index, row in enumerate(table_data):
                try:
                    # Extract HS code from various possible column names
                    hs_code = None
                    for col_name in ['HS Code', 'Code', 'Tariff Code', 'HS', 'Item']:
                        if col_name in row and row[col_name]:
                            hs_code = row[col_name].strip()
                            break
                    
                    if not hs_code:
                        continue  # Skip rows without HS codes
                    
                    # Validate HS code
                    try:
                        validated_hs_code = validate_hs_code(hs_code)
                    except DataValidationError:
                        self.logger.warning(f"Invalid HS code in Chapter {chapter.chapter_number}: {hs_code}")
                        continue
                    
                    # Extract description
                    description = ""
                    for col_name in ['Description', 'Product Description', 'Item Description', 'Goods']:
                        if col_name in row and row[col_name]:
                            description = row[col_name].strip()
                            break
                    
                    # Extract unit description
                    unit_description = None
                    for col_name in ['Unit', 'Unit of Quantity', 'UoQ', 'Statistical Unit']:
                        if col_name in row and row[col_name]:
                            unit_description = row[col_name].strip()
                            break
                    
                    # Extract duty rate information
                    rate_text = ""
                    general_rate = None
                    for col_name in ['General Rate', 'Rate', 'Duty Rate', 'General', 'Tariff Rate']:
                        if col_name in row and row[col_name]:
                            rate_text = row[col_name].strip()
                            break
                    
                    # Parse duty rate if found
                    if rate_text:
                        general_rate, rate_text = self._parse_duty_rate(rate_text)
                    
                    # Extract statistical code
                    statistical_code = None
                    for col_name in ['Statistical Code', 'Stat Code', 'Statistical', 'Code']:
                        if col_name in row and row[col_name] and col_name != 'HS Code':
                            statistical_code = row[col_name].strip()
                            break
                    
                    # Determine hierarchy level and parent code
                    level = self._determine_hierarchy_level(validated_hs_code)
                    parent_code = self._determine_parent_code(validated_hs_code)
                    
                    # Create TariffRecord
                    tariff_record = TariffRecord(
                        source_url=chapter.url,
                        hs_code=validated_hs_code,
                        description=description,
                        unit_description=unit_description,
                        parent_code=parent_code,
                        level=level,
                        general_rate=general_rate,
                        rate_text=rate_text,
                        statistical_code=statistical_code
                    )
                    
                    tariff_records.append(tariff_record)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing table row {row_index} in Chapter {chapter.chapter_number}: {e}")
                    continue
            
            self.logger.debug(f"Parsed {len(tariff_records)} tariff records from Chapter {chapter.chapter_number}")
            return tariff_records
            
        except Exception as e:
            self.logger.error(f"Error parsing tariff table for Chapter {chapter.chapter_number}: {e}")
            return []
    
    def _parse_duty_rate(self, rate_text: str) -> Tuple[Optional[float], str]:
        """
        Parse duty rate text and return (numeric_rate, full_text).
        
        Args:
            rate_text: Raw duty rate text from the tariff table
            
        Returns:
            Tuple of (numeric_rate, cleaned_rate_text)
        """
        if not rate_text:
            return None, ""
        
        # Clean the rate text
        cleaned_text = rate_text.strip()
        
        try:
            # Check for free rates
            if self.rate_patterns['free'].search(cleaned_text):
                return 0.0, cleaned_text
            
            # Check for percentage rates
            percent_match = self.rate_patterns['percentage'].search(cleaned_text)
            if percent_match:
                rate_value = float(percent_match.group(1))
                return rate_value, cleaned_text
            
            # Check for specific rates (e.g., "$2.50 per kg")
            specific_match = self.rate_patterns['specific'].search(cleaned_text)
            if specific_match:
                # For specific rates, we store the amount but return None for numeric rate
                # since it's not a percentage
                return None, cleaned_text
            
            # Check for compound rates (e.g., "15% or $2.50 per kg")
            compound_match = self.rate_patterns['compound'].search(cleaned_text)
            if compound_match:
                # Return the percentage component for compound rates
                rate_value = float(compound_match.group(1))
                return rate_value, cleaned_text
            
            # Check for complex rates with "whichever is greater/higher"
            complex_match = self.rate_patterns['complex'].search(cleaned_text)
            if complex_match:
                # Return the percentage component for complex rates
                rate_value = float(complex_match.group(1))
                return rate_value, cleaned_text
            
            # Try to extract any numeric value as a fallback
            numeric_match = re.search(r'(\d+(?:\.\d+)?)', cleaned_text)
            if numeric_match:
                rate_value = float(numeric_match.group(1))
                # If it looks like a percentage (small number), treat as percentage
                if rate_value <= 100:
                    return rate_value, cleaned_text
                else:
                    # Large number, probably specific rate
                    return None, cleaned_text
            
            # If no patterns match, return the text as-is
            return None, cleaned_text
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Error parsing duty rate '{rate_text}': {e}")
            return None, cleaned_text
    
    def _extract_chapter_notes(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract chapter notes from chapter page.
        
        Args:
            soup: BeautifulSoup object of the chapter page
            
        Returns:
            Formatted chapter notes text or None if no notes found
        """
        try:
            notes_text = []
            
            # Try multiple selectors for chapter notes
            notes_selectors = [
                '.chapter-notes',
                '.notes',
                '[class*="note"]',
                '#chapter-notes',
                '.tariff-notes',
                'div:contains("Notes")',
                'section:contains("Notes")',
                'p:contains("Note")'
            ]
            
            for selector in notes_selectors:
                try:
                    if selector.startswith('div:contains') or selector.startswith('section:contains') or selector.startswith('p:contains'):
                        # Handle text-based selectors differently
                        elements = soup.find_all(text=re.compile(r'Notes?', re.IGNORECASE))
                        for element in elements:
                            parent = element.parent
                            if parent and parent.name in ['div', 'section', 'p']:
                                notes_text.append(parent.get_text(strip=True))
                    else:
                        # Handle CSS selectors
                        notes_elements = soup.select(selector)
                        for element in notes_elements:
                            text = element.get_text(strip=True)
                            if text and len(text) > 10:  # Filter out very short text
                                notes_text.append(text)
                except Exception:
                    continue
            
            # Also look for notes in table format
            notes_tables = soup.find_all('table', class_=re.compile(r'note', re.IGNORECASE))
            for table in notes_tables:
                table_text = table.get_text(strip=True)
                if table_text and len(table_text) > 10:
                    notes_text.append(table_text)
            
            # Look for notes in specific text patterns
            all_text = soup.get_text()
            notes_patterns = [
                r'Chapter Notes?:?\s*(.+?)(?=Chapter|\n\n|\Z)',
                r'Notes? to Chapter \d+:?\s*(.+?)(?=Chapter|\n\n|\Z)',
                r'General Notes?:?\s*(.+?)(?=Chapter|\n\n|\Z)'
            ]
            
            for pattern in notes_patterns:
                matches = re.findall(pattern, all_text, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    cleaned_match = re.sub(r'\s+', ' ', match.strip())
                    if len(cleaned_match) > 20:  # Filter out very short matches
                        notes_text.append(cleaned_match)
            
            if notes_text:
                # Deduplicate and clean notes
                unique_notes = []
                seen_notes = set()
                
                for note in notes_text:
                    # Clean the note text
                    cleaned_note = re.sub(r'\s+', ' ', note.strip())
                    cleaned_note = re.sub(r'[^\w\s\.\,\;\:\(\)\-\%\$]', '', cleaned_note)
                    
                    # Skip if too short or already seen
                    if len(cleaned_note) < 20 or cleaned_note in seen_notes:
                        continue
                    
                    seen_notes.add(cleaned_note)
                    unique_notes.append(cleaned_note)
                
                if unique_notes:
                    # Join all unique notes
                    final_notes = '\n\n'.join(unique_notes)
                    self.logger.debug(f"Extracted chapter notes: {len(final_notes)} characters")
                    return final_notes
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting chapter notes: {e}")
            return None
    
    def _determine_hierarchy_level(self, hs_code: str) -> int:
        """Determine hierarchy level based on HS code length."""
        code_length = len(hs_code)
        if code_length == 2:
            return 1  # Chapter level
        elif code_length == 4:
            return 2  # Heading level
        elif code_length == 6:
            return 3  # Subheading level
        elif code_length == 8:
            return 4  # Tariff item level
        elif code_length == 10:
            return 5  # Statistical level
        else:
            return 0  # Unknown level
    
    def _determine_parent_code(self, hs_code: str) -> Optional[str]:
        """Determine parent HS code based on hierarchy."""
        if len(hs_code) <= 2:
            return None  # Chapter level has no parent
        elif len(hs_code) == 4:
            return hs_code[:2]  # Parent is chapter
        elif len(hs_code) == 6:
            return hs_code[:4]  # Parent is heading
        elif len(hs_code) == 8:
            return hs_code[:6]  # Parent is subheading
        elif len(hs_code) == 10:
            return hs_code[:8]  # Parent is tariff item
        else:
            return None
    
    def get_base_urls(self) -> List[str]:
        """Get list of base URLs for ABF scraping."""
        return [self.schedule_3_url]
    
    def parse_page_content(self, content: str, url: str) -> List[ScrapedRecord]:
        """
        Parse page content - implemented by specific scraping methods.
        This is used by the base class but ABF scraper uses specialized methods.
        """
        # This method is required by base class but ABF uses specialized parsing
        return []