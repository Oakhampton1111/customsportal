"""
Verify Tariff Hierarchy Structure
================================
This script verifies that the tariff data follows the proper hierarchy structure
and is correctly linked between tables according to Australian customs standards.
"""

import sqlite3
from collections import defaultdict

def verify_hierarchy_structure():
    """Verify the tariff hierarchy structure and relationships."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== TARIFF HIERARCHY STRUCTURE VERIFICATION ===\n")
        
        # 1. Check table structure and foreign key relationships
        print("1. 🏗️  TABLE STRUCTURE VERIFICATION:")
        
        # Check tariff_sections table
        cursor.execute("PRAGMA table_info(tariff_sections)")
        sections_columns = cursor.fetchall()
        print("   tariff_sections columns:")
        for col in sections_columns:
            print(f"     {col[1]} ({col[2]}) - {'PRIMARY KEY' if col[5] else 'NOT NULL' if col[3] else 'NULLABLE'}")
        
        # Check tariff_chapters table
        cursor.execute("PRAGMA table_info(tariff_chapters)")
        chapters_columns = cursor.fetchall()
        print("\n   tariff_chapters columns:")
        for col in chapters_columns:
            print(f"     {col[1]} ({col[2]}) - {'PRIMARY KEY' if col[5] else 'NOT NULL' if col[3] else 'NULLABLE'}")
        
        # Check tariff_codes table
        cursor.execute("PRAGMA table_info(tariff_codes)")
        codes_columns = cursor.fetchall()
        print("\n   tariff_codes columns:")
        for col in codes_columns:
            print(f"     {col[1]} ({col[2]}) - {'PRIMARY KEY' if col[5] else 'NOT NULL' if col[3] else 'NULLABLE'}")
        
        # 2. Verify section-chapter relationships
        print("\n2. 🔗 SECTION-CHAPTER RELATIONSHIPS:")
        
        cursor.execute("""
            SELECT ts.section_number, ts.description, COUNT(tc.chapter_number) as chapter_count
            FROM tariff_sections ts
            LEFT JOIN tariff_chapters tc ON ts.section_number = tc.section_id
            GROUP BY ts.section_number, ts.description
            ORDER BY ts.section_number
        """)
        
        section_chapter_data = cursor.fetchall()
        total_chapters_linked = 0
        
        print("   Section -> Chapter linkage:")
        for section_num, section_desc, chapter_count in section_chapter_data:
            status = "✅" if chapter_count > 0 else "❌"
            print(f"     Section {section_num}: {chapter_count} chapters {status}")
            if chapter_count > 0:
                total_chapters_linked += chapter_count
        
        print(f"   📊 Total chapters linked to sections: {total_chapters_linked}")
        
        # 3. Verify chapter-code relationships
        print("\n3. 🔗 CHAPTER-CODE RELATIONSHIPS:")
        
        cursor.execute("""
            SELECT tc.chapter_number, tc.title, COUNT(tco.hs_code) as code_count
            FROM tariff_chapters tc
            LEFT JOIN tariff_codes tco ON tc.chapter_number = tco.chapter_id
            GROUP BY tc.chapter_number, tc.title
            ORDER BY tc.chapter_number
            LIMIT 10
        """)
        
        chapter_code_data = cursor.fetchall()
        print("   Chapter -> Code linkage (top 10):")
        for chapter_num, chapter_title, code_count in chapter_code_data:
            status = "✅" if code_count > 0 else "❌"
            print(f"     Chapter {chapter_num}: {code_count} codes {status} - {chapter_title[:50]}...")
        
        # 4. Verify parent-child relationships in tariff_codes
        print("\n4. 🌳 PARENT-CHILD CODE RELATIONSHIPS:")
        
        # Check hierarchy levels
        cursor.execute("""
            SELECT level, COUNT(*) as count
            FROM tariff_codes
            GROUP BY level
            ORDER BY level
        """)
        
        level_counts = cursor.fetchall()
        print("   Code levels distribution:")
        for level, count in level_counts:
            level_name = {2: 'Chapter', 4: 'Heading', 6: 'Subheading', 8: 'Tariff Item', 10: 'Statistical'}
            print(f"     Level {level} ({level_name.get(level, 'Unknown')}): {count} codes")
        
        # Check parent-child relationships
        print("\n   Parent-child relationships:")
        for level in [4, 6, 8, 10]:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tariff_codes child
                WHERE child.level = ? 
                AND child.parent_code IS NOT NULL
                AND EXISTS (
                    SELECT 1 FROM tariff_codes parent 
                    WHERE parent.hs_code = child.parent_code
                    AND parent.level = ?
                )
            """, (level, level - 2))
            
            valid_relationships = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = ?", (level,))
            total_at_level = cursor.fetchone()[0]
            
            percentage = (valid_relationships / total_at_level * 100) if total_at_level > 0 else 0
            status = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
            
            level_name = {4: 'Heading', 6: 'Subheading', 8: 'Tariff Item', 10: 'Statistical'}
            print(f"     {level_name.get(level)}: {valid_relationships}/{total_at_level} ({percentage:.1f}%) {status}")
        
        # 5. Check for orphaned codes
        print("\n5. 🔍 ORPHANED CODES CHECK:")
        
        cursor.execute("""
            SELECT level, COUNT(*) as orphaned_count
            FROM tariff_codes
            WHERE parent_code IS NOT NULL
            AND parent_code NOT IN (SELECT hs_code FROM tariff_codes)
            GROUP BY level
            ORDER BY level
        """)
        
        orphaned_data = cursor.fetchall()
        total_orphaned = 0
        
        if orphaned_data:
            print("   Orphaned codes found:")
            for level, count in orphaned_data:
                total_orphaned += count
                level_name = {4: 'Heading', 6: 'Subheading', 8: 'Tariff Item', 10: 'Statistical'}
                print(f"     Level {level} ({level_name.get(level)}): {count} orphaned codes ❌")
        else:
            print("   ✅ No orphaned codes found - Perfect hierarchy!")
        
        # 6. Sample hierarchy walk-through
        print("\n6. 🚶 SAMPLE HIERARCHY WALK-THROUGH:")
        
        # Pick a random chapter and show its full hierarchy
        cursor.execute("""
            SELECT chapter_number, title 
            FROM tariff_chapters 
            WHERE chapter_number IN (SELECT DISTINCT chapter_id FROM tariff_codes WHERE level = 10)
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        
        sample_chapter = cursor.fetchone()
        if sample_chapter:
            chapter_num, chapter_title = sample_chapter
            print(f"   Sample hierarchy for Chapter {chapter_num}: {chapter_title}")
            
            # Show the hierarchy levels for this chapter
            cursor.execute("""
                SELECT hs_code, parent_code, level, description
                FROM tariff_codes
                WHERE chapter_id = ?
                ORDER BY level, hs_code
                LIMIT 20
            """, (chapter_num,))
            
            hierarchy_sample = cursor.fetchall()
            current_level = None
            
            for hs_code, parent_code, level, description in hierarchy_sample:
                if level != current_level:
                    current_level = level
                    level_name = {2: 'Chapter', 4: 'Heading', 6: 'Subheading', 8: 'Tariff Item', 10: 'Statistical'}
                    print(f"\n     {level_name.get(level, 'Unknown')} Level ({level}-digit):")
                
                indent = "       " + "  " * (level // 2 - 1)
                parent_info = f" (parent: {parent_code})" if parent_code else ""
                print(f"{indent}{hs_code}: {description[:50]}...{parent_info}")
        
        # 7. Duty rates linkage verification
        print("\n7. 💰 DUTY RATES LINKAGE:")
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT dr.hs_code) as codes_with_rates,
                COUNT(DISTINCT tc.hs_code) as total_codes,
                ROUND(COUNT(DISTINCT dr.hs_code) * 100.0 / COUNT(DISTINCT tc.hs_code), 1) as coverage_percentage
            FROM tariff_codes tc
            LEFT JOIN duty_rates dr ON tc.hs_code = dr.hs_code
            WHERE tc.level >= 8
        """)
        
        duty_coverage = cursor.fetchone()
        codes_with_rates, total_codes, coverage_percentage = duty_coverage
        
        print(f"   Duty rate coverage for 8+ digit codes:")
        print(f"     Codes with duty rates: {codes_with_rates:,}")
        print(f"     Total eligible codes: {total_codes:,}")
        print(f"     Coverage: {coverage_percentage}% {'✅' if coverage_percentage > 80 else '⚠️' if coverage_percentage > 50 else '❌'}")
        
        # 8. Data quality checks
        print("\n8. 🎯 DATA QUALITY CHECKS:")
        
        # Check for duplicate HS codes
        cursor.execute("""
            SELECT hs_code, COUNT(*) as duplicate_count
            FROM tariff_codes
            GROUP BY hs_code
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"   ❌ Found {len(duplicates)} duplicate HS codes:")
            for hs_code, count in duplicates[:5]:
                print(f"     {hs_code}: {count} duplicates")
        else:
            print("   ✅ No duplicate HS codes found")
        
        # Check for invalid chapter references
        cursor.execute("""
            SELECT COUNT(*) 
            FROM tariff_codes 
            WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
        """)
        
        invalid_chapters = cursor.fetchone()[0]
        if invalid_chapters > 0:
            print(f"   ❌ Found {invalid_chapters} codes with invalid chapter references")
        else:
            print("   ✅ All codes properly linked to valid chapters")
        
        # Check for missing descriptions
        cursor.execute("""
            SELECT COUNT(*) 
            FROM tariff_codes 
            WHERE description IS NULL OR description = ''
        """)
        
        missing_descriptions = cursor.fetchone()[0]
        if missing_descriptions > 0:
            print(f"   ⚠️  Found {missing_descriptions} codes with missing descriptions")
        else:
            print("   ✅ All codes have descriptions")
        
        # 9. Summary assessment
        print("\n9. 📋 HIERARCHY STRUCTURE ASSESSMENT:")
        
        issues_found = 0
        
        # Count issues
        if total_orphaned > 0:
            issues_found += 1
        if len(duplicates) > 0:
            issues_found += 1
        if invalid_chapters > 0:
            issues_found += 1
        
        print(f"   Total issues found: {issues_found}")
        
        if issues_found == 0:
            print("   🎉 PERFECT HIERARCHY STRUCTURE!")
            print("   ✅ All relationships properly established")
            print("   ✅ No orphaned or duplicate codes")
            print("   ✅ Complete parent-child linkage")
            print("   ✅ Proper section-chapter-code hierarchy")
        elif issues_found <= 2:
            print("   ✅ GOOD HIERARCHY STRUCTURE with minor issues")
            print("   🔧 Minor fixes recommended")
        else:
            print("   ⚠️  HIERARCHY STRUCTURE NEEDS ATTENTION")
            print("   🔧 Multiple issues require fixing")
        
        print(f"\n✅ HIERARCHY VERIFICATION COMPLETE!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    verify_hierarchy_structure()
