"""
Verify Export Codes Hierarchy
=============================
Comprehensive verification of export codes hierarchy relationships
with import tariff codes and overall data structure integrity.
"""

import sqlite3
from datetime import datetime

def verify_export_hierarchy():
    """Verify export codes hierarchy and relationships."""
    
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=" * 80)
        print("🌳 EXPORT CODES HIERARCHY VERIFICATION")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Basic Hierarchy Statistics
        print("1. 📊 HIERARCHY STATISTICS:")
        
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        total_export_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes")
        total_import_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT SUBSTR(ahecc_code, 1, 2)) FROM export_codes")
        export_chapters = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT chapter_id) FROM tariff_codes")
        import_chapters = cursor.fetchone()[0]
        
        print(f"   Export codes: {total_export_codes:,}")
        print(f"   Import codes: {total_import_codes:,}")
        print(f"   Export chapters: {export_chapters}")
        print(f"   Import chapters: {import_chapters}")
        print(f"   Export/Import ratio: {total_export_codes/total_import_codes:.2f}")
        
        # 2. Chapter Alignment Analysis
        print("\n2. 📈 CHAPTER ALIGNMENT:")
        
        cursor.execute("""
            SELECT 
                e_chapters.chapter as export_chapter,
                i_chapters.chapter as import_chapter,
                e_chapters.export_count,
                i_chapters.import_count,
                CASE 
                    WHEN i_chapters.chapter IS NOT NULL THEN 'Aligned'
                    ELSE 'Export Only'
                END as status
            FROM (
                SELECT SUBSTR(ahecc_code, 1, 2) as chapter, COUNT(*) as export_count
                FROM export_codes
                GROUP BY SUBSTR(ahecc_code, 1, 2)
            ) e_chapters
            LEFT JOIN (
                SELECT chapter_id as chapter, COUNT(*) as import_count
                FROM tariff_codes
                GROUP BY chapter_id
            ) i_chapters ON e_chapters.chapter = PRINTF('%02d', i_chapters.chapter)
            ORDER BY e_chapters.chapter
        """)
        
        chapter_alignment = cursor.fetchall()
        print("   Chapter alignment analysis:")
        print("   Export Ch | Import Ch | Export Codes | Import Codes | Status")
        print("   ----------|-----------|--------------|--------------|----------")
        
        aligned_chapters = 0
        export_only_chapters = 0
        
        for exp_ch, imp_ch, exp_count, imp_count, status in chapter_alignment:
            imp_ch_str = str(imp_ch) if imp_ch else "None"
            imp_count_str = str(imp_count) if imp_count else "0"
            print(f"      {exp_ch:2s}     |    {imp_ch_str:2s}     |    {exp_count:6,}    |    {imp_count_str:6s}    | {status}")
            
            if status == 'Aligned':
                aligned_chapters += 1
            else:
                export_only_chapters += 1
        
        print(f"\n   ✅ Aligned chapters: {aligned_chapters}")
        print(f"   ⚠️  Export-only chapters: {export_only_chapters}")
        
        # 3. Import Code Mapping Verification
        print("\n3. 🔗 IMPORT CODE MAPPING VERIFICATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes 
            WHERE corresponding_import_code IS NOT NULL
        """)
        mapped_export_codes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes e
            INNER JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
        """)
        valid_mappings = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes e
            LEFT JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            WHERE e.corresponding_import_code IS NOT NULL AND t.hs_code IS NULL
        """)
        invalid_mappings = cursor.fetchone()[0]
        
        print(f"   Total mapped export codes: {mapped_export_codes:,}")
        print(f"   Valid mappings: {valid_mappings:,}")
        print(f"   Invalid mappings: {invalid_mappings:,}")
        print(f"   Mapping accuracy: {valid_mappings/mapped_export_codes*100:.1f}%")
        
        # 4. Code Length Distribution Analysis
        print("\n4. 📏 CODE LENGTH DISTRIBUTION:")
        
        cursor.execute("""
            SELECT 
                LENGTH(corresponding_import_code) as import_length,
                COUNT(*) as count,
                COUNT(*) * 100.0 / ? as percentage
            FROM export_codes
            WHERE corresponding_import_code IS NOT NULL
            GROUP BY LENGTH(corresponding_import_code)
            ORDER BY import_length
        """, (mapped_export_codes,))
        
        length_dist = cursor.fetchall()
        print("   Import code length distribution:")
        for length, count, pct in length_dist:
            print(f"      {length}-digit: {count:4,} codes ({pct:5.1f}%)")
        
        # 5. Chapter Cross-Reference Analysis
        print("\n5. 🔄 CHAPTER CROSS-REFERENCE ANALYSIS:")
        
        cursor.execute("""
            SELECT 
                SUBSTR(e.ahecc_code, 1, 2) as export_chapter,
                SUBSTR(e.corresponding_import_code, 1, 2) as import_chapter,
                COUNT(*) as count
            FROM export_codes e
            WHERE e.corresponding_import_code IS NOT NULL
            GROUP BY SUBSTR(e.ahecc_code, 1, 2), SUBSTR(e.corresponding_import_code, 1, 2)
            HAVING COUNT(*) > 10
            ORDER BY export_chapter, count DESC
        """)
        
        cross_ref = cursor.fetchall()
        print("   Major chapter cross-references (>10 codes):")
        current_export_chapter = None
        for exp_ch, imp_ch, count in cross_ref:
            if exp_ch != current_export_chapter:
                print(f"   Export Chapter {exp_ch}:")
                current_export_chapter = exp_ch
            print(f"      -> Import Chapter {imp_ch}: {count:3,} codes")
        
        # 6. Sample Relationship Verification
        print("\n6. 🔍 SAMPLE RELATIONSHIP VERIFICATION:")
        
        cursor.execute("""
            SELECT 
                e.ahecc_code,
                e.description as export_desc,
                e.corresponding_import_code,
                t.description as import_desc,
                t.level as import_level
            FROM export_codes e
            INNER JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            WHERE SUBSTR(e.ahecc_code, 1, 2) IN ('01', '26', '72', '84', '87')
            ORDER BY e.ahecc_code
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        print("   Sample export-import relationships:")
        for ahecc, exp_desc, imp_code, imp_desc, level in samples:
            print(f"      {ahecc} -> {imp_code} (L{level})")
            print(f"         Export: {exp_desc[:50]}...")
            print(f"         Import: {imp_desc[:50]}...")
            print()
        
        # 7. Orphaned Codes Analysis
        print("7. 🔍 ORPHANED CODES ANALYSIS:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes
            WHERE corresponding_import_code IS NULL
        """)
        orphaned_exports = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                SUBSTR(ahecc_code, 1, 2) as chapter,
                COUNT(*) as orphaned_count
            FROM export_codes
            WHERE corresponding_import_code IS NULL
            GROUP BY SUBSTR(ahecc_code, 1, 2)
            ORDER BY orphaned_count DESC
            LIMIT 10
        """)
        
        orphaned_by_chapter = cursor.fetchall()
        
        print(f"   Total orphaned export codes: {orphaned_exports:,}")
        if orphaned_exports > 0:
            print("   Orphaned codes by chapter:")
            for chapter, count in orphaned_by_chapter:
                print(f"      Chapter {chapter}: {count:,} codes")
        else:
            print("   ✅ No orphaned export codes found")
        
        # 8. Data Consistency Checks
        print("\n8. ✅ DATA CONSISTENCY CHECKS:")
        
        # Check for export codes mapping to non-existent import codes
        cursor.execute("""
            SELECT e.ahecc_code, e.corresponding_import_code
            FROM export_codes e
            LEFT JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            WHERE e.corresponding_import_code IS NOT NULL 
            AND t.hs_code IS NULL
            LIMIT 5
        """)
        
        broken_mappings = cursor.fetchall()
        
        # Check for duplicate AHECC codes
        cursor.execute("""
            SELECT ahecc_code, COUNT(*) as count
            FROM export_codes
            GROUP BY ahecc_code
            HAVING COUNT(*) > 1
            LIMIT 5
        """)
        
        duplicate_codes = cursor.fetchall()
        
        # Check for inconsistent chapter mappings
        cursor.execute("""
            SELECT 
                SUBSTR(e.ahecc_code, 1, 2) as export_chapter,
                SUBSTR(e.corresponding_import_code, 1, 2) as import_chapter,
                COUNT(*) as count
            FROM export_codes e
            WHERE e.corresponding_import_code IS NOT NULL
            AND SUBSTR(e.ahecc_code, 1, 2) != SUBSTR(e.corresponding_import_code, 1, 2)
            GROUP BY export_chapter, import_chapter
            LIMIT 10
        """)
        
        cross_chapter_mappings = cursor.fetchall()
        
        print(f"   ✅ Broken mappings: {len(broken_mappings)}")
        print(f"   ✅ Duplicate AHECC codes: {len(duplicate_codes)}")
        print(f"   ✅ Cross-chapter mappings: {len(cross_chapter_mappings)}")
        
        if broken_mappings:
            print("   ⚠️  Sample broken mappings:")
            for ahecc, imp_code in broken_mappings:
                print(f"      {ahecc} -> {imp_code} (not found)")
        
        if duplicate_codes:
            print("   ⚠️  Sample duplicate codes:")
            for ahecc, count in duplicate_codes:
                print(f"      {ahecc}: {count} duplicates")
        
        # 9. Performance Analysis
        print("\n9. ⚡ PERFORMANCE ANALYSIS:")
        
        import time
        
        # Test hierarchy queries
        start_time = time.time()
        cursor.execute("""
            SELECT e.ahecc_code, t.description
            FROM export_codes e
            INNER JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            LIMIT 1000
        """)
        cursor.fetchall()
        join_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("""
            SELECT SUBSTR(ahecc_code, 1, 2), COUNT(*)
            FROM export_codes
            GROUP BY SUBSTR(ahecc_code, 1, 2)
        """)
        cursor.fetchall()
        group_time = time.time() - start_time
        
        print(f"   Join query (1000 rows): {join_time:.4f} seconds")
        print(f"   Chapter grouping: {group_time:.4f} seconds")
        
        # 10. Hierarchy Health Score
        print("\n10. 🎯 HIERARCHY HEALTH ASSESSMENT:")
        
        health_score = 0
        max_score = 100
        
        # Mapping completeness (30 points)
        mapping_percentage = mapped_export_codes / total_export_codes * 100
        if mapping_percentage >= 95:
            health_score += 30
        elif mapping_percentage >= 85:
            health_score += 25
        elif mapping_percentage >= 70:
            health_score += 20
        else:
            health_score += 10
        
        # Mapping accuracy (25 points)
        accuracy_percentage = valid_mappings / mapped_export_codes * 100 if mapped_export_codes > 0 else 0
        if accuracy_percentage >= 99:
            health_score += 25
        elif accuracy_percentage >= 95:
            health_score += 20
        elif accuracy_percentage >= 90:
            health_score += 15
        else:
            health_score += 5
        
        # Chapter coverage (20 points)
        coverage_percentage = aligned_chapters / import_chapters * 100
        if coverage_percentage >= 80:
            health_score += 20
        elif coverage_percentage >= 60:
            health_score += 15
        elif coverage_percentage >= 40:
            health_score += 10
        else:
            health_score += 5
        
        # Data consistency (15 points)
        consistency_score = 15
        if broken_mappings:
            consistency_score -= 5
        if duplicate_codes:
            consistency_score -= 5
        if orphaned_exports > total_export_codes * 0.1:  # More than 10% orphaned
            consistency_score -= 5
        
        health_score += max(0, consistency_score)
        
        # Performance (10 points)
        if join_time < 0.1 and group_time < 0.05:
            health_score += 10
        elif join_time < 0.5 and group_time < 0.1:
            health_score += 8
        else:
            health_score += 5
        
        print(f"   📊 Hierarchy Health Score: {health_score}/{max_score} ({health_score}%)")
        
        if health_score >= 90:
            status = "🟢 EXCELLENT HIERARCHY"
            recommendation = "Perfect hierarchy structure. Production ready."
        elif health_score >= 75:
            status = "🟡 GOOD HIERARCHY"
            recommendation = "Good structure with minor issues."
        elif health_score >= 60:
            status = "🟠 ACCEPTABLE HIERARCHY"
            recommendation = "Acceptable but needs improvement."
        else:
            status = "🔴 POOR HIERARCHY"
            recommendation = "Significant hierarchy issues need fixing."
        
        print(f"   📈 Status: {status}")
        print(f"   💡 Recommendation: {recommendation}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("📋 EXPORT HIERARCHY VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"✅ Export Codes: {total_export_codes:,}")
        print(f"✅ Mapped Codes: {mapped_export_codes:,} ({mapping_percentage:.1f}%)")
        print(f"✅ Valid Mappings: {valid_mappings:,} ({accuracy_percentage:.1f}%)")
        print(f"✅ Chapter Coverage: {aligned_chapters}/{import_chapters} ({coverage_percentage:.1f}%)")
        print(f"✅ Orphaned Codes: {orphaned_exports:,}")
        print(f"✅ Health Score: {health_score}/100 ({health_score}%)")
        print(f"✅ Status: {status}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during hierarchy verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    verify_export_hierarchy()
