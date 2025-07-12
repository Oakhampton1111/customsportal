"""
Migration script to create Digital Letter of Authority tables.
This script creates the tables for the comprehensive LOA system with digital signatures.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base
from config import get_settings
from models.digital_loa import (
    DigitalLetterOfAuthority, LOASignature, LOAAuditLog, LOATemplate
)

async def create_digital_loa_tables():
    """Create all Digital Letter of Authority related tables."""
    
    print("Creating Digital Letter of Authority tables...")
    
    # Get database URL from settings
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=True)
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            # Import all required models to ensure foreign key relationships work
            from models.customer import (
                Customer, CustomerSSOAccount, CustomerSession, CustomerAuthLog,
                CustomerVerification, CustomerVerificationDocument,
                CustomerShipment, CustomerDigitalAuthority
            )
            from models.digital_loa import (
                DigitalLetterOfAuthority, LOASignature, LOAAuditLog, LOATemplate
            )
            
            # Create the tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Digital Letter of Authority tables created successfully!")
            
        # Create default template
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            await create_default_template(session)
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

async def create_default_template(session: AsyncSession):
    """Create default LOA template."""
    
    try:
        # Check if default template already exists
        from sqlalchemy import select
        from models.digital_loa import LOATemplate
        
        existing_template = await session.execute(
            select(LOATemplate).where(LOATemplate.template_code == "default")
        )
        
        if existing_template.scalar_one_or_none():
            print("✅ Default template already exists")
            return
        
        # Create default template
        default_template = LOATemplate(
            template_name="Standard Letter of Authority",
            template_code="default",
            description="Standard Letter of Authority template for Australian customs clearance",
            template_content="""I/We, {company_name} (ABN: {company_abn}), hereby authorize and appoint the licensed customs broker identified below to act as our agent for all matters relating to the importation and customs clearance of goods on our behalf.

This Letter of Authority is granted under Section 181 of the Customs Act 1901 and authorizes the customs broker to:

1. Lodge import declarations and other customs documents
2. Pay duties, taxes, and charges on our behalf
3. Receive goods from customs control
4. Represent us in all dealings with the Australian Border Force
5. Sign documents and make declarations as our authorized agent

CUSTOMS BROKER DETAILS:
License Number: {customs_broker_license}

This authority shall remain in effect until revoked in writing or until the expiry date specified below.

AUTHORIZED REPRESENTATIVE:
Name: {authorized_person_name}
Title: {authorized_person_title}
Email: {authorized_person_email}

By signing this Letter of Authority, I confirm that I am authorized to bind the company and that all information provided is true and correct.""",
            legal_text="This Letter of Authority is governed by the Customs Act 1901 (Cth) and related Australian customs legislation. The signatory warrants that they have the authority to bind the company to this agreement.",
            terms_conditions="""TERMS AND CONDITIONS:

1. This authority remains valid until formally revoked in writing or until the specified expiry date.
2. The company remains liable for all duties, taxes, and charges incurred.
3. The customs broker acts as agent only and assumes no liability for the accuracy of information provided by the company.
4. Any changes to this authority must be made in writing and signed by an authorized representative.
5. This Letter of Authority is governed by Australian law and any disputes will be subject to the jurisdiction of Australian courts.""",
            required_fields=[
                "company_name", "company_abn", "company_address",
                "authorized_person_name", "authorized_person_title", 
                "authorized_person_email", "customs_broker_license", "authority_scope"
            ],
            optional_fields=[
                "reference_number", "authorized_person_phone", 
                "special_instructions", "effective_date", "expiry_date"
            ],
            validation_rules={
                "company_abn": {"type": "string", "length": 11, "pattern": "^[0-9]{11}$"},
                "authorized_person_email": {"type": "email"},
                "customs_broker_license": {"type": "string", "min_length": 5},
                "effective_date": {"type": "date", "format": "ISO8601"},
                "expiry_date": {"type": "date", "format": "ISO8601", "after": "effective_date"}
            },
            is_active=True,
            is_default=True,
            version="1.0",
            created_by="System",
            approved_by="System Administrator"
        )
        
        session.add(default_template)
        await session.commit()
        print("✅ Default LOA template created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating default template: {e}")
        await session.rollback()
        raise

async def verify_tables():
    """Verify that all tables were created successfully."""
    
    print("\nVerifying Digital Letter of Authority tables...")
    
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check if tables exist by querying their structure
            tables_to_check = [
                'digital_letters_of_authority',
                'loa_signatures', 
                'loa_audit_logs',
                'loa_templates'
            ]
            
            for table_name in tables_to_check:
                try:
                    result = await conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = result.scalar()
                    print(f"✅ Table '{table_name}' exists and is accessible (contains {count} records)")
                except Exception as e:
                    print(f"❌ Table '{table_name}' verification failed: {e}")
                    
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        raise
    finally:
        await engine.dispose()

async def main():
    """Main migration function."""
    print("=== Digital Letter of Authority Migration ===")
    print("Creating tables for comprehensive LOA system with digital signatures...")
    
    try:
        # Create tables
        await create_digital_loa_tables()
        
        # Verify tables
        await verify_tables()
        
        print("\n🎉 Digital Letter of Authority migration completed successfully!")
        print("\nCreated tables:")
        print("- digital_letters_of_authority (main LOA records)")
        print("- loa_signatures (digital signature records)")
        print("- loa_audit_logs (audit trail)")
        print("- loa_templates (LOA templates)")
        print("\nFeatures available:")
        print("- Digital signature creation and verification")
        print("- PDF generation with embedded signatures")
        print("- Comprehensive audit trail")
        print("- Template-based LOA creation")
        print("- Public verification system")
        print("- Certificate-based authentication")
        
    except Exception as e:
        print(f"\n💥 Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())