#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script for Customs Broker Portal

This script migrates all data from the local SQLite database to PostgreSQL
while handling data type conversions and maintaining referential integrity.
"""

import asyncio
import sqlite3
import asyncpg
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

class DatabaseMigrator:
    def __init__(self, sqlite_path: str, postgres_url: str):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.migration_stats = {}
        
    async def migrate_all_data(self):
        """Complete migration from SQLite to PostgreSQL"""
        
        print("🚀 Starting Customs Broker Portal database migration...")
        print(f"📁 SQLite source: {self.sqlite_path}")
        print(f"🐘 PostgreSQL target: {self.postgres_url.split('@')[1] if '@' in self.postgres_url else 'localhost'}")
        
        # Verify SQLite database exists
        if not os.path.exists(self.sqlite_path):
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")
        
        # Connect to both databases
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        
        try:
            postgres_conn = await asyncpg.connect(self.postgres_url)
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            print("💡 Make sure PostgreSQL is running and the connection string is correct")
            sqlite_conn.close()
            return False
        
        try:
            # Verify PostgreSQL schema exists
            await self.verify_postgres_schema(postgres_conn)
            
            # Migration order (respecting foreign key dependencies)
            migration_order = [
                'tariff_sections',
                'tariff_chapters', 
                'trade_agreements',
                'tariff_codes',
                'duty_rates',
                'fta_rates',
                'dumping_duties',
                'tcos',
                'gst_provisions',
                'export_codes',
                'product_classifications'
            ]
            
            total_migrated = 0
            
            for table_name in migration_order:
                migrated_count = await self.migrate_table(sqlite_conn, postgres_conn, table_name)
                total_migrated += migrated_count
                
            print(f"\n✅ Migration completed successfully!")
            print(f"📊 Total records migrated: {total_migrated:,}")
            
            # Print migration summary
            self.print_migration_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
            
        finally:
            sqlite_conn.close()
            await postgres_conn.close()
    
    async def verify_postgres_schema(self, postgres_conn):
        """Verify that PostgreSQL schema exists"""
        
        print("🔍 Verifying PostgreSQL schema...")
        
        # Check if key tables exist
        key_tables = ['tariff_codes', 'duty_rates', 'fta_rates']
        
        for table in key_tables:
            exists = await postgres_conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            
            if not exists:
                raise Exception(f"Table '{table}' not found in PostgreSQL. Please run schema.sql first.")
        
        print("✅ PostgreSQL schema verified")
    
    async def migrate_table(self, sqlite_conn, postgres_conn, table_name: str):
        """Migrate a single table"""
        
        print(f"📋 Migrating table: {table_name}")
        
        # Check if table exists in SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
            (table_name,)
        )
        
        if not cursor.fetchone():
            print(f"  ⚠️  Table {table_name} not found in SQLite, skipping...")
            self.migration_stats[table_name] = {'migrated': 0, 'status': 'skipped'}
            return 0
        
        # Get data from SQLite
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  📭 No data found in {table_name}")
            self.migration_stats[table_name] = {'migrated': 0, 'status': 'empty'}
            return 0
            
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Prepare PostgreSQL insert with conflict resolution
        placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
        columns_str = ', '.join(columns)
        
        # Use ON CONFLICT DO NOTHING to handle duplicates gracefully
        insert_query = f"""
            INSERT INTO {table_name} ({columns_str}) 
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        # Convert rows to list of tuples with proper data type handling
        data_rows = []
        for row in rows:
            converted_row = []
            for i, value in enumerate(row):
                converted_value = self.convert_data_type(value, columns[i], table_name)
                converted_row.append(converted_value)
            data_rows.append(tuple(converted_row))
        
        try:
            # Batch insert into PostgreSQL
            await postgres_conn.executemany(insert_query, data_rows)
            
            # Verify insertion
            actual_count = await postgres_conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            
            print(f"  ✅ Migrated {len(data_rows):,} rows to {table_name} (total: {actual_count:,})")
            
            self.migration_stats[table_name] = {
                'migrated': len(data_rows), 
                'total_in_postgres': actual_count,
                'status': 'success'
            }
            
            return len(data_rows)
            
        except Exception as e:
            print(f"  ❌ Error migrating {table_name}: {e}")
            self.migration_stats[table_name] = {'migrated': 0, 'status': 'error', 'error': str(e)}
            return 0
    
    def convert_data_type(self, value: Any, column_name: str, table_name: str) -> Any:
        """Convert SQLite data types to PostgreSQL compatible types"""
        
        if value is None:
            return None
            
        # Handle JSON fields (common in our schema)
        if isinstance(value, str) and value.strip().startswith(('{', '[')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        # Handle boolean fields
        if column_name.lower() in ['is_active', 'is_current', 'verified_by_broker', 'safeguard_applicable']:
            if isinstance(value, (int, bool)):
                return bool(value)
            elif isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
        
        # Handle decimal fields
        if column_name.lower() in ['general_rate', 'preferential_rate', 'duty_rate', 'confidence_score']:
            if value is not None:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
        
        # Handle date fields
        if column_name.lower().endswith('_date') or column_name.lower() in ['created_at', 'updated_at']:
            if isinstance(value, str):
                try:
                    # Try to parse various date formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S.%f']:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    return value  # Return as string if parsing fails
                except:
                    return value
        
        return value
    
    def print_migration_summary(self):
        """Print a summary of the migration results"""
        
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)
        
        total_migrated = 0
        successful_tables = 0
        
        for table_name, stats in self.migration_stats.items():
            status_icon = {
                'success': '✅',
                'empty': '📭',
                'skipped': '⚠️',
                'error': '❌'
            }.get(stats['status'], '❓')
            
            migrated = stats.get('migrated', 0)
            total_migrated += migrated
            
            if stats['status'] == 'success':
                successful_tables += 1
                total_in_db = stats.get('total_in_postgres', migrated)
                print(f"{status_icon} {table_name:<25} {migrated:>8,} rows (total: {total_in_db:,})")
            elif stats['status'] == 'error':
                print(f"{status_icon} {table_name:<25} {'ERROR':>8} - {stats.get('error', 'Unknown error')}")
            else:
                print(f"{status_icon} {table_name:<25} {migrated:>8,} rows ({stats['status']})")
        
        print("-" * 60)
        print(f"📈 Total records migrated: {total_migrated:,}")
        print(f"✅ Successful tables: {successful_tables}/{len(self.migration_stats)}")
        print("="*60)


