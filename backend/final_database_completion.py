"""
Final Database Completion Script
===============================
Complete the database population using the exact schemas.
"""

import sqlite3
from datetime import datetime, date
import json

def complete_database():
    """Complete database population with correct schemas."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== FINAL DATABASE COMPLETION ===\n")
        
        # 1. Complete tariff sections (21 total)
        print("Completing tariff sections...")
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
        
        # 2. Complete tariff chapters (97 total)
        print("Completing tariff chapters...")
        chapters_data = [
            (30, 3, "Pharmaceutical products"),
            (31, 3, "Fertilisers"),
            (32, 3, "Tanning or dyeing extracts"),
            (33, 3, "Essential oils and resinoids"),
            (34, 3, "Soap, organic surface-active agents"),
            (35, 3, "Albuminoidal substances"),
            (36, 3, "Explosives; pyrotechnic products"),
            (37, 3, "Photographic or cinematographic goods"),
            (38, 3, "Miscellaneous chemical products"),
            (39, 4, "Plastics and articles thereof"),
            (40, 4, "Rubber and articles thereof"),
            (41, 5, "Raw hides and skins"),
            (42, 5, "Articles of leather"),
            (43, 5, "Furskins and artificial fur"),
            (44, 6, "Wood and articles of wood"),
            (45, 6, "Cork and articles of cork"),
            (46, 6, "Manufactures of straw"),
            (47, 7, "Pulp of wood"),
            (48, 7, "Paper and paperboard"),
            (49, 7, "Printed books, newspapers"),
            (50, 8, "Silk"),
            (51, 8, "Wool, fine or coarse animal hair"),
            (52, 8, "Cotton"),
            (53, 8, "Other vegetable textile fibres"),
            (54, 8, "Man-made filaments"),
            (55, 8, "Man-made staple fibres"),
            (56, 8, "Wadding, felt and nonwovens"),
            (57, 8, "Carpets and other textile floor coverings"),
            (58, 8, "Special woven fabrics"),
            (59, 8, "Impregnated, coated, covered or laminated textile fabrics"),
            (60, 8, "Knitted or crocheted fabrics"),
            (61, 8, "Articles of apparel and clothing accessories, knitted or crocheted"),
            (62, 8, "Articles of apparel and clothing accessories, not knitted or crocheted"),
            (63, 8, "Other made up textile articles"),
            (64, 9, "Footwear, gaiters and the like"),
            (65, 9, "Headgear and parts thereof"),
            (66, 9, "Umbrellas, sun umbrellas"),
            (67, 9, "Prepared feathers and down"),
            (68, 10, "Articles of stone, plaster, cement"),
            (69, 10, "Ceramic products"),
            (70, 10, "Glass and glassware"),
            (71, 11, "Natural or cultured pearls"),
            (72, 12, "Iron and steel"),
            (73, 12, "Articles of iron or steel"),
            (74, 12, "Copper and articles thereof"),
            (75, 12, "Nickel and articles thereof"),
            (76, 12, "Aluminium and articles thereof"),
            (78, 12, "Lead and articles thereof"),
            (79, 12, "Zinc and articles thereof"),
            (80, 12, "Tin and articles thereof"),
            (81, 12, "Other base metals"),
            (82, 13, "Tools, implements, cutlery"),
            (83, 13, "Miscellaneous articles of base metal"),
            (84, 14, "Nuclear reactors, boilers, machinery"),
            (85, 14, "Electrical machinery and equipment"),
            (86, 15, "Railway or tramway locomotives"),
            (87, 15, "Vehicles other than railway"),
            (88, 15, "Aircraft, spacecraft"),
            (89, 15, "Ships, boats and floating structures"),
            (90, 16, "Optical, photographic instruments"),
            (91, 16, "Clocks and watches"),
            (92, 16, "Musical instruments"),
            (93, 17, "Arms and ammunition"),
            (94, 18, "Furniture; bedding, mattresses"),
            (95, 18, "Toys, games and sports requisites"),
            (96, 18, "Miscellaneous manufactured articles"),
            (97, 19, "Works of art, collectors' pieces")
        ]
        
        for chapter_data in chapters_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_chapters (chapter_number, section_id, title)
                VALUES (?, ?, ?)
            """, chapter_data)
        
        # 3. Add more tariff codes for comprehensive coverage
        print("Adding comprehensive tariff codes...")
        tariff_codes_data = [
            # Additional 4-digit codes
            ('8703', '87', 4, 'Motor cars and other motor vehicles'),
            ('8704', '87', 4, 'Motor vehicles for transport of goods'),
            ('9001', '90', 4, 'Optical fibres and optical fibre bundles'),
            ('9002', '90', 4, 'Lenses, prisms, mirrors'),
            ('9401', '94', 4, 'Seats'),
            ('9503', '95', 4, 'Tricycles, scooters, pedal cars'),
            ('8471', '84', 4, 'Automatic data processing machines'),
            ('8517', '85', 4, 'Telephone sets'),
            
            # 6-digit codes
            ('870310', '8703', 6, 'Vehicles specially designed for travelling on snow'),
            ('870410', '8704', 6, 'Dumpers designed for off-highway use'),
            ('900110', '9001', 6, 'Optical fibres, optical fibre bundles'),
            ('900211', '9002', 6, 'Objective lenses for cameras'),
            ('940110', '9401', 6, 'Seats of a kind used for aircraft'),
            ('950300', '9503', 6, 'Other toys'),
            ('847130', '8471', 6, 'Portable automatic data processing machines'),
            ('851712', '8517', 6, 'Telephones for cellular networks'),
            
            # 8-digit codes
            ('87031010', '870310', 8, 'Golf cars and similar vehicles'),
            ('87041010', '870410', 8, 'Mining dump trucks'),
            ('90011010', '900110', 8, 'Optical fibres'),
            ('90021110', '900211', 8, 'Camera lenses'),
            ('94011010', '940110', 8, 'Aircraft seats - First class'),
            ('95030010', '950300', 8, 'Electric trains'),
            ('84713010', '847130', 8, 'Laptops and notebooks'),
            ('85171210', '851712', 8, 'Smartphones'),
            
            # 10-digit codes
            ('8703101000', '87031010', 10, 'Golf cars - Complete'),
            ('8704101000', '87041010', 10, 'Mining dump trucks - Over 100 tonnes'),
            ('9001101000', '90011010', 10, 'Optical fibres - Single mode'),
            ('9002111000', '90021110', 10, 'Professional camera lenses'),
            ('9401101000', '94011010', 10, 'Aircraft seats - First class, leather'),
            ('9503001000', '95030010', 10, 'Electric train sets - Complete'),
            ('8471301000', '84713010', 10, 'Professional laptops'),
            ('8517121000', '85171210', 10, 'Premium smartphones')
        ]
        
        for code_data in tariff_codes_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_codes (hs_code, parent_code, level, description)
                VALUES (?, ?, ?, ?)
            """, code_data)
        
        # 4. Add comprehensive duty rates
        print("Adding comprehensive duty rates...")
        duty_rates_data = [
            ('8703101000', 5.0, 'ad val', 'Motor vehicles - Golf cars'),
            ('8704101000', 5.0, 'ad val', 'Mining dump trucks'),
            ('9001101000', 0.0, 'Free', 'Optical equipment'),
            ('9002111000', 0.0, 'Free', 'Professional camera equipment'),
            ('9401101000', 8.0, 'ad val', 'Aircraft furniture'),
            ('9503001000', 0.0, 'Free', 'Toys and games'),
            ('8471301000', 0.0, 'Free', 'Professional laptops'),
            ('8517121000', 0.0, 'Free', 'Premium smartphones'),
            ('8703', 5.0, 'ad val', 'Motor vehicles - general'),
            ('8704', 5.0, 'ad val', 'Commercial vehicles'),
            ('9001', 0.0, 'Free', 'Optical instruments'),
            ('9002', 0.0, 'Free', 'Optical elements'),
            ('9401', 8.0, 'ad val', 'Seating furniture'),
            ('9503', 0.0, 'Free', 'Toys and recreational items'),
            ('8471', 0.0, 'Free', 'Computer equipment'),
            ('8517', 0.0, 'Free', 'Telecommunications equipment')
        ]
        
        for duty_data in duty_rates_data:
            cursor.execute("""
                INSERT OR IGNORE INTO duty_rates (hs_code, general_rate, unit_type, rate_text)
                VALUES (?, ?, ?, ?)
            """, duty_data)
        
        # 5. Add export codes (correct schema)
        print("Adding export codes...")
        export_codes_data = [
            ('0701', 'Potatoes, fresh or chilled', 'kg', '0701'),
            ('070110', 'Seed potatoes', 'kg', '070110'),
            ('07011010', 'Certified seed potatoes', 'kg', '07011010'),
            ('1001', 'Wheat and meslin', 'tonnes', '1001'),
            ('100110', 'Durum wheat', 'tonnes', '100110'),
            ('10011010', 'Durum wheat for human consumption', 'tonnes', '10011010'),
            ('2601', 'Iron ores and concentrates', 'tonnes', '2601'),
            ('260111', 'Non-agglomerated iron ores', 'tonnes', '260111'),
            ('26011110', 'Iron ore with Fe content >= 62%', 'tonnes', '26011110'),
            ('7108', 'Gold', 'kg', '7108'),
            ('710812', 'Gold in other unwrought forms', 'kg', '710812'),
            ('71081210', 'Gold bars and ingots', 'kg', '71081210')
        ]
        
        for export_data in export_codes_data:
            cursor.execute("""
                INSERT OR IGNORE INTO export_codes (ahecc_code, description, statistical_unit, corresponding_import_code)
                VALUES (?, ?, ?, ?)
            """, export_data)
        
        # 6. Add TCOs (correct schema)
        print("Adding TCOs...")
        tco_data = [
            ('TCO-2024-008', '8703101000', 'Golf cars, electric, for resort use', 'Resort Holdings Pty Ltd', date.today(), date(2025, 12, 31), date.today(), 'G2024-001', 'No substitutable goods available', True),
            ('TCO-2024-009', '9001101000', 'Optical fibres for telecommunications', 'Telstra Corporation', date.today(), date(2026, 6, 30), date.today(), 'G2024-002', 'Specialized telecommunications grade', True),
            ('TCO-2024-010', '9401101000', 'Aircraft seats, premium class', 'Qantas Airways Ltd', date.today(), date(2025, 6, 30), date.today(), 'G2024-003', 'Premium aircraft seating', True)
        ]
        
        for tco in tco_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tcos (tco_number, hs_code, description, applicant_name, effective_date, expiry_date, gazette_date, gazette_number, substitutable_goods_determination, is_current)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tco)
        
        # 7. Add analytics data (correct schemas)
        print("Adding analytics data...")
        
        # News analytics
        news_analytics_data = [
            (date.today(), 25, json.dumps({"trade": 8, "tariffs": 7, "customs": 10}), json.dumps({"ABF": 12, "Industry": 8, "Media": 5}), json.dumps(["trade war", "tariffs", "china"])),
            (date(2024, 5, 30), 18, json.dumps({"trade": 6, "fta": 5, "exports": 7}), json.dumps({"ABF": 8, "Industry": 6, "Media": 4}), json.dumps(["fta", "agreement", "india"])),
            (date(2024, 5, 29), 22, json.dumps({"dumping": 8, "steel": 6, "investigation": 8}), json.dumps({"ABF": 10, "Industry": 7, "Media": 5}), json.dumps(["dumping", "steel", "china"]))
        ]
        
        for analytics in news_analytics_data:
            cursor.execute("""
                INSERT OR IGNORE INTO news_analytics (date, total_articles, categories_breakdown, sources_breakdown, trending_topics)
                VALUES (?, ?, ?, ?, ?)
            """, analytics)
        
        # Regulatory updates
        regulatory_data = [
            ('REG-2024-001', 'Updated Steel Tariff Rates', 'Revised anti-dumping duties on steel imports', 'Tariffs', 'Rate Change', date.today(), date.today(), json.dumps(['7208', '7209', '7210']), 'High', 'Steel tariff update'),
            ('REG-2024-002', 'New Vehicle Import Standards', 'Updated safety standards for motor vehicles', 'Standards', 'New Requirement', date(2024, 7, 1), date(2024, 7, 1), json.dumps(['8703', '8704', '8705']), 'Medium', 'Vehicle standards update'),
            ('REG-2024-003', 'Electronics Compliance Update', 'New electromagnetic compatibility requirements', 'Compliance', 'Standard Update', date(2024, 8, 1), date(2024, 8, 1), json.dumps(['8471', '8517', '8518']), 'Medium', 'Electronics compliance')
        ]
        
        for regulatory in regulatory_data:
            cursor.execute("""
                INSERT OR IGNORE INTO regulatory_updates (id, title, description, category, update_type, published_date, effective_date, affected_codes, impact_level, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, regulatory)
        
        # Ruling statistics
        statistics_data = [
            ('2024-Q1', date(2024, 1, 1), date(2024, 3, 31), 156, 142, 14, 8, 12, 5, json.dumps({"classification": 89, "tariff": 67}), json.dumps({"high": 25, "medium": 89, "low": 42})),
            ('2024-Q2', date(2024, 4, 1), date(2024, 6, 30), 142, 135, 12, 5, 8, 3, json.dumps({"classification": 78, "tariff": 64}), json.dumps({"high": 18, "medium": 82, "low": 42})),
            ('2023-Q4', date(2023, 10, 1), date(2023, 12, 31), 168, 158, 18, 10, 15, 7, json.dumps({"classification": 95, "tariff": 73}), json.dumps({"high": 32, "medium": 98, "low": 38}))
        ]
        
        for stats in statistics_data:
            cursor.execute("""
                INSERT OR IGNORE INTO ruling_statistics (period, period_start, period_end, total_rulings, active_rulings, new_rulings, superseded_rulings, anti_dumping_cases, regulatory_updates, category_breakdown, impact_level_breakdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, stats)
        
        conn.commit()
        print("\n✅ DATABASE COMPLETION SUCCESSFUL!")
        
        # Final verification
        print("\n=== FINAL DATABASE STATUS ===")
        
        tables_to_check = [
            ('tariff_sections', 21), ('tariff_chapters', 97), ('tariff_codes', 120),
            ('duty_rates', 56), ('export_codes', 35), ('tcos', 10),
            ('news_analytics', 3), ('regulatory_updates', 3), ('ruling_statistics', 3)
        ]
        
        all_complete = True
        for table, expected in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "✅" if count >= expected else "⚠️"
            if count < expected:
                all_complete = False
            print(f"{table}: {count} records {status}")
        
        if all_complete:
            print(f"\n🎯 DATABASE FULLY POPULATED!")
            print(f"🚀 Frontend ready for comprehensive testing!")
            print(f"✅ User acceptance testing can begin!")
        else:
            print(f"\n⚠️ Some tables may need more data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    complete_database()
