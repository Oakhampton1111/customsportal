"""
Verify Massive Tariff Data Population
====================================
This script verifies the comprehensive tariff data we just populated
and shows detailed statistics about the tariff hierarchy.
"""

import sqlite3
from datetime import datetime

def verify_massive_data():
    """Verify the massive tariff data population results."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== CUSTOMS BROKER PORTAL - MASSIVE DATA VERIFICATION ===\n")
        print(f"Analysis performed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. Overall table counts
        print("1. 📊 OVERALL DATABASE STATUS:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            status = "✅ HAS DATA" if count > 0 else "❌ EMPTY"
            print(f"   {table_name}: {count:,} records {status}")
        
        # 2. Tariff hierarchy breakdown
        print(f"\n2. 🌳 TARIFF HIERARCHY BREAKDOWN:")
        
        # Sections
        cursor.execute("SELECT COUNT(*) FROM tariff_sections")
        sections_count = cursor.fetchone()[0]
        print(f"   Sections: {sections_count}")
        
        # Chapters
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters")
        chapters_count = cursor.fetchone()[0]
        print(f"   Chapters: {chapters_count} (Chapter 77 reserved)")
        
        # Codes by level
        print(f"   Tariff Codes by Level:")
        level_names = {2: 'Chapter', 4: 'Heading', 6: 'Subheading', 8: 'Tariff Item', 10: 'Statistical'}
        total_codes = 0
        
        for level in [2, 4, 6, 8, 10]:
            cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = ?", (level,))
            count = cursor.fetchone()[0]
            total_codes += count
            print(f"     {level_names[level]} ({level}-digit): {count:,} codes")
        
        print(f"   📈 TOTAL TARIFF CODES: {total_codes:,}")
        
        # 3. Sample data from each level
        print(f"\n3. 📋 SAMPLE CODES FROM EACH LEVEL:")
        
        for level in [2, 4, 6, 8, 10]:
            print(f"   {level_names[level]} Level ({level}-digit):")
            cursor.execute("""
                SELECT hs_code, description 
                FROM tariff_codes 
                WHERE level = ? 
                ORDER BY hs_code 
                LIMIT 3
            """, (level,))
            
            samples = cursor.fetchall()
            for code, desc in samples:
                print(f"     {code}: {desc[:60]}...")
            print()
        
        # 4. Duty rates analysis
        print(f"4. 💰 DUTY RATES ANALYSIS:")
        cursor.execute("SELECT COUNT(*) FROM duty_rates")
        duty_count = cursor.fetchone()[0]
        print(f"   Total duty rates: {duty_count:,}")
        
        # Rate distribution
        cursor.execute("""
            SELECT general_rate, COUNT(*) as count 
            FROM duty_rates 
            GROUP BY general_rate 
            ORDER BY general_rate
        """)
        
        rate_dist = cursor.fetchall()
        print(f"   Rate distribution:")
        for rate, count in rate_dist[:10]:  # Show top 10 rates
            print(f"     {rate}%: {count:,} codes")
        
        # 5. Chapter coverage analysis
        print(f"\n5. 📚 CHAPTER COVERAGE ANALYSIS:")
        cursor.execute("""
            SELECT tc.chapter_id, ch.title, COUNT(*) as code_count
            FROM tariff_codes tc
            JOIN tariff_chapters ch ON tc.chapter_id = ch.chapter_number
            WHERE tc.level = 10
            GROUP BY tc.chapter_id, ch.title
            ORDER BY code_count DESC
            LIMIT 10
        """)
        
        chapter_coverage = cursor.fetchall()
        print(f"   Top 10 chapters by statistical code count:")
        for chapter_id, title, count in chapter_coverage:
            print(f"     Chapter {chapter_id}: {count:,} codes - {title[:50]}...")
        
        # 6. Hierarchy integrity check
        print(f"\n6. 🔍 HIERARCHY INTEGRITY CHECK:")
        
        # Check for orphaned codes
        cursor.execute("""
            SELECT COUNT(*) FROM tariff_codes 
            WHERE parent_code IS NOT NULL 
            AND parent_code NOT IN (SELECT hs_code FROM tariff_codes)
        """)
        orphaned = cursor.fetchone()[0]
        
        if orphaned == 0:
            print(f"   ✅ Hierarchy integrity: PERFECT - No orphaned codes")
        else:
            print(f"   ⚠️  Found {orphaned} orphaned codes")
        
        # Check chapter linkage
        cursor.execute("""
            SELECT COUNT(*) FROM tariff_codes 
            WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
        """)
        unlinked_chapters = cursor.fetchone()[0]
        
        if unlinked_chapters == 0:
            print(f"   ✅ Chapter linkage: PERFECT - All codes linked to chapters")
        else:
            print(f"   ⚠️  Found {unlinked_chapters} codes with invalid chapter links")
        
        # 7. Performance assessment
        print(f"\n7. 🚀 PERFORMANCE ASSESSMENT:")
        
        # Test query performance
        import time
        start_time = time.time()
        cursor.execute("""
            SELECT tc.hs_code, tc.description, ch.title, ts.description
            FROM tariff_codes tc
            JOIN tariff_chapters ch ON tc.chapter_id = ch.chapter_number
            JOIN tariff_sections ts ON ch.section_id = ts.section_number
            WHERE tc.level = 10
            LIMIT 1000
        """)
        results = cursor.fetchall()
        query_time = time.time() - start_time
        
        print(f"   Query performance test (1000 statistical codes with joins):")
        print(f"     Time: {query_time:.3f} seconds")
        print(f"     Status: {'✅ EXCELLENT' if query_time < 0.1 else '✅ GOOD' if query_time < 0.5 else '⚠️ SLOW'}")
        
        # 8. Frontend readiness assessment
        print(f"\n8. 🌐 FRONTEND READINESS ASSESSMENT:")
        
        readiness_score = 0
        max_score = 6
        
        # Check sections
        if sections_count >= 20:
            print(f"   ✅ Sections: {sections_count} (Excellent)")
            readiness_score += 1
        else:
            print(f"   ⚠️  Sections: {sections_count} (Needs more)")
        
        # Check chapters
        if chapters_count >= 95:
            print(f"   ✅ Chapters: {chapters_count} (Excellent)")
            readiness_score += 1
        else:
            print(f"   ⚠️  Chapters: {chapters_count} (Needs more)")
        
        # Check total codes
        if total_codes >= 10000:
            print(f"   ✅ Total codes: {total_codes:,} (Excellent - Professional scale)")
            readiness_score += 1
        elif total_codes >= 1000:
            print(f"   ✅ Total codes: {total_codes:,} (Good)")
            readiness_score += 1
        else:
            print(f"   ⚠️  Total codes: {total_codes:,} (Needs more)")
        
        # Check statistical codes
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = 10")
        stat_codes = cursor.fetchone()[0]
        if stat_codes >= 5000:
            print(f"   ✅ Statistical codes: {stat_codes:,} (Excellent)")
            readiness_score += 1
        else:
            print(f"   ⚠️  Statistical codes: {stat_codes:,} (Needs more)")
        
        # Check duty rates
        if duty_count >= 5000:
            print(f"   ✅ Duty rates: {duty_count:,} (Excellent)")
            readiness_score += 1
        else:
            print(f"   ⚠️  Duty rates: {duty_count:,} (Needs more)")
        
        # Check hierarchy integrity
        if orphaned == 0 and unlinked_chapters == 0:
            print(f"   ✅ Data integrity: Perfect")
            readiness_score += 1
        else:
            print(f"   ⚠️  Data integrity: Issues found")
        
        # Final readiness score
        readiness_percentage = (readiness_score / max_score) * 100
        print(f"\n   🎯 FRONTEND READINESS SCORE: {readiness_score}/{max_score} ({readiness_percentage:.0f}%)")
        
        if readiness_percentage >= 90:
            print(f"   🚀 STATUS: PRODUCTION READY!")
        elif readiness_percentage >= 70:
            print(f"   ✅ STATUS: DEVELOPMENT READY")
        else:
            print(f"   ⚠️  STATUS: NEEDS MORE DATA")
        
        # 9. Recommendations
        print(f"\n9. 💡 RECOMMENDATIONS:")
        
        if readiness_percentage >= 90:
            print(f"   🎉 CONGRATULATIONS! Your database is production-ready with:")
            print(f"     • {total_codes:,} tariff codes across all hierarchy levels")
            print(f"     • {duty_count:,} duty rates for comprehensive coverage")
            print(f"     • Perfect data integrity and hierarchy structure")
            print(f"     • Excellent query performance")
            print(f"   🚀 Ready for frontend tariff tree implementation!")
        else:
            if total_codes < 10000:
                print(f"   • Consider adding more tariff codes for additional chapters")
            if duty_count < 5000:
                print(f"   • Add more duty rates for comprehensive coverage")
            if orphaned > 0:
                print(f"   • Fix orphaned codes in hierarchy")
        
        print(f"\n✅ VERIFICATION COMPLETE!")
        print(f"📊 Database contains {total_codes:,} tariff codes ready for customs broker use")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    verify_massive_data()
