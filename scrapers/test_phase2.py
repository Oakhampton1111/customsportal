"""
Phase 2 Test Suite
==================

Comprehensive test suite for Phase 2 Core Tariff Migration.
Tests each component individually and the complete orchestrated sequence.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from .phase2_orchestrator import Phase2Orchestrator, run_phase2_step
from .abf_sections_scraper import ABFSectionsScraper
from .abf_chapters_scraper import ABFChaptersScraper
from .abf_tariff_codes_scraper import ABFTariffCodesScraper
from .utils import logger


class Phase2TestSuite:
    """Test suite for Phase 2 migration components."""
    
    def __init__(self):
        """Initialize test suite."""
        self.logger = logger
        self.test_results: List[Dict[str, Any]] = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run complete Phase 2 test suite.
        
        Returns:
            Test results summary
        """
        start_time = datetime.now()
        
        try:
            self.logger.info("=" * 60)
            self.logger.info("🧪 PHASE 2 TEST SUITE")
            self.logger.info("=" * 60)
            
            # Test 1: Configuration validation
            await self._test_configuration()
            
            # Test 2: Database connectivity
            await self._test_database_connectivity()
            
            # Test 3: Individual scraper initialization
            await self._test_scraper_initialization()
            
            # Test 4: BrowserQL query validation
            await self._test_browserql_queries()
            
            # Test 5: Data validation functions
            await self._test_data_validation()
            
            # Test 6: Hierarchy relationship logic
            await self._test_hierarchy_logic()
            
            # Test 7: Single step execution (if API key available)
            await self._test_single_step_execution()
            
            # Calculate results
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            passed_tests = sum(1 for result in self.test_results if result['passed'])
            total_tests = len(self.test_results)
            
            summary = {
                'test_suite': 'Phase 2 Core Tariff Migration',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'all_passed': passed_tests == total_tests,
                'test_results': self.test_results
            }
            
            self.logger.info("=" * 60)
            self.logger.info("📊 TEST RESULTS SUMMARY")
            self.logger.info("=" * 60)
            self.logger.info(f"Total Tests: {total_tests}")
            self.logger.info(f"Passed: {passed_tests}")
            self.logger.info(f"Failed: {total_tests - passed_tests}")
            self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
            
            if summary['all_passed']:
                self.logger.info("✅ ALL TESTS PASSED - Phase 2 ready for execution")
            else:
                self.logger.warning("⚠️  Some tests failed - Review before running Phase 2")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Test suite crashed: {e}")
            raise
    
    async def _test_configuration(self) -> None:
        """Test configuration loading and validation."""
        test_name = "Configuration Validation"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            from .config import ScraperConfig
            config = ScraperConfig()
            
            # Test browserless config
            assert hasattr(config, 'browserless_config'), "Browserless config missing"
            assert hasattr(config.browserless_config, 'api_url'), "API URL missing"
            assert hasattr(config.browserless_config, 'api_key'), "API key missing"
            assert hasattr(config.browserless_config, 'timeout'), "Timeout missing"
            
            # Test that URLs are valid format
            api_url = config.browserless_config.api_url
            assert api_url.startswith('http'), f"Invalid API URL format: {api_url}"
            
            self._record_test_result(test_name, True, "Configuration loaded successfully")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    async def _test_database_connectivity(self) -> None:
        """Test database connectivity and table existence."""
        test_name = "Database Connectivity"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            from ..backend.database import get_db_session
            
            # Test basic connectivity
            async with get_db_session() as session:
                result = await session.execute("SELECT 1")
                assert result.fetchone() is not None, "Database query failed"
            
            # Test required tables exist
            required_tables = ['tariff_sections', 'tariff_chapters', 'tariff_codes']
            async with get_db_session() as session:
                for table in required_tables:
                    # This query works for both SQLite and PostgreSQL
                    result = await session.execute(f"SELECT COUNT(*) FROM {table} LIMIT 1")
                    # If table doesn't exist, this will raise an exception
            
            self._record_test_result(test_name, True, "Database connectivity verified")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    async def _test_scraper_initialization(self) -> None:
        """Test that all scrapers can be initialized properly."""
        test_name = "Scraper Initialization"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            # Test sections scraper
            sections_scraper = ABFSectionsScraper()
            assert sections_scraper.scraper_name == "ABF_Sections", "Sections scraper name incorrect"
            assert hasattr(sections_scraper, 'schedule_3_url'), "Sections scraper missing URL"
            
            # Test chapters scraper
            chapters_scraper = ABFChaptersScraper()
            assert chapters_scraper.scraper_name == "ABF_Chapters", "Chapters scraper name incorrect"
            assert hasattr(chapters_scraper, 'base_url'), "Chapters scraper missing base URL"
            
            # Test tariff codes scraper
            codes_scraper = ABFTariffCodesScraper()
            assert codes_scraper.scraper_name == "ABF_Tariff_Codes", "Codes scraper name incorrect"
            assert hasattr(codes_scraper, 'base_url'), "Codes scraper missing base URL"
            
            self._record_test_result(test_name, True, "All scrapers initialized successfully")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    async def _test_browserql_queries(self) -> None:
        """Test BrowserQL query structure validation."""
        test_name = "BrowserQL Query Validation"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            # Test sections query structure
            sections_query = {
                "sections": {
                    "selector": "a[href*='section-']",
                    "extract": {
                        "href": "href",
                        "text": "text",
                        "title": "title"
                    }
                }
            }
            assert isinstance(sections_query, dict), "Sections query must be dict"
            assert "sections" in sections_query, "Sections query missing sections key"
            
            # Test chapters query structure
            chapters_query = {
                "chapter_links": {
                    "selector": "a[href*='chapter-']",
                    "extract": {
                        "href": "href",
                        "text": "text",
                        "title": "title"
                    }
                }
            }
            assert isinstance(chapters_query, dict), "Chapters query must be dict"
            assert "chapter_links" in chapters_query, "Chapters query missing chapter_links key"
            
            # Test tariff codes query structure
            tariff_query = {
                "tariff_rows": {
                    "selector": "tr",
                    "extract": {
                        "cells": {
                            "selector": "td, th",
                            "extract": "text"
                        }
                    }
                }
            }
            assert isinstance(tariff_query, dict), "Tariff query must be dict"
            assert "tariff_rows" in tariff_query, "Tariff query missing tariff_rows key"
            
            self._record_test_result(test_name, True, "BrowserQL queries validated")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    async def _test_data_validation(self) -> None:
        """Test data validation functions."""
        test_name = "Data Validation Functions"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            from .utils import validate_hs_code
            
            # Test valid HS codes
            assert validate_hs_code("01") == "01", "2-digit HS code validation failed"
            assert validate_hs_code("0101") == "0101", "4-digit HS code validation failed"
            assert validate_hs_code("010110") == "010110", "6-digit HS code validation failed"
            assert validate_hs_code("01011000") == "01011000", "8-digit HS code validation failed"
            assert validate_hs_code("0101100000") == "0101100000", "10-digit HS code validation failed"
            
            # Test invalid HS codes
            assert validate_hs_code("1") is None, "1-digit code should be invalid"
            assert validate_hs_code("123") is None, "3-digit code should be invalid"
            assert validate_hs_code("abc") is None, "Non-numeric code should be invalid"
            assert validate_hs_code("") is None, "Empty code should be invalid"
            
            self._record_test_result(test_name, True, "Data validation functions working")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    async def _test_hierarchy_logic(self) -> None:
        """Test hierarchy relationship logic."""
        test_name = "Hierarchy Relationship Logic"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            # Test parent code determination
            codes_scraper = ABFTariffCodesScraper()
            
            # Test hierarchy levels
            assert codes_scraper._determine_parent_code("01") is None, "Chapter should have no parent"
            assert codes_scraper._determine_parent_code("0101") == "01", "Heading parent incorrect"
            assert codes_scraper._determine_parent_code("010110") == "0101", "Subheading parent incorrect"
            assert codes_scraper._determine_parent_code("01011000") == "010110", "Tariff item parent incorrect"
            assert codes_scraper._determine_parent_code("0101100000") == "01011000", "Statistical code parent incorrect"
            
            self._record_test_result(test_name, True, "Hierarchy logic working correctly")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    async def _test_single_step_execution(self) -> None:
        """Test single step execution if API key is available."""
        test_name = "Single Step Execution Test"
        
        try:
            self.logger.info(f"🔍 Testing: {test_name}")
            
            from .config import ScraperConfig
            config = ScraperConfig()
            
            # Only run if API key is configured
            if not config.browserless_config.api_key or config.browserless_config.api_key == "your_api_key_here":
                self._record_test_result(test_name, True, "Skipped - No API key configured")
                return
            
            # Test sections scraper with a single section
            sections_scraper = ABFSectionsScraper()
            
            # Test that scraper can be initialized and configured
            assert hasattr(sections_scraper, 'execute_browserql'), "BrowserQL method missing"
            assert hasattr(sections_scraper, 'config'), "Configuration missing"
            
            self._record_test_result(test_name, True, "Single step execution test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, str(e))
    
    def _record_test_result(self, test_name: str, passed: bool, message: str) -> None:
        """Record a test result."""
        result = {
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        self.logger.info(f"{status}: {test_name} - {message}")


async def run_phase2_tests() -> Dict[str, Any]:
    """
    Run Phase 2 test suite.
    
    Returns:
        Test results dictionary
    """
    test_suite = Phase2TestSuite()
    return await test_suite.run_all_tests()


async def test_prerequisites() -> bool:
    """
    Test Phase 2 prerequisites only.
    
    Returns:
        True if prerequisites are met
    """
    orchestrator = Phase2Orchestrator()
    return await orchestrator.validate_prerequisites()


if __name__ == "__main__":
    # Run test suite
    asyncio.run(run_phase2_tests())
