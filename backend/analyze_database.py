#!/usr/bin/env python3
"""
Comprehensive database analysis script to understand current data state
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import get_settings

async def analyze_database():
    """Analyze database content in detail."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            print("=== CUSTOMS BROKER PORTAL DATABASE ANALYSIS ===\n")
            
            # 1. Table structure and counts
            print("1. TABLE OVERVIEW:")
            tables_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
            result = await conn.execute(text(tables_query))
            tables = [row[0] for row in result.fetchall()]
            
            table_counts = {}
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                table_counts[table] = count
                status = "✅ HAS DATA" if count > 0 else "❌ EMPTY"
                print(f"  {table}: {count} records {status}")
            
            # 2. Tariff hierarchy analysis
            print("\n2. TARIFF HIERARCHY ANALYSIS:")
            if table_counts.get('tariff_sections', 0) > 0:
                result = await conn.execute(text("""
                    SELECT section_number, description 
                    FROM tariff_sections 
                    ORDER BY section_number 
                    LIMIT 5
                """))
                print("  Sections (sample):")
                for row in result.fetchall():
                    print(f"    Section {row[0]}: {row[1][:60]}...")
            else:
                print("  ❌ No tariff sections found")
            
            if table_counts.get('tariff_chapters', 0) > 0:
                result = await conn.execute(text("""
                    SELECT chapter_number, title 
                    FROM tariff_chapters 
                    ORDER BY chapter_number 
                    LIMIT 5
                """))
                print("  Chapters (sample):")
                for row in result.fetchall():
                    print(f"    Chapter {row[0]}: {row[1][:60]}...")
            else:
                print("  ❌ No tariff chapters found")
            
            # 3. Tariff codes by level
            print("\n3. TARIFF CODE LEVELS:")
            if table_counts.get('tariff_codes', 0) > 0:
                for level in [2, 4, 6, 8, 10]:
                    result = await conn.execute(text(f"""
                        SELECT COUNT(*) FROM tariff_codes WHERE level = {level}
                    """))
                    count = result.scalar()
                    print(f"  Level {level}: {count} codes")
                
                # Sample codes at each level
                print("\n  Sample codes by level:")
                for level in [2, 4, 6, 8, 10]:
                    result = await conn.execute(text(f"""
                        SELECT hs_code, description 
                        FROM tariff_codes 
                        WHERE level = {level} 
                        ORDER BY hs_code 
                        LIMIT 2
                    """))
                    for row in result.fetchall():
                        print(f"    L{level}: {row[0]} - {row[1][:50]}...")
            else:
                print("  ❌ No tariff codes found")
            
            # 4. Duty rates analysis
            print("\n4. DUTY RATES ANALYSIS:")
            if table_counts.get('duty_rates', 0) > 0:
                result = await conn.execute(text("""
                    SELECT hs_code, general_rate, rate_text 
                    FROM duty_rates 
                    ORDER BY hs_code 
                    LIMIT 5
                """))
                print("  Sample duty rates:")
                for row in result.fetchall():
                    print(f"    {row[0]}: General={row[1]}, Rate Text={row[2]}")
            else:
                print("  ❌ No duty rates found")
            
            # 5. FTA rates analysis
            print("\n5. FTA RATES ANALYSIS:")
            if table_counts.get('fta_rates', 0) > 0:
                result = await conn.execute(text("""
                    SELECT agreement_code, hs_code, rate 
                    FROM fta_rates 
                    LIMIT 5
                """))
                print("  Sample FTA rates:")
                for row in result.fetchall():
                    print(f"    {row[0]} - {row[1]}: {row[2]}")
            else:
                print("  ❌ No FTA rates found - NEEDS POPULATION")
            
            # 6. Trade agreements
            print("\n6. TRADE AGREEMENTS:")
            if table_counts.get('trade_agreements', 0) > 0:
                result = await conn.execute(text("""
                    SELECT agreement_code, name, status 
                    FROM trade_agreements 
                    LIMIT 5
                """))
                print("  Sample agreements:")
                for row in result.fetchall():
                    print(f"    {row[0]}: {row[1]} ({row[2]})")
            else:
                print("  ❌ No trade agreements found - NEEDS POPULATION")
            
            # 7. Export codes
            print("\n7. EXPORT CODES (AHECC):")
            if table_counts.get('export_codes', 0) > 0:
                result = await conn.execute(text("""
                    SELECT ahecc_code, description, level 
                    FROM export_codes 
                    ORDER BY ahecc_code 
                    LIMIT 5
                """))
                print("  Sample export codes:")
                for row in result.fetchall():
                    print(f"    {row[0]} (L{row[2]}): {row[1][:50]}...")
            else:
                print("  ❌ No export codes found - NEEDS POPULATION")
            
            # 8. Other tables
            print("\n8. OTHER TABLES:")
            other_tables = ['dumping_duties', 'tcos', 'gst_provisions', 'product_classifications', 'conversations']
            for table in other_tables:
                if table in table_counts:
                    count = table_counts[table]
                    status = "✅ HAS DATA" if count > 0 else "❌ EMPTY - NEEDS POPULATION"
                    print(f"  {table}: {count} records {status}")
            
            # 9. Summary and recommendations
            print("\n9. SUMMARY & RECOMMENDATIONS:")
            print("  ✅ POPULATED TABLES:")
            for table, count in table_counts.items():
                if count > 0:
                    print(f"    - {table}: {count} records")
            
            print("\n  ❌ EMPTY TABLES NEEDING POPULATION:")
            empty_tables = [table for table, count in table_counts.items() if count == 0]
            for table in empty_tables:
                print(f"    - {table}")
            
            # 10. Tree functionality assessment
            print("\n10. TREE FUNCTIONALITY ASSESSMENT:")
            tariff_codes_count = table_counts.get('tariff_codes', 0)
            sections_count = table_counts.get('tariff_sections', 0)
            chapters_count = table_counts.get('tariff_chapters', 0)
            
            if tariff_codes_count >= 50 and sections_count > 0 and chapters_count > 0:
                print("  ✅ SUFFICIENT DATA for tariff tree functionality")
                print(f"    - {sections_count} sections, {chapters_count} chapters, {tariff_codes_count} codes")
            else:
                print("  ⚠️  INSUFFICIENT DATA for full tree functionality")
                print(f"    - Need more sections ({sections_count}), chapters ({chapters_count}), or codes ({tariff_codes_count})")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(analyze_database())
