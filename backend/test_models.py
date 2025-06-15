"""Test script to validate the new duty and FTA rate models."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import SQLAlchemy components
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Import database base
from database import Base

# Import all models directly
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter, TradeAgreement
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco

def test_models():
    """Test model creation and relationships."""
    print("🧪 Testing Customs Broker Portal Models")
    print("=" * 50)
    
    # Test model table names
    print("📋 Model Table Names:")
    print(f"  TariffCode: {TariffCode.__tablename__}")
    print(f"  TariffSection: {TariffSection.__tablename__}")
    print(f"  TariffChapter: {TariffChapter.__tablename__}")
    print(f"  TradeAgreement: {TradeAgreement.__tablename__}")
    print(f"  DutyRate: {DutyRate.__tablename__}")
    print(f"  FtaRate: {FtaRate.__tablename__}")
    print(f"  DumpingDuty: {DumpingDuty.__tablename__}")
    print(f"  Tco: {Tco.__tablename__}")
    
    # Test relationships
    print("\n🔗 Model Relationships:")
    print(f"  TariffCode.duty_rates: {hasattr(TariffCode, 'duty_rates')}")
    print(f"  TariffCode.fta_rates: {hasattr(TariffCode, 'fta_rates')}")
    print(f"  TariffCode.dumping_duties: {hasattr(TariffCode, 'dumping_duties')}")
    print(f"  TariffCode.tcos: {hasattr(TariffCode, 'tcos')}")
    print(f"  TradeAgreement.fta_rates: {hasattr(TradeAgreement, 'fta_rates')}")
    print(f"  DutyRate.tariff_code: {hasattr(DutyRate, 'tariff_code')}")
    print(f"  FtaRate.tariff_code: {hasattr(FtaRate, 'tariff_code')}")
    print(f"  FtaRate.trade_agreement: {hasattr(FtaRate, 'trade_agreement')}")
    print(f"  DumpingDuty.tariff_code: {hasattr(DumpingDuty, 'tariff_code')}")
    print(f"  Tco.tariff_code: {hasattr(Tco, 'tariff_code')}")
    
    # Test model creation (in-memory SQLite)
    print("\n🗄️  Testing Model Creation:")
    try:
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        print("  ✅ All tables created successfully!")
        
        # List created tables
        metadata = MetaData()
        metadata.reflect(bind=engine)
        tables = list(metadata.tables.keys())
        print(f"  📊 Created tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        return False
    
    # Test model instantiation
    print("\n🏗️  Testing Model Instantiation:")
    try:
        # Test DutyRate
        duty_rate = DutyRate(
            hs_code="0101010000",
            general_rate=5.0,
            unit_type="ad_valorem",
            rate_text="5%"
        )
        print(f"  ✅ DutyRate: {duty_rate}")
        
        # Test FtaRate
        fta_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=0.0,
            staging_category="A"
        )
        print(f"  ✅ FtaRate: {fta_rate}")
        
        # Test DumpingDuty
        dumping_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_type="dumping",
            duty_rate=15.5,
            case_number="ADC2023-001",
            is_active=True
        )
        print(f"  ✅ DumpingDuty: {dumping_duty}")
        
        # Test Tco
        from datetime import date
        tco = Tco(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            applicant_name="Test Applicant Pty Ltd",
            effective_date=date(2023, 1, 1),
            expiry_date=date(2025, 12, 31),
            is_current=True
        )
        print(f"  ✅ Tco: {tco}")
        
    except Exception as e:
        print(f"  ❌ Error instantiating models: {e}")
        return False
    
    print("\n🎉 All tests passed successfully!")
    return True

if __name__ == "__main__":
    test_models()