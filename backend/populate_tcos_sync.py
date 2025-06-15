"""
Comprehensive TCO Population Script (Synchronous Version)
========================================================
Populates the database with a comprehensive, realistic dataset of Australian TCOs.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple

def populate_comprehensive_tcos():
    """Populate comprehensive TCO dataset using direct SQLite connection."""
    
    print("=" * 80)
    print("🏗️  COMPREHENSIVE TCO POPULATION")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        # TCO categories based on Australian industry patterns
        tco_categories = {
            "automotive": {
                "chapters": ["84", "85", "87"],
                "descriptions": [
                    "Electric vehicle battery systems",
                    "Hybrid powertrain components", 
                    "Advanced driver assistance systems",
                    "Automotive semiconductor chips",
                    "Electric motor controllers",
                    "Regenerative braking systems",
                    "Charging infrastructure equipment",
                    "Vehicle telematics systems",
                    "Autonomous vehicle sensors",
                    "Lightweight composite panels"
                ],
                "applicants": [
                    "Tesla Motors Australia",
                    "Ford Motor Company",
                    "General Motors Holden",
                    "Toyota Motor Corporation",
                    "Hyundai Motor Company",
                    "BMW Group Australia",
                    "Mercedes-Benz Australia",
                    "Volkswagen Group Australia",
                    "Nissan Motor Co",
                    "Automotive Components Ltd"
                ]
            },
            "mining": {
                "chapters": ["84", "85", "73", "72"],
                "descriptions": [
                    "Underground mining equipment",
                    "Ore processing machinery",
                    "Mining truck components",
                    "Drilling equipment systems",
                    "Conveyor belt systems",
                    "Crushing and grinding equipment",
                    "Mineral separation equipment",
                    "Mining safety systems",
                    "Automated mining vehicles",
                    "Specialized steel alloys"
                ],
                "applicants": [
                    "BHP Billiton Limited",
                    "Rio Tinto Australia",
                    "Fortescue Metals Group",
                    "Newcrest Mining Limited",
                    "Anglo American Australia",
                    "Glencore Coal Assets",
                    "Caterpillar Underground Mining",
                    "Komatsu Australia",
                    "Sandvik Mining Systems",
                    "Atlas Copco Australia"
                ]
            },
            "manufacturing": {
                "chapters": ["84", "85", "90", "39", "76"],
                "descriptions": [
                    "Industrial automation systems",
                    "Precision manufacturing equipment",
                    "Quality control instruments",
                    "Robotic assembly systems",
                    "Advanced materials processing",
                    "Packaging machinery",
                    "Testing and measurement equipment",
                    "Computer numerical control systems",
                    "Additive manufacturing equipment",
                    "Specialized polymer compounds"
                ],
                "applicants": [
                    "Schneider Electric Australia",
                    "Siemens Australia",
                    "ABB Australia",
                    "Rockwell Automation",
                    "Honeywell Process Solutions",
                    "Emerson Process Management",
                    "Yokogawa Australia",
                    "Endress+Hauser Australia",
                    "SICK Sensors Australia",
                    "Festo Pty Ltd"
                ]
            },
            "telecommunications": {
                "chapters": ["85", "90"],
                "descriptions": [
                    "5G network infrastructure",
                    "Fiber optic equipment",
                    "Satellite communication systems",
                    "Network switching equipment",
                    "Wireless transmission systems",
                    "Data center equipment",
                    "Optical networking components",
                    "Telecommunications testing equipment",
                    "Mobile base station equipment",
                    "Network security appliances"
                ],
                "applicants": [
                    "Telstra Corporation",
                    "Optus Networks",
                    "Vodafone Hutchison Australia",
                    "NBN Co Limited",
                    "Ericsson Australia",
                    "Nokia Networks Australia",
                    "Huawei Technologies",
                    "Cisco Systems Australia",
                    "Juniper Networks",
                    "CommScope Australia"
                ]
            },
            "renewable_energy": {
                "chapters": ["84", "85", "76"],
                "descriptions": [
                    "Solar panel manufacturing equipment",
                    "Wind turbine components",
                    "Energy storage systems",
                    "Power conversion equipment",
                    "Grid integration systems",
                    "Smart grid technology",
                    "Battery management systems",
                    "Renewable energy controllers",
                    "Energy monitoring systems",
                    "Specialized aluminum frames"
                ],
                "applicants": [
                    "AGL Energy Limited",
                    "Origin Energy Limited",
                    "EnergyAustralia Holdings",
                    "Snowy Hydro Limited",
                    "Neoen Australia",
                    "Acciona Energy Australia",
                    "Goldwind Australia",
                    "Vestas Australian Wind Technology",
                    "General Electric Renewable Energy",
                    "Tesla Energy Australia"
                ]
            },
            "aerospace": {
                "chapters": ["88", "84", "85", "76"],
                "descriptions": [
                    "Aircraft engine components",
                    "Avionics systems",
                    "Composite aircraft structures",
                    "Navigation equipment",
                    "Aircraft maintenance equipment",
                    "Satellite components",
                    "Aerospace testing equipment",
                    "Flight control systems",
                    "Aircraft communication systems",
                    "Specialized titanium alloys"
                ],
                "applicants": [
                    "Boeing Australia Limited",
                    "Airbus Australia Pacific",
                    "Lockheed Martin Australia",
                    "BAE Systems Australia",
                    "Thales Australia",
                    "Northrop Grumman Australia",
                    "Raytheon Australia",
                    "Collins Aerospace",
                    "Safran Helicopter Engines",
                    "Rolls-Royce Australia"
                ]
            },
            "medical": {
                "chapters": ["90", "84", "85"],
                "descriptions": [
                    "Medical imaging equipment",
                    "Surgical instruments",
                    "Patient monitoring systems",
                    "Laboratory equipment",
                    "Diagnostic equipment",
                    "Therapeutic devices",
                    "Medical device components",
                    "Sterilization equipment",
                    "Rehabilitation equipment",
                    "Telemedicine systems"
                ],
                "applicants": [
                    "Siemens Healthineers",
                    "GE Healthcare Australia",
                    "Philips Healthcare",
                    "Medtronic Australasia",
                    "Abbott Laboratories",
                    "Johnson & Johnson Medical",
                    "Roche Diagnostics Australia",
                    "Becton Dickinson Australia",
                    "Stryker Australia",
                    "Baxter Healthcare"
                ]
            },
            "agriculture": {
                "chapters": ["84", "85", "87"],
                "descriptions": [
                    "Precision agriculture equipment",
                    "Automated harvesting systems",
                    "Irrigation control systems",
                    "Agricultural drone systems",
                    "Soil analysis equipment",
                    "Livestock monitoring systems",
                    "Grain handling equipment",
                    "Agricultural vehicle components",
                    "Farm management software systems",
                    "Specialized farming implements"
                ],
                "applicants": [
                    "John Deere Australia",
                    "Case IH Australia",
                    "New Holland Agriculture",
                    "AGCO Australia",
                    "Kubota Tractor Australia",
                    "Trimble Agriculture",
                    "Topcon Positioning Australia",
                    "Raven Industries Australia",
                    "Valley Irrigation Australia",
                    "Netafim Australia"
                ]
            }
        }
        
        def generate_tco_number(counter: int, year: int) -> str:
            """Generate realistic TCO number."""
            return f"TCO-{year}-{counter:04d}"
        
        def get_random_dates(year: int) -> Tuple[str, str, str]:
            """Generate realistic effective, expiry, and gazette dates."""
            # Gazette date: random date in the year
            gazette_day = random.randint(1, 365)
            gazette_date = date(year, 1, 1) + timedelta(days=gazette_day - 1)
            
            # Effective date: 30-90 days after gazette
            effective_offset = random.randint(30, 90)
            effective_date = gazette_date + timedelta(days=effective_offset)
            
            # Expiry date: 1-3 years after effective date
            expiry_years = random.randint(1, 3)
            expiry_date = effective_date + timedelta(days=expiry_years * 365)
            
            return (
                effective_date.strftime('%Y-%m-%d'),
                expiry_date.strftime('%Y-%m-%d'),
                gazette_date.strftime('%Y-%m-%d')
            )
        
        def get_gazette_number(gazette_date_str: str) -> str:
            """Generate realistic gazette number."""
            gazette_date = datetime.strptime(gazette_date_str, '%Y-%m-%d').date()
            year = gazette_date.year
            week = gazette_date.isocalendar()[1]
            return f"C{year}G{week:02d}"
        
        def generate_substitutable_goods_text(category: str) -> str:
            """Generate realistic substitutable goods determination text."""
            templates = [
                f"No substitutable goods of Australian origin are commercially available that are suitable for the intended use in {category} applications.",
                f"Goods of Australian origin that are substitutable are not available in commercial quantities or within a reasonable time for {category} requirements.",
                f"The applicant has demonstrated that no Australian-made goods are suitable substitutes for the specific {category} application requirements.",
                f"Technical specifications require goods not available from Australian manufacturers for {category} industry use.",
                f"Specialized {category} equipment with no commercially viable Australian alternatives available."
            ]
            return random.choice(templates)
        
        def generate_technical_specs() -> str:
            """Generate technical specifications for TCO descriptions."""
            specs = [
                "meeting specific technical requirements",
                "with advanced performance characteristics",
                "incorporating proprietary technology",
                "designed for specialized applications",
                "with enhanced durability specifications",
                "featuring integrated control systems",
                "with precision manufacturing tolerances",
                "incorporating safety-critical components",
                "designed for extreme operating conditions",
                "with specialized material composition"
            ]
            return random.choice(specs)
        
        # Get available HS codes
        print("1. 📊 FETCHING AVAILABLE HS CODES...")
        cursor.execute("SELECT hs_code FROM tariff_codes WHERE is_active = 1 ORDER BY hs_code")
        available_hs_codes = [row[0] for row in cursor.fetchall()]
        print(f"   Found {len(available_hs_codes):,} available HS codes")
        
        if not available_hs_codes:
            print("❌ No HS codes available for TCO generation")
            return
        
        # Clear existing TCO data
        print("\n2. 🧹 CLEARING EXISTING TCO DATA...")
        cursor.execute("DELETE FROM tcos")
        conn.commit()
        print("   Cleared existing TCO records")
        
        # Define target counts per category (total ~1620 TCOs)
        category_targets = {
            "automotive": 250,
            "mining": 230,
            "manufacturing": 200,
            "telecommunications": 160,
            "renewable_energy": 150,
            "aerospace": 120,
            "medical": 110,
            "agriculture": 100
        }
        
        print(f"\n3. 🏭 GENERATING TCOs BY CATEGORY...")
        
        all_tcos = []
        tco_counter = 1
        
        # Generate TCOs for each category
        for category, target_count in category_targets.items():
            if category in tco_categories:
                print(f"   Generating {target_count} TCOs for {category}...")
                
                config = tco_categories[category]
                category_hs_codes = []
                
                # Filter HS codes by chapter
                for chapter in config["chapters"]:
                    chapter_codes = [code for code in available_hs_codes if code.startswith(chapter)]
                    category_hs_codes.extend(chapter_codes)
                
                if not category_hs_codes:
                    print(f"   ⚠️  No HS codes found for {category} chapters: {config['chapters']}")
                    continue
                
                for i in range(target_count):
                    # Generate TCO for different years (2020-2024)
                    year = random.choice([2020, 2021, 2022, 2023, 2024])
                    
                    # Select random HS code from category
                    hs_code = random.choice(category_hs_codes)
                    
                    # Generate dates
                    effective_date, expiry_date, gazette_date = get_random_dates(year)
                    
                    # Determine if TCO is current (90% chance for recent years)
                    is_current = 1
                    if year < 2022:
                        is_current = random.choice([1, 0])
                    elif year == 2022:
                        is_current = random.choice([1, 1, 1, 0])  # 75% chance
                    
                    # If expired, mark as not current
                    expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                    if expiry_date_obj < date.today():
                        is_current = 0
                    
                    tco_data = (
                        generate_tco_number(tco_counter, year),
                        hs_code,
                        f"{random.choice(config['descriptions'])}, {generate_technical_specs()}",
                        random.choice(config["applicants"]),
                        effective_date,
                        expiry_date,
                        gazette_date,
                        get_gazette_number(gazette_date),
                        generate_substitutable_goods_text(category),
                        is_current,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    all_tcos.append(tco_data)
                    tco_counter += 1
        
        # Batch insert TCOs
        print(f"\n4. 💾 INSERTING {len(all_tcos):,} TCOs INTO DATABASE...")
        
        insert_sql = """
            INSERT INTO tcos (
                tco_number, hs_code, description, applicant_name,
                effective_date, expiry_date, gazette_date, gazette_number,
                substitutable_goods_determination, is_current, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        batch_size = 100
        for i in range(0, len(all_tcos), batch_size):
            batch = all_tcos[i:i + batch_size]
            cursor.executemany(insert_sql, batch)
            conn.commit()
            print(f"   Inserted batch {i//batch_size + 1}/{(len(all_tcos) + batch_size - 1)//batch_size}")
        
        # Verify insertion and generate statistics
        print(f"\n5. 📊 GENERATING SUMMARY STATISTICS...")
        
        cursor.execute("SELECT COUNT(*) FROM tcos")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE is_current = 1")
        active_count = cursor.fetchone()[0]
        
        # Chapter distribution
        cursor.execute("""
            SELECT SUBSTR(hs_code, 1, 2) as chapter, COUNT(*) as count
            FROM tcos 
            GROUP BY SUBSTR(hs_code, 1, 2)
            ORDER BY count DESC
            LIMIT 10
        """)
        chapter_stats = cursor.fetchall()
        
        # Year distribution
        cursor.execute("""
            SELECT SUBSTR(effective_date, 1, 4) as year, COUNT(*) as count
            FROM tcos 
            WHERE effective_date IS NOT NULL
            GROUP BY SUBSTR(effective_date, 1, 4)
            ORDER BY year DESC
        """)
        year_stats = cursor.fetchall()
        
        # Sample TCOs
        cursor.execute("""
            SELECT tco_number, hs_code, description, applicant_name, is_current
            FROM tcos 
            ORDER BY tco_number
            LIMIT 10
        """)
        samples = cursor.fetchall()
        
        print("\n" + "=" * 80)
        print("📊 TCO POPULATION SUMMARY")
        print("=" * 80)
        print(f"✅ Total TCOs: {total_count:,}")
        print(f"✅ Active TCOs: {active_count:,}")
        print(f"✅ Inactive TCOs: {total_count - active_count:,}")
        
        print(f"\n📈 TOP CHAPTERS BY TCO COUNT:")
        for chapter, count in chapter_stats:
            print(f"   Chapter {chapter}: {count:,} TCOs")
        
        print(f"\n📅 TCOs BY YEAR:")
        for year, count in year_stats:
            print(f"   {year}: {count:,} TCOs")
        
        print(f"\n🔍 SAMPLE TCOs:")
        for tco_num, hs_code, desc, applicant, is_current in samples:
            status = "Active" if is_current else "Inactive"
            desc_short = desc[:50] + "..." if len(desc) > 50 else desc
            print(f"   {tco_num}: {hs_code} - {desc_short} ({status})")
            print(f"      Applicant: {applicant}")
        
        print("=" * 80)
        print("✅ TCO POPULATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during TCO population: {e}")
        raise

if __name__ == "__main__":
    populate_comprehensive_tcos()
