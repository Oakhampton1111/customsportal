"""
Customer Portal Database Migration Script

This script creates all the necessary database tables for the customer portal
including SSO authentication, 100-point ID verification, and customer management.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from database import init_database, get_async_session
from sqlalchemy import text

# Import ALL models to register them with SQLAlchemy metadata
# This ensures all tables are created when calling Base.metadata.create_all()
import models.customer
import models.tariff
import models.duty
import models.dumping
import models.tco
import models.gst
import models.export
import models.classification
import models.conversation
import models.documents
import models.reports
import models.fta

async def create_customer_tables():
    """Create all customer-related tables"""
    
    print("🔧 Starting customer tables migration...")
    
    try:
        # Initialize database connection first
        await init_database()
        print("✅ Database connection initialized!")
        
        # Import Base from database module to get the metadata with all models
        from database import Base, engine
        
        # Create all tables (this will create customer tables since we imported the models)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ All customer tables created successfully!")
        
        # Verify tables were created by testing simple queries
        async for session in get_async_session():
            # Test each table by running a simple query
            tables_to_test = [
                ("customers", "SELECT COUNT(*) FROM customers"),
                ("customer_sso_accounts", "SELECT COUNT(*) FROM customer_sso_accounts"),
                ("customer_sessions", "SELECT COUNT(*) FROM customer_sessions"),
                ("customer_auth_logs", "SELECT COUNT(*) FROM customer_auth_logs"),
                ("customer_verification", "SELECT COUNT(*) FROM customer_verification"),
                ("customer_verification_documents", "SELECT COUNT(*) FROM customer_verification_documents"),
                ("customer_shipments", "SELECT COUNT(*) FROM customer_shipments"),
                ("customer_digital_authorities", "SELECT COUNT(*) FROM customer_digital_authorities")
            ]
            
            print(f"\n📊 Verifying customer tables:")
            for table_name, query in tables_to_test:
                try:
                    result = await session.execute(text(query))
                    count = result.scalar()
                    print(f"   ✅ {table_name}: {count} records")
                except Exception as e:
                    print(f"   ❌ {table_name}: Error - {e}")
            break
        
        print("\n🎉 Customer portal database migration completed successfully!")
        print("📊 All 8 customer tables created and verified")
        print("🔐 SSO authentication tables ready")
        print("🆔 100-point ID verification tables ready")
        print("📦 Customer shipment tracking tables ready")
        print("📜 Digital authority tables ready")
        print("🚀 Ready to start the SSO customer portal!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_migration():
    """Verify that all expected tables exist"""
    
    expected_tables = [
        'customers',
        'customer_sso_accounts', 
        'customer_sessions',
        'customer_auth_logs',
        'customer_verification',
        'customer_verification_documents',
        'customer_shipments',
        'customer_digital_authorities'
    ]
    
    print("\n🔍 Verifying migration...")
    
    try:
        async for session in get_async_session():
            for table_name in expected_tables:
                # For SQLite, check if table exists using sqlite_master
                result = await session.execute(text(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{table_name}';
                """))
                
                exists = result.scalar() is not None
                status = "✅" if exists else "❌"
                print(f"   {status} {table_name}")
                
                if not exists:
                    raise Exception(f"Table {table_name} was not created")
        
        print("✅ All customer tables verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Customer Portal Database Migration")
    print("=" * 50)
    
    async def run_migration():
        success = await create_customer_tables()
        if success:
            success = await verify_migration()
        
        if success:
            print("\n" + "=" * 50)
            print("✨ Migration completed! Customer portal is ready for use.")
            print("🔗 Next step: Update main.py to include customer authentication routes")
            return True
        else:
            print("\n" + "=" * 50)
            print("💥 Migration failed! Please check the errors above.")
            return False
    
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)