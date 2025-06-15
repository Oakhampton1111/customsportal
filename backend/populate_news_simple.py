#!/usr/bin/env python3
"""
Populate news and regulatory updates with correct column structure.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from pathlib import Path

def populate_news_simple():
    """Populate news and regulatory updates."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("📰 POPULATING NEWS AND REGULATORY UPDATES")
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
                'update_type': 'policy_change',
                'impact_level': 'high',
                'summary': 'AUKFTA delivers significant benefits for Australian exporters with new preferential rates',
                'full_text': 'The Australia-UK Free Trade Agreement continues to deliver significant benefits for Australian exporters. New preferential tariff schedules have been implemented for agricultural products, with beef and lamb exports seeing substantial duty reductions. Importers should review their supply chains to take advantage of these preferential rates.'
            },
            {
                'id': 'UPD-2024-002',
                'title': 'New Biosecurity Import Conditions for Plant Products',
                'description': 'Enhanced phytosanitary requirements for fresh fruits and vegetables from Southeast Asia',
                'category': 'Biosecurity',
                'update_type': 'regulatory_change',
                'impact_level': 'high',
                'summary': 'Updated import conditions require enhanced certification for plant products',
                'full_text': 'The Department of Agriculture has updated import conditions for plant-based products from Southeast Asian countries. Enhanced phytosanitary requirements are now in effect for fresh fruits, vegetables, and processed plant materials. Importers must ensure compliance with new certification requirements.'
            },
            {
                'id': 'UPD-2024-003',
                'title': 'Integrated Cargo System Modernization',
                'description': 'ABF upgrading ICS with AI-powered risk assessment and automated classification',
                'category': 'Technology',
                'update_type': 'system_upgrade',
                'impact_level': 'medium',
                'summary': 'New ICS features include automated classification suggestions and real-time duty calculation',
                'full_text': 'The Australian Border Force is upgrading the Integrated Cargo System with enhanced AI-powered risk assessment capabilities. New features include automated classification suggestions and real-time duty calculation. The system will be fully operational by December 2024.'
            },
            {
                'id': 'UPD-2024-004',
                'title': 'RCEP Agreement Tariff Staging Updates',
                'description': 'Several product categories moved to lower tariff stages in RCEP third year',
                'category': 'Trade Agreements',
                'update_type': 'tariff_change',
                'impact_level': 'medium',
                'summary': 'Electronics, textiles, and automotive parts see reduced tariffs under RCEP',
                'full_text': 'The Regional Comprehensive Economic Partnership has entered its third year of implementation. Several product categories have moved to lower tariff stages, including electronics, textiles, and automotive parts. Businesses should review their RCEP utilization strategies to maximize cost savings.'
            },
            {
                'id': 'UPD-2024-005',
                'title': 'Updated Chemical Import Regulations',
                'description': 'AICIS publishes new assessment requirements for industrial chemicals',
                'category': 'Chemicals',
                'update_type': 'regulatory_change',
                'impact_level': 'high',
                'summary': 'New notification thresholds and risk assessment procedures effective July 1, 2024',
                'full_text': 'The Australian Industrial Chemicals Introduction Scheme has published new assessment requirements for industrial chemicals. New notification thresholds and risk assessment procedures are effective from July 1, 2024. Chemical importers should review their compliance procedures.'
            },
            {
                'id': 'UPD-2024-006',
                'title': 'Steel Import Anti-Dumping Investigation',
                'description': 'Anti-Dumping Commission initiates investigation into steel imports from multiple countries',
                'category': 'Anti-Dumping',
                'update_type': 'investigation',
                'impact_level': 'high',
                'summary': 'Provisional measures may be imposed pending investigation outcome',
                'full_text': 'The Anti-Dumping Commission has initiated an investigation into steel imports from multiple countries. Provisional measures may be imposed pending the outcome of the investigation. Steel importers should monitor developments and consider supply chain adjustments.'
            },
            {
                'id': 'UPD-2024-007',
                'title': 'Digital Customs Declaration Platform Launch',
                'description': 'New mobile-responsive platform with automated data validation launched',
                'category': 'Technology',
                'update_type': 'system_launch',
                'impact_level': 'medium',
                'summary': 'Platform integrates with major shipping lines and freight forwarders',
                'full_text': 'A new digital platform for customs declarations has been launched, featuring mobile-responsive design and automated data validation. The platform integrates with major shipping lines and freight forwarders, streamlining the import process for businesses of all sizes.'
            },
            {
                'id': 'UPD-2024-008',
                'title': 'Therapeutic Goods Administration Import Updates',
                'description': 'TGA streamlines import procedures for medical devices and pharmaceuticals',
                'category': 'Medical',
                'update_type': 'process_improvement',
                'impact_level': 'medium',
                'summary': 'New electronic lodgment systems reduce processing times by up to 50%',
                'full_text': 'The TGA has streamlined import procedures for medical devices and pharmaceuticals. New electronic lodgment systems are now available for import permits, reducing processing times by up to 50%. Healthcare product importers can benefit from faster clearance procedures.'
            },
            {
                'id': 'UPD-2024-009',
                'title': 'Counterfeit Electronics Detection Initiative',
                'description': 'Joint ABF and industry initiative to combat counterfeit electronics imports',
                'category': 'Enforcement',
                'update_type': 'enforcement_action',
                'impact_level': 'high',
                'summary': 'Enhanced screening procedures focus on consumer electronics safety and IP protection',
                'full_text': 'A joint initiative between Australian Border Force and industry partners has been launched to combat counterfeit electronics imports. Enhanced screening procedures are in place for consumer electronics, with particular focus on safety compliance and intellectual property protection.'
            },
            {
                'id': 'UPD-2024-010',
                'title': 'Environmental Protection Import Standards',
                'description': 'New standards for electronic waste and battery imports implemented',
                'category': 'Environment',
                'update_type': 'regulatory_change',
                'impact_level': 'medium',
                'summary': 'Enhanced documentation includes end-of-life disposal plans and recycling certificates',
                'full_text': 'New environmental protection standards have been implemented for electronic waste and battery imports. Enhanced documentation requirements include end-of-life disposal plans and recycling certificates. Electronics importers must ensure compliance with circular economy principles.'
            },
            {
                'id': 'UPD-2024-011',
                'title': 'CPTPP Rules of Origin Clarification',
                'description': 'DFAT issues new guidance on Rules of Origin requirements under CPTPP',
                'category': 'Trade Agreements',
                'update_type': 'guidance_update',
                'impact_level': 'medium',
                'summary': 'Key clarifications include yarn-forward rules for textiles and automotive RVC calculations',
                'full_text': 'The Department of Foreign Affairs and Trade has issued new guidance on Rules of Origin requirements under the Comprehensive and Progressive Trans-Pacific Partnership. Key clarifications include yarn-forward rules for textiles and regional value content calculations for automotive products.'
            },
            {
                'id': 'UPD-2024-012',
                'title': 'Textile Industry Compliance Review',
                'description': 'ACCC conducting comprehensive review of textile import compliance',
                'category': 'Compliance',
                'update_type': 'compliance_review',
                'impact_level': 'medium',
                'summary': 'Focus on country of origin labeling, fiber content, and safety standards',
                'full_text': 'The Australian Competition and Consumer Commission is conducting a comprehensive review of textile import compliance. Focus areas include country of origin labeling, fiber content declarations, and safety standards. Textile importers should ensure full compliance with consumer protection laws.'
            },
            {
                'id': 'UPD-2024-013',
                'title': 'AI-Powered Tariff Classification Assistant',
                'description': 'New AI system deployed to assist with tariff classification queries',
                'category': 'Technology',
                'update_type': 'system_enhancement',
                'impact_level': 'medium',
                'summary': 'System provides real-time classification suggestions based on product descriptions and images',
                'full_text': 'A new artificial intelligence system has been deployed to assist with tariff classification queries. The system provides real-time classification suggestions based on product descriptions and images, improving accuracy and reducing classification disputes.'
            },
            {
                'id': 'UPD-2024-014',
                'title': 'Automotive Parts Quality Standards Update',
                'description': 'New quality standards for automotive parts imports implemented',
                'category': 'Automotive',
                'update_type': 'standards_update',
                'impact_level': 'medium',
                'summary': 'Enhanced testing requirements for safety-critical components',
                'full_text': 'New quality standards for automotive parts imports have been implemented in collaboration with the Australian automotive industry. Enhanced testing requirements apply to safety-critical components including brakes, airbags, and steering systems.'
            },
            {
                'id': 'UPD-2024-015',
                'title': 'Blockchain Pilot for Supply Chain Verification',
                'description': 'ABF launches blockchain pilot program for supply chain verification',
                'category': 'Technology',
                'update_type': 'pilot_program',
                'impact_level': 'low',
                'summary': 'Initiative focuses on high-value goods and critical supply chains',
                'full_text': 'The Australian Border Force has launched a blockchain pilot program for supply chain verification. The initiative focuses on high-value goods and critical supply chains, providing enhanced traceability and authenticity verification for imported products.'
            }
        ]
        
        total_inserted = 0
        
        for update in updates:
            # Generate dates
            pub_date = date.today() - timedelta(days=random.randint(1, 90))
            effective_date = pub_date + timedelta(days=random.randint(10, 60))
            
            try:
                cursor.execute("""
                    INSERT INTO regulatory_updates (
                        id, title, description, category, update_type,
                        published_date, effective_date, status, impact_level,
                        summary, full_text, document_url, contact_info,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    update['id'],
                    update['title'],
                    update['description'],
                    update['category'],
                    update['update_type'],
                    pub_date,
                    effective_date,
                    'active',
                    update['impact_level'],
                    update['summary'],
                    update['full_text'],
                    f"https://abf.gov.au/updates/{update['id'].lower()}",
                    'customs.enquiries@abf.gov.au',
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
        
        cursor.execute("SELECT COUNT(*) FROM regulatory_updates WHERE status = 'active'")
        active_updates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM regulatory_updates")
        unique_categories = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL NEWS AND UPDATES STATISTICS:")
        print(f"Total updates: {total_updates:,}")
        print(f"Active updates: {active_updates:,}")
        print(f"Categories covered: {unique_categories:,}")
        
        if total_updates >= 15:
            print("🎉 EXCELLENT NEWS COVERAGE ACHIEVED!")
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
        
        # Show recent updates by impact level
        print("\nHigh Impact Updates:")
        cursor.execute("""
            SELECT title, published_date 
            FROM regulatory_updates 
            WHERE impact_level = 'high'
            ORDER BY published_date DESC 
            LIMIT 5
        """)
        
        for title, pub_date in cursor.fetchall():
            print(f"  🔴 {pub_date}: {title[:60]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate_news_simple()
