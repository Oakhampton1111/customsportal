#!/usr/bin/env python3
"""
Verify Database Completion
=========================
Comprehensive verification of all database tables and sample data.
"""

import sqlite3
from pathlib import Path

def verify_database():
    """Verify all database tables are populated."""
    db_path = Path('customs_portal.db')
    if not db_path.exists():
        print('❌ Database not found.')
        return
    
    conn = sqlite3.connect(db_path)
    try:
        print("=== DATABASE COMPLETION VERIFICATION ===\n")
        
        # Define all expected tables and their expected minimum record counts
        expected_tables = {
            # Existing tables (should have data)
            'tariff_sections': 21,
            'tariff_chapters': 97,
            'tariff_codes': 100,
            'duty_rates': 50,
            'dumping_duties': 10,
            'export_codes': 50,
            'gst_provisions': 10,
            'product_classifications': 20,
            'tcos': 10,
            'trade_agreements': 5,
            
            # Previously empty tables (should now have data)
            'fta_rates': 10,
            'conversations': 1,
            'conversation_messages': 2,
            
            # New tables (should have data)
            'news_items': 3,
            'system_alerts': 2,
            'trade_summaries': 1,
            'news_analytics': 0,  # Optional
            'tariff_rulings': 1,
            'anti_dumping_decisions': 1,
            'regulatory_updates': 0,  # Optional
            'ruling_statistics': 0   # Optional
        }
        
        all_good = True
        
        for table, min_expected in expected_tables.items():
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count >= min_expected:
                    status = "✅"
                    status_text = "OK"
                elif count > 0:
                    status = "⚠️"
                    status_text = "PARTIAL"
                else:
                    status = "❌"
                    status_text = "EMPTY"
                    all_good = False
                
                print(f"  {table:<25} {count:>6} records {status} {status_text}")
                
                # Show sample data for key tables
                if table in ['news_items', 'tariff_rulings', 'fta_rates', 'conversations'] and count > 0:
                    cursor = conn.execute(f"SELECT * FROM {table} LIMIT 1")
                    sample = cursor.fetchone()
                    if sample:
                        print(f"    Sample: {sample[0] if len(sample) > 0 else 'N/A'}")
                        
            except sqlite3.OperationalError as e:
                print(f"  {table:<25} {'ERROR':>6} ❌ {e}")
                all_good = False
        
        print(f"\n{'='*50}")
        if all_good:
            print("✅ DATABASE COMPLETION: ALL TABLES POPULATED SUCCESSFULLY!")
            print("\n🎯 READY FOR FRONTEND-BACKEND INTEGRATION")
            print("🚀 READY FOR USER ACCEPTANCE TESTING")
        else:
            print("❌ DATABASE COMPLETION: SOME ISSUES FOUND")
            print("   Please review the tables marked with ❌")
        
        # Additional verification: Check tariff hierarchy integrity
        print(f"\n{'='*50}")
        print("🔍 TARIFF HIERARCHY INTEGRITY CHECK:")
        
        # Check sections
        cursor = conn.execute("SELECT COUNT(*) FROM tariff_sections")
        sections_count = cursor.fetchone()[0]
        
        # Check chapters
        cursor = conn.execute("SELECT COUNT(*) FROM tariff_chapters")
        chapters_count = cursor.fetchone()[0]
        
        # Check codes
        cursor = conn.execute("SELECT COUNT(*) FROM tariff_codes")
        codes_count = cursor.fetchone()[0]
        
        print(f"  Sections: {sections_count} (Expected: 21)")
        print(f"  Chapters: {chapters_count} (Expected: 97)")
        print(f"  Codes: {codes_count} (Expected: 100+)")
        
        if sections_count >= 21 and chapters_count >= 97 and codes_count >= 100:
            print("  ✅ Tariff hierarchy is complete and ready!")
        else:
            print("  ⚠️ Tariff hierarchy may need attention")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_database()
