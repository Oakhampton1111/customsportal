#!/usr/bin/env python3
"""
Populate comprehensive customs rulings with all required fields.
"""

import sqlite3
import random
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# Comprehensive product data
COMPREHENSIVE_PRODUCTS = [
    # Electronics & Technology
    ('8471.30.00', 'Laptop Computers', 'Portable data processing machines for business and personal use'),
    ('8517.12.00', 'Smartphones', 'Cellular telephones with advanced computing capabilities'),
    ('8528.72.00', 'LED Televisions', 'Liquid crystal display television receivers'),
    ('8518.30.00', 'Audio Headphones', 'Personal audio equipment and headphones'),
    ('8543.70.90', 'Smart Devices', 'Internet-connected home automation devices'),
    ('8504.40.00', 'Power Adapters', 'Electronic power supply units and adapters'),
    ('8536.69.90', 'USB Connectors', 'Universal serial bus cables and connectors'),
    ('9013.80.90', 'Laser Equipment', 'Laser projection and optical equipment'),
    ('8525.80.00', 'Digital Cameras', 'Digital video and still image recording equipment'),
    ('8471.60.00', 'Input Devices', 'Computer keyboards and pointing devices'),
    
    # Automotive & Transport
    ('8708.29.90', 'Auto Body Parts', 'Vehicle body panels and exterior components'),
    ('8708.99.90', 'Brake Systems', 'Automotive brake components and safety systems'),
    ('8511.30.00', 'Ignition Systems', 'Vehicle ignition and electrical systems'),
    ('8708.80.00', 'Suspension Parts', 'Vehicle suspension and shock absorption systems'),
    ('8714.20.00', 'Bicycle Parts', 'Bicycle components and accessories'),
    ('8716.80.00', 'Wheeled Containers', 'Shopping trolleys and mobile containers'),
    ('8708.10.00', 'Vehicle Bumpers', 'Automotive impact protection systems'),
    ('8512.20.00', 'Auto Lighting', 'Vehicle lighting and signaling equipment'),
    ('8708.40.00', 'Transmission Parts', 'Gearbox and transmission components'),
    ('8483.40.00', 'Automotive Gears', 'Vehicle drive and gear components'),
    
    # Textiles & Apparel
    ('6204.62.00', 'Cotton Trousers', 'Women\'s cotton casual and business trousers'),
    ('6109.10.00', 'Cotton T-Shirts', 'Cotton knitted shirts and casual tops'),
    ('6302.21.00', 'Bed Linens', 'Cotton bed sheets and household textiles'),
    ('6217.10.00', 'Fashion Accessories', 'Clothing accessories and fashion items'),
    ('6403.99.00', 'Leather Footwear', 'Leather shoes and fashion footwear'),
    ('6506.10.00', 'Safety Helmets', 'Protective headwear and safety equipment'),
    ('6302.60.00', 'Kitchen Linens', 'Toilet and kitchen textile products'),
    ('6211.43.00', 'Synthetic Garments', 'Women\'s synthetic fiber clothing'),
    ('6404.19.00', 'Sports Footwear', 'Athletic shoes and sports footwear'),
    ('6115.96.00', 'Synthetic Hosiery', 'Synthetic fiber socks and hosiery'),
    
    # Food & Agriculture
    ('2008.99.90', 'Fruit Preparations', 'Processed fruit preserves and preparations'),
    ('1905.90.90', 'Baked Goods', 'Biscuits, crackers and bakery products'),
    ('2203.00.00', 'Beer Products', 'Malted alcoholic beverages'),
    ('0813.50.00', 'Dried Fruit Mixes', 'Mixed dried fruits and trail mixes'),
    ('2106.90.90', 'Food Supplements', 'Dietary supplements and food preparations'),
    ('1704.90.00', 'Sugar Confectionery', 'Candy and sugar-based confections'),
    ('2005.99.00', 'Prepared Vegetables', 'Processed and pickled vegetables'),
    ('0901.21.00', 'Coffee Products', 'Roasted coffee beans and ground coffee'),
    ('1806.32.00', 'Chocolate Products', 'Chocolate confections and products'),
    ('2009.89.00', 'Fruit Juices', 'Concentrated fruit juices and beverages'),
    
    # Medical & Healthcare
    ('9018.39.90', 'Medical Instruments', 'Diagnostic and medical examination equipment'),
    ('3004.90.90', 'Pharmaceuticals', 'Medicinal preparations and compounds'),
    ('9021.39.00', 'Medical Devices', 'Orthopedic appliances and prosthetics'),
    ('3005.90.00', 'Medical Supplies', 'First aid materials and medical dressings'),
    ('9018.19.00', 'Examination Equipment', 'Medical diagnostic instruments'),
    ('3006.60.00', 'Contraceptives', 'Chemical contraceptive preparations'),
    ('9402.90.00', 'Medical Furniture', 'Hospital beds and medical furniture'),
    ('3822.00.00', 'Diagnostic Reagents', 'Laboratory test kits and reagents'),
    ('9018.90.00', 'Surgical Instruments', 'Medical and surgical tools'),
    ('3926.90.90', 'Medical Plastics', 'Disposable medical plastic products'),
    
    # Industrial & Manufacturing
    ('8481.80.90', 'Industrial Valves', 'Flow control and pressure regulation valves'),
    ('7326.90.90', 'Steel Products', 'Fabricated steel components and structures'),
    ('8414.51.00', 'Industrial Fans', 'Ventilation and air circulation equipment'),
    ('8536.50.00', 'Control Switches', 'Industrial electrical control devices'),
    ('3926.90.90', 'Plastic Components', 'Industrial plastic parts and fittings'),
    ('7318.15.00', 'Fasteners', 'Industrial bolts, screws and fastening systems'),
    ('8302.41.00', 'Building Hardware', 'Architectural hardware and fittings'),
    ('8467.21.00', 'Power Tools', 'Industrial drilling and cutting tools'),
    ('8421.39.00', 'Filtration Equipment', 'Industrial filters and separation systems'),
    ('8479.89.00', 'Industrial Machinery', 'Specialized manufacturing equipment'),
    
    # Home & Garden
    ('9403.60.00', 'Wooden Furniture', 'Household wooden furniture and furnishings'),
    ('7013.49.00', 'Decorative Glass', 'Ornamental glassware and home accessories'),
    ('6302.21.00', 'Home Textiles', 'Decorative linens and household fabrics'),
    ('8211.92.00', 'Kitchen Cutlery', 'Knives and kitchen cutting implements'),
    ('8509.80.00', 'Kitchen Appliances', 'Food preparation and kitchen equipment'),
    ('9404.90.00', 'Bedding Products', 'Pillows and bedding accessories'),
    ('3924.10.00', 'Kitchen Utensils', 'Plastic tableware and kitchen tools'),
    ('6911.10.00', 'Porcelain Tableware', 'Ceramic dinnerware and serving pieces'),
    ('9405.40.00', 'LED Lighting', 'Household lighting fixtures and lamps'),
    ('8716.80.00', 'Garden Equipment', 'Outdoor carts and garden tools'),
    
    # Sports & Recreation
    ('9506.62.00', 'Sports Balls', 'Footballs and recreational sports equipment'),
    ('9504.50.00', 'Gaming Equipment', 'Video game consoles and gaming devices'),
    ('9506.99.00', 'Sports Equipment', 'General sporting goods and accessories'),
    ('9503.00.00', 'Toys', 'Children\'s toys and recreational items'),
    ('8712.00.00', 'Bicycles', 'Recreational and transportation bicycles'),
    ('9506.31.00', 'Golf Equipment', 'Golf clubs and golfing accessories'),
    ('9507.30.00', 'Fishing Equipment', 'Fishing reels and angling gear'),
    ('9506.91.00', 'Exercise Equipment', 'Fitness machines and exercise devices'),
    ('9505.90.00', 'Party Supplies', 'Entertainment and celebration items'),
    ('6404.11.00', 'Athletic Footwear', 'Sports shoes and athletic footwear')
]

