"""
Comprehensive Dumping Duties and GST Provisions Data Verification
================================================================
Verifies data quality, integrity, and completeness of dumping duties and GST provisions.
"""

import sqlite3
import time
from datetime import datetime, date
from typing import Dict, List, Tuple

def verify_dumping_gst_data():
    """Comprehensive verification of dumping duties and GST provisions data."""
    
    print("=" * 80)
    print("COMPREHENSIVE DUMPING DUTIES & GST PROVISIONS VERIFICATION")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        verification_score = 0
        max_score = 100
        
        # ================================================================
        # DUMPING DUTIES VERIFICATION
        # ================================================================
        print("PART 1: DUMPING DUTIES VERIFICATION")
        print("=" * 50)
        
        # 1. Basic Data Counts
        print("1. BASIC DATA INTEGRITY:")
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties")
        total_duties = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE is_active = 1")
        active_duties = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM dumping_duties")
        unique_hs_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT country_code) FROM dumping_duties")
        unique_countries = cursor.fetchone()[0]
        
        print(f"   Total dumping duties: {total_duties:,}")
        print(f"   Active duties: {active_duties:,}")
        print(f"   Unique HS codes: {unique_hs_codes:,}")
        print(f"   Unique countries: {unique_countries}")
        
        if total_duties >= 900:
            verification_score += 10
            print("   ✓ Sufficient data volume")
        else:
            print("   ✗ Insufficient data volume")
        
        # 2. Data Quality Checks
        print("\n2. DATA QUALITY CHECKS:")
        
        # Check for null values in critical fields
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE hs_code IS NULL OR country_code IS NULL")
        null_critical = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE duty_type IS NULL")
        null_duty_type = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE duty_rate IS NULL AND duty_amount IS NULL")
        no_duty_specified = cursor.fetchone()[0]
        
        print(f"   Records with null critical fields: {null_critical}")
        print(f"   Records with null duty type: {null_duty_type}")
        print(f"   Records with no duty specified: {no_duty_specified}")
        
        if null_critical == 0 and null_duty_type == 0:
            verification_score += 10
            print("   ✓ No critical null values")
        else:
            print("   ✗ Critical null values found")
        
        # 3. HS Code Validation
        print("\n3. HS CODE VALIDATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM dumping_duties d
            INNER JOIN tariff_codes tc ON d.hs_code = tc.hs_code
        """)
        valid_hs_codes = cursor.fetchone()[0]
        
        hs_code_integrity = (valid_hs_codes / total_duties * 100) if total_duties > 0 else 0
        
        print(f"   Valid HS code relationships: {valid_hs_codes}/{total_duties}")
        print(f"   HS code integrity: {hs_code_integrity:.1f}%")
        
        if hs_code_integrity >= 99.0:
            verification_score += 10
            print("   ✓ Excellent HS code integrity")
        elif hs_code_integrity >= 95.0:
            verification_score += 8
            print("   ✓ Good HS code integrity")
        else:
            print("   ✗ Poor HS code integrity")
        
        # 4. Country Code Validation
        print("\n4. COUNTRY CODE VALIDATION:")
        
        cursor.execute("""
            SELECT country_code, COUNT(*) as count
            FROM dumping_duties 
            WHERE LENGTH(country_code) != 3
            GROUP BY country_code
        """)
        invalid_countries = cursor.fetchall()
        
        if not invalid_countries:
            verification_score += 5
            print("   ✓ All country codes are valid 3-letter format")
        else:
            print(f"   ✗ Invalid country codes found: {invalid_countries}")
        
        # 5. Duty Rate Validation
        print("\n5. DUTY RATE VALIDATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM dumping_duties 
            WHERE duty_rate IS NOT NULL AND (duty_rate < 0 OR duty_rate > 100)
        """)
        invalid_rates = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT AVG(duty_rate), MIN(duty_rate), MAX(duty_rate)
            FROM dumping_duties 
            WHERE duty_rate IS NOT NULL
        """)
        rate_stats = cursor.fetchone()
        avg_rate, min_rate, max_rate = rate_stats if rate_stats[0] else (0, 0, 0)
        
        print(f"   Invalid duty rates (outside 0-100%): {invalid_rates}")
        print(f"   Average duty rate: {avg_rate:.2f}%")
        print(f"   Rate range: {min_rate:.2f}% - {max_rate:.2f}%")
        
        if invalid_rates == 0:
            verification_score += 5
            print("   ✓ All duty rates are within valid range")
        else:
            print("   ✗ Invalid duty rates found")
        
        # 6. Case Number Format
        print("\n6. CASE NUMBER VALIDATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM dumping_duties 
            WHERE case_number IS NOT NULL 
            AND (case_number LIKE 'AD %/%' OR case_number LIKE 'CV %/%' OR case_number LIKE 'ADC %/%')
        """)
        valid_case_numbers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE case_number IS NOT NULL")
        total_case_numbers = cursor.fetchone()[0]
        
        case_format_integrity = (valid_case_numbers / total_case_numbers * 100) if total_case_numbers > 0 else 0
        
        print(f"   Valid case number format: {valid_case_numbers}/{total_case_numbers}")
        print(f"   Case number format integrity: {case_format_integrity:.1f}%")
        
        if case_format_integrity >= 95.0:
            verification_score += 5
            print("   ✓ Good case number format integrity")
        else:
            print("   ✗ Poor case number format integrity")
        
        # ================================================================
        # GST PROVISIONS VERIFICATION
        # ================================================================
        print("\n" + "=" * 50)
        print("PART 2: GST PROVISIONS VERIFICATION")
        print("=" * 50)
        
        # 1. Basic Data Counts
        print("1. BASIC DATA INTEGRITY:")
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions")
        total_provisions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE is_active = 1")
        active_provisions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT exemption_type) FROM gst_provisions")
        unique_exemption_types = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE hs_code IS NOT NULL")
        provisions_with_hs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE hs_code IS NULL")
        general_provisions = cursor.fetchone()[0]
        
        print(f"   Total GST provisions: {total_provisions:,}")
        print(f"   Active provisions: {active_provisions:,}")
        print(f"   Unique exemption types: {unique_exemption_types}")
        print(f"   Provisions with HS codes: {provisions_with_hs:,}")
        print(f"   General provisions: {general_provisions:,}")
        
        if total_provisions >= 650:
            verification_score += 10
            print("   ✓ Sufficient data volume")
        else:
            print("   ✗ Insufficient data volume")
        
        # 2. Data Quality Checks
        print("\n2. DATA QUALITY CHECKS:")
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE exemption_type IS NULL")
        null_exemption_type = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE description IS NULL OR description = ''")
        null_description = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE schedule_reference IS NULL")
        null_schedule = cursor.fetchone()[0]
        
        print(f"   Records with null exemption type: {null_exemption_type}")
        print(f"   Records with null/empty description: {null_description}")
        print(f"   Records with null schedule reference: {null_schedule}")
        
        if null_exemption_type == 0 and null_description == 0 and null_schedule == 0:
            verification_score += 10
            print("   ✓ No critical null values")
        else:
            print("   ✗ Critical null values found")
        
        # 3. HS Code Validation for GST Provisions
        print("\n3. HS CODE VALIDATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM gst_provisions g
            INNER JOIN tariff_codes tc ON g.hs_code = tc.hs_code
            WHERE g.hs_code IS NOT NULL
        """)
        valid_gst_hs_codes = cursor.fetchone()[0]
        
        gst_hs_integrity = (valid_gst_hs_codes / provisions_with_hs * 100) if provisions_with_hs > 0 else 100
        
        print(f"   Valid HS code relationships: {valid_gst_hs_codes}/{provisions_with_hs}")
        print(f"   HS code integrity: {gst_hs_integrity:.1f}%")
        
        if gst_hs_integrity >= 99.0:
            verification_score += 10
            print("   ✓ Excellent HS code integrity")
        elif gst_hs_integrity >= 95.0:
            verification_score += 8
            print("   ✓ Good HS code integrity")
        else:
            print("   ✗ Poor HS code integrity")
        
        # 4. Exemption Type Distribution
        print("\n4. EXEMPTION TYPE DISTRIBUTION:")
        
        cursor.execute("""
            SELECT exemption_type, COUNT(*) as count
            FROM gst_provisions 
            GROUP BY exemption_type
            ORDER BY count DESC
            LIMIT 10
        """)
        exemption_distribution = cursor.fetchall()
        
        print("   Top exemption types:")
        for exemption_type, count in exemption_distribution:
            percentage = (count / total_provisions * 100) if total_provisions > 0 else 0
            print(f"      {exemption_type}: {count:,} ({percentage:.1f}%)")
        
        if len(exemption_distribution) >= 10:
            verification_score += 5
            print("   ✓ Good exemption type diversity")
        else:
            print("   ✗ Limited exemption type diversity")
        
        # 5. Threshold Value Validation
        print("\n5. THRESHOLD VALUE VALIDATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM gst_provisions 
            WHERE value_threshold IS NOT NULL AND value_threshold < 0
        """)
        negative_thresholds = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*), AVG(value_threshold), MIN(value_threshold), MAX(value_threshold)
            FROM gst_provisions 
            WHERE value_threshold IS NOT NULL
        """)
        threshold_stats = cursor.fetchone()
        threshold_count, avg_threshold, min_threshold, max_threshold = threshold_stats
        
        print(f"   Provisions with thresholds: {threshold_count:,}")
        print(f"   Negative thresholds: {negative_thresholds}")
        if threshold_count > 0:
            print(f"   Average threshold: ${avg_threshold:,.2f}")
            print(f"   Threshold range: ${min_threshold:,.2f} - ${max_threshold:,.2f}")
        
        if negative_thresholds == 0:
            verification_score += 5
            print("   ✓ No negative threshold values")
        else:
            print("   ✗ Negative threshold values found")
        
        # ================================================================
        # PERFORMANCE TESTING
        # ================================================================
        print("\n" + "=" * 50)
        print("PART 3: PERFORMANCE TESTING")
        print("=" * 50)
        
        # Test query performance
        test_queries = [
            ("Dumping duties by country", "SELECT country_code, COUNT(*) FROM dumping_duties GROUP BY country_code"),
            ("Active duties with HS codes", "SELECT d.*, tc.description FROM dumping_duties d JOIN tariff_codes tc ON d.hs_code = tc.hs_code WHERE d.is_active = 1 LIMIT 100"),
            ("GST provisions by type", "SELECT exemption_type, COUNT(*) FROM gst_provisions GROUP BY exemption_type"),
            ("GST provisions with thresholds", "SELECT * FROM gst_provisions WHERE value_threshold IS NOT NULL ORDER BY value_threshold DESC LIMIT 100"),
            ("Combined duties and provisions", "SELECT COUNT(*) FROM dumping_duties d JOIN gst_provisions g ON d.hs_code = g.hs_code")
        ]
        
        total_query_time = 0
        for query_name, query_sql in test_queries:
            start_time = time.time()
            cursor.execute(query_sql)
            results = cursor.fetchall()
            end_time = time.time()
            
            query_time = (end_time - start_time) * 1000  # Convert to milliseconds
            total_query_time += query_time
            
            print(f"   {query_name}: {query_time:.2f}ms ({len(results)} results)")
        
        avg_query_time = total_query_time / len(test_queries)
        print(f"   Average query time: {avg_query_time:.2f}ms")
        
        if avg_query_time < 100:
            verification_score += 10
            print("   ✓ Excellent query performance")
        elif avg_query_time < 500:
            verification_score += 8
            print("   ✓ Good query performance")
        elif avg_query_time < 1000:
            verification_score += 5
            print("   ✓ Acceptable query performance")
        else:
            print("   ✗ Poor query performance")
        
        # ================================================================
        # FINAL VERIFICATION SUMMARY
        # ================================================================
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        
        # Calculate final score and status
        final_score = (verification_score / max_score) * 100
        
        if final_score >= 90:
            status = "EXCELLENT"
            status_icon = "✓"
        elif final_score >= 80:
            status = "GOOD"
            status_icon = "✓"
        elif final_score >= 70:
            status = "ACCEPTABLE"
            status_icon = "⚠"
        else:
            status = "NEEDS IMPROVEMENT"
            status_icon = "✗"
        
        print(f"OVERALL DATA QUALITY SCORE: {final_score:.1f}/100")
        print(f"STATUS: {status_icon} {status}")
        print()
        
        print("DATASET SUMMARY:")
        print(f"  Dumping Duties: {total_duties:,} total ({active_duties:,} active)")
        print(f"  GST Provisions: {total_provisions:,} total ({active_provisions:,} active)")
        print(f"  Unique HS Codes (Duties): {unique_hs_codes:,}")
        print(f"  Unique Countries: {unique_countries}")
        print(f"  Exemption Types: {unique_exemption_types}")
        print()
        
        print("KEY METRICS:")
        print(f"  Dumping Duties HS Code Integrity: {hs_code_integrity:.1f}%")
        print(f"  GST Provisions HS Code Integrity: {gst_hs_integrity:.1f}%")
        print(f"  Average Query Performance: {avg_query_time:.2f}ms")
        print()
        
        if final_score >= 80:
            print("RECOMMENDATION: Data is ready for production use")
        elif final_score >= 70:
            print("RECOMMENDATION: Data is acceptable with minor improvements needed")
        else:
            print("RECOMMENDATION: Data quality improvements required before production use")
        
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_dumping_gst_data()
