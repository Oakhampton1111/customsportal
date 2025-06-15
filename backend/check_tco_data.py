"""
Check existing TCO data in the database.
"""

import sqlite3
from datetime import datetime

def check_tco_data():
    """Check existing TCO data."""
    
    try:
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        print("=" * 60)
        print("📋 TCO DATA CHECK")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check if tcos table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tcos'
        """)
        
        table_exists = cursor.fetchone()
        if not table_exists:
            print("❌ TCO table does not exist")
            return
        
        print("✅ TCO table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(tcos)")
        schema = cursor.fetchall()
        
        print("\n📊 TABLE SCHEMA:")
        for col_info in schema:
            col_id, name, data_type, not_null, default, pk = col_info
            print(f"   {name}: {data_type} {'NOT NULL' if not_null else 'NULL'} {'PK' if pk else ''}")
        
        # Count total TCOs
        cursor.execute("SELECT COUNT(*) FROM tcos")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📈 TOTAL TCOs: {total_count}")
        
        if total_count > 0:
            # Count active TCOs
            cursor.execute("SELECT COUNT(*) FROM tcos WHERE is_current = 1")
            active_count = cursor.fetchone()[0]
            
            # Count by HS code chapters
            cursor.execute("""
                SELECT SUBSTR(hs_code, 1, 2) as chapter, COUNT(*) as count
                FROM tcos 
                GROUP BY SUBSTR(hs_code, 1, 2)
                ORDER BY count DESC
                LIMIT 10
            """)
            chapter_counts = cursor.fetchall()
            
            print(f"📊 ACTIVE TCOs: {active_count}")
            print(f"📊 INACTIVE TCOs: {total_count - active_count}")
            
            print("\n📈 TOP CHAPTERS BY TCO COUNT:")
            for chapter, count in chapter_counts:
                print(f"   Chapter {chapter}: {count} TCOs")
            
            # Sample TCOs
            cursor.execute("""
                SELECT tco_number, hs_code, description, applicant_name, 
                       effective_date, expiry_date, is_current
                FROM tcos 
                ORDER BY tco_number
                LIMIT 10
            """)
            
            samples = cursor.fetchall()
            
            print("\n🔍 SAMPLE TCOs:")
            for tco_num, hs_code, desc, applicant, eff_date, exp_date, is_current in samples:
                status = "Active" if is_current else "Inactive"
                desc_short = desc[:40] + "..." if len(desc) > 40 else desc
                print(f"   {tco_num}: {hs_code} - {desc_short} ({status})")
        else:
            print("\n⚠️  No TCO data found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking TCO data: {e}")

if __name__ == "__main__":
    check_tco_data()
