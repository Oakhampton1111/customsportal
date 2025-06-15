"""
Fix Chapter References
=====================
This script identifies and fixes the 60 codes with invalid chapter references.
"""

import sqlite3

def fix_chapter_references():
    """Fix codes with invalid chapter references."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== FIXING INVALID CHAPTER REFERENCES ===\n")
        
        # 1. Find codes with invalid chapter references
        print("1. 🔍 IDENTIFYING INVALID CHAPTER REFERENCES:")
        
        cursor.execute("""
            SELECT hs_code, chapter_id, description
            FROM tariff_codes 
            WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
            ORDER BY hs_code
        """)
        
        invalid_codes = cursor.fetchall()
        print(f"   Found {len(invalid_codes)} codes with invalid chapter references:")
        
        # Group by invalid chapter_id
        chapter_groups = {}
        for hs_code, chapter_id, description in invalid_codes:
            if chapter_id not in chapter_groups:
                chapter_groups[chapter_id] = []
            chapter_groups[chapter_id].append((hs_code, description))
        
        for chapter_id, codes in chapter_groups.items():
            print(f"     Invalid Chapter {chapter_id}: {len(codes)} codes")
            for hs_code, desc in codes[:3]:  # Show first 3 examples
                print(f"       {hs_code}: {desc[:50]}...")
            if len(codes) > 3:
                print(f"       ... and {len(codes) - 3} more")
        
        # 2. Fix the chapter references based on HS code patterns
        print(f"\n2. 🔧 FIXING CHAPTER REFERENCES:")
        
        fixes_made = 0
        
        for hs_code, chapter_id, description in invalid_codes:
            # Extract the correct chapter from the HS code
            if len(hs_code) >= 2:
                # For codes starting with digits, extract first 2 digits
                if hs_code[:2].isdigit():
                    correct_chapter = int(hs_code[:2])
                else:
                    # For non-numeric codes, try to infer from pattern
                    continue
                
                # Check if this chapter exists in tariff_chapters
                cursor.execute("SELECT chapter_number FROM tariff_chapters WHERE chapter_number = ?", (correct_chapter,))
                if cursor.fetchone():
                    # Update the chapter_id
                    cursor.execute("""
                        UPDATE tariff_codes 
                        SET chapter_id = ? 
                        WHERE hs_code = ?
                    """, (correct_chapter, hs_code))
                    
                    fixes_made += 1
                    if fixes_made <= 10:  # Show first 10 fixes
                        print(f"     Fixed {hs_code}: Chapter {chapter_id} → {correct_chapter}")
                    elif fixes_made == 11:
                        print(f"     ... continuing fixes ...")
        
        print(f"\n   ✅ Fixed {fixes_made} chapter references")
        
        # 3. Handle remaining unfixable codes
        cursor.execute("""
            SELECT COUNT(*)
            FROM tariff_codes 
            WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
        """)
        
        remaining_invalid = cursor.fetchone()[0]
        
        if remaining_invalid > 0:
            print(f"\n3. 🗑️  REMOVING UNFIXABLE CODES:")
            print(f"   Found {remaining_invalid} codes that cannot be fixed")
            
            # Show what we're removing
            cursor.execute("""
                SELECT hs_code, chapter_id, description
                FROM tariff_codes 
                WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
                LIMIT 5
            """)
            
            unfixable = cursor.fetchall()
            print("   Codes to be removed (sample):")
            for hs_code, chapter_id, desc in unfixable:
                print(f"     {hs_code} (Chapter {chapter_id}): {desc[:50]}...")
            
            # Remove unfixable codes
            cursor.execute("""
                DELETE FROM tariff_codes 
                WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
            """)
            
            print(f"   🗑️  Removed {remaining_invalid} unfixable codes")
        
        # 4. Also remove corresponding duty rates for removed codes
        print(f"\n4. 🧹 CLEANING UP DUTY RATES:")
        
        cursor.execute("""
            DELETE FROM duty_rates 
            WHERE hs_code NOT IN (SELECT hs_code FROM tariff_codes)
        """)
        
        orphaned_duties = cursor.rowcount
        if orphaned_duties > 0:
            print(f"   🗑️  Removed {orphaned_duties} orphaned duty rates")
        else:
            print(f"   ✅ No orphaned duty rates found")
        
        conn.commit()
        
        # 5. Final verification
        print(f"\n5. ✅ FINAL VERIFICATION:")
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM tariff_codes 
            WHERE chapter_id NOT IN (SELECT chapter_number FROM tariff_chapters)
        """)
        
        final_invalid = cursor.fetchone()[0]
        
        if final_invalid == 0:
            print("   🎉 ALL CHAPTER REFERENCES NOW VALID!")
        else:
            print(f"   ⚠️  Still {final_invalid} invalid references remaining")
        
        # Show final counts
        cursor.execute("SELECT COUNT(*) FROM tariff_codes")
        total_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM duty_rates")
        total_duties = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL DATABASE STATE:")
        print(f"   Total tariff codes: {total_codes:,}")
        print(f"   Total duty rates: {total_duties:,}")
        print(f"   Invalid chapter references: {final_invalid}")
        
        if final_invalid == 0:
            print(f"\n🚀 DATABASE INTEGRITY: PERFECT!")
        
    except Exception as e:
        print(f"❌ Error during fixes: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_chapter_references()
