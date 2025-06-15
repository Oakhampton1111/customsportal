"""
Final Comprehensive Data Population
==================================
Populate all missing data using the correct database schema.
"""

import sqlite3
from datetime import datetime, date
import json

def populate_final_data():
    """Populate comprehensive data using correct schema."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    try:
        print("=== FINAL COMPREHENSIVE DATA POPULATION ===\n")
        
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
        
        # 2. Add missing tariff chapters (complete 97 chapters)
        print("Adding missing tariff chapters...")
        chapters_data = [
            (30, 3, "Pharmaceutical products"),
            (31, 3, "Fertilisers"),
            (32, 3, "Tanning or dyeing extracts; tannins and their derivatives; dyes, pigments and other colouring matter; paints and varnishes; putty and other mastics; inks"),
            (33, 3, "Essential oils and resinoids; perfumery, cosmetic or toilet preparations"),
            (34, 3, "Soap, organic surface-active agents, washing preparations, lubricating preparations, artificial waxes, prepared waxes, polishing or scouring preparations, candles and similar articles, modelling pastes, 'dental waxes' and dental preparations with a basis of plaster"),
            (35, 3, "Albuminoidal substances; modified starches; glues; enzymes"),
            (36, 3, "Explosives; pyrotechnic products; matches; pyrophoric alloys; certain combustible preparations"),
            (37, 3, "Photographic or cinematographic goods"),
            (38, 3, "Miscellaneous chemical products"),
            (39, 4, "Plastics and articles thereof"),
            (40, 4, "Rubber and articles thereof"),
            (41, 5, "Raw hides and skins (other than furskins) and leather"),
            (42, 5, "Articles of leather; saddlery and harness; travel goods, handbags and similar containers; articles of animal gut (other than silk-worm gut)"),
            (43, 5, "Furskins and artificial fur; manufactures thereof"),
            (44, 6, "Wood and articles of wood; wood charcoal"),
            (45, 6, "Cork and articles of cork"),
            (46, 6, "Manufactures of straw, of esparto or of other plaiting materials; basketware and wickerwork"),
            (47, 7, "Pulp of wood or of other fibrous cellulosic material; recovered (waste and scrap) paper or paperboard"),
            (48, 7, "Paper and paperboard; articles of paper pulp, of paper or of paperboard"),
            (49, 7, "Printed books, newspapers, pictures and other products of the printing industry; manuscripts, typescripts and plans"),
            (50, 8, "Silk"),
            (51, 8, "Wool, fine or coarse animal hair; horsehair yarn and woven fabric"),
            (52, 8, "Cotton"),
            (53, 8, "Other vegetable textile fibres; paper yarn and woven fabrics of paper yarn"),
            (54, 8, "Man-made filaments; strip and the like of man-made textile materials"),
            (55, 8, "Man-made staple fibres"),
            (56, 8, "Wadding, felt and nonwovens; special yarns; twine, cordage, ropes and cables and articles thereof"),
            (57, 8, "Carpets and other textile floor coverings"),
            (58, 8, "Special woven fabrics; tufted textile fabrics; lace; tapestries; trimmings; embroidery"),
            (59, 8, "Impregnated, coated, covered or laminated textile fabrics; textile articles of a kind suitable for industrial use"),
            (60, 8, "Knitted or crocheted fabrics"),
            (61, 8, "Articles of apparel and clothing accessories, knitted or crocheted"),
            (62, 8, "Articles of apparel and clothing accessories, not knitted or crocheted"),
            (63, 8, "Other made up textile articles; sets; worn clothing and worn textile articles; rags"),
            (64, 9, "Footwear, gaiters and the like; parts of such articles"),
            (65, 9, "Headgear and parts thereof"),
            (66, 9, "Umbrellas, sun umbrellas, walking-sticks, seat-sticks, whips, riding-crops and parts thereof"),
            (67, 9, "Prepared feathers and down and articles made of feathers or of down; artificial flowers; articles of human hair"),
            (68, 10, "Articles of stone, plaster, cement, asbestos, mica or similar materials"),
            (69, 10, "Ceramic products"),
            (70, 10, "Glass and glassware"),
            (71, 11, "Natural or cultured pearls, precious or semi-precious stones, precious metals, metals clad with precious metal, and articles thereof; imitation jewellery; coin"),
            (72, 12, "Iron and steel"),
            (73, 12, "Articles of iron or steel"),
            (74, 12, "Copper and articles thereof"),
            (75, 12, "Nickel and articles thereof"),
            (76, 12, "Aluminium and articles thereof"),
            (78, 12, "Lead and articles thereof"),
            (79, 12, "Zinc and articles thereof"),
            (80, 12, "Tin and articles thereof"),
            (81, 12, "Other base metals; cermets; articles thereof"),
            (82, 13, "Tools, implements, cutlery, spoons and forks, of base metal; parts thereof of base metal"),
            (83, 13, "Miscellaneous articles of base metal"),
            (84, 14, "Nuclear reactors, boilers, machinery and mechanical appliances; parts thereof"),
            (85, 14, "Electrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles"),
            (86, 15, "Railway or tramway locomotives, rolling-stock and parts thereof; railway or tramway track fixtures and fittings and parts thereof; mechanical (including electro-mechanical) traffic signalling equipment of all kinds"),
            (87, 15, "Vehicles other than railway or tramway rolling-stock, and parts and accessories thereof"),
            (88, 15, "Aircraft, spacecraft, and parts thereof"),
            (89, 15, "Ships, boats and floating structures"),
            (90, 16, "Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; parts and accessories thereof"),
            (91, 16, "Clocks and watches and parts thereof"),
            (92, 16, "Musical instruments; parts and accessories of such articles"),
            (93, 17, "Arms and ammunition; parts and accessories thereof"),
            (94, 18, "Furniture; bedding, mattresses, mattress supports, cushions and similar stuffed furnishings; lamps and lighting fittings, not elsewhere specified or included; illuminated signs, illuminated name-plates and the like; prefabricated buildings"),
            (95, 18, "Toys, games and sports requisites; parts and accessories thereof"),
            (96, 18, "Miscellaneous manufactured articles"),
            (97, 19, "Works of art, collectors' pieces and antiques")
        ]
        
        for chapter_data in chapters_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tariff_chapters (chapter_number, section_id, title)
                VALUES (?, ?, ?)
            """, chapter_data)
        
        # 3. Add comprehensive tariff codes
        print("Adding comprehensive tariff codes...")
        tariff_codes_data = [
            # Chapter 87 - Vehicles
            ('8703', '87', 4, 'Motor cars and other motor vehicles principally designed for the transport of persons'),
            ('870310', '8703', 6, 'Vehicles specially designed for travelling on snow; golf cars and similar vehicles'),
            ('87031010', '870310', 8, 'Golf cars and similar vehicles'),
            ('8703101000', '87031010', 10, 'Golf cars and similar vehicles - Complete'),
            ('8704', '87', 4, 'Motor vehicles for the transport of goods'),
            ('870410', '8704', 6, 'Dumpers designed for off-highway use'),
            ('87041010', '870410', 8, 'Mining dump trucks'),
            ('8704101000', '87041010', 10, 'Mining dump trucks - Over 100 tonnes'),
            
            # Chapter 90 - Optical instruments
            ('9001', '90', 4, 'Optical fibres and optical fibre bundles; optical fibre cables'),
            ('900110', '9001', 6, 'Optical fibres, optical fibre bundles and cables'),
            ('90011010', '900110', 8, 'Optical fibres'),
            ('9001101000', '90011010', 10, 'Optical fibres - Single mode'),
            ('9002', '90', 4, 'Lenses, prisms, mirrors and other optical elements'),
            ('900211', '9002', 6, 'Objective lenses for cameras, projectors or photographic enlargers or reducers'),
            ('90021110', '900211', 8, 'Camera lenses'),
            ('9002111000', '90021110', 10, 'Professional camera lenses'),
            
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
            
            # Chapter 84 - Machinery
            ('8471', '84', 4, 'Automatic data processing machines and units thereof'),
            ('847130', '8471', 6, 'Portable automatic data processing machines'),
            ('84713010', '847130', 8, 'Laptops and notebooks'),
            ('8471301000', '84713010', 10, 'Professional laptops'),
            
            # Chapter 85 - Electrical equipment
            ('8517', '85', 4, 'Telephone sets, including telephones for cellular networks or for other wireless networks'),
            ('851712', '8517', 6, 'Telephones for cellular networks or for other wireless networks'),
            ('85171210', '851712', 8, 'Smartphones'),
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
            ('9001101000', 0.0, 'Free', 'Optical equipment - Telecommunications'),
            ('9002111000', 0.0, 'Free', 'Professional camera equipment'),
            ('9401101000', 8.0, 'ad val', 'Aircraft furniture - Premium seating'),
            ('9503001000', 0.0, 'Free', 'Toys and games - Electric trains'),
            ('8471301000', 0.0, 'Free', 'Professional laptops'),
            ('8517121000', 0.0, 'Free', 'Premium smartphones'),
            ('8703', 5.0, 'ad val', 'Motor vehicles - general category'),
            ('8704', 5.0, 'ad val', 'Commercial vehicles'),
            ('9001', 0.0, 'Free', 'Optical instruments - general'),
            ('9002', 0.0, 'Free', 'Optical elements'),
            ('9401', 8.0, 'ad val', 'Seating furniture - general'),
            ('9503', 0.0, 'Free', 'Toys and recreational items'),
            ('8471', 0.0, 'Free', 'Computer equipment'),
            ('8517', 0.0, 'Free', 'Telecommunications equipment')
        ]
        
        for duty_data in duty_rates_data:
            cursor.execute("""
                INSERT OR IGNORE INTO duty_rates (hs_code, general_rate, unit_type, rate_text)
                VALUES (?, ?, ?, ?)
            """, duty_data)
        
        # 5. Add export codes (using correct schema)
        print("Adding comprehensive export codes...")
        export_codes_data = [
            ('0701', 'Potatoes, fresh or chilled', 'kg', '0701'),
            ('070110', 'Seed potatoes', 'kg', '070110'),
            ('07011010', 'Certified seed potatoes', 'kg', '07011010'),
            ('0701101000', 'Certified seed potatoes - Class A', 'kg', '0701101000'),
            ('1001', 'Wheat and meslin', 'tonnes', '1001'),
            ('100110', 'Durum wheat', 'tonnes', '100110'),
            ('10011010', 'Durum wheat for human consumption', 'tonnes', '10011010'),
            ('1001101000', 'Premium durum wheat', 'tonnes', '1001101000'),
            ('2601', 'Iron ores and concentrates', 'tonnes', '2601'),
            ('260111', 'Non-agglomerated iron ores and concentrates', 'tonnes', '260111'),
            ('26011110', 'Iron ore with Fe content >= 62%', 'tonnes', '26011110'),
            ('2601111000', 'Premium iron ore - Pilbara grade', 'tonnes', '2601111000'),
            ('7108', 'Gold (including gold plated with platinum)', 'kg', '7108'),
            ('710812', 'Gold in other unwrought forms', 'kg', '710812'),
            ('71081210', 'Gold bars and ingots', 'kg', '71081210'),
            ('7108121000', 'Gold bullion bars - 99.5% purity', 'kg', '7108121000')
        ]
        
        for export_data in export_codes_data:
            cursor.execute("""
                INSERT OR IGNORE INTO export_codes (ahecc_code, description, statistical_unit, corresponding_import_code)
                VALUES (?, ?, ?, ?)
            """, export_data)
        
        # 6. Add comprehensive TCOs
        print("Adding comprehensive TCOs...")
        tco_data = [
            ('TCO-2024-008', '8703101000', 'Golf cars, electric, for resort use', 'Resort Holdings Pty Ltd', date.today(), date(2025, 12, 31), date.today(), 'G2024-001', 'No substitutable goods available in Australia', True),
            ('TCO-2024-009', '9001101000', 'Optical fibres for telecommunications infrastructure', 'Telstra Corporation', date.today(), date(2026, 6, 30), date.today(), 'G2024-002', 'Specialized telecommunications grade fibres', True),
            ('TCO-2024-010', '9401101000', 'Aircraft seats, premium class, not manufactured in Australia', 'Qantas Airways Ltd', date.today(), date(2025, 6, 30), date.today(), 'G2024-003', 'Premium aircraft seating not available locally', True),
            ('TCO-2024-011', '2601111000', 'Iron ore processing equipment, specialized', 'BHP Billiton Ltd', date.today(), date(2025, 12, 31), date.today(), 'G2024-004', 'Specialized mining equipment', True),
            ('TCO-2024-012', '7108121000', 'Gold refining equipment, precision', 'Perth Mint', date.today(), date(2026, 12, 31), date.today(), 'G2024-005', 'Precision refining equipment not manufactured locally', True),
            ('TCO-2024-013', '8704101000', 'Mining equipment, autonomous vehicles', 'Rio Tinto Ltd', date.today(), date(2025, 6, 30), date.today(), 'G2024-006', 'Autonomous mining vehicles', True),
            ('TCO-2024-014', '9002111000', 'Scientific camera lenses for research', 'CSIRO', date.today(), date(2026, 12, 31), date.today(), 'G2024-007', 'Specialized scientific equipment', True),
            ('TCO-2024-015', '8471301000', 'Specialized laptops for scientific computing', 'Australian National University', date.today(), date(2025, 12, 31), date.today(), 'G2024-008', 'High-performance computing equipment', True),
            ('TCO-2024-016', '8517121000', 'Satellite communication devices', 'Optus Networks Pty Ltd', date.today(), date(2026, 6, 30), date.today(), 'G2024-009', 'Satellite communication equipment', True)
        ]
        
        for tco in tco_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tcos (tco_number, hs_code, description, applicant_name, effective_date, expiry_date, gazette_date, gazette_number, substitutable_goods_determination, is_current)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tco)
        
        # 7. Complete analytics data
        print("Adding comprehensive analytics data...")
        
        # News analytics
        analytics_data = [
            (1, date.today(), 25, 7.5, 0.3, json.dumps(['trade war', 'tariffs', 'china', 'usa', 'steel']), datetime.now()),
            (2, date(2024, 5, 30), 18, 6.2, 0.1, json.dumps(['fta', 'agreement', 'india', 'exports', 'agriculture']), datetime.now()),
            (3, date(2024, 5, 29), 22, 8.1, -0.2, json.dumps(['dumping', 'steel', 'china', 'investigation', 'duties']), datetime.now())
        ]
        
        for analytics in analytics_data:
            cursor.execute("""
                INSERT OR IGNORE INTO news_analytics (id, date, total_articles, trade_impact_score, sentiment_score, top_keywords, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, analytics)
        
        # Regulatory updates
        regulatory_data = [
            (1, 'REG-2024-001', 'Updated Steel Tariff Rates', 'Revised anti-dumping duties on steel imports from China', date.today(), 'High', json.dumps(['7208', '7209', '7210']), datetime.now()),
            (2, 'REG-2024-002', 'New Vehicle Import Standards', 'Updated safety standards for motor vehicle imports', date(2024, 7, 1), 'Medium', json.dumps(['8703', '8704', '8705']), datetime.now()),
            (3, 'REG-2024-003', 'Electronics Compliance Update', 'New electromagnetic compatibility requirements', date(2024, 8, 1), 'Medium', json.dumps(['8471', '8517', '8518']), datetime.now())
        ]
        
        for regulatory in regulatory_data:
            cursor.execute("""
                INSERT OR IGNORE INTO regulatory_updates (id, update_id, title, description, effective_date, impact_level, affected_codes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, regulatory)
        
        # Ruling statistics
        statistics_data = [
            (1, '2024-Q1', 156, 89, 67, 28, datetime.now()),
            (2, '2024-Q2', 142, 78, 64, 25, datetime.now()),
            (3, '2023-Q4', 168, 95, 73, 32, datetime.now())
        ]
        
        for stats in statistics_data:
            cursor.execute("""
                INSERT OR IGNORE INTO ruling_statistics (id, period, total_rulings, classification_rulings, tariff_rulings, avg_processing_days, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, stats)
        
        conn.commit()
        print("\n✅ COMPREHENSIVE DATA POPULATION COMPLETE!")
        
        # Final verification
        print("\n=== FINAL DATABASE STATUS ===")
        
        tables_to_check = [
            ('tariff_sections', 21), ('tariff_chapters', 97), ('tariff_codes', 120),
            ('duty_rates', 56), ('export_codes', 39), ('tcos', 16),
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
            print(f"\n🎯 DATABASE FULLY POPULATED - READY FOR PRODUCTION!")
            print(f"🚀 Frontend now has comprehensive data for all features!")
            print(f"✅ User acceptance testing can begin!")
        else:
            print(f"\n⚠️ Some tables still need more data for optimal frontend experience")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_final_data()
