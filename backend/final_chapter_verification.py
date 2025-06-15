#!/usr/bin/env python3
"""Final verification of chapter notes completion."""

import sqlite3
from pathlib import Path

def final_verification():
    """Verify all chapters have notes."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        total_with_notes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters")
        total_chapters = cursor.fetchone()[0]
        
        print("="*60)
        print("CHAPTER NOTES POPULATION - FINAL VERIFICATION")
        print("="*60)
        print(f"Total chapters in database: {total_chapters}")
        print(f"Chapters with notes: {total_with_notes}")
        print(f"Completion rate: {(total_with_notes/total_chapters)*100:.1f}%")
        
        if total_with_notes == total_chapters:
            print("\n✅ SUCCESS: ALL CHAPTERS NOW HAVE NOTES!")
            print("\nChapter notes will now be displayed in the frontend")
            print("when users browse the tariff hierarchy tree.")
        else:
            print(f"\n⚠️  {total_chapters - total_with_notes} chapters still missing notes")
        
        print("="*60)
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_verification()
