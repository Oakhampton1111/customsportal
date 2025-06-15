"""
ABF Chapters Scraper - Phase 2 Day 3-4
=======================================

Browserless-powered scraper for extracting ABF Working Tariff chapters.
This is the second step in the Phase 2 migration sequence.

Prerequisites: tariff_sections table populated (Day 1-2)
Populates: tariff_chapters table
Next: ABF Tariff Codes Scraper (Day 5-10)
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
class ABFChapterData:
    """Data structure for ABF tariff chapters."""
    chapter_number: int
    title: str
    chapter_notes: Optional[str]
    section_id: int
    url: str


class ABFChaptersScraper(BrowserlessScraper):
    """
    ABF Chapters Scraper using Browserless API.
    
    Extracts all 99 chapters from ABF Working Tariff sections
    and populates the tariff_chapters table with proper section relationships.
    
    Phase 2 - Day 3-4 Implementation
    """
    
    def __init__(self):
        """Initialize ABF chapters scraper."""
        super().__init__("ABF_Chapters")
        self.base_url = "https://www.abf.gov.au"
        self.chapters_data: List[ABFChapterData] = []
        self.section_mapping: Dict[int, int] = {}  # section_number -> section_id
        
    async def load_sections_mapping(self) -> None:
        """
        Load section number to section ID mapping from database.
        Required for proper foreign key relationships.
        """
        try:
            from ..backend.models.hierarchy import TariffSection
            from ..backend.database import get_db_session
            
            async with get_db_session() as session:
                sections = await session.execute(
                    "SELECT section_number, id FROM tariff_sections ORDER BY section_number"
                )
                
                for section_number, section_id in sections:
                    self.section_mapping[section_number] = section_id
                
                self.logger.info(f"Loaded {len(self.section_mapping)} section mappings")
                
                if not self.section_mapping:
                    raise ScrapingError("No sections found in database. Run ABF Sections scraper first.")
                    
        except Exception as e:
            self.logger.error(f"Error loading sections mapping: {e}")
            raise ScrapingError(f"Failed to load sections: {e}")
    
    async def scrape_chapters(self) -> List[ABFChapterData]:
        """
        Main method to scrape all ABF tariff chapters from all sections.
        
        Returns:
            List of ABFChapterData objects
        """
        try:
            self.logger.info("Starting ABF chapters scraping...")
            
            # Load section mappings first
            await self.load_sections_mapping()
            
            # Get all section URLs from database
            section_urls = await self._get_section_urls()
            
            self.logger.info(f"Processing {len(section_urls)} sections for chapters")
            
            # Process each section to extract chapters
            for section_number, section_url in section_urls.items():
                section_id = self.section_mapping.get(section_number)
                if not section_id:
                    self.logger.warning(f"No section ID found for section {section_number}")
                    continue
                
                chapters = await self._scrape_section_chapters(section_url, section_number, section_id)
                self.chapters_data.extend(chapters)
                
                self.logger.info(f"Section {section_number}: Found {len(chapters)} chapters")
            
            self.logger.info(f"Successfully extracted {len(self.chapters_data)} chapters total")
            return self.chapters_data
            
        except Exception as e:
            self.logger.error(f"Error scraping ABF chapters: {e}")
            raise ScrapingError(f"Failed to scrape ABF chapters: {e}")
    
    async def _get_section_urls(self) -> Dict[int, str]:
        """
        Get section URLs from the main Schedule 3 page.
        
        Returns:
            Dictionary mapping section_number to section_url
        """
        try:
            schedule_3_url = "https://www.abf.gov.au/importing-exporting-and-manufacturing/importing/tariff-classification/current-tariff/schedule-3"
            
            # BrowserQL query to get section links
            sections_query = {
                "section_links": {
                    "selector": "a[href*='section-']",
                    "extract": {
                        "href": "href",
                        "text": "text"
                    }
                }
            }
            
            result = await self.execute_browserql(sections_query, schedule_3_url)
            
            if not result or 'section_links' not in result:
                raise ScrapingError("No section links found")
            
            section_urls = {}
            for link in result['section_links']:
                href = link.get('href', '')
                text = link.get('text', '')
                
                # Extract section number
                section_match = re.search(r'section-(\d+)', href)
                if section_match:
                    section_number = int(section_match.group(1))
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    section_urls[section_number] = full_url
            
            return section_urls
            
        except Exception as e:
            self.logger.error(f"Error getting section URLs: {e}")
            raise
    
    async def _scrape_section_chapters(self, section_url: str, section_number: int, section_id: int) -> List[ABFChapterData]:
        """
        Scrape chapters from a specific section page.
        
        Args:
            section_url: URL of the section page
            section_number: Section number for logging
            section_id: Database section ID for foreign key
            
        Returns:
            List of ABFChapterData objects for this section
        """
        try:
            self.logger.debug(f"Scraping chapters from section {section_number}: {section_url}")
            
            # BrowserQL query to extract chapter information
            chapters_query = {
                "chapter_links": {
                    "selector": "a[href*='chapter-']",
                    "extract": {
                        "href": "href",
                        "text": "text",
                        "title": "title"
                    }
                },
                "chapter_headings": {
                    "selector": "h2, h3, .chapter-title",
                    "extract": "text"
                }
            }
            
            result = await self.execute_browserql(chapters_query, section_url)
            
            if not result or 'chapter_links' not in result:
                self.logger.warning(f"No chapter links found in section {section_number}")
                return []
            
            chapters = []
            chapter_links = result['chapter_links']
            
            for link_data in chapter_links:
                chapter_data = await self._parse_chapter_data(link_data, section_id)
                if chapter_data:
                    chapters.append(chapter_data)
            
            return chapters
            
        except Exception as e:
            self.logger.error(f"Error scraping chapters from section {section_number}: {e}")
            return []
    
    async def _parse_chapter_data(self, link_data: Dict[str, Any], section_id: int) -> Optional[ABFChapterData]:
        """
        Parse chapter data from link information.
        
        Args:
            link_data: Dictionary containing href, text, and title from BrowserQL
            section_id: Database section ID for foreign key
            
        Returns:
            ABFChapterData object or None if parsing fails
        """
        try:
            href = link_data.get('href', '')
            text = link_data.get('text', '').strip()
            title_attr = link_data.get('title', '').strip()
            
            if not href or not text:
                return None
            
            # Extract chapter number from href (e.g., "chapter-01" -> 1)
            chapter_match = re.search(r'chapter-(\d+)', href)
            if not chapter_match:
                self.logger.warning(f"Could not extract chapter number from href: {href}")
                return None
            
            chapter_number = int(chapter_match.group(1))
            
            # Parse title from text
            # Format is usually "Chapter 01 - Live Animals" or just the title
            title_match = re.match(r'Chapter\s+\d+\s*[-–]\s*(.+)', text, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                # Remove "Chapter XX" prefix if present
                title = re.sub(r'^Chapter\s+\d+\s*[-–]?\s*', '', text, flags=re.IGNORECASE).strip()
            
            # Build full URL
            full_url = href if href.startswith('http') else f"{self.base_url}{href}"
            
            # Extract chapter notes from the chapter page
            chapter_notes = await self._extract_chapter_notes(full_url)
            
            chapter_data = ABFChapterData(
                chapter_number=chapter_number,
                title=title,
                chapter_notes=chapter_notes,
                section_id=section_id,
                url=full_url
            )
            
            self.logger.debug(f"Parsed chapter {chapter_number:02d}: {title}")
            return chapter_data
            
        except Exception as e:
            self.logger.error(f"Error parsing chapter data {link_data}: {e}")
            return None
    
    async def _extract_chapter_notes(self, chapter_url: str) -> Optional[str]:
        """
        Extract chapter notes from chapter page.
        
        Args:
            chapter_url: URL of the chapter page
            
        Returns:
            Chapter notes text or None
        """
        try:
            # BrowserQL query to extract chapter notes
            notes_query = {
                "chapter_notes": {
                    "selector": ".chapter-notes, .notes, .chapter-note, [class*='note']",
                    "extract": "text"
                },
                "note_headings": {
                    "selector": "h2:contains('Note'), h3:contains('Note'), h4:contains('Note')",
                    "extract": "text"
                },
                "note_content": {
                    "selector": "p, div, .content",
                    "extract": "text"
                }
            }
            
            result = await self.execute_browserql(notes_query, chapter_url)
            
            if not result:
                return None
            
            notes_text = []
            
            # Collect notes from dedicated notes sections
            if 'chapter_notes' in result and result['chapter_notes']:
                for note in result['chapter_notes']:
                    if note and len(note.strip()) > 20:  # Filter out short/empty notes
                        notes_text.append(note.strip())
            
            # Look for notes in content that mention "Note" or "Notes"
            if 'note_content' in result:
                for content in result['note_content']:
                    if not content:
                        continue
                    
                    # Look for note patterns
                    if re.search(r'\b(note|notes?)\b.*:', content, re.IGNORECASE):
                        if len(content.strip()) > 20:
                            notes_text.append(content.strip())
            
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
                    final_notes = '\n\n'.join(unique_notes)
                    self.logger.debug(f"Extracted chapter notes: {len(final_notes)} characters")
                    return final_notes
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not extract chapter notes from {chapter_url}: {e}")
            return None
    
    async def save_to_database(self, chapters: List[ABFChapterData]) -> int:
        """
        Save chapters data to tariff_chapters table.
        
        Args:
            chapters: List of ABFChapterData objects
            
        Returns:
            Number of records saved
        """
        try:
            from ..backend.models.hierarchy import TariffChapter
            from ..backend.database import get_db_session
            
            saved_count = 0
            
            async with get_db_session() as session:
                for chapter_data in chapters:
                    # Check if chapter already exists
                    existing = await session.execute(
                        "SELECT id FROM tariff_chapters WHERE chapter_number = ?",
                        (chapter_data.chapter_number,)
                    )
                    existing_record = existing.fetchone()
                    
                    if existing_record:
                        # Update existing record
                        await session.execute(
                            """UPDATE tariff_chapters 
                               SET title = ?, chapter_notes = ?, section_id = ?
                               WHERE chapter_number = ?""",
                            (chapter_data.title, chapter_data.chapter_notes, 
                             chapter_data.section_id, chapter_data.chapter_number)
                        )
                        self.logger.debug(f"Updated chapter {chapter_data.chapter_number:02d}")
                    else:
                        # Create new record
                        await session.execute(
                            """INSERT INTO tariff_chapters 
                               (chapter_number, title, chapter_notes, section_id)
                               VALUES (?, ?, ?, ?)""",
                            (chapter_data.chapter_number, chapter_data.title,
                             chapter_data.chapter_notes, chapter_data.section_id)
                        )
                        self.logger.debug(f"Created chapter {chapter_data.chapter_number:02d}")
                    
                    saved_count += 1
                
                await session.commit()
                self.logger.info(f"Successfully saved {saved_count} chapters to database")
                
            return saved_count
            
        except Exception as e:
            self.logger.error(f"Error saving chapters to database: {e}")
            raise DataValidationError(f"Failed to save chapters: {e}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the complete ABF chapters scraping workflow.
        
        Returns:
            Dictionary with scraping metrics and results
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("=== ABF Chapters Scraper - Phase 2 Day 3-4 ===")
            
            # Step 1: Scrape chapters data
            chapters = await self.scrape_chapters()
            
            if not chapters:
                raise ScrapingError("No chapters data extracted")
            
            # Step 2: Save to database
            saved_count = await self.save_to_database(chapters)
            
            # Calculate metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            metrics = {
                'scraper_name': 'ABF_Chapters',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'chapters_found': len(chapters),
                'chapters_saved': saved_count,
                'success': True,
                'phase': 'Phase 2 - Day 3-4',
                'next_step': 'ABF Tariff Codes Scraper (Day 5-10)'
            }
            
            self.logger.info(f"ABF Chapters scraping completed successfully in {duration:.2f}s")
            self.logger.info(f"Found {len(chapters)} chapters, saved {saved_count} to database")
            self.logger.info("Ready for Phase 2 Day 5-10: ABF Tariff Codes Scraper")
            
            return metrics
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_metrics = {
                'scraper_name': 'ABF_Chapters',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'success': False,
                'error': str(e),
                'phase': 'Phase 2 - Day 3-4'
            }
            
            self.logger.error(f"ABF Chapters scraping failed after {duration:.2f}s: {e}")
            raise


# Convenience function for direct execution
async def run_abf_chapters_scraper() -> Dict[str, Any]:
    """
    Convenience function to run ABF chapters scraper.
    
    Returns:
        Scraping metrics dictionary
    """
    scraper = ABFChaptersScraper()
    return await scraper.run()


if __name__ == "__main__":
    # Direct execution for testing
    asyncio.run(run_abf_chapters_scraper())
