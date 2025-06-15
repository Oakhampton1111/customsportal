#!/usr/bin/env python3
"""
Populate comprehensive customs classification rulings.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from pathlib import Path

# Sample realistic customs rulings
SAMPLE_RULINGS = [
    {
        'ruling_number': 'N24001',
        'hs_code': '8471.30.00',
        'product_description': 'Portable automatic data processing machines, weighing not more than 10 kg, consisting of at least a central processing unit, a keyboard and a display',
        'classification_reasoning': 'The goods are portable computers with integrated keyboard and display. Classification under heading 84.71 as automatic data processing machines is appropriate as they meet the definition of complete digital computers.',
        'ruling_date': date(2024, 1, 15),
        'effective_date': date(2024, 2, 1),
        'applicant_name': 'Tech Import Solutions Pty Ltd',
        'status': 'active'
    },
    {
        'ruling_number': 'N24002', 
        'hs_code': '3004.90.90',
        'product_description': 'Medicaments consisting of mixed or unmixed products for therapeutic or prophylactic uses, put up in measured doses',
        'classification_reasoning': 'The pharmaceutical products are therapeutic medicaments containing active pharmaceutical ingredients, packaged in measured doses for retail sale. Classification under heading 30.04 is appropriate.',
        'ruling_date': date(2024, 1, 20),
        'effective_date': date(2024, 2, 5),
        'applicant_name': 'MedPharm Imports Ltd',
        'status': 'active'
    },
    {
        'ruling_number': 'N24003',
        'hs_code': '8517.12.00', 
        'product_description': 'Telephones for cellular networks or for other wireless networks',
        'classification_reasoning': 'The devices are smartphones capable of cellular communication and wireless network connectivity. They incorporate telephone functions as their primary purpose, warranting classification under heading 85.17.',
        'ruling_date': date(2024, 2, 1),
        'effective_date': date(2024, 2, 15),
        'applicant_name': 'Mobile Tech Distributors',
        'status': 'active'
    },
    {
        'ruling_number': 'N24004',
        'hs_code': '6204.62.00',
        'product_description': 'Women\'s or girls\' trousers, bib and brace overalls, breeches and shorts, of cotton',
        'classification_reasoning': 'The garments are women\'s trousers made of cotton fabric, not knitted or crocheted. Classification under heading 62.04 for women\'s clothing articles is appropriate.',
        'ruling_date': date(2024, 2, 10),
        'effective_date': date(2024, 2, 25),
        'applicant_name': 'Fashion Forward Imports',
        'status': 'active'
    },
    {
        'ruling_number': 'N24005',
        'hs_code': '8708.29.90',
        'product_description': 'Other parts and accessories of bodies (including cabs) for motor vehicles',
        'classification_reasoning': 'The automotive body panels and trim pieces are specifically designed for motor vehicles and constitute body parts. Classification under heading 87.08 for vehicle parts is appropriate.',
        'ruling_date': date(2024, 2, 15),
        'effective_date': date(2024, 3, 1),
        'applicant_name': 'Auto Parts Australia Pty Ltd',
        'status': 'active'
    },
    {
        'ruling_number': 'N23045',
        'hs_code': '9018.39.90',
        'product_description': 'Other instruments and appliances used in medical, surgical, dental or veterinary sciences',
        'classification_reasoning': 'The medical diagnostic equipment is specifically designed for medical use and incorporates specialized sensors and software for patient monitoring. Classification under heading 90.18 is appropriate.',
        'ruling_date': date(2023, 11, 20),
        'effective_date': date(2023, 12, 5),
        'applicant_name': 'MedTech Solutions Ltd',
        'status': 'active'
    },
    {
        'ruling_number': 'N23046',
        'hs_code': '2203.00.00',
        'product_description': 'Beer made from malt',
        'classification_reasoning': 'The beverages are fermented alcoholic drinks made from malted barley and hops, meeting the definition of beer. Classification under heading 22.03 is appropriate regardless of alcohol content variations.',
        'ruling_date': date(2023, 12, 1),
        'effective_date': date(2023, 12, 15),
        'applicant_name': 'Craft Beer Imports Pty Ltd',
        'status': 'active'
    },
    {
        'ruling_number': 'N23047',
        'hs_code': '7013.49.00',
        'product_description': 'Other glassware of a kind used for table, kitchen, toilet, office, indoor decoration or similar purposes',
        'classification_reasoning': 'The decorative glass items are designed for household and decorative use, manufactured from glass materials. Classification under heading 70.13 for glassware is appropriate.',
        'ruling_date': date(2023, 12, 10),
        'effective_date': date(2023, 12, 24),
        'applicant_name': 'Home Decor Imports',
        'status': 'active'
    },
    {
        'ruling_number': 'N23048',
        'hs_code': '8544.42.90',
        'product_description': 'Other electric conductors, for a voltage not exceeding 1,000 V, fitted with connectors',
        'classification_reasoning': 'The electrical cables are insulated conductors with fitted connectors designed for low voltage applications. Classification under heading 85.44 for insulated electric conductors is appropriate.',
        'ruling_date': date(2023, 12, 15),
        'effective_date': date(2024, 1, 1),
        'applicant_name': 'Electrical Components Ltd',
        'status': 'active'
    },
    {
        'ruling_number': 'N23049',
        'hs_code': '4016.99.90',
        'product_description': 'Other articles of vulcanised rubber other than hard rubber',
        'classification_reasoning': 'The rubber gaskets and seals are manufactured from vulcanised rubber and designed for industrial sealing applications. Classification under heading 40.16 for other rubber articles is appropriate.',
        'ruling_date': date(2023, 12, 20),
        'effective_date': date(2024, 1, 5),
        'applicant_name': 'Industrial Seals Australia',
        'status': 'active'
    }
]

def generate_additional_rulings():
    """Generate additional realistic rulings for various product categories."""
    additional_rulings = []
    
    # Common HS codes and product types for rulings
    common_classifications = [
        ('8528.72.00', 'Reception apparatus for television', 'Consumer electronics'),
        ('6109.10.00', 'T-shirts, singlets and other vests, knitted or crocheted, of cotton', 'Textiles'),
        ('3926.90.90', 'Other articles of plastics', 'Plastics'),
        ('8414.51.00', 'Table, floor, wall, window, ceiling or roof fans', 'Electrical appliances'),
        ('9403.60.00', 'Other wooden furniture', 'Furniture'),
        ('2008.99.90', 'Other fruit, nuts and other edible parts of plants', 'Food products'),
        ('8481.80.90', 'Other taps, cocks, valves and similar appliances', 'Industrial equipment'),
        ('6302.21.00', 'Bed linen, printed, of cotton', 'Home textiles'),
        ('8536.69.90', 'Other plugs and sockets', 'Electrical components'),
        ('7326.90.90', 'Other articles of iron or steel', 'Metal products'),
        ('3304.99.00', 'Other beauty or make-up preparations', 'Cosmetics'),
        ('8302.41.00', 'Other mountings, fittings and similar articles suitable for buildings', 'Hardware'),
        ('4202.92.00', 'Other containers, with outer surface of sheeting of plastics or textile materials', 'Bags and containers'),
        ('9505.90.00', 'Other festive, carnival or other entertainment articles', 'Entertainment items'),
        ('8211.92.00', 'Other knives having fixed blades', 'Cutlery'),
        ('6217.10.00', 'Other made up clothing accessories', 'Clothing accessories'),
        ('8467.21.00', 'Drills of all kinds', 'Power tools'),
        ('3923.30.00', 'Carboys, bottles, flasks and similar articles', 'Plastic containers'),
        ('8509.80.00', 'Other electro-mechanical domestic appliances', 'Kitchen appliances'),
        ('9404.90.00', 'Other articles of bedding and similar furnishing', 'Bedding')
    ]
    
    companies = [
        'Global Trade Solutions Pty Ltd', 'Import Specialists Australia', 'Trade Connect Ltd',
        'International Commerce Group', 'Customs Compliance Services', 'Border Trade Partners',
        'Australian Import Co', 'Trade Facilitation Services', 'Cross Border Solutions',
        'Import Excellence Pty Ltd', 'Trade Advisory Group', 'Customs Consulting Australia'
    ]
    
    for i, (hs_code, product_desc, category) in enumerate(common_classifications):
        ruling_num = f"N24{10 + i:03d}"
        
        ruling_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 120))
        effective_date = ruling_date + timedelta(days=random.randint(10, 30))
        
        reasoning = f"The {category.lower()} products meet the specific criteria for classification under heading {hs_code[:4]}. " \
                   f"Based on the General Interpretative Rules and the product's essential character, " \
                   f"this classification is appropriate for customs purposes."
        
        additional_rulings.append({
            'ruling_number': ruling_num,
            'hs_code': hs_code,
            'product_description': product_desc,
            'classification_reasoning': reasoning,
            'ruling_date': ruling_date,
            'effective_date': effective_date,
            'applicant_name': random.choice(companies),
            'status': 'active'
        })
    
    return additional_rulings

def populate_customs_rulings():
    """Populate comprehensive customs classification rulings."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Populating customs classification rulings...")
        
        # Combine sample and generated rulings
        all_rulings = SAMPLE_RULINGS + generate_additional_rulings()
        
        inserted = 0
        
        for ruling in all_rulings:
            try:
                cursor.execute("""
                    INSERT INTO tariff_rulings (
                        ruling_number, title, description, hs_code, 
                        commodity_description, ruling_date, effective_date,
                        status, tariff_classification, applicant, 
                        ruling_text, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ruling['ruling_number'],
                    f"Classification Ruling {ruling['ruling_number']}",
                    ruling['classification_reasoning'],
                    ruling['hs_code'],
                    ruling['product_description'],
                    ruling['ruling_date'],
                    ruling['effective_date'],
                    ruling['status'],
                    ruling['hs_code'],
                    ruling['applicant_name'],
                    ruling['classification_reasoning'],
                    datetime.now()
                ))
                inserted += 1
                
            except sqlite3.IntegrityError:
                # Skip if ruling number already exists
                continue
        
        conn.commit()
        
        print(f"✅ Successfully inserted {inserted} customs rulings")
        
        # Verification
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings")
        total_rulings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings WHERE status = 'active'")
        active_rulings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM tariff_rulings")
        unique_codes = cursor.fetchone()[0]
        
        print(f"Total rulings in database: {total_rulings}")
        print(f"Active rulings: {active_rulings}")
        print(f"Unique HS codes covered: {unique_codes}")
        
        # Show recent rulings
        print("\nRecent Rulings:")
        cursor.execute("""
            SELECT ruling_number, hs_code, SUBSTR(commodity_description, 1, 50) || '...' as description
            FROM tariff_rulings 
            ORDER BY ruling_date DESC 
            LIMIT 5
        """)
        
        for ruling_num, hs_code, description in cursor.fetchall():
            print(f"  {ruling_num}: {hs_code} - {description}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate_customs_rulings()
