#!/usr/bin/env python3
"""Check FTA rates table structure."""

import sqlite3
from pathlib import Path

def check_fta_structure():
    db_path = Path('customs_portal.db')
    if not db_path.exists():
        print('❌ Database not found.')
        return
    
    conn = sqlite3.connect(db_path)
    try:
        # Check table structure
        cursor = conn.execute("PRAGMA table_info(fta_rates)")
        columns = cursor.fetchall()
        
        print("FTA Rates table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check sample data
        cursor = conn.execute("SELECT * FROM fta_rates LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nSample data ({len(rows)} rows):")
        for row in rows:
            print(f"  {row}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_fta_structure()
