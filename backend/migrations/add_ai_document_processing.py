"""
Database migration script to add AI document processing tables.

This migration adds the necessary tables for AI-powered document processing,
including processing records, extracted fields, and processing templates.
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from database import get_database_url
from models.ai_document_processing import (
    AIDocumentProcessing, ExtractedField, ProcessingTemplate
)
from models.documents import Document

logger = logging.getLogger(__name__)


async def run_migration():
    """Run the AI document processing migration."""
    
    # Create async engine
    engine = create_async_engine(get_database_url(), echo=True)
    
    try:
        # Create all tables
        from database import Base
        async with engine.begin() as conn:
            # Create the new tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("AI document processing tables created successfully")
        
        # Add any initial data if needed
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            # Add default processing templates
            await add_default_templates(session)
            await session.commit()
            logger.info("Default processing templates added successfully")
        
        logger.info("AI document processing migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


async def add_default_templates(session: AsyncSession):
    """Add default processing templates for common document types."""
    
    # Commercial Invoice Template
    commercial_invoice_template = ProcessingTemplate(
        name="Commercial Invoice Standard",
        description="Standard template for processing commercial invoices",
        document_type="commercial_invoice",
        field_definitions={
            "required_fields": [
                "invoice_number",
                "invoice_date", 
                "seller_name",
                "buyer_name",
                "total_amount",
                "currency"
            ],
            "optional_fields": [
                "seller_address",
                "buyer_address",
                "payment_terms",
                "incoterms",
                "country_of_origin",
                "hs_codes",
                "item_descriptions",
                "quantities",
                "unit_prices"
            ],
            "field_types": {
                "invoice_number": "text",
                "invoice_date": "date",
                "seller_name": "text",
                "buyer_name": "text",
                "total_amount": "currency",
                "currency": "text",
                "quantities": "number",
                "unit_prices": "currency"
            }
        },
        validation_rules={
            "invoice_number": {
                "required": True,
                "pattern": "^[A-Z0-9-]+$",
                "max_length": 50
            },
            "total_amount": {
                "required": True,
                "min_value": 0,
                "data_type": "decimal"
            },
            "currency": {
                "required": True,
                "allowed_values": ["AUD", "USD", "EUR", "GBP", "JPY", "CNY"]
            }
        },
        extraction_prompts={
            "invoice_number": "Look for invoice number, invoice #, or similar identifiers",
            "total_amount": "Find the total amount, grand total, or final sum",
            "currency": "Identify the currency code (AUD, USD, etc.) or currency symbol"
        },
        created_by="system",
        version="1.0"
    )
    
    # Packing List Template
    packing_list_template = ProcessingTemplate(
        name="Packing List Standard",
        description="Standard template for processing packing lists",
        document_type="packing_list",
        field_definitions={
            "required_fields": [
                "packing_list_number",
                "date",
                "shipper_name",
                "consignee_name"
            ],
            "optional_fields": [
                "total_packages",
                "total_weight",
                "total_volume",
                "package_types",
                "item_descriptions",
                "quantities",
                "weights",
                "dimensions"
            ],
            "field_types": {
                "packing_list_number": "text",
                "date": "date",
                "shipper_name": "text",
                "consignee_name": "text",
                "total_packages": "number",
                "total_weight": "number",
                "total_volume": "number"
            }
        },
        validation_rules={
            "packing_list_number": {
                "required": True,
                "max_length": 50
            },
            "total_packages": {
                "min_value": 1,
                "data_type": "integer"
            }
        },
        extraction_prompts={
            "packing_list_number": "Look for packing list number, P/L number, or similar",
            "total_packages": "Find total number of packages, cartons, or containers",
            "total_weight": "Look for gross weight, net weight, or total weight"
        },
        created_by="system",
        version="1.0"
    )
    
    # Bill of Lading Template
    bill_of_lading_template = ProcessingTemplate(
        name="Bill of Lading Standard",
        description="Standard template for processing bills of lading",
        document_type="bill_of_lading",
        field_definitions={
            "required_fields": [
                "bl_number",
                "date",
                "vessel_name",
                "shipper_name",
                "consignee_name"
            ],
            "optional_fields": [
                "voyage_number",
                "port_of_loading",
                "port_of_discharge",
                "notify_party",
                "container_numbers",
                "seal_numbers",
                "freight_terms"
            ],
            "field_types": {
                "bl_number": "text",
                "date": "date",
                "vessel_name": "text",
                "voyage_number": "text",
                "shipper_name": "text",
                "consignee_name": "text"
            }
        },
        validation_rules={
            "bl_number": {
                "required": True,
                "max_length": 50
            },
            "vessel_name": {
                "required": True,
                "max_length": 100
            }
        },
        extraction_prompts={
            "bl_number": "Look for B/L number, bill of lading number, or BL reference",
            "vessel_name": "Find the vessel name or ship name",
            "port_of_loading": "Look for port of loading, POL, or loading port"
        },
        created_by="system",
        version="1.0"
    )
    
    # Certificate of Origin Template
    certificate_template = ProcessingTemplate(
        name="Certificate of Origin Standard",
        description="Standard template for processing certificates of origin",
        document_type="certificate_of_origin",
        field_definitions={
            "required_fields": [
                "certificate_number",
                "issue_date",
                "exporter_name",
                "country_of_origin"
            ],
            "optional_fields": [
                "exporter_address",
                "consignee_name",
                "destination_country",
                "goods_description",
                "hs_codes",
                "issuing_authority"
            ],
            "field_types": {
                "certificate_number": "text",
                "issue_date": "date",
                "exporter_name": "text",
                "country_of_origin": "text",
                "destination_country": "text"
            }
        },
        validation_rules={
            "certificate_number": {
                "required": True,
                "max_length": 50
            },
            "country_of_origin": {
                "required": True,
                "max_length": 50
            }
        },
        extraction_prompts={
            "certificate_number": "Look for certificate number, cert number, or reference",
            "country_of_origin": "Find the country of origin or manufacturing country",
            "issuing_authority": "Look for issuing authority, chamber of commerce, or certifying body"
        },
        created_by="system",
        version="1.0"
    )
    
    # Add templates to session
    session.add(commercial_invoice_template)
    session.add(packing_list_template)
    session.add(bill_of_lading_template)
    session.add(certificate_template)
    
    logger.info("Added 4 default processing templates")


async def rollback_migration():
    """Rollback the AI document processing migration."""
    
    engine = create_async_engine(get_database_url(), echo=True)
    
    try:
        async with engine.begin() as conn:
            # Drop the tables in reverse order (due to foreign key constraints)
            await conn.execute(text("DROP TABLE IF EXISTS extracted_fields CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS processing_templates CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS ai_document_processing CASCADE"))
            
            logger.info("AI document processing tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("Rolling back AI document processing migration...")
        asyncio.run(rollback_migration())
        print("Rollback completed")
    else:
        print("Running AI document processing migration...")
        asyncio.run(run_migration())
        print("Migration completed")