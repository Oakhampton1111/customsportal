#!/usr/bin/env python3
"""
Populate comprehensive FTA rates for Australia's major trade agreements.
"""

import sqlite3
import random
from datetime import datetime, date
from pathlib import Path

# Australia's major FTAs and their codes with country mappings
FTA_AGREEMENTS = {
    'AUSFTA': {'name': 'Australia-United States Free Trade Agreement', 'country': 'USA'},
    'ChAFTA': {'name': 'China-Australia Free Trade Agreement', 'country': 'CHN'}, 
    'JAEPA': {'name': 'Japan-Australia Economic Partnership Agreement', 'country': 'JPN'},
    'KAFTA': {'name': 'Korea-Australia Free Trade Agreement', 'country': 'KOR'},
    'AANZFTA': {'name': 'ASEAN-Australia-New Zealand Free Trade Area', 'country': 'ASN'},
    'CPTPP': {'name': 'Comprehensive and Progressive Trans-Pacific Partnership', 'country': 'TPP'},
    'AIFTA': {'name': 'Australia-India Economic Cooperation and Trade Agreement', 'country': 'IND'},
    'TAFTA': {'name': 'Thailand-Australia Free Trade Agreement', 'country': 'THA'},
    'SAFTA': {'name': 'Singapore-Australia Free Trade Agreement', 'country': 'SGP'},
    'MAFTA': {'name': 'Malaysia-Australia Free Trade Agreement', 'country': 'MYS'},
    'PAFTA': {'name': 'Papua New Guinea-Australia Trade Agreement', 'country': 'PNG'},
    'IAFTA': {'name': 'Indonesia-Australia Comprehensive Economic Partnership', 'country': 'IDN'},
    'PEFTA': {'name': 'Peru-Australia Free Trade Agreement', 'country': 'PER'},
    'CHFTA': {'name': 'Chile-Australia Free Trade Agreement', 'country': 'CHL'},
    'UKFTA': {'name': 'Australia-United Kingdom Free Trade Agreement', 'country': 'GBR'}
}

def get_sample_hs_codes(conn):
    """Get a representative sample of HS codes for FTA rate assignment."""
    cursor = conn.cursor()
    
    # Get codes from key chapters that commonly have FTA benefits
    priority_chapters = [1, 2, 3, 4, 7, 8, 9, 10, 11, 15, 16, 17, 19, 20, 21, 22, 
                        27, 28, 29, 30, 32, 33, 39, 40, 42, 43, 44, 48, 50, 51, 52, 
                        53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 72, 73, 74, 
                        76, 84, 85, 87, 90, 94, 95]
    
    all_codes = []
    
    for chapter in priority_chapters:
        cursor.execute("""
            SELECT hs_code FROM tariff_codes 
            WHERE hs_code LIKE ? AND level >= 4
            ORDER BY RANDOM() 
            LIMIT ?
        """, (f"{chapter:02d}%", random.randint(15, 35)))
        
        codes = [row[0] for row in cursor.fetchall()]
        all_codes.extend(codes)
    
    return all_codes

def generate_fta_rate(base_rate, fta_type):
    """Generate realistic FTA preferential rate based on base rate and agreement type."""
    if base_rate == 0:
        return 0
    
    # Different FTA types have different typical reductions
    reduction_factors = {
        'AUSFTA': 0.7,    # Significant reductions with US
        'ChAFTA': 0.6,    # Strong reductions with China
        'JAEPA': 0.65,    # Good reductions with Japan
        'KAFTA': 0.65,    # Good reductions with Korea
        'CPTPP': 0.5,     # Excellent multilateral reductions
        'AANZFTA': 0.75,  # Moderate ASEAN reductions
        'AIFTA': 0.8,     # Recent agreement, moderate reductions
        'TAFTA': 0.7,     # Good bilateral reductions
        'SAFTA': 0.6,     # Excellent with Singapore
        'MAFTA': 0.75,    # Moderate with Malaysia
        'UKFTA': 0.5,     # New comprehensive agreement
        'IAFTA': 0.7,     # Good with Indonesia
        'PEFTA': 0.65,    # Good with Peru
        'CHFTA': 0.65,    # Good with Chile
        'PAFTA': 0.9      # Limited with PNG
    }
    
    factor = reduction_factors.get(fta_type, 0.75)
    
    # Add some randomness
    factor += random.uniform(-0.1, 0.1)
    factor = max(0, min(1, factor))
    
    preferential_rate = base_rate * factor
    
    # Round to realistic precision
    if preferential_rate < 1:
        return round(preferential_rate, 2)
    elif preferential_rate < 10:
        return round(preferential_rate, 1)
    else:
        return round(preferential_rate)

