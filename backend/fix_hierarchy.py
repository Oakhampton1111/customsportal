#!/usr/bin/env python3
"""
Fix Tariff Hierarchy Data
========================
This script fixes the missing tariff sections and chapters data
to ensure proper hierarchy for the frontend tree functionality.
"""

import sqlite3
from pathlib import Path

def main():
    """Fix the hierarchy data in the database."""
    
    # Connect to SQLite database
    db_path = Path('customs_portal.db')
    if not db_path.exists():
        print('❌ Database not found. Please run migration first.')
        return False
    
    # Read the fix script
    fix_script_path = Path('../database/fix_hierarchy_data.sql')
    if not fix_script_path.exists():
        print('❌ Fix script not found.')
        return False
    
    with open(fix_script_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Execute the fix
    conn = sqlite3.connect(db_path)
    try:
        print("🔧 Applying hierarchy data fixes...")
        
        # Split by semicolon and execute each statement
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement += line + " "
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
        
        executed_count = 0
        for stmt in statements:
            if stmt and stmt != ';':
                try:
                    conn.execute(stmt)
                    executed_count += 1
                    if executed_count <= 5:  # Show first few for progress
                        print(f"✅ Executed: {stmt[:60]}...")
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed" in str(e):
                        print(f"⚠️  Skipped duplicate: {stmt[:40]}...")
                    else:
                        print(f"❌ Error: {e}")
                except Exception as e:
                    print(f"❌ Error executing statement: {e}")
                    print(f"Statement: {stmt[:100]}...")
        
        conn.commit()
        print(f'✅ Hierarchy data fix completed! Executed {executed_count} statements.')
        
        # Verify the fix
        cursor = conn.execute('SELECT COUNT(*) FROM tariff_sections')
        sections_count = cursor.fetchone()[0]
        
        cursor = conn.execute('SELECT COUNT(*) FROM tariff_chapters')
        chapters_count = cursor.fetchone()[0]
        
        cursor = conn.execute('SELECT COUNT(*) FROM tariff_codes')
        codes_count = cursor.fetchone()[0]
        
        print(f'✅ Verification: {sections_count} sections, {chapters_count} chapters, {codes_count} tariff codes')
        
        # Show some sample data
        print("\n📊 Sample tariff sections:")
        cursor = conn.execute('SELECT section_number, title FROM tariff_sections ORDER BY section_number LIMIT 10')
        for row in cursor.fetchall():
            print(f"  Section {row[0]}: {row[1]}")
        
        print("\n📊 Sample tariff chapters:")
        cursor = conn.execute('SELECT chapter_number, title FROM tariff_chapters ORDER BY chapter_number LIMIT 10')
        for row in cursor.fetchall():
            print(f"  Chapter {row[0]}: {row[1]}")
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database hierarchy is now ready for frontend tree functionality!")
    else:
        print("\n💥 Fix failed. Please check the errors above.")
