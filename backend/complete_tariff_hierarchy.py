"""
Complete Tariff Hierarchy Population
===================================
Populate missing tariff sections, chapters, codes, duty rates, export codes, and TCOs
to ensure comprehensive database for frontend testing.
"""

import sqlite3
from datetime import datetime, date
import json

def populate_complete_hierarchy():
    """Populate complete tariff hierarchy with realistic Australian data."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== COMPLETING TARIFF HIERARCHY ===\n")
        
        # 1. Complete Tariff Sections (21 sections)
        print("Adding missing tariff sections...")
        sections_data = [
            (17, "Vehicles, aircraft, vessels and associated transport equipment", "Chapters 86-89"),
            (18, "Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; clocks and watches; musical instruments; parts and accessories thereof", "Chapters 90-92"),
            (19, "Arms and ammunition; parts and accessories thereof", "Chapter 93"),
            (20, "Miscellaneous manufactured articles", "Chapters 94-96"),
            (21, "Works of art, collectors' pieces and antiques", "Chapter 97")
        ]
        
        for section_data in sections_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_sections (section_number, title, description)
                VALUES (?, ?, ?)
            """, section_data)
        
        # 2. Complete Tariff Chapters (97 chapters)
        print("Adding missing tariff chapters...")
        chapters_data = [
            # Section XVII
            (86, 17, "Railway or tramway locomotives, rolling-stock and parts thereof; railway or tramway track fixtures and fittings and parts thereof; mechanical (including electro-mechanical) traffic signalling equipment of all kinds"),
            (87, 17, "Vehicles other than railway or tramway rolling-stock, and parts and accessories thereof"),
            (88, 17, "Aircraft, spacecraft, and parts thereof"),
            (89, 17, "Ships, boats and floating structures"),
            
            # Section XVIII
            (90, 18, "Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; parts and accessories thereof"),
            (91, 18, "Clocks and watches and parts thereof"),
            (92, 18, "Musical instruments; parts and accessories of such articles"),
            
            # Section XIX
            (93, 19, "Arms and ammunition; parts and accessories thereof"),
            
            # Section XX
            (94, 20, "Furniture; bedding, mattresses, mattress supports, cushions and similar stuffed furnishings; lamps and lighting fittings, not elsewhere specified or included; illuminated signs, illuminated name-plates and the like; prefabricated buildings"),
            (95, 20, "Toys, games and sports requisites; parts and accessories thereof"),
            (96, 20, "Miscellaneous manufactured articles"),
            
            # Section XXI
            (97, 21, "Works of art, collectors' pieces and antiques")
        ]
        
        for chapter_data in chapters_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_chapters (chapter_number, section_id, title)
                VALUES (?, ?, ?)
            """, chapter_data)
        
        # 3. Add more tariff codes for better hierarchy
        print("Adding additional tariff codes...")
        additional_codes = [
            # Chapter 87 - Vehicles
            ('8703', '87', 4, 'Motor cars and other motor vehicles principally designed for the transport of persons'),
            ('870310', '8703', 6, 'Vehicles specially designed for travelling on snow; golf cars and similar vehicles'),
            ('87031010', '870310', 8, 'Golf cars and similar vehicles'),
            ('8703101000', '87031010', 10, 'Golf cars and similar vehicles - Complete'),
            
            # Chapter 90 - Optical instruments
            ('9001', '90', 4, 'Optical fibres and optical fibre bundles; optical fibre cables'),
            ('900110', '9001', 6, 'Optical fibres, optical fibre bundles and cables'),
            ('90011010', '900110', 8, 'Optical fibres'),
            ('9001101000', '90011010', 10, 'Optical fibres - Single mode'),
            
            # Chapter 94 - Furniture
            ('9401', '94', 4, 'Seats (other than those of heading 94.02), whether or not convertible into beds'),
            ('940110', '9401', 6, 'Seats of a kind used for aircraft'),
            ('94011010', '940110', 8, 'Seats of a kind used for aircraft - First class'),
            ('9401101000', '94011010', 10, 'Aircraft seats - First class, leather'),
            
            # Chapter 95 - Toys
            ('9503', '95', 4, 'Tricycles, scooters, pedal cars and similar wheeled toys; dolls carriages'),
            ('950300', '9503', 6, 'Other toys; reduced-size scale models and similar recreational models'),
            ('95030010', '950300', 8, 'Electric trains, including tracks, signals and other accessories'),
            ('9503001000', '95030010', 10, 'Electric train sets - Complete with tracks')
        ]
        
        for code_data in additional_codes:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_codes (hs_code, parent_code, level, description)
                VALUES (?, ?, ?, ?)
            """, code_data)
        
        # 4. Add more duty rates
        print("Adding additional duty rates...")
        duty_rates_data = [
            ('8703101000', 'General', 5.0, 0.0, 10.0, 'Motor vehicles', date.today()),
            ('9001101000', 'General', 0.0, 0.0, 10.0, 'Optical equipment', date.today()),
            ('9401101000', 'General', 8.0, 0.0, 10.0, 'Aircraft furniture', date.today()),
            ('9503001000', 'General', 0.0, 0.0, 10.0, 'Toys and games', date.today()),
            ('8703', 'General', 5.0, 0.0, 10.0, 'Motor vehicles - general', date.today()),
            ('9001', 'General', 0.0, 0.0, 10.0, 'Optical instruments', date.today()),
            ('9401', 'General', 8.0, 0.0, 10.0, 'Seating furniture', date.today()),
            ('9503', 'General', 0.0, 0.0, 10.0, 'Toys and recreational items', date.today())
        ]
        
        for duty_data in duty_rates_data:
            cursor.execute("""
                INSERT OR IGNORE INTO duty_rates (hs_code, rate_type, customs_duty, excise_duty, gst_rate, description, effective_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, duty_data)
        
        # 5. Add more export codes (AHECC)
        print("Adding additional export codes...")
        export_codes_data = [
            ('0701', '07', 4, 'Potatoes, fresh or chilled', 'Vegetables'),
            ('070110', '0701', 6, 'Seed potatoes', 'Seed potatoes for planting'),
            ('07011010', '070110', 8, 'Certified seed potatoes', 'Certified seed potatoes'),
            ('0701101000', '07011010', 10, 'Certified seed potatoes - Class A'),
            
            ('1001', '10', 4, 'Wheat and meslin', 'Cereals'),
            ('100110', '1001', 6, 'Durum wheat', 'Hard wheat varieties'),
            ('10011010', '100110', 8, 'Durum wheat for human consumption', 'Food grade durum'),
            ('1001101000', '10011010', 10, 'Premium durum wheat'),
            
            ('2601', '26', 4, 'Iron ores and concentrates', 'Mineral products'),
            ('260111', '2601', 6, 'Non-agglomerated iron ores and concentrates', 'Raw iron ore'),
            ('26011110', '260111', 8, 'Iron ore with Fe content >= 62%', 'High grade iron ore'),
            ('2601111000', '26011110', 10, 'Premium iron ore - Pilbara grade'),
            
            ('7108', '71', 4, 'Gold (including gold plated with platinum)', 'Precious metals'),
            ('710812', '7108', 6, 'Gold in other unwrought forms', 'Unwrought gold'),
            ('71081210', '710812', 8, 'Gold bars and ingots', 'Investment gold'),
            ('7108121000', '71081210', 10, 'Gold bullion bars - 99.5% purity')
        ]
        
        for export_data in export_codes_data:
            cursor.execute("""
                INSERT OR IGNORE INTO export_codes (ahecc_code, parent_code, level, description, category)
                VALUES (?, ?, ?, ?, ?)
            """, export_data)
        
        # 6. Add more TCOs
        print("Adding additional TCOs...")
        tco_data = [
            ('TCO-2024-008', '8703101000', 'Golf cars, electric, for resort use', 'Granted', 0.0, date.today(), date(2025, 12, 31), 'Tourism industry development'),
            ('TCO-2024-009', '9001101000', 'Optical fibres for telecommunications infrastructure', 'Granted', 0.0, date.today(), date(2026, 6, 30), 'National broadband network'),
            ('TCO-2024-010', '9401101000', 'Aircraft seats, premium class, not manufactured in Australia', 'Under Review', 5.0, date.today(), None, 'Aviation industry support'),
            ('TCO-2024-011', '2601111000', 'Iron ore processing equipment, specialized', 'Granted', 0.0, date.today(), date(2025, 12, 31), 'Mining industry efficiency'),
            ('TCO-2024-012', '7108121000', 'Gold refining equipment, precision', 'Granted', 0.0, date.today(), date(2026, 12, 31), 'Precious metals processing')
        ]
        
        for tco in tco_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tcos (tco_number, hs_code, description, status, duty_rate, effective_date, expiry_date, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, tco)
        
        # 7. Add empty analytics tables data
        print("Adding analytics data...")
        cursor.execute("""
            INSERT OR IGNORE INTO news_analytics (id, date, total_articles, trade_impact_score, sentiment_score, top_keywords, created_at)
            VALUES (1, ?, 25, 7.5, 0.3, ?, ?)
        """, (date.today(), json.dumps(['trade war', 'tariffs', 'china', 'usa', 'steel']), datetime.now()))
        
        cursor.execute("""
            INSERT OR IGNORE INTO regulatory_updates (id, update_id, title, description, effective_date, impact_level, affected_codes, created_at)
            VALUES (1, 'REG-2024-001', 'Updated Steel Tariff Rates', 'Revised anti-dumping duties on steel imports from China', ?, 'High', ?, ?)
        """, (date.today(), json.dumps(['7208', '7209', '7210']), datetime.now()))
        
        cursor.execute("""
            INSERT OR IGNORE INTO ruling_statistics (id, period, total_rulings, classification_rulings, tariff_rulings, avg_processing_days, created_at)
            VALUES (1, '2024-Q1', 156, 89, 67, 28, ?)
        """, (datetime.now(),))
        
        conn.commit()
        print("\n✅ Tariff hierarchy completion successful!")
        
        # Verify the results
        print("\n=== VERIFICATION ===")
        cursor.execute("SELECT COUNT(*) FROM tariff_sections")
        sections = cursor.fetchone()[0]
        print(f"Tariff sections: {sections}")
        
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters")
        chapters = cursor.fetchone()[0]
        print(f"Tariff chapters: {chapters}")
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes")
        codes = cursor.fetchone()[0]
        print(f"Tariff codes: {codes}")
        
        cursor.execute("SELECT COUNT(*) FROM duty_rates")
        duties = cursor.fetchone()[0]
        print(f"Duty rates: {duties}")
        
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        exports = cursor.fetchone()[0]
        print(f"Export codes: {exports}")
        
        cursor.execute("SELECT COUNT(*) FROM tcos")
        tcos = cursor.fetchone()[0]
        print(f"TCOs: {tcos}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_complete_hierarchy()