COMPANIES = [
    'Global Trade Solutions Pty Ltd', 'Australian Import Specialists', 'Trade Compliance Partners',
    'Border Solutions Australia', 'Customs Advisory Group', 'Import Excellence Ltd',
    'Trade Facilitation Services', 'Compliance First Australia', 'International Trade Partners',
    'Customs Consulting Group', 'Trade Navigator Australia', 'Border Compliance Solutions'
]

def generate_reference_documents():
    """Generate realistic reference documents."""
    docs = [
        "Australian Harmonized Export Commodity Classification",
        "World Customs Organization HS Convention",
        "Australian Border Force Tariff Classification Ruling Guidelines",
        "Customs Tariff Act 1995 (Cth)",
        "World Trade Organization Agreement on Rules of Origin"
    ]
    return json.dumps(random.sample(docs, random.randint(2, 4)))

def generate_related_rulings():
    """Generate related ruling references."""
    rulings = [
        f"TR-{random.randint(2020, 2023)}-{random.randint(100, 999)}",
        f"N{random.randint(20, 24)}{random.randint(100, 999)}",
        f"CR-{random.randint(2021, 2024)}-{random.randint(50, 200)}"
    ]
    return json.dumps(random.sample(rulings, random.randint(1, 2)))

def populate_comprehensive_rulings():
    """Populate comprehensive customs rulings."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🏛️ POPULATING COMPREHENSIVE CUSTOMS RULINGS")
        print("=" * 60)
        
        # Check existing rulings
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings")
        existing_count = cursor.fetchone()[0]
        print(f"Existing rulings: {existing_count}")
        
        total_inserted = 0
        ruling_counter = 1001
        
        for hs_code, product_type, description in COMPREHENSIVE_PRODUCTS:
            ruling_number = f"N24{ruling_counter:03d}"
            
            # Generate dates
            ruling_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 120))
            effective_date = ruling_date + timedelta(days=random.randint(10, 30))
            
            # Generate detailed ruling text
            chapter = hs_code[:2]
            heading = hs_code[:4]
            
            ruling_text = f"The goods described as {description.lower()} are classified under " \
                         f"heading {heading} of the Harmonized System. This classification is " \
                         f"based on the essential character of the goods and their primary function. " \
                         f"The goods fall within Chapter {chapter} and meet the specific criteria " \
                         f"outlined in the HS nomenclature for this product category."
            
            try:
                cursor.execute("""
                    INSERT INTO tariff_rulings (
                        ruling_number, title, description, hs_code,
                        commodity_description, ruling_date, effective_date,
                        status, tariff_classification, duty_rate, origin_country,
                        applicant, ruling_text, reference_documents, related_rulings,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ruling_number,
                    f"{product_type} Classification Ruling",
                    f"Tariff classification ruling for {description.lower()}",
                    hs_code,
                    description,
                    ruling_date,
                    effective_date,
                    'active',
                    hs_code,
                    f"{random.uniform(0, 25):.1f}%",
                    random.choice(['CN', 'US', 'JP', 'DE', 'KR', 'TH', 'VN', 'MY']),
                    random.choice(COMPANIES),
                    ruling_text,
                    generate_reference_documents(),
                    generate_related_rulings(),
                    datetime.now()
                ))
                total_inserted += 1
                
                if total_inserted % 10 == 0:
                    print(f"  Added {total_inserted} rulings...")
                
            except sqlite3.IntegrityError as e:
                print(f"  Skipped {ruling_number}: {e}")
                continue
            
            ruling_counter += 1
        
        conn.commit()
        
        print(f"\n✅ Successfully added {total_inserted} new customs rulings")
        
        # Final verification
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings")
        total_rulings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings WHERE status = 'active'")
        active_rulings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM tariff_rulings")
        unique_codes = cursor.fetchone()[0]
        
        print(f"\n📊 FINAL CUSTOMS RULINGS STATISTICS:")
        print(f"Total rulings: {total_rulings:,}")
        print(f"Active rulings: {active_rulings:,}")
        print(f"Unique HS codes covered: {unique_codes:,}")
        
        if total_rulings >= 50:
            print("🎉 EXCELLENT CUSTOMS RULINGS COVERAGE ACHIEVED!")
        elif total_rulings >= 25:
            print("👍 GOOD CUSTOMS RULINGS COVERAGE!")
        else:
            print("⚠️ More rulings recommended")
        
        # Show recent rulings
        print("\nRecent Rulings Added:")
        cursor.execute("""
            SELECT ruling_number, title, hs_code 
            FROM tariff_rulings 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        for ruling_number, title, hs_code in cursor.fetchall():
            print(f"  {ruling_number}: {title} ({hs_code})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate_comprehensive_rulings()
