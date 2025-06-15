#!/usr/bin/env python3
"""
Add comprehensive news and regulatory updates with correct table structure.
"""

import sqlite3
import json
import random
from datetime import datetime, date, timedelta
from pathlib import Path

def add_news_final():
    """Add comprehensive news and regulatory updates."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("📰 ADDING COMPREHENSIVE NEWS AND REGULATORY UPDATES")
        print("=" * 60)
        
        # Check existing updates
        cursor.execute("SELECT COUNT(*) FROM regulatory_updates")
        existing_count = cursor.fetchone()[0]
        print(f"Existing updates: {existing_count}")
        
        # Comprehensive news updates
        updates = [
            {
                'id': 'UPD-2024-001',
                'title': 'Australia-UK Free Trade Agreement Implementation Update',
                'description': 'New preferential tariff schedules implemented for agricultural products under AUKFTA',
                'category': 'Trade Agreements',
                'update_type': 'Policy Change',
                'affected_codes': ['0201', '0202', '0203', '0204'],
                'impact_level': 'High',
                'summary': 'AUKFTA delivers significant benefits for Australian exporters with new preferential rates for beef and lamb exports'
            },
            {
                'id': 'UPD-2024-002',
                'title': 'New Biosecurity Import Conditions for Plant Products',
                'description': 'Enhanced phytosanitary requirements for fresh fruits and vegetables from Southeast Asia',
                'category': 'Biosecurity',
                'update_type': 'Regulatory Change',
                'affected_codes': ['0801', '0802', '0803', '0804', '0805'],
                'impact_level': 'High',
                'summary': 'Updated import conditions require enhanced certification for plant products from Southeast Asian countries'
            },
            {
                'id': 'UPD-2024-003',
                'title': 'Integrated Cargo System Modernization',
                'description': 'ABF upgrading ICS with AI-powered risk assessment and automated classification',
                'category': 'Technology',
                'update_type': 'System Upgrade',
                'affected_codes': ['ALL'],
                'impact_level': 'Medium',
                'summary': 'New ICS features include automated classification suggestions and real-time duty calculation'
            },
            {
                'id': 'UPD-2024-004',
                'title': 'RCEP Agreement Tariff Staging Updates',
                'description': 'Several product categories moved to lower tariff stages in RCEP third year',
                'category': 'Trade Agreements',
                'update_type': 'Tariff Change',
                'affected_codes': ['8471', '8517', '6204', '8708'],
                'impact_level': 'Medium',
                'summary': 'Electronics, textiles, and automotive parts see reduced tariffs under RCEP staging'
            },
            {
                'id': 'UPD-2024-005',
                'title': 'Updated Chemical Import Regulations',
                'description': 'AICIS publishes new assessment requirements for industrial chemicals',
                'category': 'Chemicals',
                'update_type': 'Regulatory Change',
                'affected_codes': ['2901', '2902', '2903', '2904', '3901'],
                'impact_level': 'High',
                'summary': 'New notification thresholds and risk assessment procedures effective July 1, 2024'
            },
            {
                'id': 'UPD-2024-006',
                'title': 'Steel Import Anti-Dumping Investigation',
                'description': 'Anti-Dumping Commission initiates investigation into steel imports from multiple countries',
                'category': 'Anti-Dumping',
                'update_type': 'Investigation',
                'affected_codes': ['7208', '7209', '7210', '7211'],
                'impact_level': 'High',
                'summary': 'Provisional measures may be imposed pending investigation outcome for steel products'
            },
            {
                'id': 'UPD-2024-007',
                'title': 'Digital Customs Declaration Platform Launch',
                'description': 'New mobile-responsive platform with automated data validation launched',
                'category': 'Technology',
                'update_type': 'System Launch',
                'affected_codes': ['ALL'],
                'impact_level': 'Medium',
                'summary': 'Platform integrates with major shipping lines and freight forwarders for streamlined processing'
            },
            {
                'id': 'UPD-2024-008',
                'title': 'Therapeutic Goods Administration Import Updates',
                'description': 'TGA streamlines import procedures for medical devices and pharmaceuticals',
                'category': 'Medical',
                'update_type': 'Process Improvement',
                'affected_codes': ['3004', '9018', '9021', '3005'],
                'impact_level': 'Medium',
                'summary': 'New electronic lodgment systems reduce processing times by up to 50%'
            },
            {
                'id': 'UPD-2024-009',
                'title': 'Counterfeit Electronics Detection Initiative',
                'description': 'Joint ABF and industry initiative to combat counterfeit electronics imports',
                'category': 'Enforcement',
                'update_type': 'Enforcement Action',
                'affected_codes': ['8471', '8517', '8528', '8518'],
                'impact_level': 'High',
                'summary': 'Enhanced screening procedures focus on consumer electronics safety and IP protection'
            },
            {
                'id': 'UPD-2024-010',
                'title': 'Environmental Protection Import Standards',
                'description': 'New standards for electronic waste and battery imports implemented',
                'category': 'Environment',
                'update_type': 'Standards Update',
                'affected_codes': ['8506', '8507', '8548'],
                'impact_level': 'Medium',
                'summary': 'Enhanced documentation includes end-of-life disposal plans and recycling certificates'
            },
            {
                'id': 'UPD-2024-011',
                'title': 'CPTPP Rules of Origin Clarification',
                'description': 'DFAT issues new guidance on Rules of Origin requirements under CPTPP',
                'category': 'Trade Agreements',
                'update_type': 'Guidance Update',
                'affected_codes': ['6204', '8708', '5201'],
                'impact_level': 'Medium',
                'summary': 'Key clarifications include yarn-forward rules for textiles and automotive RVC calculations'
            },
            {
                'id': 'UPD-2024-012',
                'title': 'Textile Industry Compliance Review',
                'description': 'ACCC conducting comprehensive review of textile import compliance',
                'category': 'Compliance',
                'update_type': 'Compliance Review',
                'affected_codes': ['6204', '6109', '6302', '6217'],
                'impact_level': 'Medium',
                'summary': 'Focus on country of origin labeling, fiber content, and safety standards'
            },
            {
                'id': 'UPD-2024-013',
                'title': 'AI-Powered Tariff Classification Assistant',
                'description': 'New AI system deployed to assist with tariff classification queries',
                'category': 'Technology',
                'update_type': 'System Enhancement',
                'affected_codes': ['ALL'],
                'impact_level': 'Low',
                'summary': 'System provides real-time classification suggestions based on product descriptions and images'
            },
            {
                'id': 'UPD-2024-014',
                'title': 'Automotive Parts Quality Standards Update',
                'description': 'New quality standards for automotive parts imports implemented',
                'category': 'Automotive',
                'update_type': 'Standards Update',
                'affected_codes': ['8708', '8511', '8512', '8483'],
                'impact_level': 'Medium',
                'summary': 'Enhanced testing requirements for safety-critical components including brakes and airbags'
            },
            {
                'id': 'UPD-2024-015',
                'title': 'Blockchain Pilot for Supply Chain Verification',
                'description': 'ABF launches blockchain pilot program for supply chain verification',
                'category': 'Technology',
                'update_type': 'Pilot Program',
                'affected_codes': ['7113', '7108', '2701'],
                'impact_level': 'Low',
                'summary': 'Initiative focuses on high-value goods and critical supply chains for enhanced traceability'
            },
            {
                'id': 'UPD-2024-016',
                'title': 'Food Safety Import Requirements Update',
                'description': 'Enhanced food safety requirements for processed food imports',
                'category': 'Food Safety',
                'update_type': 'Regulatory Change',
                'affected_codes': ['1905', '2008', '2106', '1806'],
                'impact_level': 'High',
                'summary': 'New HACCP certification requirements for processed food products from specific countries'
            },
            {
                'id': 'UPD-2024-017',
                'title': 'Renewable Energy Equipment Incentives',
                'description': 'New tariff concessions for renewable energy equipment imports',
                'category': 'Energy',
                'update_type': 'Incentive Program',
                'affected_codes': ['8541', '8501', '8502'],
                'impact_level': 'Medium',
                'summary': 'Reduced duties on solar panels, wind turbines, and battery storage systems'
            },
            {
                'id': 'UPD-2024-018',
                'title': 'Tobacco Product Import Restrictions',
                'description': 'Enhanced restrictions on tobacco product imports and packaging requirements',
                'category': 'Health',
                'update_type': 'Regulatory Change',
                'affected_codes': ['2402', '2403'],
                'impact_level': 'High',
                'summary': 'New plain packaging requirements and enhanced health warning standards'
            }
        ]
        
        total_inserted = 0
        
        for update in updates:
            # Generate dates
            pub_date = date.today() - timedelta(days=random.randint(1, 120))
            effective_date = pub_date + timedelta(days=random.randint(10, 90))
            
            try:
                cursor.execute("""
                    INSERT INTO regulatory_updates (
                        id, title, description, category, update_type,
                        published_date, effective_date, affected_codes,
                        impact_level, summary, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    update['id'],
                    update['title'],
                    update['description'],
                    update['category'],
                    update['update_type'],
                    pub_date,
                    effective_date,
                    json.dumps(update['affected_codes']),
                    update['impact_level'],
                    update['summary'],
                    datetime.now(),
                    datetime.now()
                ))
                total_inserted += 1
                print(f"  ✅ Added: {update['title'][:50]}...")
                
            except sqlite3.IntegrityError as e:
                print(f"  ❌ Failed to add {update['id']}: {e}")
                continue
        
        conn.commit()
        
        print(f"\n✅ Successfully added {total_inserted} news and regulatory updates")
        
        # Final verification
        cursor.execute("SELECT COUNT(*) FROM regulatory_updates")
        total_updates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM regulatory_updates")
        unique_categories = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL NEWS AND UPDATES STATISTICS:")
        print(f"Total updates: {total_updates:,}")
        print(f"Categories covered: {unique_categories:,}")
        
        if total_updates >= 20:
            print("🎉 EXCELLENT NEWS COVERAGE ACHIEVED!")
        elif total_updates >= 15:
            print("👍 VERY GOOD NEWS COVERAGE!")
        elif total_updates >= 10:
            print("👍 GOOD NEWS COVERAGE!")
        else:
            print("⚠️ More news updates recommended")
        
        # Show category distribution
        print("\nUpdates by Category:")
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM regulatory_updates 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        for category, count in cursor.fetchall():
            print(f"  {category}: {count} updates")
        
        # Show high impact updates
        print("\nHigh Impact Updates:")
        cursor.execute("""
            SELECT title, published_date 
            FROM regulatory_updates 
            WHERE impact_level = 'High'
            ORDER BY published_date DESC 
            LIMIT 5
        """)
        
        for title, pub_date in cursor.fetchall():
            print(f"  🔴 {pub_date}: {title[:55]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_news_final()
