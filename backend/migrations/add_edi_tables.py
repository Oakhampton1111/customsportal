"""
Migration script to add EDI tables for job registration and customs declarations.

This script creates the following tables:
- edi_messages: For storing all EDI communications
- edi_jobs: For tracking customs clearance jobs
- customs_declarations: For formal customs declarations
- declaration_items: For individual items within declarations
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Import all models to ensure they're registered with SQLAlchemy
from database import Base
from config import get_settings
from models.customer import (
    Customer, CustomerSSOAccount, CustomerSession, CustomerAuthLog,
    CustomerVerification, CustomerVerificationDocument, CustomerShipment,
    CustomerDigitalAuthority
)
from models.edi import (
    EDIMessage, EDIJob, CustomsDeclaration, DeclarationItem
)
from models.documents import (
    Document, DocumentCategoryMapping, DocumentCategoryDefinition, DocumentShare
)
from models.tariff import TariffCode


async def create_edi_tables():
    """Create EDI tables in the database."""
    print("Creating EDI tables...")
    
    # Get database URL from settings
    settings = get_settings()
    database_url = settings.database_url
    
    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            # Create the EDI tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ EDI tables created successfully!")
        
        # Verify tables were created
        async with engine.begin() as conn:
            # Check if EDI tables exist
            tables_to_check = [
                'edi_messages',
                'edi_jobs', 
                'customs_declarations',
                'declaration_items'
            ]
            
            for table_name in tables_to_check:
                result = await conn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                )
                if result.fetchone():
                    print(f"✅ Table '{table_name}' created successfully")
                else:
                    print(f"❌ Table '{table_name}' was not created")
        
        print("\n🎉 EDI migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating EDI tables: {e}")
        raise
    finally:
        await engine.dispose()


async def verify_table_structure():
    """Verify the structure of created tables."""
    print("\nVerifying table structure...")
    
    # Get database URL from settings
    settings = get_settings()
    database_url = settings.database_url
    
    engine = create_async_engine(database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check EDI messages table structure
            result = await conn.execute(text("PRAGMA table_info(edi_messages)"))
            columns = result.fetchall()
            print(f"\nedi_messages table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check EDI jobs table structure
            result = await conn.execute(text("PRAGMA table_info(edi_jobs)"))
            columns = result.fetchall()
            print(f"\nedi_jobs table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check customs declarations table structure
            result = await conn.execute(text("PRAGMA table_info(customs_declarations)"))
            columns = result.fetchall()
            print(f"\ncustoms_declarations table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check declaration items table structure
            result = await conn.execute(text("PRAGMA table_info(declaration_items)"))
            columns = result.fetchall()
            print(f"\ndeclaration_items table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check foreign key constraints
            print("\nChecking foreign key constraints...")
            
            # EDI messages foreign keys
            result = await conn.execute(text("PRAGMA foreign_key_list(edi_messages)"))
            fks = result.fetchall()
            print(f"edi_messages has {len(fks)} foreign key constraints")
            
            # EDI jobs foreign keys
            result = await conn.execute(text("PRAGMA foreign_key_list(edi_jobs)"))
            fks = result.fetchall()
            print(f"edi_jobs has {len(fks)} foreign key constraints")
            
            # Customs declarations foreign keys
            result = await conn.execute(text("PRAGMA foreign_key_list(customs_declarations)"))
            fks = result.fetchall()
            print(f"customs_declarations has {len(fks)} foreign key constraints")
            
            # Declaration items foreign keys
            result = await conn.execute(text("PRAGMA foreign_key_list(declaration_items)"))
            fks = result.fetchall()
            print(f"declaration_items has {len(fks)} foreign key constraints")
            
    except Exception as e:
        print(f"❌ Error verifying table structure: {e}")
        raise
    finally:
        await engine.dispose()


async def test_basic_operations():
    """Test basic database operations with the new tables."""
    print("\nTesting basic database operations...")
    
    # Get database URL from settings
    settings = get_settings()
    database_url = settings.database_url
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Test creating a sample EDI message
            from models.edi import EDIMessage, EDIMessageType, EDIDirection, EDIMessageStatus
            
            test_message = EDIMessage(
                message_id="TEST_001",
                message_type=EDIMessageType.CUSCAR,
                direction=EDIDirection.INBOUND,
                raw_message="UNB+UNOC:3+SENDER+ABF+20250107+TEST001'UNH+1+CUSCAR:D:03B:UN:EAN008'UNT+2+1'UNZ+1+TEST001'",
                status=EDIMessageStatus.PENDING
            )
            
            session.add(test_message)
            await session.commit()
            await session.refresh(test_message)
            
            print(f"✅ Created test EDI message with ID: {test_message.id}")
            
            # Clean up test data
            await session.delete(test_message)
            await session.commit()
            
            print("✅ Test operations completed successfully")
            
    except Exception as e:
        print(f"❌ Error during test operations: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main migration function."""
    print("🚀 Starting EDI tables migration...")
    print("=" * 50)
    
    try:
        # Create tables
        await create_edi_tables()
        
        # Verify structure
        await verify_table_structure()
        
        # Test operations
        await test_basic_operations()
        
        print("\n" + "=" * 50)
        print("🎉 EDI migration completed successfully!")
        print("\nNew tables created:")
        print("  - edi_messages: For storing all EDI communications")
        print("  - edi_jobs: For tracking customs clearance jobs")
        print("  - customs_declarations: For formal customs declarations")
        print("  - declaration_items: For individual items within declarations")
        print("\nYou can now use the EDI API endpoints for:")
        print("  - Job registration and management")
        print("  - Customs declaration creation and submission")
        print("  - EDI message processing and status tracking")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())