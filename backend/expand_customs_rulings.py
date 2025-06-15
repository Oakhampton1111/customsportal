#!/usr/bin/env python3
"""
Expand customs rulings to comprehensive coverage with realistic classification guidance.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from pathlib import Path

# Comprehensive product categories and their typical HS codes
PRODUCT_CATEGORIES = {
    'Electronics & Technology': [
        ('8471.30.00', 'Laptop computers and portable data processing machines'),
        ('8517.12.00', 'Smartphones and cellular telephones'),
        ('8528.72.00', 'LED televisions and display monitors'),
        ('8518.30.00', 'Headphones and audio equipment'),
        ('8543.70.90', 'Smart home devices and IoT equipment'),
        ('8504.40.00', 'Power adapters and electronic converters'),
        ('8536.69.90', 'USB connectors and charging cables'),
        ('9013.80.90', 'Laser projection equipment'),
        ('8525.80.00', 'Digital cameras and video recording equipment'),
        ('8471.60.00', 'Computer keyboards and input devices')
    ],
    'Automotive & Transport': [
        ('8708.29.90', 'Automotive body panels and trim components'),
        ('8708.99.90', 'Vehicle brake systems and safety components'),
        ('8511.30.00', 'Automotive ignition systems and distributors'),
        ('8708.80.00', 'Suspension systems and shock absorbers'),
        ('8714.20.00', 'Bicycle parts and accessories'),
        ('8716.80.00', 'Shopping trolleys and wheeled containers'),
        ('8708.10.00', 'Vehicle bumpers and impact protection'),
        ('8512.20.00', 'Automotive lighting systems'),
        ('8708.40.00', 'Gear boxes and transmission components'),
        ('8483.40.00', 'Automotive gears and drive components')
    ],
    'Textiles & Apparel': [
        ('6204.62.00', 'Women\'s cotton trousers and casual wear'),
        ('6109.10.00', 'Cotton t-shirts and casual tops'),
        ('6302.21.00', 'Cotton bed linen and home textiles'),
        ('6217.10.00', 'Fashion accessories and clothing items'),
        ('6403.99.00', 'Leather footwear and fashion shoes'),
        ('6506.10.00', 'Safety helmets and protective headwear'),
        ('6302.60.00', 'Toilet and kitchen linen'),
        ('6211.43.00', 'Women\'s synthetic garments'),
        ('6404.19.00', 'Sports footwear and athletic shoes'),
        ('6115.96.00', 'Synthetic hosiery and socks')
    ],
    'Food & Agriculture': [
        ('2008.99.90', 'Processed fruit preparations and preserves'),
        ('1905.90.90', 'Biscuits, crackers and baked goods'),
        ('2203.00.00', 'Beer and malted beverages'),
        ('0813.50.00', 'Dried fruit mixtures and trail mixes'),
        ('2106.90.90', 'Food preparations and dietary supplements'),
        ('1704.90.00', 'Sugar confectionery and candy products'),
        ('2005.99.00', 'Prepared vegetables and pickled products'),
        ('0901.21.00', 'Roasted coffee beans and ground coffee'),
        ('1806.32.00', 'Chocolate products and confections'),
        ('2009.89.00', 'Fruit juices and beverage concentrates')
    ],
    'Medical & Healthcare': [
        ('9018.39.90', 'Medical diagnostic instruments and equipment'),
        ('3004.90.90', 'Pharmaceutical preparations and medicines'),
        ('9021.39.00', 'Orthopedic appliances and medical devices'),
        ('3005.90.00', 'Medical dressings and first aid supplies'),
        ('9018.19.00', 'Medical examination equipment'),
        ('3006.60.00', 'Chemical contraceptive preparations'),
        ('9402.90.00', 'Medical furniture and hospital equipment'),
        ('3822.00.00', 'Diagnostic reagents and test kits'),
        ('9018.90.00', 'Medical instruments and surgical tools'),
        ('3926.90.90', 'Medical plastic disposables and supplies')
    ],
    'Industrial & Manufacturing': [
        ('8481.80.90', 'Industrial valves and flow control devices'),
        ('7326.90.90', 'Steel fabricated products and components'),
        ('8414.51.00', 'Industrial fans and ventilation equipment'),
        ('8536.50.00', 'Industrial switches and control devices'),
        ('3926.90.90', 'Industrial plastic components and fittings'),
        ('7318.15.00', 'Industrial bolts, screws and fasteners'),
        ('8302.41.00', 'Building hardware and architectural fittings'),
        ('8467.21.00', 'Industrial power tools and equipment'),
        ('8421.39.00', 'Industrial filtration and separation equipment'),
        ('8479.89.00', 'Specialized industrial machinery')
    ],
    'Home & Garden': [
        ('9403.60.00', 'Wooden furniture and home furnishings'),
        ('7013.49.00', 'Decorative glassware and home accessories'),
        ('6302.21.00', 'Home textiles and decorative linens'),
        ('8211.92.00', 'Kitchen knives and cutlery sets'),
        ('8509.80.00', 'Kitchen appliances and food processors'),
        ('9404.90.00', 'Bedding accessories and pillows'),
        ('3924.10.00', 'Kitchen utensils and plastic tableware'),
        ('6911.10.00', 'Porcelain tableware and dinnerware'),
        ('9405.40.00', 'LED lighting fixtures and lamps'),
        ('8716.80.00', 'Garden carts and outdoor equipment')
    ],
    'Sports & Recreation': [
        ('9506.62.00', 'Footballs and sports balls'),
        ('9504.50.00', 'Video game consoles and gaming equipment'),
        ('9506.99.00', 'Sporting goods and recreational equipment'),
        ('9503.00.00', 'Toys and children\'s recreational items'),
        ('8712.00.00', 'Bicycles and cycling equipment'),
        ('9506.31.00', 'Golf clubs and golfing accessories'),
        ('9507.30.00', 'Fishing reels and angling equipment'),
        ('9506.91.00', 'Exercise equipment and fitness machines'),
        ('9505.90.00', 'Party supplies and entertainment items'),
        ('6404.11.00', 'Sports footwear and athletic shoes')
    ]
}

COMPANIES = [
    'Global Trade Solutions Pty Ltd', 'Australian Import Specialists', 'Trade Compliance Partners',
    'Border Solutions Australia', 'Customs Advisory Group', 'Import Excellence Ltd',
    'Trade Facilitation Services', 'Compliance First Australia', 'International Trade Partners',
    'Customs Consulting Group', 'Trade Navigator Australia', 'Border Compliance Solutions',
    'Australian Trade Services', 'Import Advisory Partners', 'Customs Classification Experts',
    'Trade Regulation Specialists', 'Border Trade Solutions', 'Compliance Management Group',
    'International Customs Services', 'Trade Documentation Experts', 'Australian Border Solutions',
    'Customs Brokerage Partners', 'Trade Compliance Australia', 'Import Regulation Services',
    'Border Management Solutions', 'Trade Advisory Australia', 'Customs Excellence Group',
    'International Trade Solutions', 'Border Facilitation Services', 'Trade Compliance Experts'
]

def generate_classification_reasoning(hs_code, product_desc, category):
    """Generate realistic classification reasoning."""
    chapter = hs_code[:2]
    heading = hs_code[:4]
    
    reasonings = [
        f"The goods are {product_desc.lower()} which fall under Chapter {chapter} covering {category.lower()}. "
        f"Classification under heading {heading} is appropriate based on the product's essential character and primary function. "
        f"The goods meet the specific criteria outlined in the Harmonized System nomenclature.",
        
        f"These products are {product_desc.lower()} designed for {category.lower()} applications. "
        f"Under the General Interpretative Rules, classification in heading {heading} is correct as the goods' "
        f"primary purpose and construction align with the heading description.",
        
        f"The {product_desc.lower()} are classified under heading {heading} in accordance with "
        f"the Harmonized System structure for {category.lower()}. The classification is supported by "
        f"the product specifications and intended use as described in the application.",
        
        f"Classification under heading {heading} is appropriate for these {product_desc.lower()} "
        f"based on their material composition, manufacturing process, and intended application in {category.lower()}. "
        f"This aligns with established classification precedents and HS interpretative guidance.",
        
        f"The goods constitute {product_desc.lower()} falling within the scope of Chapter {chapter}. "
        f"Heading {heading} provides the most specific classification based on the product's "
        f"technical specifications and primary function in {category.lower()} applications."
    ]
    
    return random.choice(reasonings)

def expand_customs_rulings():
    """Create comprehensive customs classification rulings."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("⚖️ EXPANDING CUSTOMS RULINGS TO COMPREHENSIVE COVERAGE")
        print("=" * 60)
        
        # Check existing rulings
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings")
        existing_count = cursor.fetchone()[0]
        print(f"Existing rulings: {existing_count}")
        
        total_inserted = 0
        ruling_counter = 1000  # Start from N24100
        
        for category, products in PRODUCT_CATEGORIES.items():
            print(f"\nAdding rulings for {category}...")
            
            for hs_code, product_desc in products:
                # Generate multiple rulings per product type (variations)
                variations = [
                    f"{product_desc}",
                    f"Commercial grade {product_desc.lower()}",
                    f"Industrial {product_desc.lower()}",
                    f"Consumer {product_desc.lower()}",
                    f"Professional {product_desc.lower()}"
                ]
                
                for i, variation in enumerate(variations):
                    ruling_number = f"N24{ruling_counter + i:03d}"
                    
                    # Generate dates
                    ruling_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 150))
                    effective_date = ruling_date + timedelta(days=random.randint(10, 30))
                    
                    # Generate reasoning
                    reasoning = generate_classification_reasoning(hs_code, variation, category)
                    
                    # Select company
                    company = random.choice(COMPANIES)
                    
                    try:
                        cursor.execute("""
                            INSERT INTO tariff_rulings (
                                ruling_number, title, description, hs_code,
                                commodity_description, ruling_date, effective_date,
                                status, tariff_classification, duty_rate, applicant,
                                ruling_text, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ruling_number,
                            f"Classification Ruling {ruling_number} - {category}",
                            reasoning,
                            hs_code,
                            variation,
                            ruling_date,
                            effective_date,
                            'active',
                            hs_code,
                            f"{random.uniform(0, 25):.1f}%",  # Add duty rate
                            company,
                            reasoning,
                            datetime.now()
                        ))
                        total_inserted += 1
                        
                    except sqlite3.IntegrityError:
                        continue  # Skip duplicates
                
                ruling_counter += 5  # Increment for next product
        
        # Add some historical rulings (2023)
        print("\nAdding historical rulings from 2023...")
        
        historical_products = [
            ('8471.30.00', 'Legacy computer systems and data processing equipment'),
            ('3004.90.90', 'Specialized pharmaceutical compounds'),
            ('8517.12.00', 'Previous generation mobile communication devices'),
            ('6204.62.00', 'Traditional textile garments'),
            ('8708.29.90', 'Classic automotive components'),
            ('9018.39.90', 'Established medical diagnostic equipment'),
            ('2203.00.00', 'Traditional brewing products'),
            ('7013.49.00', 'Classic glassware and decorative items'),
            ('8544.42.90', 'Standard electrical cable assemblies'),
            ('4016.99.90', 'Traditional rubber manufacturing products')
        ]
        
        for hs_code, product_desc in historical_products:
            ruling_number = f"N23{ruling_counter:03d}"
            ruling_date = date(2023, random.randint(1, 12), random.randint(1, 28))
            effective_date = ruling_date + timedelta(days=random.randint(10, 30))
            
            reasoning = f"Historical classification ruling for {product_desc.lower()}. " \
                       f"Classification under heading {hs_code[:4]} established based on " \
                       f"product specifications and regulatory requirements at time of ruling."
            
            try:
                cursor.execute("""
                    INSERT INTO tariff_rulings (
                        ruling_number, title, description, hs_code,
                        commodity_description, ruling_date, effective_date,
                        status, tariff_classification, duty_rate, applicant,
                        ruling_text, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ruling_number,
                    f"Historical Classification Ruling {ruling_number}",
                    reasoning,
                    hs_code,
                    product_desc,
                    ruling_date,
                    effective_date,
                    'active',
                    hs_code,
                    f"{random.uniform(0, 25):.1f}%",  # Add duty rate
                    random.choice(COMPANIES),
                    reasoning,
                    datetime.now()
                ))
                total_inserted += 1
                
            except sqlite3.IntegrityError:
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
        
        if total_rulings >= 100:
            print("🎉 EXCELLENT CUSTOMS RULINGS COVERAGE ACHIEVED!")
        elif total_rulings >= 50:
            print("👍 GOOD CUSTOMS RULINGS COVERAGE!")
        else:
            print("⚠️ More rulings could be beneficial")
        
        # Show category distribution
        print("\nRulings by Product Category:")
        for category in PRODUCT_CATEGORIES.keys():
            cursor.execute("""
                SELECT COUNT(*) FROM tariff_rulings 
                WHERE title LIKE ?
            """, (f"%{category}%",))
            count = cursor.fetchone()[0]
            print(f"  {category}: {count} rulings")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    expand_customs_rulings()
