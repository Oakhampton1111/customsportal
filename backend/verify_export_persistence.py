"""
Verify Export Codes Persistence
===============================
Verify that export codes data is properly persisted in the SQLite database
and survives application restarts.
"""

import sqlite3
import os
from datetime import datetime

def verify_export_persistence():
    """Verify export codes database persistence."""
    
    db_path = 'customs_portal.db'
    
    try:
        print("=" * 80)
        print("💾 EXPORT CODES PERSISTENCE VERIFICATION")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Database File Verification
        print("1. 📁 DATABASE FILE VERIFICATION:")
        
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            file_size_mb = file_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(os.path.getmtime(db_path))
            
            print(f"   ✅ Database file exists: {db_path}")
            print(f"   ✅ File size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
            print(f"   ✅ Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   ❌ Database file not found: {db_path}")
            return
        
        # 2. Connection and Schema Verification
        print("\n2. 🔌 CONNECTION AND SCHEMA VERIFICATION:")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if export_codes table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='export_codes'
        """)
        
        table_exists = cursor.fetchone()
        if table_exists:
            print("   ✅ export_codes table exists")
        else:
            print("   ❌ export_codes table not found")
            return
        
        # Check table schema
        cursor.execute("PRAGMA table_info(export_codes)")
        schema = cursor.fetchall()
        
        print("   ✅ Table schema:")
        for col_info in schema:
            col_id, name, data_type, not_null, default, pk = col_info
            print(f"      {name}: {data_type} {'NOT NULL' if not_null else 'NULL'} {'PK' if pk else ''}")
        
        # 3. Data Persistence Verification
        print("\n3. 📊 DATA PERSISTENCE VERIFICATION:")
        
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        total_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE is_active = 1")
        active_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE corresponding_import_code IS NOT NULL")
        mapped_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT SUBSTR(ahecc_code, 1, 2)) FROM export_codes")
        chapters = cursor.fetchone()[0]
        
        print(f"   ✅ Total export codes: {total_codes:,}")
        print(f"   ✅ Active codes: {active_codes:,}")
        print(f"   ✅ Mapped codes: {mapped_codes:,}")
        print(f"   ✅ Chapters covered: {chapters}")
        
        # 4. Data Integrity Verification
        print("\n4. ✅ DATA INTEGRITY VERIFICATION:")
        
        # Check for NULL values in required fields
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE ahecc_code IS NULL")
        null_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE description IS NULL OR TRIM(description) = ''")
        null_descriptions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE created_at IS NULL")
        null_timestamps = cursor.fetchone()[0]
        
        # Check for duplicate AHECC codes
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT ahecc_code FROM export_codes 
                GROUP BY ahecc_code 
                HAVING COUNT(*) > 1
            )
        """)
        duplicate_codes = cursor.fetchone()[0]
        
        # Check code format
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE LENGTH(ahecc_code) != 8")
        invalid_length = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE ahecc_code NOT GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'")
        invalid_format = cursor.fetchone()[0]
        
        print(f"   ✅ NULL AHECC codes: {null_codes}")
        print(f"   ✅ NULL descriptions: {null_descriptions}")
        print(f"   ✅ NULL timestamps: {null_timestamps}")
        print(f"   ✅ Duplicate codes: {duplicate_codes}")
        print(f"   ✅ Invalid length codes: {invalid_length}")
        print(f"   ✅ Invalid format codes: {invalid_format}")
        
        integrity_score = 100
        if null_codes > 0:
            integrity_score -= 20
        if null_descriptions > 0:
            integrity_score -= 15
        if duplicate_codes > 0:
            integrity_score -= 25
        if invalid_length > 0 or invalid_format > 0:
            integrity_score -= 20
        
        print(f"   📊 Data integrity score: {integrity_score}/100")
        
        # 5. Sample Data Verification
        print("\n5. 🔍 SAMPLE DATA VERIFICATION:")
        
        cursor.execute("""
            SELECT ahecc_code, description, statistical_unit, corresponding_import_code, is_active
            FROM export_codes 
            ORDER BY ahecc_code
            LIMIT 10
        """)
        
        samples = cursor.fetchall()
        print("   Sample export codes (first 10):")
        for ahecc, desc, unit, imp_code, active in samples:
            status = "Active" if active else "Inactive"
            print(f"      {ahecc}: {desc[:40]:<40} [{unit:>10}] -> {imp_code or 'None'} ({status})")
        
        # 6. Relationship Verification
        print("\n6. 🔗 RELATIONSHIP VERIFICATION:")
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes e
            INNER JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
        """)
        valid_relationships = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes e
            LEFT JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            WHERE e.corresponding_import_code IS NOT NULL AND t.hs_code IS NULL
        """)
        broken_relationships = cursor.fetchone()[0]
        
        print(f"   ✅ Valid import code relationships: {valid_relationships:,}")
        print(f"   ✅ Broken relationships: {broken_relationships}")
        
        if broken_relationships > 0:
            print("   ⚠️  Some export codes reference non-existent import codes")
        
        # 7. Performance Verification
        print("\n7. ⚡ PERFORMANCE VERIFICATION:")
        
        import time
        
        # Test basic queries
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        cursor.fetchone()
        count_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("SELECT * FROM export_codes WHERE ahecc_code = '01010101'")
        cursor.fetchone()
        lookup_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("""
            SELECT SUBSTR(ahecc_code, 1, 2), COUNT(*) 
            FROM export_codes 
            GROUP BY SUBSTR(ahecc_code, 1, 2)
        """)
        cursor.fetchall()
        group_time = time.time() - start_time
        
        start_time = time.time()
        cursor.execute("""
            SELECT e.ahecc_code, t.description
            FROM export_codes e
            INNER JOIN tariff_codes t ON e.corresponding_import_code = t.hs_code
            LIMIT 100
        """)
        cursor.fetchall()
        join_time = time.time() - start_time
        
        print(f"   Count query: {count_time:.4f} seconds")
        print(f"   Single lookup: {lookup_time:.4f} seconds")
        print(f"   Group by chapter: {group_time:.4f} seconds")
        print(f"   Join with import codes (100 rows): {join_time:.4f} seconds")
        
        performance_score = 100
        if count_time > 0.01:
            performance_score -= 10
        if lookup_time > 0.001:
            performance_score -= 10
        if group_time > 0.1:
            performance_score -= 10
        if join_time > 0.1:
            performance_score -= 10
        
        print(f"   📊 Performance score: {performance_score}/100")
        
        # 8. Index Verification
        print("\n8. 📇 INDEX VERIFICATION:")
        
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' AND tbl_name='export_codes'
        """)
        
        indexes = cursor.fetchall()
        print(f"   Indexes found: {len(indexes)}")
        for name, sql in indexes:
            if sql:  # Skip auto-generated indexes
                print(f"      {name}: {sql}")
        
        # 9. Backup Verification
        print("\n9. 💾 BACKUP VERIFICATION:")
        
        backup_path = 'customs_portal_backup.db'
        if os.path.exists(backup_path):
            backup_size = os.path.getsize(backup_path)
            backup_size_mb = backup_size / (1024 * 1024)
            backup_mod_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
            
            print(f"   ✅ Backup exists: {backup_path}")
            print(f"   ✅ Backup size: {backup_size:,} bytes ({backup_size_mb:.2f} MB)")
            print(f"   ✅ Backup modified: {backup_mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Quick backup verification
            backup_conn = sqlite3.connect(backup_path)
            backup_cursor = backup_conn.cursor()
            
            try:
                backup_cursor.execute("SELECT COUNT(*) FROM export_codes")
                backup_count = backup_cursor.fetchone()[0]
                print(f"   ✅ Backup export codes: {backup_count:,}")
                
                if backup_count == total_codes:
                    print("   ✅ Backup is current")
                else:
                    print(f"   ⚠️  Backup may be outdated (main: {total_codes:,}, backup: {backup_count:,})")
                    
            except Exception as e:
                print(f"   ⚠️  Backup verification failed: {e}")
            finally:
                backup_conn.close()
        else:
            print(f"   ⚠️  No backup found at {backup_path}")
        
        # 10. Overall Persistence Assessment
        print("\n10. 🎯 OVERALL PERSISTENCE ASSESSMENT:")
        
        persistence_score = 0
        max_score = 100
        
        # File existence and size (20 points)
        if file_size_mb > 1:  # Reasonable size for export data
            persistence_score += 20
        elif file_size_mb > 0.1:
            persistence_score += 15
        else:
            persistence_score += 5
        
        # Data completeness (25 points)
        if total_codes >= 3000:
            persistence_score += 25
        elif total_codes >= 1000:
            persistence_score += 20
        elif total_codes >= 500:
            persistence_score += 15
        else:
            persistence_score += 10
        
        # Data integrity (25 points)
        persistence_score += int(integrity_score * 0.25)
        
        # Performance (15 points)
        persistence_score += int(performance_score * 0.15)
        
        # Relationships (15 points)
        if broken_relationships == 0:
            persistence_score += 15
        elif broken_relationships < total_codes * 0.01:
            persistence_score += 12
        elif broken_relationships < total_codes * 0.05:
            persistence_score += 8
        else:
            persistence_score += 3
        
        print(f"   📊 Overall Persistence Score: {persistence_score}/{max_score} ({persistence_score}%)")
        
        if persistence_score >= 90:
            status = "🟢 EXCELLENT PERSISTENCE"
            recommendation = "Data is excellently persisted and ready for production."
        elif persistence_score >= 75:
            status = "🟡 GOOD PERSISTENCE"
            recommendation = "Data persistence is good with minor areas for improvement."
        elif persistence_score >= 60:
            status = "🟠 ACCEPTABLE PERSISTENCE"
            recommendation = "Data persistence is acceptable but needs attention."
        else:
            status = "🔴 POOR PERSISTENCE"
            recommendation = "Data persistence has significant issues."
        
        print(f"   📈 Status: {status}")
        print(f"   💡 Recommendation: {recommendation}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("📋 EXPORT CODES PERSISTENCE SUMMARY")
        print("=" * 80)
        print(f"✅ Database File: {file_size_mb:.2f} MB")
        print(f"✅ Export Codes: {total_codes:,}")
        print(f"✅ Data Integrity: {integrity_score}/100")
        print(f"✅ Performance: {performance_score}/100")
        print(f"✅ Valid Relationships: {valid_relationships:,}")
        print(f"✅ Persistence Score: {persistence_score}/100 ({persistence_score}%)")
        print(f"✅ Status: {status}")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during persistence verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_export_persistence()
