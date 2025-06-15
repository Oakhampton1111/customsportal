#!/usr/bin/env python3
"""Simple script to add customs rulings one by one with error handling."""

import sqlite3
import random
from datetime import datetime, date, timedelta

def add_rulings_simple():
    """Add customs rulings with detailed error handling."""
    conn = sqlite3.connect('customs_portal.db')
    cursor = conn.cursor()
    
    print("Adding customs rulings...")
    
    # Simple test rulings
    rulings = [
        {
            'ruling_number': 'N24001',
            'title': 'Laptop Computer Classification',
            'description': 'Classification of portable laptop computers under HS 8471.30.00',
            'hs_code': '8471.30.00',
            'commodity_description': 'Portable laptop computers for business use',
            'ruling_date': date(2024, 1, 15),
            'effective_date': date(2024, 2, 1),
            'status': 'active',
            'tariff_classification': '8471.30.00',
            'duty_rate': '5.0%',
            'applicant': 'Tech Import Solutions Pty Ltd',
            'ruling_text': 'These laptop computers are classified under heading 8471.30 as portable automatic data processing machines.'
        },
        {
            'ruling_number': 'N24002',
            'title': 'Smartphone Classification',
            'description': 'Classification of smartphones under HS 8517.12.00',
            'hs_code': '8517.12.00',
            'commodity_description': 'Smartphones with cellular communication capability',
            'ruling_date': date(2024, 1, 20),
            'effective_date': date(2024, 2, 5),
            'status': 'active',
            'tariff_classification': '8517.12.00',
            'duty_rate': '0.0%',
            'applicant': 'Mobile Device Importers',
            'ruling_text': 'These devices are classified as cellular telephones under heading 8517.12.'
        }
    ]
    
    added = 0
    for ruling in rulings:
        try:
            cursor.execute("""
                INSERT INTO tariff_rulings (
                    ruling_number, title, description, hs_code,
                    commodity_description, ruling_date, effective_date,
                    status, tariff_classification, duty_rate, applicant,
                    ruling_text, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ruling['ruling_number'],
                ruling['title'],
                ruling['description'],
                ruling['hs_code'],
                ruling['commodity_description'],
                ruling['ruling_date'],
                ruling['effective_date'],
                ruling['status'],
                ruling['tariff_classification'],
                ruling['duty_rate'],
                ruling['applicant'],
                ruling['ruling_text'],
                datetime.now()
            ))
            added += 1
            print(f"✅ Added ruling {ruling['ruling_number']}")
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Failed to add {ruling['ruling_number']}: {e}")
        except Exception as e:
            print(f"❌ Error with {ruling['ruling_number']}: {e}")
    
    conn.commit()
    
    # Now add more rulings with unique numbers
    print("\nAdding more comprehensive rulings...")
    
    products = [
        ('8528.72.00', 'LED Television Sets', 'Consumer electronics television displays'),
        ('6204.62.00', 'Cotton Trousers', 'Women\'s cotton casual trousers'),
        ('8708.29.90', 'Auto Body Parts', 'Automotive body panels and components'),
        ('3004.90.90', 'Pharmaceutical Products', 'Medicinal preparations and compounds'),
        ('2008.99.90', 'Fruit Preparations', 'Processed fruit preserves and preparations'),
        ('9403.60.00', 'Wooden Furniture', 'Household wooden furniture items'),
        ('8481.80.90', 'Industrial Valves', 'Flow control valves for industrial use'),
        ('9506.62.00', 'Sports Balls', 'Footballs and recreational sports balls'),
        ('8544.42.90', 'Electric Cables', 'Insulated electric cables and wiring'),
        ('7013.49.00', 'Glassware Items', 'Decorative and household glassware')
    ]
    
    for i, (hs_code, title, description) in enumerate(products, 3):
        ruling_number = f"N240{i:02d}"
        
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
                f"{title} Classification Ruling",
                f"Classification ruling for {description.lower()} under HS code {hs_code}",
                hs_code,
                description,
                date(2024, 1, 10 + i),
                date(2024, 2, 1 + i),
                'active',
                hs_code,
                f"{random.uniform(0, 20):.1f}%",
                f"Import Solutions Company {i}",
                f"These goods are classified under heading {hs_code[:4]} based on their material composition and intended use.",
                datetime.now()
            ))
            added += 1
            print(f"✅ Added ruling {ruling_number}")
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Failed to add {ruling_number}: {e}")
        except Exception as e:
            print(f"❌ Error with {ruling_number}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully added {added} new rulings")

if __name__ == "__main__":
    add_rulings_simple()
