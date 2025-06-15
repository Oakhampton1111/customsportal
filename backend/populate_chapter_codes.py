#!/usr/bin/env python3
"""
Populate missing 2-digit chapter level tariff codes.

This script adds the missing 2-digit chapter level codes to complete
the tariff hierarchy. Currently we only have 4-digit heading codes,
but we need 2-digit chapter codes for proper navigation.
"""

import sqlite3
from datetime import datetime

def populate_chapter_codes():
    """Add 2-digit chapter level codes based on existing chapters."""
    
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== POPULATING CHAPTER LEVEL CODES ===")
        
        # Get all chapters
        cursor.execute("""
            SELECT id, chapter_number, title, chapter_notes, section_id 
            FROM tariff_chapters 
            ORDER BY chapter_number
        """)
        chapters = cursor.fetchall()
        
        print(f"Found {len(chapters)} chapters to process")
        
        # Check existing 2-digit codes
        cursor.execute("SELECT hs_code FROM tariff_codes WHERE level = 2")
        existing_2digit = {row[0] for row in cursor.fetchall()}
        
        added_count = 0
        
        for chapter_id, chapter_number, title, chapter_notes, section_id in chapters:
            # Format as 2-digit code
            hs_code = f"{chapter_number:02d}"
            
            if hs_code in existing_2digit:
                print(f"Chapter {hs_code} already exists, skipping")
                continue
            
            # Insert chapter level code
            cursor.execute("""
                INSERT INTO tariff_codes (
                    hs_code, description, unit_description, parent_code, level,
                    chapter_notes, section_id, chapter_id, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hs_code,                    # hs_code
                title,                      # description  
                "Various",                  # unit_description
                None,                       # parent_code (chapters are top level)
                2,                          # level
                chapter_notes,              # chapter_notes
                section_id,                 # section_id
                chapter_id,                 # chapter_id
                True,                       # is_active
                datetime.now(),             # created_at
                datetime.now()              # updated_at
            ))
            
            print(f"Added chapter {hs_code}: {title}")
            added_count += 1
        
        # Now update 4-digit codes to have proper parent relationships
        print("\n=== UPDATING PARENT RELATIONSHIPS ===")
        
        cursor.execute("""
            SELECT hs_code FROM tariff_codes WHERE level = 4
        """)
        heading_codes = [row[0] for row in cursor.fetchall()]
        
        updated_count = 0
        for heading_code in heading_codes:
            # Parent should be the 2-digit chapter
            parent_code = heading_code[:2]
            
            cursor.execute("""
                UPDATE tariff_codes 
                SET parent_code = ? 
                WHERE hs_code = ? AND level = 4
            """, (parent_code, heading_code))
            
            updated_count += 1
        
        conn.commit()
        
        print(f"\n=== SUMMARY ===")
        print(f"Added {added_count} chapter level codes")
        print(f"Updated {updated_count} heading codes with parent relationships")
        
        # Verify the results
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = 2")
        chapter_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = 4 AND parent_code IS NOT NULL")
        headings_with_parents = cursor.fetchone()[0]
        
        print(f"Total 2-digit codes: {chapter_count}")
        print(f"4-digit codes with parents: {headings_with_parents}")
        
        print("\n=== TESTING API ENDPOINT ===")
        print("You can now test:")
        print("- http://127.0.0.1:8000/api/tariff/detail/01")
        print("- http://127.0.0.1:8000/api/tariff/detail/0101") 
        print("- http://127.0.0.1:8000/api/tariff/tree/1")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    populate_chapter_codes()
