"""
Verify Export Codes Database
============================
Comprehensive verification of AHECC export codes data quality, 
structure, and readiness for production use.
"""

import sqlite3
from datetime import datetime

def verify_export_codes():
    """Comprehensive verification of export codes database."""
    
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("🔍 EXPORT CODES VERIFICATION REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Basic Counts
        print("1. 📊 BASIC STATISTICS:")
        
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        total_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE is_active = 1")
        active_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE corresponding_import_code IS NOT NULL")
        mapped_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT SUBSTR(ahecc_code, 1, 2)) FROM export_codes")
        chapters_covered = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT statistical_unit) FROM export_codes")
        units_count = cursor.fetchone()[0]
        
        print(f"   Total export codes: {total_codes:,}")
        print(f"   Active codes: {active_codes:,} ({active_codes/total_codes*100:.1f}%)")
        print(f"   Mapped to import codes: {mapped_codes:,} ({mapped_codes/total_codes*100:.1f}%)")
        print(f"   Chapters covered: {chapters_covered}")
        print(f"   Statistical units: {units_count}")
        
        # 2. Code Format Validation
        print("\n2. 🔍 CODE FORMAT VALIDATION:")
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE LENGTH(ahecc_code) != 8")
        invalid_length = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE ahecc_code NOT GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'")
        invalid_format = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT ahecc_code) FROM export_codes")
        unique_codes = cursor.fetchone()[0]
        
        duplicates = total_codes - unique_codes
        
        print(f"   ✅ Valid 8-digit format: {total_codes - invalid_length:,}/{total_codes:,}")
        print(f"   ✅ Numeric format: {total_codes - invalid_format:,}/{total_codes:,}")
        print(f"   ✅ Unique codes: {unique_codes:,} (duplicates: {duplicates})")
        
        if invalid_length > 0:
            print(f"   ⚠️  {invalid_length} codes with invalid length")
        if invalid_format > 0:
            print(f"   ⚠️  {invalid_format} codes with invalid format")
        if duplicates > 0:
            print(f"   ⚠️  {duplicates} duplicate codes found")
        
        # 3. Chapter Distribution Analysis
        print("\n3. 📈 CHAPTER DISTRIBUTION:")
        
        cursor.execute("""
            SELECT 
                SUBSTR(ahecc_code, 1, 2) as chapter,
                COUNT(*) as count,
                COUNT(*) * 100.0 / ? as percentage
            FROM export_codes 
            GROUP BY SUBSTR(ahecc_code, 1, 2)
            ORDER BY count DESC
            LIMIT 20
        """, (total_codes,))
        
        chapter_dist = cursor.fetchall()
        print("   Top 20 chapters by export code count:")
        for chapter, count, pct in chapter_dist:
            print(f"      Chapter {chapter}: {count:4,} codes ({pct:5.1f}%)")
        
        # 4. Statistical Units Analysis
        print("\n4. 📏 STATISTICAL UNITS ANALYSIS:")
        
        cursor.execute("""
            SELECT 
                statistical_unit,
                COUNT(*) as count,
                COUNT(*) * 100.0 / ? as percentage
            FROM export_codes 
            WHERE statistical_unit IS NOT NULL
            GROUP BY statistical_unit
            ORDER BY count DESC
        """, (total_codes,))
        
        units_dist = cursor.fetchall()
        print("   Statistical units distribution:")
        for unit, count, pct in units_dist:
            print(f"      {unit:15}: {count:4,} codes ({pct:5.1f}%)")
        
        # 5. Import Code Mapping Analysis
        print("\n5. 🔗 IMPORT CODE MAPPING ANALYSIS:")
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN corresponding_import_code IS NULL THEN 'No mapping'
                    WHEN LENGTH(corresponding_import_code) = 8 THEN '8-digit mapping'
                    WHEN LENGTH(corresponding_import_code) = 10 THEN '10-digit mapping'
                    ELSE 'Other length'
                END as mapping_type,
                COUNT(*) as count,
                COUNT(*) * 100.0 / ? as percentage
            FROM export_codes
            GROUP BY mapping_type
            ORDER BY count DESC
        """, (total_codes,))
        
        mapping_dist = cursor.fetchall()
        print("   Import code mapping distribution:")
        for mapping_type, count, pct in mapping_dist:
            print(f"      {mapping_type:15}: {count:4,} codes ({pct:5.1f}%)")
        
        # 6. Data Quality Checks
        print("\n6. ✅ DATA QUALITY CHECKS:")
        
        # Check for empty descriptions
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE description IS NULL OR TRIM(description) = ''")
        empty_descriptions = cursor.fetchone()[0]
        
        # Check for very short descriptions
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE LENGTH(description) < 10")
        short_descriptions = cursor.fetchone()[0]
        
        # Check for missing statistical units
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE statistical_unit IS NULL OR TRIM(statistical_unit) = ''")
        missing_units = cursor.fetchone()[0]
        
        # Check for invalid import code references
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes e
            LEFT JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            WHERE e.corresponding_import_code IS NOT NULL 
            AND t.hs_code IS NULL
        """)
        invalid_mappings = cursor.fetchone()[0]
        
        print(f"   ✅ Descriptions: {total_codes - empty_descriptions:,}/{total_codes:,} non-empty")
        print(f"   ✅ Description length: {total_codes - short_descriptions:,}/{total_codes:,} adequate length")
        print(f"   ✅ Statistical units: {total_codes - missing_units:,}/{total_codes:,} specified")
        print(f"   ✅ Valid import mappings: {mapped_codes - invalid_mappings:,}/{mapped_codes:,}")
        
        if empty_descriptions > 0:
            print(f"   ⚠️  {empty_descriptions} codes with empty descriptions")
        if short_descriptions > 0:
            print(f"   ⚠️  {short_descriptions} codes with very short descriptions")
        if missing_units > 0:
            print(f"   ⚠️  {missing_units} codes missing statistical units")
        if invalid_mappings > 0:
            print(f"   ⚠️  {invalid_mappings} codes with invalid import code mappings")
        
        # 7. Sample Data Inspection
        print("\n7. 🔍 SAMPLE DATA INSPECTION:")
        
        # Sample from different chapters
        cursor.execute("""
            SELECT ahecc_code, description, statistical_unit, corresponding_import_code
            FROM export_codes 
            WHERE SUBSTR(ahecc_code, 1, 2) IN ('01', '26', '72', '84', '87')
            ORDER BY ahecc_code
            LIMIT 15
        """)
        
        samples = cursor.fetchall()
        print("   Sample export codes from various chapters:")
        for ahecc, desc, unit, import_code in samples:
            print(f"      {ahecc}: {desc[:45]:<45} [{unit:>10}] -> {import_code or 'None'}")
        
        # 8. Performance Analysis
        print("\n8. ⚡ PERFORMANCE ANALYSIS:")
        
        # Test query performance
        import time
        
        # Test 1: Simple count
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        cursor.fetchone()
        count_time = time.time() - start_time
        
        # Test 2: Chapter grouping
        start_time = time.time()
        cursor.execute("""
            SELECT SUBSTR(ahecc_code, 1, 2), COUNT(*) 
            FROM export_codes 
            GROUP BY SUBSTR(ahecc_code, 1, 2)
        """)
        cursor.fetchall()
        group_time = time.time() - start_time
        
        # Test 3: Join with tariff codes
        start_time = time.time()
        cursor.execute("""
            SELECT e.ahecc_code, e.description, t.description
            FROM export_codes e
            LEFT JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            LIMIT 100
        """)
        cursor.fetchall()
        join_time = time.time() - start_time
        
        print(f"   Count query: {count_time:.4f} seconds")
        print(f"   Group query: {group_time:.4f} seconds")
        print(f"   Join query (100 rows): {join_time:.4f} seconds")
        
        # 9. Readiness Assessment
        print("\n9. 🎯 READINESS ASSESSMENT:")
        
        # Calculate readiness score
        readiness_score = 0
        max_score = 100
        
        # Data volume (20 points)
        if total_codes >= 3000:
            readiness_score += 20
        elif total_codes >= 1000:
            readiness_score += 15
        elif total_codes >= 500:
            readiness_score += 10
        else:
            readiness_score += 5
        
        # Data quality (30 points)
        quality_score = 0
        if empty_descriptions == 0:
            quality_score += 8
        if short_descriptions < total_codes * 0.05:  # Less than 5%
            quality_score += 7
        if missing_units < total_codes * 0.05:
            quality_score += 8
        if invalid_mappings == 0:
            quality_score += 7
        
        readiness_score += quality_score
        
        # Code format (15 points)
        if invalid_length == 0 and invalid_format == 0:
            readiness_score += 15
        elif invalid_length + invalid_format < total_codes * 0.01:
            readiness_score += 10
        else:
            readiness_score += 5
        
        # Chapter coverage (15 points)
        if chapters_covered >= 15:
            readiness_score += 15
        elif chapters_covered >= 10:
            readiness_score += 10
        else:
            readiness_score += 5
        
        # Import mapping (10 points)
        mapping_percentage = mapped_codes / total_codes * 100
        if mapping_percentage >= 95:
            readiness_score += 10
        elif mapping_percentage >= 80:
            readiness_score += 8
        elif mapping_percentage >= 60:
            readiness_score += 6
        else:
            readiness_score += 3
        
        # Performance (10 points)
        if count_time < 0.01 and group_time < 0.1 and join_time < 0.1:
            readiness_score += 10
        elif count_time < 0.05 and group_time < 0.5 and join_time < 0.5:
            readiness_score += 8
        else:
            readiness_score += 5
        
        print(f"   📊 Overall Readiness Score: {readiness_score}/{max_score} ({readiness_score}%)")
        
        if readiness_score >= 90:
            status = "🟢 PRODUCTION READY"
            recommendation = "Excellent! Ready for production deployment."
        elif readiness_score >= 75:
            status = "🟡 MOSTLY READY"
            recommendation = "Good quality. Minor improvements recommended."
        elif readiness_score >= 60:
            status = "🟠 DEVELOPMENT READY"
            recommendation = "Suitable for development. Needs improvement for production."
        else:
            status = "🔴 NEEDS WORK"
            recommendation = "Significant improvements needed before deployment."
        
        print(f"   📈 Status: {status}")
        print(f"   💡 Recommendation: {recommendation}")
        
        # 10. Summary
        print(f"\n" + "=" * 80)
        print("📋 EXPORT CODES VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"✅ Total Export Codes: {total_codes:,}")
        print(f"✅ Chapters Covered: {chapters_covered}")
        print(f"✅ Import Mappings: {mapped_codes:,} ({mapped_codes/total_codes*100:.1f}%)")
        print(f"✅ Statistical Units: {units_count}")
        print(f"✅ Data Quality: {quality_score}/30 points")
        print(f"✅ Overall Score: {readiness_score}/100 ({readiness_score}%)")
        print(f"✅ Status: {status}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    verify_export_codes()
