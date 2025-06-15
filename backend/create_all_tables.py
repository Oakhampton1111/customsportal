"""
Script to create all database tables explicitly
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from database import Base, create_database_engine

# Import all models to ensure SQLAlchemy is aware of them
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter, TradeAgreement
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.export import ExportCode
from models.classification import ProductClassification
from models.conversation import Conversation, ConversationMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_all_tables():
    """Create all database tables"""
    engine = await create_database_engine()
    
    logger.info("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("All tables created successfully!")
    
    # Verify tables
    async with engine.begin() as conn:
        result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await result.fetchall()
        logger.info(f"Tables created: {[table[0] for table in tables]}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_all_tables())
