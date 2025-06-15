"""
Comprehensive TCO Data Verification Script
==========================================
Verifies the quality, completeness, and integrity of TCO data in the database.
"""

import sqlite3
import time
from datetime import datetime, date
from typing import Dict, List, Tuple

def verify_tco_data():
    """Comprehensive verification of TCO data."""
    
    print("=" * 80)
    print("🔍 COMPREHENSIVE TCO DATA VERIFICATION")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        # 1. Basic Data Counts
        print("1. 📊 BASIC DATA COUNTS:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos")
        total_tcos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE is_current = 1")
        active_tcos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE is_current = 0")
        inactive_tcos = cursor.fetchone()[0]
        
        print(f"   Total TCOs: {total_tcos:,}")
        print(f"   Active TCOs: {active_tcos:,}")
        print(f"   Inactive TCOs: {inactive_tcos:,}")
        print(f"   Active percentage: {(active_tcos/total_tcos*100):.1f}%")
        
        # 2. TCO Number Format Validation
        print("\n2. 🔢 TCO NUMBER FORMAT VALIDATION:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE tco_number IS NULL OR tco_number = ''")
        null_tco_numbers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT tco_number) FROM tcos")
        unique_tco_numbers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tcos 
            WHERE tco_number NOT LIKE 'TCO-%-%'
        """)
        invalid_format = cursor.fetchone()[0]
        
        print(f"   NULL/Empty TCO numbers: {null_tco_numbers}")
        print(f"   Unique TCO numbers: {unique_tco_numbers:,}")
        print(f"   Duplicate TCO numbers: {total_tcos - unique_tco_numbers}")
        print(f"   Invalid format: {invalid_format}")
        
        # 3. HS Code Validation
        print("\n3. 🏷️  HS CODE VALIDATION:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE hs_code IS NULL OR hs_code = ''")
        null_hs_codes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tcos t
            INNER JOIN tariff_codes tc ON t.hs_code = tc.hs_code
        """)
        valid_hs_codes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tcos t
            LEFT JOIN tariff_codes tc ON t.hs_code = tc.hs_code
            WHERE tc.hs_code IS NULL
        """)
        invalid_hs_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM tcos")
        unique_hs_codes = cursor.fetchone()[0]
        
        print(f"   NULL/Empty HS codes: {null_hs_codes}")
        print(f"   Valid HS code references: {valid_hs_codes:,}")
        print(f"   Invalid HS code references: {invalid_hs_codes}")
        print(f"   Unique HS codes used: {unique_hs_codes:,}")
        print(f"   HS code validation rate: {(valid_hs_codes/total_tcos*100):.1f}%")
        
        # 4. Chapter Distribution Analysis
        print("\n4. 📈 CHAPTER DISTRIBUTION ANALYSIS:")
        
        cursor.execute("""
            SELECT SUBSTR(hs_code, 1, 2) as chapter, COUNT(*) as count
            FROM tcos 
            GROUP BY SUBSTR(hs_code, 1, 2)
            ORDER BY count DESC
        """)
        chapter_distribution = cursor.fetchall()
        
        print(f"   Chapters covered: {len(chapter_distribution)}")
        print("   Top 10 chapters by TCO count:")
        for i, (chapter, count) in enumerate(chapter_distribution[:10]):
            percentage = (count / total_tcos) * 100
            print(f"      {i+1:2d}. Chapter {chapter}: {count:4d} TCOs ({percentage:5.1f}%)")
        
        # 5. Date Validation
        print("\n5. 📅 DATE VALIDATION:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE effective_date IS NULL")
        null_effective_dates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE expiry_date IS NULL")
        null_expiry_dates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE gazette_date IS NULL")
        null_gazette_dates = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tcos 
            WHERE effective_date IS NOT NULL AND expiry_date IS NOT NULL 
            AND effective_date >= expiry_date
        """)
        invalid_date_ranges = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tcos 
            WHERE expiry_date IS NOT NULL AND expiry_date < date('now')
        """)
        expired_tcos = cursor.fetchone()[0]
        
        print(f"   NULL effective dates: {null_effective_dates}")
        print(f"   NULL expiry dates: {null_expiry_dates}")
        print(f"   NULL gazette dates: {null_gazette_dates}")
        print(f"   Invalid date ranges: {invalid_date_ranges}")
        print(f"   Expired TCOs: {expired_tcos}")
        
        # 6. Applicant Analysis
        print("\n6. 🏢 APPLICANT ANALYSIS:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE applicant_name IS NULL OR applicant_name = ''")
        null_applicants = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT applicant_name) FROM tcos WHERE applicant_name IS NOT NULL")
        unique_applicants = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT applicant_name, COUNT(*) as count
            FROM tcos 
            WHERE applicant_name IS NOT NULL
            GROUP BY applicant_name
            ORDER BY count DESC
            LIMIT 10
        """)
        top_applicants = cursor.fetchall()
        
        print(f"   NULL/Empty applicants: {null_applicants}")
        print(f"   Unique applicants: {unique_applicants}")
        print("   Top 10 applicants by TCO count:")
        for i, (applicant, count) in enumerate(top_applicants):
            print(f"      {i+1:2d}. {applicant}: {count} TCOs")
        
        # 7. Description Quality Check
        print("\n7. 📝 DESCRIPTION QUALITY CHECK:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE description IS NULL OR description = ''")
        null_descriptions = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(LENGTH(description)) FROM tcos WHERE description IS NOT NULL")
        avg_description_length = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE LENGTH(description) < 20")
        short_descriptions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE LENGTH(description) > 200")
        long_descriptions = cursor.fetchone()[0]
        
        print(f"   NULL/Empty descriptions: {null_descriptions}")
        print(f"   Average description length: {avg_description_length:.1f} characters")
        print(f"   Short descriptions (<20 chars): {short_descriptions}")
        print(f"   Long descriptions (>200 chars): {long_descriptions}")
        
        # 8. Gazette Information Analysis
        print("\n8. 📰 GAZETTE INFORMATION ANALYSIS:")
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE gazette_number IS NOT NULL")
        with_gazette_number = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT gazette_number) FROM tcos WHERE gazette_number IS NOT NULL")
        unique_gazette_numbers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT gazette_number, COUNT(*) as count
            FROM tcos 
            WHERE gazette_number IS NOT NULL
            GROUP BY gazette_number
            ORDER BY count DESC
            LIMIT 5
        """)
        gazette_distribution = cursor.fetchall()
        
        print(f"   TCOs with gazette number: {with_gazette_number}")
        print(f"   Unique gazette numbers: {unique_gazette_numbers}")
        print("   Top gazette numbers by TCO count:")
        for gazette_num, count in gazette_distribution:
            print(f"      {gazette_num}: {count} TCOs")
        
        # 9. Year Distribution Analysis
        print("\n9. 📊 YEAR DISTRIBUTION ANALYSIS:")
        
        cursor.execute("""
            SELECT SUBSTR(effective_date, 1, 4) as year, 
                   COUNT(*) as total,
                   SUM(CASE WHEN is_current = 1 THEN 1 ELSE 0 END) as active
            FROM tcos 
            WHERE effective_date IS NOT NULL
            GROUP BY SUBSTR(effective_date, 1, 4)
            ORDER BY year DESC
        """)
        year_distribution = cursor.fetchall()
        
        print("   TCO distribution by year:")
        for year, total, active in year_distribution:
            inactive = total - active
            print(f"      {year}: {total:3d} total ({active:3d} active, {inactive:3d} inactive)")
        
        # 10. Performance Testing
        print("\n10. ⚡ PERFORMANCE TESTING:")
        
        # Test basic queries
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM tcos")
        cursor.fetchone()
        count_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("SELECT * FROM tcos WHERE tco_number = 'TCO-2024-0001'")
        cursor.fetchone()
        lookup_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("""
            SELECT SUBSTR(hs_code, 1, 2), COUNT(*) 
            FROM tcos 
            GROUP BY SUBSTR(hs_code, 1, 2)
        """)
        cursor.fetchall()
        group_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("""
            SELECT t.tco_number, tc.description
            FROM tcos t
            INNER JOIN tariff_codes tc ON t.hs_code = tc.hs_code
            LIMIT 100
        """)
        cursor.fetchall()
        join_time = time.time() - start_time
        
        print(f"   Count query: {count_time:.4f} seconds")
        print(f"   Single TCO lookup: {lookup_time:.4f} seconds")
        print(f"   Group by chapter: {group_time:.4f} seconds")
        print(f"   Join with tariff codes (100 rows): {join_time:.4f} seconds")
        
        # 11. Data Quality Scoring
        print("\n11. 🎯 DATA QUALITY SCORING:")
        
        quality_score = 100
        
        # Deduct points for data issues
        if null_tco_numbers > 0:
            quality_score -= 15
        if total_tcos - unique_tco_numbers > 0:
            quality_score -= 20
        if invalid_format > 0:
            quality_score -= 10
        if null_hs_codes > 0:
            quality_score -= 15
        if invalid_hs_codes > 0:
            quality_score -= 25
        if invalid_date_ranges > 0:
            quality_score -= 10
        if null_descriptions > 0:
            quality_score -= 10
        if short_descriptions > total_tcos * 0.1:  # More than 10% short descriptions
            quality_score -= 5
        
        print(f"   Data Quality Score: {quality_score}/100")
        
        if quality_score >= 95:
            status = "🟢 EXCELLENT"
            recommendation = "TCO data is excellent and ready for production use."
        elif quality_score >= 85:
            status = "🟡 GOOD"
            recommendation = "TCO data is good with minor issues to address."
        elif quality_score >= 70:
            status = "🟠 ACCEPTABLE"
            recommendation = "TCO data is acceptable but needs improvement."
        else:
            status = "🔴 POOR"
            recommendation = "TCO data has significant issues that need attention."
        
        print(f"   Status: {status}")
        print(f"   Recommendation: {recommendation}")
        
        # 12. Sample Data Inspection
        print("\n12. 🔍 SAMPLE DATA INSPECTION:")
        
        cursor.execute("""
            SELECT tco_number, hs_code, description, applicant_name, 
                   effective_date, expiry_date, is_current
            FROM tcos 
            WHERE is_current = 1
            ORDER BY effective_date DESC
            LIMIT 5
        """)
        
        recent_active = cursor.fetchall()
        
        print("   Recent active TCOs:")
        for tco_num, hs_code, desc, applicant, eff_date, exp_date, is_current in recent_active:
            desc_short = desc[:60] + "..." if len(desc) > 60 else desc
            print(f"      {tco_num}: {hs_code}")
            print(f"         {desc_short}")
            print(f"         Applicant: {applicant}")
            print(f"         Effective: {eff_date}, Expires: {exp_date}")
            print()
        
        # Summary
        print("=" * 80)
        print("📋 TCO DATA VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"✅ Total TCOs: {total_tcos:,}")
        print(f"✅ Active TCOs: {active_tcos:,}")
        print(f"✅ Chapters Covered: {len(chapter_distribution)}")
        print(f"✅ Unique Applicants: {unique_applicants}")
        print(f"✅ HS Code Validation: {(valid_hs_codes/total_tcos*100):.1f}%")
        print(f"✅ Data Quality Score: {quality_score}/100")
        print(f"✅ Status: {status}")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during TCO verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_tco_data()
