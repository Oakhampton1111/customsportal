"""
ABF Sections Scraper - Phase 2 Day 1-2
=====================================

Browserless-powered scraper for extracting ABF Working Tariff sections.
This is the first step in the Phase 2 migration sequence.

Populates: tariff_sections table
Next: ABF Chapters Scraper (Day 3-4)
"""

import asyncio
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from .browserless_scraper import BrowserlessScraper, BrowserlessError
from .utils import logger, ScrapingError, DataValidationError


@dataclass
class ABFSectionData:
    """Data structure for ABF tariff sections."""
    section_number: int
    title: str
    description: str
    chapter_range: str
    url: str


class ABFSectionsScraper(BrowserlessScraper):
    """
    ABF Sections Scraper using Browserless API.
    
    Extracts all 21 tariff sections from the ABF Working Tariff Schedule 3
    main page and populates the tariff_sections table.
    
    Phase 2 - Day 1-2 Implementation
    """
    
    def __init__(self):
        """Initialize ABF sections scraper."""
        super().__init__("ABF_Sections")
        self.schedule_3_url = "https://www.abf.gov.au/importing-exporting-and-manufacturing/importing/tariff-classification/current-tariff/schedule-3"
        self.sections_data: List[ABFSectionData] = []
        
    async def scrape_sections(self) -> List[ABFSectionData]:
        """
        Main method to scrape all ABF tariff sections.
        
        Returns:
            List of ABFSectionData objects
        """
        try:
            self.logger.info("Starting ABF sections scraping...")
            
            # BrowserQL query to extract section links and information
            sections_query = {
                "sections": {
                    "selector": "a[href*='section-']",
                    "extract": {
                        "href": "href",
                        "text": "text",
                        "title": "title"
                    }
                },
                "section_descriptions": {
                    "selector": ".section-description, .tariff-section-desc",
                    "extract": "text"
                }
            }
            
            self.logger.info(f"Executing BrowserQL query on {self.schedule_3_url}")
            result = await self.execute_browserql(sections_query, self.schedule_3_url)
            
            if not result or 'sections' not in result:
                raise ScrapingError("No sections data found in BrowserQL result")
            
            sections_links = result['sections']
            self.logger.info(f"Found {len(sections_links)} section links")
            
            # Process each section link
            for link_data in sections_links:
                section_data = await self._parse_section_data(link_data)
                if section_data:
                    self.sections_data.append(section_data)
            
            self.logger.info(f"Successfully extracted {len(self.sections_data)} sections")
            return self.sections_data
            
        except Exception as e:
            self.logger.error(f"Error scraping ABF sections: {e}")
            raise ScrapingError(f"Failed to scrape ABF sections: {e}")
    
    async def _parse_section_data(self, link_data: Dict[str, Any]) -> Optional[ABFSectionData]:
        """
        Parse section data from link information.
        
        Args:
            link_data: Dictionary containing href, text, and title from BrowserQL
            
        Returns:
            ABFSectionData object or None if parsing fails
        """
        try:
            href = link_data.get('href', '')
            text = link_data.get('text', '').strip()
            title_attr = link_data.get('title', '').strip()
            
            if not href or not text:
                self.logger.warning(f"Incomplete section data: {link_data}")
                return None
            
            # Extract section number from href (e.g., "section-1" -> 1)
            section_match = re.search(r'section-(\d+)', href)
            if not section_match:
                self.logger.warning(f"Could not extract section number from href: {href}")
                return None
            
            section_number = int(section_match.group(1))
            
            # Parse title and description from text
            # Format is usually "Section I - Live Animals; Animal Products"
            title_match = re.match(r'Section\s+([IVX]+)\s*[-–]\s*(.+)', text, re.IGNORECASE)
            if title_match:
                roman_numeral = title_match.group(1)
                title = title_match.group(2).strip()
                
                # Convert Roman numeral to number for validation
                roman_to_int = {
                    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
                    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
                    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
                    'XXI': 21
                }
                
                expected_section = roman_to_int.get(roman_numeral, section_number)
                if expected_section != section_number:
                    self.logger.warning(f"Section number mismatch: URL={section_number}, Roman={expected_section}")
            else:
                # Fallback parsing
                title = text.replace(f'Section {section_number}', '').strip(' -–')
            
            # Extract chapter range - need to scrape the section page for this
            chapter_range = await self._extract_chapter_range(href)
            
            # Build full URL
            full_url = href if href.startswith('http') else f"https://www.abf.gov.au{href}"
            
            # Use title_attr as description if available, otherwise use title
            description = title_attr if title_attr and title_attr != text else title
            
            section_data = ABFSectionData(
                section_number=section_number,
                title=title,
                description=description,
                chapter_range=chapter_range or "",
                url=full_url
            )
            
            self.logger.debug(f"Parsed section {section_number}: {title}")
            return section_data
            
        except Exception as e:
            self.logger.error(f"Error parsing section data {link_data}: {e}")
            return None
    
    async def _extract_chapter_range(self, section_href: str) -> Optional[str]:
        """
        Extract chapter range from section page.
        
        Args:
            section_href: Relative or absolute URL to section page
            
        Returns:
            Chapter range string (e.g., "01-05") or None
        """
        try:
            # Build full URL if needed
            section_url = section_href if section_href.startswith('http') else f"https://www.abf.gov.au{section_href}"
            
            # BrowserQL query to find chapter range information
            chapter_range_query = {
                "chapter_info": {
                    "selector": ".chapter-range, .chapters, h2, h3, .section-content",
                    "extract": "text"
                },
                "chapter_links": {
                    "selector": "a[href*='chapter-']",
                    "extract": {
                        "href": "href",
                        "text": "text"
                    }
                }
            }
            
            result = await self.execute_browserql(chapter_range_query, section_url)
            
            if not result:
                return None
            
            # Try to extract from chapter links first
            if 'chapter_links' in result and result['chapter_links']:
                chapter_numbers = []
                for link in result['chapter_links']:
                    chapter_match = re.search(r'chapter-(\d+)', link.get('href', ''))
                    if chapter_match:
                        chapter_numbers.append(int(chapter_match.group(1)))
                
                if chapter_numbers:
                    chapter_numbers.sort()
                    min_chapter = min(chapter_numbers)
                    max_chapter = max(chapter_numbers)
                    return f"{min_chapter:02d}-{max_chapter:02d}"
            
            # Try to extract from text content
            if 'chapter_info' in result:
                for text in result['chapter_info']:
                    if not text:
                        continue
                    
                    # Look for patterns like "Chapters 01-05" or "Chapters 1 to 5"
                    range_patterns = [
                        r'Chapters?\s+(\d+)\s*[-–to]\s*(\d+)',
                        r'Chapter\s+(\d+)\s*[-–to]\s*(\d+)',
                        r'(\d+)\s*[-–]\s*(\d+)'
                    ]
                    
                    for pattern in range_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            start_chapter = int(match.group(1))
                            end_chapter = int(match.group(2))
                            return f"{start_chapter:02d}-{end_chapter:02d}"
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not extract chapter range from {section_href}: {e}")
            return None
    
    async def save_to_database(self, sections: List[ABFSectionData]) -> int:
        """
        Save sections data to tariff_sections table.
        
        Args:
            sections: List of ABFSectionData objects
            
        Returns:
            Number of records saved
        """
        try:
            from ..backend.models.hierarchy import TariffSection
            from ..backend.database import get_db_session
            
            saved_count = 0
            
            async with get_db_session() as session:
                for section_data in sections:
                    # Check if section already exists
                    existing = await session.get(TariffSection, section_data.section_number)
                    
                    if existing:
                        # Update existing record
                        existing.title = section_data.title
                        existing.description = section_data.description
                        existing.chapter_range = section_data.chapter_range
                        self.logger.debug(f"Updated section {section_data.section_number}")
                    else:
                        # Create new record
                        new_section = TariffSection(
                            section_number=section_data.section_number,
                            title=section_data.title,
                            description=section_data.description,
                            chapter_range=section_data.chapter_range
                        )
                        session.add(new_section)
                        self.logger.debug(f"Created section {section_data.section_number}")
                    
                    saved_count += 1
                
                await session.commit()
                self.logger.info(f"Successfully saved {saved_count} sections to database")
                
            return saved_count
            
        except Exception as e:
            self.logger.error(f"Error saving sections to database: {e}")
            raise DataValidationError(f"Failed to save sections: {e}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the complete ABF sections scraping workflow.
        
        Returns:
            Dictionary with scraping metrics and results
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("=== ABF Sections Scraper - Phase 2 Day 1-2 ===")
            
            # Step 1: Scrape sections data
            sections = await self.scrape_sections()
            
            if not sections:
                raise ScrapingError("No sections data extracted")
            
            # Step 2: Save to database
            saved_count = await self.save_to_database(sections)
            
            # Calculate metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            metrics = {
                'scraper_name': 'ABF_Sections',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'sections_found': len(sections),
                'sections_saved': saved_count,
                'success': True,
                'phase': 'Phase 2 - Day 1-2',
                'next_step': 'ABF Chapters Scraper (Day 3-4)'
            }
            
            self.logger.info(f"ABF Sections scraping completed successfully in {duration:.2f}s")
            self.logger.info(f"Found {len(sections)} sections, saved {saved_count} to database")
            self.logger.info("Ready for Phase 2 Day 3-4: ABF Chapters Scraper")
            
            return metrics
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_metrics = {
                'scraper_name': 'ABF_Sections',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'success': False,
                'error': str(e),
                'phase': 'Phase 2 - Day 1-2'
            }
            
            self.logger.error(f"ABF Sections scraping failed after {duration:.2f}s: {e}")
            raise


# Convenience function for direct execution
async def run_abf_sections_scraper() -> Dict[str, Any]:
    """
    Convenience function to run ABF sections scraper.
    
    Returns:
        Scraping metrics dictionary
    """
    scraper = ABFSectionsScraper()
    return await scraper.run()


if __name__ == "__main__":
    # Direct execution for testing
    asyncio.run(run_abf_sections_scraper())
