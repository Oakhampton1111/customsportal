"""
ABF Tariff Codes Scraper - Phase 2 Day 5-10
============================================

Browserless-powered scraper for extracting ABF Working Tariff codes.
This is the CRITICAL third step in the Phase 2 migration sequence.

Prerequisites: 
- tariff_sections table populated (Day 1-2)
- tariff_chapters table populated (Day 3-4)

Populates: tariff_codes table with hierarchical HS codes
Next: ABF Duty Rates Scraper (Day 11-15)

CRITICAL: This MUST complete before Phase 3 as all other data depends on tariff codes.
"""

import asyncio
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass

from .browserless_scraper import BrowserlessScraper, BrowserlessError
from .utils import logger, ScrapingError, DataValidationError, validate_hs_code


@dataclass
class ABFTariffCodeData:
    """Data structure for ABF tariff codes."""
    hs_code: str
    description: str
    unit_description: Optional[str]
    parent_code: Optional[str]
    level: int
    chapter_notes: Optional[str]
    section_id: Optional[int]
    chapter_id: Optional[int]
    chapter_number: int
    url: str


class ABFTariffCodesScraper(BrowserlessScraper):
    """
    ABF Tariff Codes Scraper using Browserless API.
    
    Extracts hierarchical HS codes (2,4,6,8,10 digit levels) from all ABF 
    Working Tariff chapters and populates the tariff_codes table with 
    proper parent-child relationships.
    
    Phase 2 - Day 5-10 Implementation (CRITICAL)
    """
    
    def __init__(self):
        """Initialize ABF tariff codes scraper."""
        super().__init__("ABF_Tariff_Codes")
        self.base_url = "https://www.abf.gov.au"
        self.tariff_codes_data: List[ABFTariffCodeData] = []
        self.chapter_mapping: Dict[int, Tuple[int, int]] = {}  # chapter_number -> (chapter_id, section_id)
        self.processed_codes: Set[str] = set()
        
    async def load_chapter_mapping(self) -> None:
        """
        Load chapter number to chapter/section ID mapping from database.
        Required for proper foreign key relationships.
        """
        try:
            from ..backend.database import get_db_session
            
            async with get_db_session() as session:
                result = await session.execute(
                    """SELECT tc.chapter_number, tc.id as chapter_id, tc.section_id 
                       FROM tariff_chapters tc 
                       ORDER BY tc.chapter_number"""
                )
                
                for chapter_number, chapter_id, section_id in result:
                    self.chapter_mapping[chapter_number] = (chapter_id, section_id)
                
                self.logger.info(f"Loaded {len(self.chapter_mapping)} chapter mappings")
                
                if not self.chapter_mapping:
                    raise ScrapingError("No chapters found in database. Run ABF Chapters scraper first.")
                    
        except Exception as e:
            self.logger.error(f"Error loading chapter mapping: {e}")
            raise ScrapingError(f"Failed to load chapters: {e}")
    
    async def scrape_tariff_codes(self) -> List[ABFTariffCodeData]:
        """
        Main method to scrape all ABF tariff codes from all chapters.
        
        Returns:
            List of ABFTariffCodeData objects
        """
        try:
            self.logger.info("Starting ABF tariff codes scraping...")
            self.logger.info("⚠️  CRITICAL PHASE: This must complete before Phase 3")
            
            # Load chapter mappings first
            await self.load_chapter_mapping()
            
            # Get all chapter URLs from database
            chapter_urls = await self._get_chapter_urls()
            
            self.logger.info(f"Processing {len(chapter_urls)} chapters for tariff codes")
            
            # Process each chapter to extract hierarchical tariff codes
            for chapter_number, chapter_url in chapter_urls.items():
                chapter_id, section_id = self.chapter_mapping.get(chapter_number, (None, None))
                if not chapter_id:
                    self.logger.warning(f"No chapter ID found for chapter {chapter_number}")
                    continue
                
                codes = await self._scrape_chapter_tariff_codes(
                    chapter_url, chapter_number, chapter_id, section_id
                )
                self.tariff_codes_data.extend(codes)
                
                self.logger.info(f"Chapter {chapter_number:02d}: Found {len(codes)} tariff codes")
                
                # Add small delay to respect rate limits
                await asyncio.sleep(1)
            
            # Post-process to establish parent-child relationships
            await self._establish_hierarchy_relationships()
            
            self.logger.info(f"Successfully extracted {len(self.tariff_codes_data)} tariff codes total")
            return self.tariff_codes_data
            
        except Exception as e:
            self.logger.error(f"Error scraping ABF tariff codes: {e}")
            raise ScrapingError(f"Failed to scrape ABF tariff codes: {e}")
    
    async def _get_chapter_urls(self) -> Dict[int, str]:
        """
        Get chapter URLs by scraping section pages.
        
        Returns:
            Dictionary mapping chapter_number to chapter_url
        """
        try:
            # First get all section URLs
            schedule_3_url = "https://www.abf.gov.au/importing-exporting-and-manufacturing/importing/tariff-classification/current-tariff/schedule-3"
            
            sections_query = {
                "section_links": {
                    "selector": "a[href*='section-']",
                    "extract": {
                        "href": "href"
                    }
                }
            }
            
            result = await self.execute_browserql(sections_query, schedule_3_url)
            
            if not result or 'section_links' not in result:
                raise ScrapingError("No section links found")
            
            chapter_urls = {}
            
            # For each section, get chapter links
            for section_link in result['section_links']:
                section_href = section_link.get('href', '')
                if not section_href:
                    continue
                
                section_url = section_href if section_href.startswith('http') else f"{self.base_url}{section_href}"
                
                # Get chapters from this section
                chapters_query = {
                    "chapter_links": {
                        "selector": "a[href*='chapter-']",
                        "extract": {
                            "href": "href"
                        }
                    }
                }
                
                section_result = await self.execute_browserql(chapters_query, section_url)
                
                if section_result and 'chapter_links' in section_result:
                    for chapter_link in section_result['chapter_links']:
                        chapter_href = chapter_link.get('href', '')
                        if not chapter_href:
                            continue
                        
                        # Extract chapter number
                        chapter_match = re.search(r'chapter-(\d+)', chapter_href)
                        if chapter_match:
                            chapter_number = int(chapter_match.group(1))
                            chapter_url = chapter_href if chapter_href.startswith('http') else f"{self.base_url}{chapter_href}"
                            chapter_urls[chapter_number] = chapter_url
            
            return chapter_urls
            
        except Exception as e:
            self.logger.error(f"Error getting chapter URLs: {e}")
            raise
    
    async def _scrape_chapter_tariff_codes(self, chapter_url: str, chapter_number: int, 
                                         chapter_id: int, section_id: int) -> List[ABFTariffCodeData]:
        """
        Scrape tariff codes from a specific chapter page.
        
        Args:
            chapter_url: URL of the chapter page
            chapter_number: Chapter number for validation
            chapter_id: Database chapter ID for foreign key
            section_id: Database section ID for foreign key
            
        Returns:
            List of ABFTariffCodeData objects for this chapter
        """
        try:
            self.logger.debug(f"Scraping tariff codes from chapter {chapter_number:02d}: {chapter_url}")
            
            # BrowserQL query to extract tariff table data
            tariff_query = {
                "tariff_tables": {
                    "selector": "table.tariff-table, table[class*='tariff'], table[class*='schedule']",
                    "extract": "outerHTML"
                },
                "tariff_rows": {
                    "selector": "tr",
                    "extract": {
                        "cells": {
                            "selector": "td, th",
                            "extract": "text"
                        },
                        "links": {
                            "selector": "a",
                            "extract": {
                                "href": "href",
                                "text": "text"
                            }
                        }
                    }
                },
                "chapter_notes": {
                    "selector": ".chapter-notes, .notes, [class*='note']",
                    "extract": "text"
                }
            }
            
            result = await self.execute_browserql(tariff_query, chapter_url)
            
            if not result:
                self.logger.warning(f"No data found for chapter {chapter_number:02d}")
                return []
            
            codes = []
            
            # Extract chapter notes
            chapter_notes = None
            if 'chapter_notes' in result and result['chapter_notes']:
                notes_text = []
                for note in result['chapter_notes']:
                    if note and len(note.strip()) > 20:
                        notes_text.append(note.strip())
                if notes_text:
                    chapter_notes = '\n\n'.join(notes_text)
            
            # Process tariff table rows
            if 'tariff_rows' in result:
                for row_data in result['tariff_rows']:
                    row_codes = await self._parse_tariff_row(
                        row_data, chapter_number, chapter_id, section_id, chapter_notes, chapter_url
                    )
                    codes.extend(row_codes)
            
            # Deduplicate codes by HS code
            unique_codes = {}
            for code in codes:
                if code.hs_code not in unique_codes:
                    unique_codes[code.hs_code] = code
                else:
                    # Keep the one with more complete data
                    existing = unique_codes[code.hs_code]
                    if len(code.description) > len(existing.description):
                        unique_codes[code.hs_code] = code
            
            return list(unique_codes.values())
            
        except Exception as e:
            self.logger.error(f"Error scraping tariff codes from chapter {chapter_number:02d}: {e}")
            return []
    
    async def _parse_tariff_row(self, row_data: Dict[str, Any], chapter_number: int,
                              chapter_id: int, section_id: int, chapter_notes: Optional[str],
                              chapter_url: str) -> List[ABFTariffCodeData]:
        """
        Parse tariff codes from a table row.
        
        Args:
            row_data: Row data from BrowserQL
            chapter_number: Chapter number for validation
            chapter_id: Database chapter ID
            section_id: Database section ID
            chapter_notes: Chapter notes text
            chapter_url: Source URL
            
        Returns:
            List of ABFTariffCodeData objects extracted from this row
        """
        try:
            cells = row_data.get('cells', [])
            if not cells or len(cells) < 2:
                return []
            
            codes = []
            
            # Typical table structure: [HS Code] [Description] [Unit] [Rate] [...]
            for i, cell_text in enumerate(cells):
                if not cell_text or not cell_text.strip():
                    continue
                
                cell_text = cell_text.strip()
                
                # Look for HS code patterns
                hs_code_patterns = [
                    r'\b(\d{2})\.(\d{2})\b',           # 2-digit chapter: 01.00
                    r'\b(\d{4})\.(\d{2})\b',          # 4-digit heading: 0101.00
                    r'\b(\d{4})\.(\d{2})\.(\d{2})\b', # 6-digit subheading: 0101.10.00
                    r'\b(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\b', # 8-digit: 0101.10.10.00
                    r'\b(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})\b', # 10-digit: 0101.10.10.10.00
                    r'\b(\d{2,10})\b'                 # Simple numeric codes
                ]
                
                for pattern in hs_code_patterns:
                    matches = re.finditer(pattern, cell_text)
                    for match in matches:
                        # Extract and clean HS code
                        if '.' in match.group(0):
                            # Remove dots: 0101.10.00 -> 01011000
                            hs_code = re.sub(r'\.', '', match.group(0))
                        else:
                            hs_code = match.group(1) if match.lastindex else match.group(0)
                        
                        # Validate HS code format and length
                        if not re.match(r'^\d+$', hs_code):
                            continue
                        
                        # Ensure it starts with the correct chapter
                        if len(hs_code) >= 2:
                            code_chapter = int(hs_code[:2])
                            if code_chapter != chapter_number:
                                continue
                        
                        # Validate HS code length (2, 4, 6, 8, or 10 digits)
                        if len(hs_code) not in [2, 4, 6, 8, 10]:
                            continue
                        
                        # Skip if already processed
                        if hs_code in self.processed_codes:
                            continue
                        
                        # Extract description (usually in next cell or same cell after code)
                        description = self._extract_description(cell_text, cells, i, hs_code)
                        
                        if not description:
                            continue
                        
                        # Extract unit description if available
                        unit_description = self._extract_unit_description(cells, i)
                        
                        # Determine hierarchy level and parent code
                        level = len(hs_code)
                        parent_code = self._determine_parent_code(hs_code)
                        
                        tariff_code = ABFTariffCodeData(
                            hs_code=hs_code,
                            description=description,
                            unit_description=unit_description,
                            parent_code=parent_code,
                            level=level,
                            chapter_notes=chapter_notes,
                            section_id=section_id,
                            chapter_id=chapter_id,
                            chapter_number=chapter_number,
                            url=chapter_url
                        )
                        
                        codes.append(tariff_code)
                        self.processed_codes.add(hs_code)
                        
                        self.logger.debug(f"Extracted HS code: {hs_code} - {description[:50]}...")
            
            return codes
            
        except Exception as e:
            self.logger.error(f"Error parsing tariff row: {e}")
            return []
    
    def _extract_description(self, cell_text: str, all_cells: List[str], cell_index: int, hs_code: str) -> Optional[str]:
        """Extract description for the HS code."""
        try:
            # Remove the HS code from the cell text to get description
            description = re.sub(r'\b\d{2,10}(?:\.\d{2})*\b', '', cell_text).strip()
            description = re.sub(r'^[-–\s]+|[-–\s]+$', '', description).strip()
            
            # If description is empty or too short, try next cell
            if not description or len(description) < 5:
                if cell_index + 1 < len(all_cells):
                    next_cell = all_cells[cell_index + 1].strip()
                    # Make sure next cell doesn't contain another HS code
                    if not re.search(r'\b\d{4,10}(?:\.\d{2})*\b', next_cell):
                        description = next_cell
            
            # Clean up description
            if description:
                description = re.sub(r'\s+', ' ', description).strip()
                # Remove common prefixes/suffixes
                description = re.sub(r'^[-–\s]*|[-–\s]*$', '', description)
                
                if len(description) >= 5:
                    return description
            
            return None
            
        except Exception:
            return None
    
    def _extract_unit_description(self, all_cells: List[str], cell_index: int) -> Optional[str]:
        """Extract unit description if available."""
        try:
            # Look for unit patterns in surrounding cells
            unit_patterns = [
                r'\b(kg|kilogram|gram|tonne|litre|meter|piece|number|each|pair|dozen)\b',
                r'\b(per\s+\w+)\b',
                r'\b(unit|units)\b'
            ]
            
            # Check current and next few cells
            for i in range(cell_index, min(cell_index + 3, len(all_cells))):
                cell = all_cells[i].strip().lower()
                for pattern in unit_patterns:
                    match = re.search(pattern, cell, re.IGNORECASE)
                    if match:
                        return match.group(0)
            
            return None
            
        except Exception:
            return None
    
    def _determine_parent_code(self, hs_code: str) -> Optional[str]:
        """Determine parent HS code based on hierarchy."""
        try:
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
                
        except Exception:
            return None
    
    async def _establish_hierarchy_relationships(self) -> None:
        """
        Post-process to establish proper parent-child relationships.
        Ensures all parent codes exist before children are saved.
        """
        try:
            self.logger.info("Establishing hierarchy relationships...")
            
            # Group codes by level
            codes_by_level = {2: [], 4: [], 6: [], 8: [], 10: []}
            
            for code in self.tariff_codes_data:
                if code.level in codes_by_level:
                    codes_by_level[code.level].append(code)
            
            # Ensure parent codes exist for each level
            all_codes = {code.hs_code: code for code in self.tariff_codes_data}
            
            for level in [4, 6, 8, 10]:  # Skip level 2 (chapters have no parents)
                for code in codes_by_level[level]:
                    if code.parent_code and code.parent_code not in all_codes:
                        # Create missing parent code
                        parent_code = await self._create_missing_parent(code.parent_code, code)
                        if parent_code:
                            all_codes[parent_code.hs_code] = parent_code
                            self.tariff_codes_data.append(parent_code)
            
            self.logger.info(f"Hierarchy relationships established. Total codes: {len(self.tariff_codes_data)}")
            
        except Exception as e:
            self.logger.error(f"Error establishing hierarchy relationships: {e}")
    
    async def _create_missing_parent(self, parent_hs_code: str, child_code: ABFTariffCodeData) -> Optional[ABFTariffCodeData]:
        """Create a missing parent code based on child code information."""
        try:
            parent_level = len(parent_hs_code)
            parent_parent_code = self._determine_parent_code(parent_hs_code)
            
            # Generate a generic description for the parent
            description = f"HS Code {parent_hs_code} (Auto-generated parent)"
            
            parent_code = ABFTariffCodeData(
                hs_code=parent_hs_code,
                description=description,
                unit_description=None,
                parent_code=parent_parent_code,
                level=parent_level,
                chapter_notes=child_code.chapter_notes,
                section_id=child_code.section_id,
                chapter_id=child_code.chapter_id,
                chapter_number=child_code.chapter_number,
                url=child_code.url
            )
            
            self.logger.debug(f"Created missing parent code: {parent_hs_code}")
            return parent_code
            
        except Exception as e:
            self.logger.error(f"Error creating missing parent {parent_hs_code}: {e}")
            return None
    
    async def save_to_database(self, tariff_codes: List[ABFTariffCodeData]) -> int:
        """
        Save tariff codes to tariff_codes table with proper hierarchy.
        
        Args:
            tariff_codes: List of ABFTariffCodeData objects
            
        Returns:
            Number of records saved
        """
        try:
            from ..backend.database import get_db_session
            
            saved_count = 0
            
            # Sort by level to ensure parents are saved before children
            sorted_codes = sorted(tariff_codes, key=lambda x: x.level)
            
            async with get_db_session() as session:
                for code_data in sorted_codes:
                    # Validate HS code
                    validated_code = validate_hs_code(code_data.hs_code)
                    if not validated_code:
                        self.logger.warning(f"Invalid HS code: {code_data.hs_code}")
                        continue
                    
                    # Check if code already exists
                    existing = await session.execute(
                        "SELECT id FROM tariff_codes WHERE hs_code = ?",
                        (validated_code,)
                    )
                    existing_record = existing.fetchone()
                    
                    if existing_record:
                        # Update existing record
                        await session.execute(
                            """UPDATE tariff_codes 
                               SET description = ?, unit_description = ?, parent_code = ?,
                                   level = ?, chapter_notes = ?, section_id = ?, chapter_id = ?
                               WHERE hs_code = ?""",
                            (code_data.description, code_data.unit_description, code_data.parent_code,
                             code_data.level, code_data.chapter_notes, code_data.section_id,
                             code_data.chapter_id, validated_code)
                        )
                        self.logger.debug(f"Updated tariff code {validated_code}")
                    else:
                        # Create new record
                        await session.execute(
                            """INSERT INTO tariff_codes 
                               (hs_code, description, unit_description, parent_code, level,
                                chapter_notes, section_id, chapter_id, is_active)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (validated_code, code_data.description, code_data.unit_description,
                             code_data.parent_code, code_data.level, code_data.chapter_notes,
                             code_data.section_id, code_data.chapter_id, True)
                        )
                        self.logger.debug(f"Created tariff code {validated_code}")
                    
                    saved_count += 1
                
                await session.commit()
                self.logger.info(f"Successfully saved {saved_count} tariff codes to database")
                
            return saved_count
            
        except Exception as e:
            self.logger.error(f"Error saving tariff codes to database: {e}")
            raise DataValidationError(f"Failed to save tariff codes: {e}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the complete ABF tariff codes scraping workflow.
        
        Returns:
            Dictionary with scraping metrics and results
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("=== ABF Tariff Codes Scraper - Phase 2 Day 5-10 ===")
            self.logger.info("⚠️  CRITICAL: This must complete before Phase 3")
            
            # Step 1: Scrape tariff codes data
            tariff_codes = await self.scrape_tariff_codes()
            
            if not tariff_codes:
                raise ScrapingError("No tariff codes data extracted")
            
            # Step 2: Save to database
            saved_count = await self.save_to_database(tariff_codes)
            
            # Calculate metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Analyze hierarchy distribution
            level_counts = {}
            for code in tariff_codes:
                level_counts[code.level] = level_counts.get(code.level, 0) + 1
            
            metrics = {
                'scraper_name': 'ABF_Tariff_Codes',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'tariff_codes_found': len(tariff_codes),
                'tariff_codes_saved': saved_count,
                'hierarchy_distribution': level_counts,
                'success': True,
                'phase': 'Phase 2 - Day 5-10',
                'next_step': 'ABF Duty Rates Scraper (Day 11-15)',
                'critical_milestone': 'COMPLETED - Ready for Phase 3'
            }
            
            self.logger.info(f"ABF Tariff Codes scraping completed successfully in {duration:.2f}s")
            self.logger.info(f"Found {len(tariff_codes)} tariff codes, saved {saved_count} to database")
            self.logger.info(f"Hierarchy distribution: {level_counts}")
            self.logger.info("✅ CRITICAL MILESTONE COMPLETE - Ready for Phase 3")
            self.logger.info("Next: ABF Duty Rates Scraper (Day 11-15)")
            
            return metrics
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_metrics = {
                'scraper_name': 'ABF_Tariff_Codes',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'success': False,
                'error': str(e),
                'phase': 'Phase 2 - Day 5-10',
                'critical_failure': True
            }
            
            self.logger.error(f"❌ CRITICAL FAILURE: ABF Tariff Codes scraping failed after {duration:.2f}s: {e}")
            self.logger.error("⚠️  Phase 3 cannot proceed until this is resolved")
            raise


# Convenience function for direct execution
async def run_abf_tariff_codes_scraper() -> Dict[str, Any]:
    """
    Convenience function to run ABF tariff codes scraper.
    
    Returns:
        Scraping metrics dictionary
    """
    scraper = ABFTariffCodesScraper()
    return await scraper.run()


if __name__ == "__main__":
    # Direct execution for testing
    asyncio.run(run_abf_tariff_codes_scraper())
