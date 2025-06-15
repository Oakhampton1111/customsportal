#!/usr/bin/env python3
"""
Check chapter notes in the tariff database.
"""

import sqlite3
import sys
from pathlib import Path

def check_chapter_notes():
    """Check if chapter notes exist in the database."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check total chapters
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters")
        total_chapters = cursor.fetchone()[0]
        print(f"Total chapters in database: {total_chapters}")
        
        # Check chapters with notes
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        chapters_with_notes = cursor.fetchone()[0]
        print(f"Chapters with notes: {chapters_with_notes}")
        
        # Show sample chapters with notes
        cursor.execute("""
            SELECT chapter_number, title, chapter_notes 
            FROM tariff_chapters 
            WHERE chapter_notes IS NOT NULL AND chapter_notes != ''
            ORDER BY chapter_number 
            LIMIT 5
        """)
        
        print("\nSample chapters with notes:")
        for row in cursor.fetchall():
            chapter_num, title, notes = row
            print(f"\nChapter {chapter_num:02d}: {title}")
            print(f"Notes: {notes[:200]}{'...' if len(notes) > 200 else ''}")
        
        # Show chapters without notes
        cursor.execute("""
            SELECT chapter_number, title 
            FROM tariff_chapters 
            WHERE chapter_notes IS NULL OR chapter_notes = ''
            ORDER BY chapter_number 
            LIMIT 10
        """)
        
        print(f"\nSample chapters WITHOUT notes:")
        for row in cursor.fetchall():
            chapter_num, title = row
            print(f"Chapter {chapter_num:02d}: {title}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking chapter notes: {e}")

if __name__ == "__main__":
    check_chapter_notes()
