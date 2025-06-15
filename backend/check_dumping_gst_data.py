"""
Check Existing Dumping Duties and GST Provisions Data
====================================================
Inspects current data in dumping_duties and gst_provisions tables.
"""

import sqlite3
from datetime import datetime

def check_dumping_gst_data():
    """Check existing dumping duties and GST provisions data."""
    
    print("=" * 80)
    print("🔍 CHECKING DUMPING DUTIES & GST PROVISIONS DATA")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        print("1. 📋 TABLE EXISTENCE CHECK:")
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('dumping_duties', 'gst_provisions')
            ORDER BY name
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"   Existing tables: {existing_tables}")
        
        if 'dumping_duties' in existing_tables:
            print("\n2. 🚫 DUMPING DUTIES DATA:")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(dumping_duties)")
            schema = cursor.fetchall()
            print(f"   Schema columns: {len(schema)}")
            for col_info in schema:
                print(f"      {col_info[1]} ({col_info[2]})")
            
            # Get data counts
            cursor.execute("SELECT COUNT(*) FROM dumping_duties")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE is_active = 1")
            active_count = cursor.fetchone()[0]
            
            print(f"\n   Total dumping duties: {total_count}")
            print(f"   Active dumping duties: {active_count}")
            
            if total_count > 0:
                # Country distribution
                cursor.execute("""
                    SELECT country_code, COUNT(*) as count
                    FROM dumping_duties 
                    GROUP BY country_code
                    ORDER BY count DESC
                    LIMIT 10
                """)
                countries = cursor.fetchall()
                
                print(f"   Countries with duties:")
                for country, count in countries:
                    print(f"      {country}: {count} duties")
                
                # Sample records
                cursor.execute("""
                    SELECT hs_code, country_code, duty_type, duty_rate, duty_amount, 
                           case_number, is_active
                    FROM dumping_duties 
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                samples = cursor.fetchall()
                
                print(f"\n   Sample dumping duties:")
                for hs_code, country, duty_type, rate, amount, case_num, active in samples:
                    status = "Active" if active else "Inactive"
                    rate_str = f"{rate}%" if rate else "N/A"
                    amount_str = f"${amount}" if amount else "N/A"
                    print(f"      {hs_code} - {country}: {duty_type}, Rate: {rate_str}, Amount: {amount_str} ({status})")
                    if case_num:
                        print(f"         Case: {case_num}")
        else:
            print("\n2. ❌ DUMPING DUTIES TABLE NOT FOUND")
        
        if 'gst_provisions' in existing_tables:
            print("\n3. 💰 GST PROVISIONS DATA:")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(gst_provisions)")
            schema = cursor.fetchall()
            print(f"   Schema columns: {len(schema)}")
            for col_info in schema:
                print(f"      {col_info[1]} ({col_info[2]})")
            
            # Get data counts
            cursor.execute("SELECT COUNT(*) FROM gst_provisions")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE is_active = 1")
            active_count = cursor.fetchone()[0]
            
            print(f"\n   Total GST provisions: {total_count}")
            print(f"   Active GST provisions: {active_count}")
            
            if total_count > 0:
                # Exemption type distribution
                cursor.execute("""
                    SELECT exemption_type, COUNT(*) as count
                    FROM gst_provisions 
                    WHERE exemption_type IS NOT NULL
                    GROUP BY exemption_type
                    ORDER BY count DESC
                    LIMIT 10
                """)
                exemption_types = cursor.fetchall()
                
                print(f"   Exemption types:")
                for exemption_type, count in exemption_types:
                    print(f"      {exemption_type}: {count} provisions")
                
                # Sample records
                cursor.execute("""
                    SELECT hs_code, schedule_reference, exemption_type, description, 
                           value_threshold, is_active
                    FROM gst_provisions 
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                samples = cursor.fetchall()
                
                print(f"\n   Sample GST provisions:")
                for hs_code, schedule_ref, exemption_type, desc, threshold, active in samples:
                    status = "Active" if active else "Inactive"
                    hs_display = hs_code if hs_code else "General"
                    desc_short = desc[:50] + "..." if desc and len(desc) > 50 else desc or "No description"
                    threshold_str = f"${threshold:,.2f}" if threshold else "No threshold"
                    print(f"      {hs_display}: {exemption_type}")
                    print(f"         {desc_short}")
                    print(f"         Schedule: {schedule_ref}, Threshold: {threshold_str} ({status})")
        else:
            print("\n3. ❌ GST PROVISIONS TABLE NOT FOUND")
        
        # Check relationships
        if 'dumping_duties' in existing_tables:
            print("\n4. 🔗 DUMPING DUTIES RELATIONSHIPS:")
            
            cursor.execute("""
                SELECT COUNT(*) FROM dumping_duties d
                INNER JOIN tariff_codes tc ON d.hs_code = tc.hs_code
            """)
            valid_relationships = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM dumping_duties")
            total_duties = cursor.fetchone()[0]
            
            if total_duties > 0:
                print(f"   Valid HS code relationships: {valid_relationships}/{total_duties}")
                print(f"   Relationship integrity: {(valid_relationships/total_duties*100):.1f}%")
        
        if 'gst_provisions' in existing_tables:
            print("\n5. 🔗 GST PROVISIONS RELATIONSHIPS:")
            
            cursor.execute("""
                SELECT COUNT(*) FROM gst_provisions g
                INNER JOIN tariff_codes tc ON g.hs_code = tc.hs_code
                WHERE g.hs_code IS NOT NULL
            """)
            valid_relationships = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE hs_code IS NOT NULL")
            provisions_with_hs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE hs_code IS NULL")
            general_provisions = cursor.fetchone()[0]
            
            print(f"   Provisions with HS codes: {provisions_with_hs}")
            print(f"   General provisions (no HS code): {general_provisions}")
            if provisions_with_hs > 0:
                print(f"   Valid HS code relationships: {valid_relationships}/{provisions_with_hs}")
                print(f"   Relationship integrity: {(valid_relationships/provisions_with_hs*100):.1f}%")
        
        print("\n" + "=" * 80)
        print("✅ DATA CHECK COMPLETED")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during data check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_dumping_gst_data()
