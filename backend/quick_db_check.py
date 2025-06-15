#!/usr/bin/env python3
"""
Quick Database Check
===================
Simple script to verify database population status.
"""

import sqlite3
from pathlib import Path

def main():
    """Check database status."""
    
    db_path = Path('customs_portal.db')
    if not db_path.exists():
        print('❌ Database not found.')
        return
    
    conn = sqlite3.connect(db_path)
    try:
        print("=== CUSTOMS BROKER PORTAL DATABASE STATUS ===\n")
        
        # Get all tables and their counts
        tables = {}
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        for (table_name,) in cursor.fetchall():
            if not table_name.startswith('sqlite_'):
                count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = count_cursor.fetchone()[0]
                tables[table_name] = count
        
        print("📊 TABLE OVERVIEW:")
        for table, count in tables.items():
            status = "✅ HAS DATA" if count > 0 else "❌ EMPTY"
            print(f"  {table}: {count} records {status}")
        
        # Check hierarchy specifically
        print("\n🌳 HIERARCHY STATUS:")
        
        sections_count = tables.get('tariff_sections', 0)
        chapters_count = tables.get('tariff_chapters', 0)
        codes_count = tables.get('tariff_codes', 0)
        
        print(f"  Sections: {sections_count}")
        print(f"  Chapters: {chapters_count}")
        print(f"  Codes: {codes_count}")
        
        if sections_count > 0 and chapters_count > 0 and codes_count > 0:
            print("  ✅ Hierarchy is complete for frontend tree functionality!")
        else:
            print("  ❌ Hierarchy is incomplete!")
        
        # Sample data
        if sections_count > 0:
            print("\n📋 SAMPLE SECTIONS:")
            cursor = conn.execute("SELECT section_number, title FROM tariff_sections ORDER BY section_number LIMIT 5")
            for row in cursor.fetchall():
                print(f"  Section {row[0]}: {row[1]}")
        
        if chapters_count > 0:
            print("\n📋 SAMPLE CHAPTERS:")
            cursor = conn.execute("SELECT chapter_number, title FROM tariff_chapters ORDER BY chapter_number LIMIT 5")
            for row in cursor.fetchall():
                print(f"  Chapter {row[0]}: {row[1]}")
        
        if codes_count > 0:
            print("\n📋 SAMPLE TARIFF CODES:")
            cursor = conn.execute("SELECT hs_code, description FROM tariff_codes ORDER BY hs_code LIMIT 5")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1][:50]}...")
        
        # Check what's missing
        print("\n⚠️  MISSING DATA:")
        missing = []
        if tables.get('fta_rates', 0) == 0:
            missing.append("FTA rates (preferential trade agreement rates)")
        if tables.get('conversations', 0) == 0:
            missing.append("AI conversations (chat history)")
        if tables.get('conversation_messages', 0) == 0:
            missing.append("Conversation messages")
        
        if missing:
            for item in missing:
                print(f"  ❌ {item}")
        else:
            print("  ✅ All critical data is present!")
        
        print(f"\n🎯 SUMMARY:")
        total_tables = len(tables)
        populated_tables = sum(1 for count in tables.values() if count > 0)
        print(f"  Tables: {populated_tables}/{total_tables} populated")
        print(f"  Frontend tree ready: {'✅ YES' if sections_count > 0 and chapters_count > 0 and codes_count > 0 else '❌ NO'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
