"""Quick validation of model imports."""
try:
    from models import TariffCode, TariffSection, TariffChapter, TradeAgreement, DutyRate, FtaRate
    print("✅ All model imports successful!")
    print(f"TariffCode table: {TariffCode.__tablename__}")
    print(f"TariffSection table: {TariffSection.__tablename__}")
    print(f"TariffChapter table: {TariffChapter.__tablename__}")
    print(f"TradeAgreement table: {TradeAgreement.__tablename__}")
    print(f"DutyRate table: {DutyRate.__tablename__}")
    print(f"FtaRate table: {FtaRate.__tablename__}")
    
    # Test relationships
    print("\n✅ Testing relationships:")
    print(f"TariffCode.duty_rates: {hasattr(TariffCode, 'duty_rates')}")
    print(f"TariffCode.fta_rates: {hasattr(TariffCode, 'fta_rates')}")
    print(f"TradeAgreement.fta_rates: {hasattr(TradeAgreement, 'fta_rates')}")
    print(f"DutyRate.tariff_code: {hasattr(DutyRate, 'tariff_code')}")
    print(f"FtaRate.tariff_code: {hasattr(FtaRate, 'tariff_code')}")
    print(f"FtaRate.trade_agreement: {hasattr(FtaRate, 'trade_agreement')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()