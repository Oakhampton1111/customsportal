"""
Populate Comprehensive Database Data
===================================
Add comprehensive data to ensure frontend has enough realistic content for testing.
"""

import sqlite3
from datetime import datetime, date
import json

def populate_comprehensive_data():
    """Populate comprehensive data for all tables."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== POPULATING COMPREHENSIVE DATABASE DATA ===\n")
        
        # 1. Add missing tariff sections (complete 21 sections)
        print("Adding missing tariff sections...")
        sections_data = [
            (17, "Vehicles, aircraft, vessels and associated transport equipment"),
            (18, "Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; clocks and watches; musical instruments; parts and accessories thereof"),
            (19, "Arms and ammunition; parts and accessories thereof"),
            (20, "Miscellaneous manufactured articles"),
            (21, "Works of art, collectors' pieces and antiques")
        ]
        
        for section_data in sections_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_sections (section_number, title)
                VALUES (?, ?)
            """, section_data)
        
        # 2. Add missing tariff chapters
        print("Adding missing tariff chapters...")
        chapters_data = [
            (86, 17, "Railway or tramway locomotives, rolling-stock and parts thereof"),
            (87, 17, "Vehicles other than railway or tramway rolling-stock, and parts and accessories thereof"),
            (88, 17, "Aircraft, spacecraft, and parts thereof"),
            (89, 17, "Ships, boats and floating structures"),
            (90, 18, "Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus"),
            (91, 18, "Clocks and watches and parts thereof"),
            (92, 18, "Musical instruments; parts and accessories of such articles"),
            (93, 19, "Arms and ammunition; parts and accessories thereof"),
            (94, 20, "Furniture; bedding, mattresses, mattress supports, cushions and similar stuffed furnishings"),
            (95, 20, "Toys, games and sports requisites; parts and accessories thereof"),
            (96, 20, "Miscellaneous manufactured articles"),
            (97, 21, "Works of art, collectors' pieces and antiques")
        ]
        
        for chapter_data in chapters_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_chapters (chapter_number, section_id, title)
                VALUES (?, ?, ?)
            """, chapter_data)
        
        # 3. Add more tariff codes for comprehensive hierarchy
        print("Adding comprehensive tariff codes...")
        tariff_codes_data = [
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
            ('9503001000', '95030010', 10, 'Electric train sets - Complete with tracks'),
            
            # Additional codes for better coverage
            ('8704', '87', 4, 'Motor vehicles for the transport of goods'),
            ('870410', '8704', 6, 'Dumpers designed for off-highway use'),
            ('87041010', '870410', 8, 'Mining dump trucks'),
            ('8704101000', '87041010', 10, 'Mining dump trucks - Over 100 tonnes'),
            
            ('9002', '90', 4, 'Lenses, prisms, mirrors and other optical elements'),
            ('900211', '9002', 6, 'Objective lenses for cameras, projectors or photographic enlargers or reducers'),
            ('90021110', '900211', 8, 'Camera lenses'),
            ('9002111000', '90021110', 10, 'Professional camera lenses')
        ]
        
        for code_data in tariff_codes_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_codes (hs_code, parent_code, level, description)
                VALUES (?, ?, ?, ?)
            """, code_data)
        
        # 4. Add more duty rates (using correct schema)
        print("Adding comprehensive duty rates...")
        duty_rates_data = [
            ('8703101000', 5.0, 'ad val', 'Motor vehicles - Golf cars'),
            ('9001101000', 0.0, 'Free', 'Optical equipment - Telecommunications'),
            ('9401101000', 8.0, 'ad val', 'Aircraft furniture - Premium seating'),
            ('9503001000', 0.0, 'Free', 'Toys and games - Electric trains'),
            ('8703', 5.0, 'ad val', 'Motor vehicles - general category'),
            ('9001', 0.0, 'Free', 'Optical instruments - general'),
            ('9401', 8.0, 'ad val', 'Seating furniture - general'),
            ('9503', 0.0, 'Free', 'Toys and recreational items'),
            ('8704101000', 5.0, 'ad val', 'Mining dump trucks'),
            ('9002111000', 0.0, 'Free', 'Professional camera equipment')
        ]
        
        for duty_data in duty_rates_data:
            cursor.execute("""
                INSERT OR IGNORE INTO duty_rates (hs_code, general_rate, unit_type, rate_text)
                VALUES (?, ?, ?, ?)
            """, duty_data)
        
        # 5. Add more export codes (AHECC)
        print("Adding comprehensive export codes...")
        export_codes_data = [
            ('0701', '07', 4, 'Potatoes, fresh or chilled', 'Vegetables'),
            ('070110', '0701', 6, 'Seed potatoes', 'Seeds'),
            ('07011010', '070110', 8, 'Certified seed potatoes', 'Certified seeds'),
            ('0701101000', '07011010', 10, 'Certified seed potatoes - Class A', 'Premium seeds'),
            
            ('1001', '10', 4, 'Wheat and meslin', 'Cereals'),
            ('100110', '1001', 6, 'Durum wheat', 'Hard wheat'),
            ('10011010', '100110', 8, 'Durum wheat for human consumption', 'Food grade'),
            ('1001101000', '10011010', 10, 'Premium durum wheat', 'Premium grade'),
            
            ('2601', '26', 4, 'Iron ores and concentrates', 'Minerals'),
            ('260111', '2601', 6, 'Non-agglomerated iron ores and concentrates', 'Raw ore'),
            ('26011110', '260111', 8, 'Iron ore with Fe content >= 62%', 'High grade'),
            ('2601111000', '26011110', 10, 'Premium iron ore - Pilbara grade', 'Premium ore'),
            
            ('7108', '71', 4, 'Gold (including gold plated with platinum)', 'Precious metals'),
            ('710812', '7108', 6, 'Gold in other unwrought forms', 'Unwrought gold'),
            ('71081210', '710812', 8, 'Gold bars and ingots', 'Investment gold'),
            ('7108121000', '71081210', 10, 'Gold bullion bars - 99.5% purity', 'Bullion')
        ]
        
        for export_data in export_codes_data:
            cursor.execute("""
                INSERT OR IGNORE INTO export_codes (ahecc_code, parent_code, level, description, category)
                VALUES (?, ?, ?, ?, ?)
            """, export_data)
        
        # 6. Add more TCOs
        print("Adding comprehensive TCOs...")
        tco_data = [
            ('TCO-2024-008', '8703101000', 'Golf cars, electric, for resort use', 'Granted', 0.0, date.today(), date(2025, 12, 31), 'Tourism industry development'),
            ('TCO-2024-009', '9001101000', 'Optical fibres for telecommunications infrastructure', 'Granted', 0.0, date.today(), date(2026, 6, 30), 'National broadband network'),
            ('TCO-2024-010', '9401101000', 'Aircraft seats, premium class, not manufactured in Australia', 'Under Review', 5.0, date.today(), None, 'Aviation industry support'),
            ('TCO-2024-011', '2601111000', 'Iron ore processing equipment, specialized', 'Granted', 0.0, date.today(), date(2025, 12, 31), 'Mining industry efficiency'),
            ('TCO-2024-012', '7108121000', 'Gold refining equipment, precision', 'Granted', 0.0, date.today(), date(2026, 12, 31), 'Precious metals processing'),
            ('TCO-2024-013', '8704101000', 'Mining equipment, autonomous vehicles', 'Granted', 0.0, date.today(), date(2025, 6, 30), 'Mining automation'),
            ('TCO-2024-014', '9002111000', 'Scientific camera lenses for research', 'Granted', 0.0, date.today(), date(2026, 12, 31), 'Scientific research')
        ]
        
        for tco in tco_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tcos (tco_number, hs_code, description, status, duty_rate, effective_date, expiry_date, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, tco)
        
        # 7. Add analytics data for completeness
        print("Adding analytics and statistics data...")
        
        # News analytics
        cursor.execute("""
            INSERT OR IGNORE INTO news_analytics (id, date, total_articles, trade_impact_score, sentiment_score, top_keywords, created_at)
            VALUES (1, ?, 25, 7.5, 0.3, ?, ?)
        """, (date.today(), json.dumps(['trade war', 'tariffs', 'china', 'usa', 'steel']), datetime.now()))
        
        cursor.execute("""
            INSERT OR IGNORE INTO news_analytics (id, date, total_articles, trade_impact_score, sentiment_score, top_keywords, created_at)
            VALUES (2, ?, 18, 6.2, 0.1, ?, ?)
        """, (date(2024, 5, 30), json.dumps(['fta', 'agreement', 'india', 'exports', 'agriculture']), datetime.now()))
        
        # Regulatory updates
        cursor.execute("""
            INSERT OR IGNORE INTO regulatory_updates (id, update_id, title, description, effective_date, impact_level, affected_codes, created_at)
            VALUES (1, 'REG-2024-001', 'Updated Steel Tariff Rates', 'Revised anti-dumping duties on steel imports from China', ?, 'High', ?, ?)
        """, (date.today(), json.dumps(['7208', '7209', '7210']), datetime.now()))
        
        cursor.execute("""
            INSERT OR IGNORE INTO regulatory_updates (id, update_id, title, description, effective_date, impact_level, affected_codes, created_at)
            VALUES (2, 'REG-2024-002', 'New Vehicle Import Standards', 'Updated safety standards for motor vehicle imports', ?, 'Medium', ?, ?)
        """, (date(2024, 7, 1), json.dumps(['8703', '8704', '8705']), datetime.now()))
        
        # Ruling statistics
        cursor.execute("""
            INSERT OR IGNORE INTO ruling_statistics (id, period, total_rulings, classification_rulings, tariff_rulings, avg_processing_days, created_at)
            VALUES (1, '2024-Q1', 156, 89, 67, 28, ?)
        """, (datetime.now(),))
        
        cursor.execute("""
            INSERT OR IGNORE INTO ruling_statistics (id, period, total_rulings, classification_rulings, tariff_rulings, avg_processing_days, created_at)
            VALUES (2, '2024-Q2', 142, 78, 64, 25, ?)
        """, (datetime.now(),))
        
        conn.commit()
        print("\n✅ Comprehensive data population successful!")
        
        # Verify the results
        print("\n=== FINAL VERIFICATION ===")
        
        tables_to_check = [
            'tariff_sections', 'tariff_chapters', 'tariff_codes', 'duty_rates',
            'export_codes', 'tcos', 'news_analytics', 'regulatory_updates', 'ruling_statistics'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
        
        print(f"\n🎯 Database now has comprehensive data for frontend testing!")
        print(f"🚀 Ready for full system integration and user acceptance testing!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_comprehensive_data()