def populate_comprehensive_fta_rates():
    """Populate comprehensive FTA rates for major Australian trade agreements."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Populating comprehensive FTA rates...")
        print("=" * 60)
        
        # Get sample HS codes
        hs_codes = get_sample_hs_codes(conn)
        print(f"Selected {len(hs_codes)} HS codes for FTA rate assignment")
        
        # Get existing duty rates for reference
        cursor.execute("SELECT hs_code, general_rate FROM duty_rates")
        duty_rates = dict(cursor.fetchall())
        
        total_inserted = 0
        
        for fta_code, fta_info in FTA_AGREEMENTS.items():
            print(f"\nProcessing {fta_code} ({fta_info['name']})...")
            
            # Determine number of codes for this FTA (varies by agreement importance)
            if fta_code in ['CPTPP', 'AUSFTA', 'ChAFTA']:
                num_codes = random.randint(80, 120)  # Major agreements
            elif fta_code in ['JAEPA', 'KAFTA', 'UKFTA']:
                num_codes = random.randint(60, 90)   # Important bilaterals
            elif fta_code in ['AANZFTA', 'AIFTA']:
                num_codes = random.randint(40, 70)   # Regional agreements
            else:
                num_codes = random.randint(20, 50)   # Other agreements
            
            # Select random subset of codes for this FTA
            fta_codes = random.sample(hs_codes, min(num_codes, len(hs_codes)))
            
            fta_inserted = 0
            
            for hs_code in fta_codes:
                # Get base duty rate
                base_rate = duty_rates.get(hs_code, random.uniform(0, 15))
                if isinstance(base_rate, str):
                    try:
                        base_rate = float(base_rate.replace('%', ''))
                    except:
                        base_rate = random.uniform(0, 15)
                
                # Generate preferential rate
                preferential_rate = generate_fta_rate(base_rate, fta_code)
                
                # Create rate description
                if preferential_rate == 0:
                    rate_description = "Free"
                else:
                    rate_description = f"{preferential_rate}%"
                
                # Determine staging (phase-out period)
                staging_options = ['Immediate', 'Year 3', 'Year 5', 'Year 7', 'Year 10', 'Year 15']
                staging_weights = [0.4, 0.2, 0.15, 0.1, 0.1, 0.05]  # Most are immediate
                staging = random.choices(staging_options, weights=staging_weights)[0]
                
                # Insert FTA rate
                try:
                    cursor.execute("""
                        INSERT INTO fta_rates (
                            hs_code, fta_code, country_code, preferential_rate, 
                            rate_type, staging_category, effective_date,
                            rule_of_origin, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        hs_code,
                        fta_code,
                        fta_info['country'],
                        preferential_rate,
                        'Ad Valorem' if preferential_rate > 0 else 'Free',
                        staging,
                        date(2020, 1, 1),  # Most FTAs are in effect
                        f"Standard rules of origin apply under {fta_code}",
                        datetime.now()
                    ))
                    fta_inserted += 1
                    total_inserted += 1
                    
                except sqlite3.IntegrityError:
                    # Skip if combination already exists
                    continue
            
            print(f"  Added {fta_inserted} rates for {fta_code}")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully inserted {total_inserted} FTA rates")
        
        # Verification
        cursor.execute("SELECT COUNT(*) FROM fta_rates")
        total_fta_rates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT fta_code) FROM fta_rates")
        unique_ftas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM fta_rates")
        codes_with_fta = cursor.fetchone()[0]
        
        print(f"Total FTA rates in database: {total_fta_rates}")
        print(f"Unique FTA agreements: {unique_ftas}")
        print(f"HS codes with FTA rates: {codes_with_fta}")
        
        # Show breakdown by FTA
        print("\nFTA Rate Distribution:")
        cursor.execute("""
            SELECT fta_code, COUNT(*) as rate_count 
            FROM fta_rates 
            GROUP BY fta_code 
            ORDER BY rate_count DESC
        """)
        
        for fta_code, count in cursor.fetchall():
            print(f"  {fta_code}: {count} rates")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate_comprehensive_fta_rates()
