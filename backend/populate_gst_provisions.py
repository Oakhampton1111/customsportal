"""
Comprehensive GST Provisions Population Script
==============================================
Populates the database with realistic GST provisions and exemptions
based on Australian GST legislation patterns.
"""

import sqlite3
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple, Optional

def populate_gst_provisions():
    """Populate comprehensive GST provisions dataset."""
    
    print("=" * 80)
    print("COMPREHENSIVE GST PROVISIONS POPULATION")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect('customs_portal.db')
        cursor = conn.cursor()
        
        # GST provision categories based on Australian GST Act
        gst_categories = {
            "food_and_beverages": {
                "chapters": ["04", "07", "08", "09", "10", "11", "15", "16", "17", "18", "19", "20", "21", "22"],
                "exemption_types": ["gst_free", "input_taxed", "reduced_rate"],
                "provisions": [
                    {
                        "description": "Fresh fruit and vegetables",
                        "schedule": "Schedule 2, Item 1",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Must be fresh and unprocessed"
                    },
                    {
                        "description": "Bread and bread rolls",
                        "schedule": "Schedule 2, Item 2", 
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Excludes luxury breads and pastries"
                    },
                    {
                        "description": "Milk and dairy products",
                        "schedule": "Schedule 2, Item 3",
                        "exemption_type": "gst_free", 
                        "threshold": None,
                        "conditions": "Basic dairy products only"
                    },
                    {
                        "description": "Meat and poultry",
                        "schedule": "Schedule 2, Item 4",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Fresh, chilled or frozen meat"
                    },
                    {
                        "description": "Seafood",
                        "schedule": "Schedule 2, Item 5",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Fresh, chilled or frozen seafood"
                    }
                ]
            },
            "medical_and_health": {
                "chapters": ["30", "90"],
                "exemption_types": ["gst_free", "input_taxed"],
                "provisions": [
                    {
                        "description": "Pharmaceutical products listed on PBS",
                        "schedule": "Schedule 3, Item 1",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Must be listed on Pharmaceutical Benefits Scheme"
                    },
                    {
                        "description": "Medical devices and equipment",
                        "schedule": "Schedule 3, Item 2",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Therapeutic goods registered with TGA"
                    },
                    {
                        "description": "Prosthetic and orthotic devices",
                        "schedule": "Schedule 3, Item 3",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Prescribed by medical practitioner"
                    },
                    {
                        "description": "Hearing aids and accessories",
                        "schedule": "Schedule 3, Item 4",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "Fitted by qualified audiologist"
                    }
                ]
            },
            "education_and_childcare": {
                "chapters": ["49", "95"],
                "exemption_types": ["gst_free", "input_taxed"],
                "provisions": [
                    {
                        "description": "Educational textbooks and materials",
                        "schedule": "Schedule 3, Item 10",
                        "exemption_type": "gst_free",
                        "threshold": None,
                        "conditions": "For use in formal education courses"
                    },
                    {
                        "description": "Children's toys and educational materials",
                        "schedule": "Schedule 3, Item 11",
                        "exemption_type": "gst_free",
                        "threshold": 50.00,
                        "conditions": "Educational toys for children under 14"
                    }
                ]
            },
            "low_value_imports": {
                "chapters": ["all"],
                "exemption_types": ["low_value", "de_minimis"],
                "provisions": [
                    {
                        "description": "Low value goods imported by post",
                        "schedule": "Schedule 4, Item 17",
                        "exemption_type": "low_value",
                        "threshold": 1000.00,
                        "conditions": "Goods imported by post with value not exceeding $1,000"
                    },
                    {
                        "description": "Low value goods imported other than by post",
                        "schedule": "Schedule 4, Item 18",
                        "exemption_type": "low_value",
                        "threshold": 1000.00,
                        "conditions": "Goods imported other than by post with value not exceeding $1,000"
                    },
                    {
                        "description": "Personal gifts",
                        "schedule": "Schedule 4, Item 19",
                        "exemption_type": "low_value",
                        "threshold": 1000.00,
                        "conditions": "Gifts sent to individuals, not for commercial purposes"
                    }
                ]
            },
            "diplomatic_and_official": {
                "chapters": ["all"],
                "exemption_types": ["diplomatic", "official"],
                "provisions": [
                    {
                        "description": "Diplomatic missions goods",
                        "schedule": "Schedule 4, Item 3",
                        "exemption_type": "diplomatic",
                        "threshold": None,
                        "conditions": "Goods imported by diplomatic missions"
                    },
                    {
                        "description": "Consular officers goods",
                        "schedule": "Schedule 4, Item 4",
                        "exemption_type": "diplomatic",
                        "threshold": None,
                        "conditions": "Goods imported by consular officers"
                    },
                    {
                        "description": "International organization goods",
                        "schedule": "Schedule 4, Item 5",
                        "exemption_type": "official",
                        "threshold": None,
                        "conditions": "Goods imported by recognized international organizations"
                    }
                ]
            },
            "manufacturing_inputs": {
                "chapters": ["28", "29", "39", "40", "54", "55", "72", "73", "74", "76", "84", "85"],
                "exemption_types": ["manufacturing", "duty_concession"],
                "provisions": [
                    {
                        "description": "Raw materials for manufacturing",
                        "schedule": "Schedule 4, Item 20",
                        "exemption_type": "manufacturing",
                        "threshold": 10000.00,
                        "conditions": "Materials used in approved manufacturing processes"
                    },
                    {
                        "description": "Machinery and equipment for manufacturing",
                        "schedule": "Schedule 4, Item 21",
                        "exemption_type": "manufacturing",
                        "threshold": 50000.00,
                        "conditions": "Machinery used in approved manufacturing facilities"
                    },
                    {
                        "description": "Components for local assembly",
                        "schedule": "Schedule 4, Item 22",
                        "exemption_type": "manufacturing",
                        "threshold": 5000.00,
                        "conditions": "Components assembled into finished goods in Australia"
                    }
                ]
            },
            "agricultural_inputs": {
                "chapters": ["01", "02", "03", "05", "06", "12", "23", "31", "84"],
                "exemption_types": ["agricultural", "primary_production"],
                "provisions": [
                    {
                        "description": "Live animals for breeding",
                        "schedule": "Schedule 4, Item 12",
                        "exemption_type": "agricultural",
                        "threshold": None,
                        "conditions": "Live animals imported for breeding purposes"
                    },
                    {
                        "description": "Seeds and planting materials",
                        "schedule": "Schedule 4, Item 13",
                        "exemption_type": "agricultural",
                        "threshold": None,
                        "conditions": "Seeds and plants for agricultural production"
                    },
                    {
                        "description": "Agricultural machinery",
                        "schedule": "Schedule 4, Item 14",
                        "exemption_type": "agricultural",
                        "threshold": 25000.00,
                        "conditions": "Machinery used in primary production"
                    },
                    {
                        "description": "Fertilizers and agricultural chemicals",
                        "schedule": "Schedule 4, Item 15",
                        "exemption_type": "agricultural",
                        "threshold": None,
                        "conditions": "Approved fertilizers and chemicals for agricultural use"
                    }
                ]
            },
            "transport_and_vehicles": {
                "chapters": ["86", "87", "88", "89"],
                "exemption_types": ["transport", "temporary_import"],
                "provisions": [
                    {
                        "description": "Temporary import of vehicles",
                        "schedule": "Schedule 4, Item 25",
                        "exemption_type": "temporary_import",
                        "threshold": None,
                        "conditions": "Vehicles temporarily imported for specific purposes"
                    },
                    {
                        "description": "Commercial vehicle parts",
                        "schedule": "Schedule 4, Item 26",
                        "exemption_type": "transport",
                        "threshold": 2000.00,
                        "conditions": "Parts for commercial transport vehicles"
                    }
                ]
            },
            "energy_and_resources": {
                "chapters": ["25", "26", "27"],
                "exemption_types": ["energy", "resources"],
                "provisions": [
                    {
                        "description": "Renewable energy equipment",
                        "schedule": "Schedule 4, Item 30",
                        "exemption_type": "energy",
                        "threshold": 100000.00,
                        "conditions": "Equipment for renewable energy generation"
                    },
                    {
                        "description": "Mining equipment and machinery",
                        "schedule": "Schedule 4, Item 31",
                        "exemption_type": "resources",
                        "threshold": 75000.00,
                        "conditions": "Equipment used in mining operations"
                    }
                ]
            }
        }
        
        def get_random_hs_codes_for_chapters(chapters: List[str], count: int) -> List[str]:
            """Get random HS codes for specified chapters."""
            if "all" in chapters:
                cursor.execute("SELECT hs_code FROM tariff_codes WHERE is_active = 1 ORDER BY RANDOM() LIMIT ?", (count,))
            else:
                chapter_conditions = " OR ".join([f"hs_code LIKE '{chapter}%'" for chapter in chapters])
                cursor.execute(
                    f"SELECT hs_code FROM tariff_codes WHERE ({chapter_conditions}) AND is_active = 1 ORDER BY RANDOM() LIMIT ?",
                    (count,)
                )
            return [row[0] for row in cursor.fetchall()]
        
        # Get available HS codes by category
        print("1. FETCHING AVAILABLE HS CODES BY CATEGORY...")
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE is_active = 1")
        total_hs_codes = cursor.fetchone()[0]
        print(f"   Total active HS codes: {total_hs_codes:,}")
        
        # Clear existing GST provisions (keep the 11 existing ones for now)
        print("\n2. PREPARING FOR NEW DATA...")
        cursor.execute("SELECT COUNT(*) FROM gst_provisions")
        existing_count = cursor.fetchone()[0]
        print(f"   Existing GST provisions: {existing_count}")
        print("   Will add new provisions without clearing existing data")
        
        # Generate comprehensive GST provisions
        print(f"\n3. GENERATING GST PROVISIONS BY CATEGORY...")
        
        all_provisions = []
        
        # Target counts per category (total ~600 new provisions)
        category_targets = {
            "food_and_beverages": 120,
            "medical_and_health": 80,
            "education_and_childcare": 40,
            "low_value_imports": 30,  # These are general provisions
            "diplomatic_and_official": 20,  # These are general provisions
            "manufacturing_inputs": 150,
            "agricultural_inputs": 100,
            "transport_and_vehicles": 60,
            "energy_and_resources": 40
        }
        
        for category, target_count in category_targets.items():
            if category in gst_categories:
                print(f"   Generating {target_count} provisions for {category}...")
                
                config = gst_categories[category]
                
                # Get HS codes for this category (except for general provisions)
                if config["chapters"] == ["all"]:
                    # General provisions - no specific HS codes
                    category_hs_codes = [None] * target_count
                else:
                    category_hs_codes = get_random_hs_codes_for_chapters(config["chapters"], target_count)
                    # Pad with None if not enough HS codes
                    while len(category_hs_codes) < target_count:
                        category_hs_codes.append(None)
                
                for i in range(target_count):
                    # Select base provision template
                    base_provision = random.choice(config["provisions"])
                    
                    # Get HS code (may be None for general provisions)
                    hs_code = category_hs_codes[i] if i < len(category_hs_codes) else None
                    
                    # Generate variations of the base provision
                    if category == "food_and_beverages":
                        descriptions = [
                            f"Fresh {random.choice(['organic', 'locally grown', 'imported'])} produce",
                            f"{random.choice(['Frozen', 'Canned', 'Dried'])} food products",
                            f"Basic food items for human consumption",
                            f"Unprocessed {random.choice(['meat', 'dairy', 'grain'])} products",
                            f"Essential food items under health regulations"
                        ]
                        description = random.choice(descriptions)
                    elif category == "medical_and_health":
                        descriptions = [
                            f"Medical devices for {random.choice(['diagnostic', 'therapeutic', 'surgical'])} use",
                            f"Pharmaceutical products for {random.choice(['chronic', 'acute', 'preventive'])} treatment",
                            f"Health equipment for {random.choice(['hospitals', 'clinics', 'home care'])}",
                            f"Prosthetic devices and {random.choice(['mobility aids', 'hearing aids', 'vision aids'])}",
                            f"Medical supplies for {random.choice(['emergency', 'routine', 'specialized'])} care"
                        ]
                        description = random.choice(descriptions)
                    elif category == "manufacturing_inputs":
                        descriptions = [
                            f"Raw materials for {random.choice(['automotive', 'electronics', 'textiles', 'chemical'])} manufacturing",
                            f"Industrial {random.choice(['machinery', 'equipment', 'tools'])} for production",
                            f"Components for {random.choice(['assembly', 'processing', 'packaging'])} operations",
                            f"Manufacturing supplies for {random.choice(['quality control', 'safety', 'efficiency'])}",
                            f"Production inputs for {random.choice(['export', 'domestic', 'specialized'])} markets"
                        ]
                        description = random.choice(descriptions)
                    elif category == "agricultural_inputs":
                        descriptions = [
                            f"Agricultural {random.choice(['seeds', 'fertilizers', 'pesticides'])} for crop production",
                            f"Livestock {random.choice(['feed', 'medicines', 'equipment'])} for farming",
                            f"Farm machinery for {random.choice(['planting', 'harvesting', 'processing'])}",
                            f"Irrigation and {random.choice(['water management', 'soil improvement'])} equipment",
                            f"Agricultural supplies for {random.choice(['organic', 'sustainable', 'commercial'])} farming"
                        ]
                        description = random.choice(descriptions)
                    else:
                        # Use base description with minor variations
                        variations = [
                            base_provision["description"],
                            f"Specialized {base_provision['description'].lower()}",
                            f"Commercial {base_provision['description'].lower()}",
                            f"Professional {base_provision['description'].lower()}"
                        ]
                        description = random.choice(variations)
                    
                    # Generate schedule reference variations
                    schedule_base = base_provision["schedule"].split(",")[0]  # Get base schedule
                    item_num = random.randint(1, 50)
                    schedule_ref = f"{schedule_base}, Item {item_num}"
                    
                    # Determine exemption type
                    exemption_type = random.choice(config["exemption_types"])
                    
                    # Set threshold based on exemption type and category
                    threshold = None
                    if base_provision["threshold"]:
                        # Add some variation to the threshold
                        base_threshold = base_provision["threshold"]
                        variation = random.uniform(0.8, 1.2)  # ±20% variation
                        threshold = round(base_threshold * variation, 2)
                    elif exemption_type in ["manufacturing", "agricultural"] and category not in ["low_value_imports", "diplomatic_and_official"]:
                        # Set random thresholds for manufacturing/agricultural
                        threshold_ranges = {
                            "manufacturing": (5000.00, 100000.00),
                            "agricultural": (1000.00, 50000.00),
                            "transport": (2000.00, 25000.00),
                            "energy": (50000.00, 200000.00)
                        }
                        if exemption_type in threshold_ranges:
                            min_val, max_val = threshold_ranges[exemption_type]
                            threshold = round(random.uniform(min_val, max_val), 2)
                    
                    # Generate conditions
                    conditions = base_provision["conditions"]
                    if random.random() < 0.3:  # 30% chance of additional conditions
                        additional_conditions = [
                            "Subject to customs verification",
                            "Requires prior approval from relevant authority",
                            "Must meet Australian standards",
                            "Limited to registered importers",
                            "Subject to annual review"
                        ]
                        conditions += f". {random.choice(additional_conditions)}"
                    
                    provision_data = (
                        hs_code,
                        schedule_ref,
                        exemption_type,
                        description,
                        threshold,
                        conditions,
                        1,  # is_active
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    all_provisions.append(provision_data)
        
        # Add some specific high-value exemptions
        print(f"   Generating specific high-value exemptions...")
        
        high_value_exemptions = [
            ("84", "manufacturing", "Industrial machinery for export manufacturing", 500000.00),
            ("85", "manufacturing", "Electronic equipment for technology manufacturing", 300000.00),
            ("87", "transport", "Commercial vehicles for transport operators", 150000.00),
            ("90", "medical", "Advanced medical equipment for hospitals", 1000000.00),
            ("88", "transport", "Aircraft parts and components", 2000000.00)
        ]
        
        for chapter, exemption_type, desc, threshold in high_value_exemptions:
            # Get random HS codes from the chapter
            cursor.execute(
                "SELECT hs_code FROM tariff_codes WHERE hs_code LIKE ? AND is_active = 1 ORDER BY RANDOM() LIMIT 5",
                (f"{chapter}%",)
            )
            hs_codes = [row[0] for row in cursor.fetchall()]
            
            for hs_code in hs_codes:
                provision_data = (
                    hs_code,
                    f"Schedule 4, Item {random.randint(50, 99)}",
                    exemption_type,
                    desc,
                    threshold,
                    "Subject to ministerial approval and compliance verification",
                    1,  # is_active
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                all_provisions.append(provision_data)
        
        # Batch insert provisions
        print(f"\n4. INSERTING {len(all_provisions):,} GST PROVISIONS...")
        
        insert_sql = """
            INSERT INTO gst_provisions (
                hs_code, schedule_reference, exemption_type, description,
                value_threshold, conditions, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        batch_size = 100
        for i in range(0, len(all_provisions), batch_size):
            batch = all_provisions[i:i + batch_size]
            cursor.executemany(insert_sql, batch)
            conn.commit()
            print(f"   Inserted batch {i//batch_size + 1}/{(len(all_provisions) + batch_size - 1)//batch_size}")
        
        # Generate summary statistics
        print(f"\n5. GENERATING SUMMARY STATISTICS...")
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        # Exemption type distribution
        cursor.execute("""
            SELECT exemption_type, COUNT(*) as count
            FROM gst_provisions 
            GROUP BY exemption_type
            ORDER BY count DESC
        """)
        type_stats = cursor.fetchall()
        
        # Threshold distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN value_threshold IS NULL THEN 'No threshold'
                    WHEN value_threshold < 1000 THEN 'Under $1,000'
                    WHEN value_threshold < 10000 THEN '$1,000 - $10,000'
                    WHEN value_threshold < 50000 THEN '$10,000 - $50,000'
                    WHEN value_threshold < 100000 THEN '$50,000 - $100,000'
                    ELSE 'Over $100,000'
                END as threshold_range,
                COUNT(*) as count
            FROM gst_provisions 
            GROUP BY threshold_range
            ORDER BY count DESC
        """)
        threshold_stats = cursor.fetchall()
        
        # Sample provisions
        cursor.execute("""
            SELECT hs_code, exemption_type, description, value_threshold, 
                   schedule_reference, is_active
            FROM gst_provisions 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        samples = cursor.fetchall()
        
        print("\n" + "=" * 80)
        print("GST PROVISIONS POPULATION SUMMARY")
        print("=" * 80)
        print(f"Total provisions: {total_count:,}")
        print(f"Active provisions: {active_count:,}")
        print(f"Inactive provisions: {total_count - active_count:,}")
        
        print(f"\nPROVISIONS BY EXEMPTION TYPE:")
        for exemption_type, count in type_stats:
            print(f"   {exemption_type}: {count:,} provisions")
        
        print(f"\nPROVISIONS BY THRESHOLD RANGE:")
        for threshold_range, count in threshold_stats:
            print(f"   {threshold_range}: {count:,} provisions")
        
        print(f"\nSAMPLE PROVISIONS:")
        for hs_code, exemption_type, desc, threshold, schedule_ref, is_active in samples:
            status = "Active" if is_active else "Inactive"
            hs_display = hs_code if hs_code else "General"
            threshold_str = f"${threshold:,.2f}" if threshold else "No threshold"
            desc_short = desc[:60] + "..." if len(desc) > 60 else desc
            print(f"   {hs_display}: {exemption_type}")
            print(f"      {desc_short}")
            print(f"      Schedule: {schedule_ref}, Threshold: {threshold_str} ({status})")
        
        print("=" * 80)
        print("GST PROVISIONS POPULATION COMPLETED!")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"Error during GST provisions population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_gst_provisions()
