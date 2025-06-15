"""
Comprehensive Anti-Dumping Duties Population Script
==================================================
Populates the database with realistic anti-dumping and countervailing duties
based on Australian Anti-Dumping Commission data patterns.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple

def populate_dumping_duties():
    """Populate comprehensive anti-dumping duties dataset."""
    
    print("=" * 80)
    print("COMPREHENSIVE ANTI-DUMPING DUTIES POPULATION")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        # Anti-dumping case patterns based on Australian data
        dumping_cases = {
            "steel_products": {
                "chapters": ["72", "73"],
                "countries": ["CHN", "KOR", "TWN", "THA", "IND", "VNM", "MYS"],
                "products": [
                    "Hot-rolled structural steel sections",
                    "Cold-rolled steel coil",
                    "Galvanized steel coil", 
                    "Steel reinforcing bar",
                    "Stainless steel plate",
                    "Steel pipe and tube",
                    "Wire rod",
                    "Steel angles and channels",
                    "Prepainted galvanized steel",
                    "Steel mesh and fencing"
                ],
                "duty_ranges": {
                    "CHN": (8.5, 25.0),
                    "KOR": (5.0, 18.0),
                    "TWN": (4.0, 15.0),
                    "THA": (3.0, 12.0),
                    "IND": (6.0, 20.0),
                    "VNM": (7.0, 22.0),
                    "MYS": (4.5, 14.0)
                },
                "investigation_types": ["dumping", "countervailing", "both"],
                "major_exporters": {
                    "CHN": ["Baosteel Group", "Ansteel Group", "Wuhan Iron & Steel", "Shougang Group", "Maanshan Iron & Steel"],
                    "KOR": ["POSCO", "Hyundai Steel", "Dongkuk Steel", "SeAH Steel", "Nexteel"],
                    "TWN": ["China Steel Corporation", "Feng Hsin Steel", "Yieh Phui Enterprise", "Sheng Yu Steel"],
                    "THA": ["Sahaviriya Steel Industries", "G Steel", "Tata Steel Thailand"],
                    "IND": ["Tata Steel", "JSW Steel", "SAIL", "Jindal Steel", "Essar Steel"],
                    "VNM": ["Hoa Phat Group", "Hoa Sen Group", "Nam Kim Steel", "Pomina Steel"],
                    "MYS": ["Lion Industries", "Southern Steel", "Megasteel", "Ann Joo Resources"]
                }
            },
            "aluminum_products": {
                "chapters": ["76"],
                "countries": ["CHN", "RUS", "IND", "TUR", "ARE"],
                "products": [
                    "Aluminum extrusions",
                    "Aluminum sheet and plate",
                    "Aluminum foil",
                    "Aluminum road wheels",
                    "Aluminum cans and containers",
                    "Aluminum wire and cable",
                    "Aluminum composite panels",
                    "Aluminum window frames",
                    "Aluminum heat sinks",
                    "Aluminum scaffolding"
                ],
                "duty_ranges": {
                    "CHN": (10.0, 30.0),
                    "RUS": (8.0, 25.0),
                    "IND": (5.0, 18.0),
                    "TUR": (4.0, 15.0),
                    "ARE": (3.0, 12.0)
                },
                "investigation_types": ["dumping", "countervailing"],
                "major_exporters": {
                    "CHN": ["Hongqiao Group", "China Zhongwang", "Aluminum Corp of China", "East Hope Group"],
                    "RUS": ["UC Rusal", "Alcoa Russia", "SUAL"],
                    "IND": ["Hindalco Industries", "National Aluminium", "Vedanta Aluminium"],
                    "TUR": ["Assan Aluminyum", "Aksa Akrilik", "Eczacibasi"],
                    "ARE": ["Emirates Global Aluminium", "Dubal Aluminium"]
                }
            },
            "chemical_products": {
                "chapters": ["28", "29", "39"],
                "countries": ["CHN", "IND", "KOR", "TWN", "SGP"],
                "products": [
                    "Polyethylene terephthalate",
                    "Sodium gluconate",
                    "Citric acid",
                    "Polyvinyl chloride",
                    "Caustic soda",
                    "Hydrogen peroxide",
                    "Acetic acid",
                    "Polyethylene",
                    "Polypropylene",
                    "Styrene monomer"
                ],
                "duty_ranges": {
                    "CHN": (12.0, 35.0),
                    "IND": (8.0, 25.0),
                    "KOR": (6.0, 20.0),
                    "TWN": (5.0, 18.0),
                    "SGP": (4.0, 15.0)
                },
                "investigation_types": ["dumping", "countervailing"],
                "major_exporters": {
                    "CHN": ["Sinopec", "PetroChina", "CNOOC", "Wanhua Chemical", "Hengli Petrochemical"],
                    "IND": ["Reliance Industries", "Indian Oil", "ONGC Petro", "Haldia Petrochemicals"],
                    "KOR": ["LG Chem", "SK Innovation", "Lotte Chemical", "Hanwha Solutions"],
                    "TWN": ["Formosa Plastics", "China Petrochemical", "Nan Ya Plastics"],
                    "SGP": ["ExxonMobil Chemical", "Shell Eastern", "Chevron Phillips"]
                }
            },
            "paper_products": {
                "chapters": ["48"],
                "countries": ["CHN", "IND", "IDN", "THA", "VNM"],
                "products": [
                    "A4 copy paper",
                    "Tissue paper",
                    "Cardboard packaging",
                    "Newsprint paper",
                    "Coated paper",
                    "Kraft paper",
                    "Security paper",
                    "Filter paper",
                    "Wallpaper",
                    "Paper bags"
                ],
                "duty_ranges": {
                    "CHN": (15.0, 40.0),
                    "IND": (10.0, 30.0),
                    "IDN": (8.0, 25.0),
                    "THA": (6.0, 20.0),
                    "VNM": (7.0, 22.0)
                },
                "investigation_types": ["dumping"],
                "major_exporters": {
                    "CHN": ["Nine Dragons Paper", "Lee & Man Paper", "Shanying International"],
                    "IND": ["ITC Limited", "JK Paper", "West Coast Paper Mills"],
                    "IDN": ["Asia Pulp & Paper", "Indah Kiat Pulp & Paper", "Tjiwi Kimia"],
                    "THA": ["SCG Paper", "Double A Paper", "Phoenix Pulp & Paper"],
                    "VNM": ["Saigon Paper", "Tan Mai Paper", "Hoa Binh Paper"]
                }
            },
            "textile_products": {
                "chapters": ["54", "55", "56"],
                "countries": ["CHN", "IND", "PAK", "BGD", "VNM"],
                "products": [
                    "Polyester staple fiber",
                    "Cotton yarn",
                    "Synthetic filament yarn",
                    "Non-woven fabrics",
                    "Carpet backing",
                    "Industrial textiles",
                    "Geotextiles",
                    "Filter fabrics",
                    "Rope and cordage",
                    "Elastic tapes"
                ],
                "duty_ranges": {
                    "CHN": (10.0, 28.0),
                    "IND": (8.0, 24.0),
                    "PAK": (6.0, 20.0),
                    "BGD": (5.0, 18.0),
                    "VNM": (7.0, 22.0)
                },
                "investigation_types": ["dumping"],
                "major_exporters": {
                    "CHN": ["Hengli Group", "Tongkun Group", "Xinfengming Group"],
                    "IND": ["Reliance Industries", "Aditya Birla Group", "Welspun Group"],
                    "PAK": ["Nishat Mills", "Gul Ahmed", "Kohinoor Mills"],
                    "BGD": ["Beximco Textiles", "Square Textiles", "Envoy Textiles"],
                    "VNM": ["Vinatex", "TNG Investment", "Phong Phu Corporation"]
                }
            }
        }
        
        def generate_case_number(year: int, case_type: str, sequence: int) -> str:
            """Generate realistic ADC case number."""
            type_code = {
                "dumping": "AD",
                "countervailing": "CV", 
                "both": "ADC"
            }.get(case_type, "ADC")
            return f"{type_code} {year}/{sequence:03d}"
        
        def generate_notice_number(year: int, month: int) -> str:
            """Generate realistic gazette notice number."""
            return f"C{year}G{month:02d}"
        
        def get_random_dates(year: int) -> Tuple[str, str]:
            """Generate realistic effective and expiry dates."""
            # Effective date: random date in the year
            effective_day = random.randint(1, 365)
            effective_date = date(year, 1, 1) + timedelta(days=effective_day - 1)
            
            # Expiry date: 5 years after effective (standard ADC period)
            expiry_date = effective_date + timedelta(days=5 * 365)
            
            return (
                effective_date.strftime('%Y-%m-%d'),
                expiry_date.strftime('%Y-%m-%d')
            )
        
        # Get available HS codes by chapter
        print("1. FETCHING AVAILABLE HS CODES BY CHAPTER...")
        chapter_codes = {}
        for category, config in dumping_cases.items():
            for chapter in config["chapters"]:
                cursor.execute(
                    "SELECT hs_code FROM tariff_codes WHERE hs_code LIKE ? AND is_active = 1",
                    (f"{chapter}%",)
                )
                codes = [row[0] for row in cursor.fetchall()]
                if chapter not in chapter_codes:
                    chapter_codes[chapter] = []
                chapter_codes[chapter].extend(codes)
        
        total_available = sum(len(codes) for codes in chapter_codes.values())
        print(f"   Found {total_available:,} HS codes across {len(chapter_codes)} chapters")
        
        # Clear existing dumping duties (keep the 14 existing ones for now)
        print("\n2. PREPARING FOR NEW DATA...")
        cursor.execute("SELECT COUNT(*) FROM dumping_duties")
        existing_count = cursor.fetchone()[0]
        print(f"   Existing dumping duties: {existing_count}")
        print("   Will add new duties without clearing existing data")
        
        # Generate comprehensive dumping duties
        print(f"\n3. GENERATING ANTI-DUMPING DUTIES BY CATEGORY...")
        
        all_duties = []
        case_counter = 200  # Start from 200 to avoid conflicts
        
        # Target counts per category (total ~800 new duties)
        category_targets = {
            "steel_products": 300,
            "aluminum_products": 150,
            "chemical_products": 200,
            "paper_products": 100,
            "textile_products": 150
        }
        
        for category, target_count in category_targets.items():
            if category in dumping_cases:
                print(f"   Generating {target_count} duties for {category}...")
                
                config = dumping_cases[category]
                category_hs_codes = []
                
                # Get HS codes for this category
                for chapter in config["chapters"]:
                    if chapter in chapter_codes:
                        category_hs_codes.extend(chapter_codes[chapter])
                
                if not category_hs_codes:
                    print(f"   No HS codes found for {category}")
                    continue
                
                for i in range(target_count):
                    # Select random country and HS code
                    country = random.choice(config["countries"])
                    hs_code = random.choice(category_hs_codes)
                    
                    # Generate duty details
                    investigation_type = random.choice(config["investigation_types"])
                    duty_range = config["duty_ranges"][country]
                    duty_rate = round(random.uniform(duty_range[0], duty_range[1]), 2)
                    
                    # Generate dates (cases from 2019-2024)
                    year = random.choice([2019, 2020, 2021, 2022, 2023, 2024])
                    effective_date, expiry_date = get_random_dates(year)
                    
                    # Determine if duty is active (90% chance for recent years)
                    is_active = 1
                    if year < 2021:
                        is_active = random.choice([1, 0])
                    elif year == 2021:
                        is_active = random.choice([1, 1, 1, 0])  # 75% chance
                    
                    # Select exporter (30% chance of specific exporter)
                    exporter_name = None
                    if random.random() < 0.3 and country in config["major_exporters"]:
                        exporter_name = random.choice(config["major_exporters"][country])
                    
                    # Generate case details
                    case_number = generate_case_number(year, investigation_type, case_counter)
                    notice_number = generate_notice_number(year, random.randint(1, 12))
                    
                    duty_data = (
                        hs_code,
                        country,
                        exporter_name,
                        investigation_type,
                        duty_rate,
                        None,  # duty_amount (using percentage rates)
                        None,  # unit
                        effective_date,
                        expiry_date,
                        case_number,
                        f"{investigation_type.title()} investigation",
                        notice_number,
                        is_active,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    all_duties.append(duty_data)
                    case_counter += 1
        
        # Add some specific duties (per unit) for certain products
        print(f"   Generating specific duties for selected products...")
        
        specific_duty_products = [
            ("72081010", "CHN", 125.50, "tonne"),  # Hot-rolled steel
            ("72081020", "CHN", 98.75, "tonne"),   # Hot-rolled steel
            ("76011000", "CHN", 0.85, "kg"),       # Aluminum unwrought
            ("39011000", "IND", 0.12, "kg"),       # Polyethylene
            ("48025590", "CHN", 0.08, "kg"),       # Paper products
        ]
        
        for hs_code, country, amount, unit in specific_duty_products:
            year = random.choice([2022, 2023, 2024])
            effective_date, expiry_date = get_random_dates(year)
            case_number = generate_case_number(year, "dumping", case_counter)
            notice_number = generate_notice_number(year, random.randint(1, 12))
            
            duty_data = (
                hs_code,
                country,
                None,  # exporter_name
                "dumping",
                None,  # duty_rate
                amount,  # duty_amount
                unit,
                effective_date,
                expiry_date,
                case_number,
                "Dumping investigation",
                notice_number,
                1,  # is_active
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            all_duties.append(duty_data)
            case_counter += 1
        
        # Batch insert duties
        print(f"\n4. INSERTING {len(all_duties):,} ANTI-DUMPING DUTIES...")
        
        insert_sql = """
            INSERT INTO dumping_duties (
                hs_code, country_code, exporter_name, duty_type,
                duty_rate, duty_amount, unit, effective_date, expiry_date,
                case_number, investigation_type, notice_number, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        batch_size = 100
        for i in range(0, len(all_duties), batch_size):
            batch = all_duties[i:i + batch_size]
            cursor.executemany(insert_sql, batch)
            conn.commit()
            print(f"   Inserted batch {i//batch_size + 1}/{(len(all_duties) + batch_size - 1)//batch_size}")
        
        # Generate summary statistics
        print(f"\n5. GENERATING SUMMARY STATISTICS...")
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        # Country distribution
        cursor.execute("""
            SELECT country_code, COUNT(*) as count
            FROM dumping_duties 
            GROUP BY country_code
            ORDER BY count DESC
            LIMIT 10
        """)
        country_stats = cursor.fetchall()
        
        # Duty type distribution
        cursor.execute("""
            SELECT duty_type, COUNT(*) as count
            FROM dumping_duties 
            GROUP BY duty_type
            ORDER BY count DESC
        """)
        type_stats = cursor.fetchall()
        
        # Sample duties
        cursor.execute("""
            SELECT hs_code, country_code, duty_type, duty_rate, duty_amount, 
                   unit, case_number, is_active
            FROM dumping_duties 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        samples = cursor.fetchall()
        
        print("\n" + "=" * 80)
        print("ANTI-DUMPING DUTIES POPULATION SUMMARY")
        print("=" * 80)
        print(f"Total duties: {total_count:,}")
        print(f"Active duties: {active_count:,}")
        print(f"Inactive duties: {total_count - active_count:,}")
        
        print(f"\nTOP COUNTRIES BY DUTY COUNT:")
        for country, count in country_stats:
            print(f"   {country}: {count:,} duties")
        
        print(f"\nDUTIES BY TYPE:")
        for duty_type, count in type_stats:
            print(f"   {duty_type}: {count:,} duties")
        
        print(f"\nSAMPLE DUTIES:")
        for hs_code, country, duty_type, rate, amount, unit, case_num, is_active in samples:
            status = "Active" if is_active else "Inactive"
            if rate:
                duty_str = f"{rate}% ad valorem"
            elif amount and unit:
                duty_str = f"${amount}/{unit}"
            else:
                duty_str = "No duty specified"
            print(f"   {hs_code} - {country}: {duty_type}")
            print(f"      Duty: {duty_str}, Case: {case_num} ({status})")
        
        print("=" * 80)
        print("ANTI-DUMPING DUTIES POPULATION COMPLETED!")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"Error during dumping duties population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_dumping_duties()