async def validate_migration(sqlite_path: str, postgres_url: str):
    """Validate that migration was successful by comparing record counts"""
    
    print("\n🔍 Validating migration...")
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    postgres_conn = await asyncpg.connect(postgres_url)
    
    tables = [
        'tariff_codes', 'duty_rates', 'fta_rates', 'dumping_duties',
        'tcos', 'gst_provisions', 'export_codes', 'product_classifications',
        'tariff_sections', 'tariff_chapters', 'trade_agreements'
    ]
    
    validation_results = {}
    all_match = True
    
    print("\n" + "="*80)
    print("🔍 VALIDATION RESULTS")
    print("="*80)
    print(f"{'Table':<25} {'SQLite':<12} {'PostgreSQL':<12} {'Status':<10}")
    print("-" * 80)
    
    for table in tables:
        try:
            # Count rows in SQLite
            sqlite_count = sqlite_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.OperationalError:
            sqlite_count = 0  # Table doesn't exist in SQLite
        
        try:
            # Count rows in PostgreSQL
            postgres_count = await postgres_conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        except:
            postgres_count = 0  # Table doesn't exist in PostgreSQL
        
        match = sqlite_count == postgres_count
        if not match:
            all_match = False
        
        status_icon = "✅" if match else "❌"
        status_text = "MATCH" if match else "DIFF"
        
        validation_results[table] = {
            'sqlite_count': sqlite_count,
            'postgres_count': postgres_count,
            'match': match
        }
        
        print(f"{table:<25} {sqlite_count:<12,} {postgres_count:<12,} {status_icon} {status_text}")
    
    print("-" * 80)
    print(f"Overall validation: {'✅ PASSED' if all_match else '❌ FAILED'}")
    print("="*80)
    
    sqlite_conn.close()
    await postgres_conn.close()
    
    return validation_results, all_match


async def main():
    """Main migration function"""
    
    # Default paths
    sqlite_path = "backend/customs_portal.db"
    
    # Get PostgreSQL URL from environment or use default
    postgres_url = os.getenv(
        'DATABASE_URL', 
        'postgresql://customs_user:password@localhost:5432/customs_broker_portal'
    )
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        sqlite_path = sys.argv[1]
    if len(sys.argv) > 2:
        postgres_url = sys.argv[2]
    
    print("🏛️  Customs Broker Portal - Database Migration")
    print("=" * 60)
    
    # Run migration
    migrator = DatabaseMigrator(sqlite_path, postgres_url)
    success = await migrator.migrate_all_data()
    
    if success:
        # Run validation
        validation_results, validation_passed = await validate_migration(sqlite_path, postgres_url)
        
        if validation_passed:
            print("\n🎉 Migration completed successfully and validation passed!")
            print("💡 Your PostgreSQL database is ready for production use.")
            return 0
        else:
            print("\n⚠️  Migration completed but validation found discrepancies.")
            print("💡 Please review the validation results above.")
            return 1
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
