#!/usr/bin/env python3
# =====================================================
# Browserless Scraper Test Script
# =====================================================
# 
# Test script to validate the new Browserless API integration
# for the ABF Working Tariff scraper. This script performs:
# - Configuration validation
# - Basic API connectivity test
# - Single section scraping proof-of-concept
# - Data quality validation against expected schema
# =====================================================

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add scrapers directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_settings
from abf_browserless_scraper import ABFBrowserlessScraper
from utils import logger


async def test_browserless_config():
    """Test Browserless API configuration."""
    print("\n=== Testing Browserless Configuration ===")
    
    try:
        settings = get_settings()
        browserless_config = settings.browserless
        
        print(f"✓ API URL: {browserless_config.api_url}")
        print(f"✓ API Key: {'*' * (len(browserless_config.api_key) - 4) + browserless_config.api_key[-4:] if browserless_config.api_key else 'NOT SET'}")
        print(f"✓ Timeout: {browserless_config.timeout}s")
        print(f"✓ Max Sessions: {browserless_config.max_sessions}")
        
        if not browserless_config.api_key:
            print("⚠️  WARNING: Browserless API key not set. Set BROWSERLESS_API_KEY environment variable.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_browserless_connectivity():
    """Test basic connectivity to Browserless API."""
    print("\n=== Testing Browserless API Connectivity ===")
    
    try:
        scraper = ABFBrowserlessScraper()
        
        # Test with a simple query on a basic page
        test_url = "https://httpbin.org/html"
        test_query = '{"title": {"selector": "title", "extract": "text"}}'
        
        print(f"Testing connectivity with: {test_url}")
        
        result = await scraper.execute_browserql(test_query, test_url)
        
        if result and "title" in result:
            print(f"✓ API connectivity successful")
            print(f"✓ Response: {result}")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False


async def test_abf_scraper():
    """Test ABF Browserless scraper with a single section."""
    print("\n=== Testing ABF Browserless Scraper ===")
    
    try:
        scraper = ABFBrowserlessScraper()
        
        print("Initializing scraper...")
        print(f"Base URL: {scraper.base_url}")
        
        # Test query building
        queries = scraper.build_extraction_queries()
        print(f"✓ Built {len(queries)} extraction queries")
        
        # Test section URL extraction (limited for testing)
        print("Testing section URL extraction...")
        section_urls = await scraper._get_section_urls()
        
        if section_urls:
            print(f"✓ Found {len(section_urls)} section URLs")
            print(f"First section: {section_urls[0]}")
            
            # Test scraping first section (limited records)
            print("Testing single section scraping...")
            records = await scraper._scrape_section(section_urls[0])
            
            if records:
                print(f"✓ Extracted {len(records)} records")
                
                # Validate first record
                first_record = records[0]
                print(f"Sample record:")
                print(f"  HS Code: {first_record.hs_code}")
                print(f"  Description: {first_record.description[:100]}...")
                print(f"  Level: {first_record.level}")
                print(f"  Parent Code: {first_record.parent_code}")
                
                return True
            else:
                print("⚠️  No records extracted from test section")
                return False
        else:
            print("❌ No section URLs found")
            return False
            
    except Exception as e:
        print(f"❌ ABF scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_validation():
    """Test data validation and database compatibility."""
    print("\n=== Testing Data Validation ===")
    
    try:
        scraper = ABFBrowserlessScraper()
        
        # Create a sample record for validation
        from base_scraper import TariffRecord
        
        sample_record = TariffRecord(
            source_url="https://test.example.com",
            hs_code="0101.10.00",
            description="Live horses - Pure-bred breeding animals",
            unit_description="Number",
            parent_code="0101.10",
            level=3,
            general_rate=0.0,
            rate_text="Free"
        )
        
        # Test validation
        is_valid = scraper.validate_record(sample_record)
        
        if is_valid:
            print("✓ Sample record validation passed")
            print(f"  Validated HS Code: {sample_record.hs_code}")
            print(f"  Content Hash: {sample_record.content_hash}")
            return True
        else:
            print("❌ Sample record validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Data validation test failed: {e}")
        return False


async def main():
    """Run all Browserless scraper tests."""
    print("🚀 Starting Browserless Scraper Tests")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    test_results = []
    
    # Run tests
    test_results.append(("Configuration", await test_browserless_config()))
    test_results.append(("Connectivity", await test_browserless_connectivity()))
    test_results.append(("Data Validation", await test_data_validation()))
    test_results.append(("ABF Scraper", await test_abf_scraper()))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Browserless integration is ready.")
    else:
        print("⚠️  Some tests failed. Check configuration and API access.")
    
    return passed == total


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("BROWSERLESS_API_KEY"):
        print("⚠️  BROWSERLESS_API_KEY environment variable not set.")
        print("Set it with: export BROWSERLESS_API_KEY=your_api_key")
        print("Or add it to your .env file")
        print("\nRunning tests with limited functionality...")
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
