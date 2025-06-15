#!/usr/bin/env python3
"""
Check the current population status of all database tables.
"""

import sqlite3
from pathlib import Path

def check_database_status():
    """Check population status of all tables."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("="*80)
        print("CUSTOMS BROKER PORTAL - DATABASE POPULATION STATUS")
        print("="*80)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Total tables in database: {len(tables)}\n")
        
        # Check each table
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # Get sample data info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                status = "✅ POPULATED" if count > 0 else "❌ EMPTY"
                print(f"{table:<25} | {count:>8} records | {status}")
                
                # Show key details for important tables
                if count > 0 and table in ['tariff_codes', 'dumping_duties', 'gst_provisions', 'tcos', 'duty_rates', 'fta_rates']:
                    if table == 'tariff_codes':
                        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = 1")
                        sections = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = 2") 
                        chapters = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level >= 4")
                        detailed = cursor.fetchone()[0]
                        print(f"{'':25} | Sections: {sections}, Chapters: {chapters}, Detailed codes: {detailed}")
                    
                    elif table == 'dumping_duties':
                        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE is_active = 1")
                        active = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(DISTINCT country_code) FROM dumping_duties")
                        countries = cursor.fetchone()[0]
                        print(f"{'':25} | Active: {active}, Countries: {countries}")
                    
                    elif table == 'gst_provisions':
                        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE is_active = 1")
                        active = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(DISTINCT exemption_type) FROM gst_provisions")
                        types = cursor.fetchone()[0]
                        print(f"{'':25} | Active: {active}, Exemption types: {types}")
                    
                    elif table == 'tcos':
                        cursor.execute("SELECT COUNT(*) FROM tcos WHERE status = 'active'")
                        active = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(DISTINCT applicant) FROM tcos")
                        applicants = cursor.fetchone()[0]
                        print(f"{'':25} | Active: {active}, Applicants: {applicants}")
                
            except Exception as e:
                print(f"{table:<25} | ERROR: {str(e)}")
        
        print("\n" + "="*80)
        print("SUMMARY OF WHAT'S POPULATED:")
        print("="*80)
        
        # Check major data categories
        populated_tables = []
        empty_tables = []
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    populated_tables.append(table)
                else:
                    empty_tables.append(table)
            except:
                empty_tables.append(table)
        
        print(f"✅ POPULATED TABLES ({len(populated_tables)}):")
        for table in populated_tables:
            print(f"   - {table}")
        
        if empty_tables:
            print(f"\n❌ EMPTY TABLES ({len(empty_tables)}):")
            for table in empty_tables:
                print(f"   - {table}")
        
        print("\n" + "="*80)
        print("NEXT STEPS - TABLES TO POPULATE:")
        print("="*80)
        
        # Identify what needs to be populated
        priority_empty = []
        for table in empty_tables:
            if table in ['duty_rates', 'fta_rates', 'export_codes', 'product_classifications', 'customs_rulings', 'news_updates']:
                priority_empty.append(table)
        
        if priority_empty:
            print("HIGH PRIORITY:")
            for table in priority_empty:
                if table == 'duty_rates':
                    print(f"   - {table}: MFN duty rates for tariff codes")
                elif table == 'fta_rates':
                    print(f"   - {table}: Free Trade Agreement preferential rates")
                elif table == 'export_codes':
                    print(f"   - {table}: Australian Harmonized Export Commodity Classification")
                elif table == 'product_classifications':
                    print(f"   - {table}: AI-powered product classification data")
                elif table == 'customs_rulings':
                    print(f"   - {table}: Official customs classification rulings")
                elif table == 'news_updates':
                    print(f"   - {table}: Trade and customs news updates")
        else:
            print("🎉 ALL PRIORITY TABLES ARE POPULATED!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database status: {e}")

if __name__ == "__main__":
    check_database_status()
