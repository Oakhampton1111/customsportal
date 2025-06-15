#!/usr/bin/env python3
"""
Check data completeness and quality across all populated tables.
"""

import sqlite3
from pathlib import Path

def check_data_completeness():
    """Check data completeness and identify gaps."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("="*80)
        print("DATA COMPLETENESS & QUALITY ANALYSIS")
        print("="*80)
        
        # 1. Tariff Codes Analysis
        print("\n1. TARIFF CODES COMPLETENESS:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes")
        total_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE description IS NOT NULL AND description != ''")
        codes_with_desc = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE unit_description IS NOT NULL AND unit_description != ''")
        codes_with_units = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        codes_with_notes = cursor.fetchone()[0]
        
        print(f"Total tariff codes: {total_codes}")
        print(f"Codes with descriptions: {codes_with_desc} ({codes_with_desc/total_codes*100:.1f}%)")
        print(f"Codes with unit descriptions: {codes_with_units} ({codes_with_units/total_codes*100:.1f}%)")
        print(f"Codes with chapter notes: {codes_with_notes} ({codes_with_notes/total_codes*100:.1f}%)")
        
        # 2. Duty Rates Analysis
        print("\n2. DUTY RATES COMPLETENESS:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM duty_rates")
        total_duties = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM duty_rates")
        codes_with_duties = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM duty_rates WHERE general_rate IS NOT NULL")
        duties_with_general = cursor.fetchone()[0]
        
        print(f"Total duty rate records: {total_duties}")
        print(f"Unique HS codes with duties: {codes_with_duties}")
        print(f"Records with general rates: {duties_with_general} ({duties_with_general/total_duties*100:.1f}%)")
        
        # 3. FTA Rates Analysis
        print("\n3. FTA RATES COMPLETENESS:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM fta_rates")
        total_fta = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT fta_code) FROM fta_rates")
        unique_ftas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM fta_rates")
        codes_with_fta = cursor.fetchone()[0]
        
        print(f"Total FTA rate records: {total_fta}")
        print(f"Unique FTA agreements: {unique_ftas}")
        print(f"HS codes with FTA rates: {codes_with_fta}")
        
        # 4. Export Codes Analysis
        print("\n4. EXPORT CODES (AHECC) COMPLETENESS:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        total_exports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_codes WHERE description IS NOT NULL AND description != ''")
        exports_with_desc = cursor.fetchone()[0]
        
        print(f"Total export codes: {total_exports}")
        print(f"Codes with descriptions: {exports_with_desc} ({exports_with_desc/total_exports*100:.1f}%)")
        
        # 5. Special Trade Measures
        print("\n5. SPECIAL TRADE MEASURES:")
        print("-" * 40)
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE is_active = 1")
        active_dumping = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE is_active = 1")
        active_gst = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE is_current = 1")
        active_tcos = cursor.fetchone()[0]
        
        print(f"Active anti-dumping duties: {active_dumping}")
        print(f"Active GST provisions: {active_gst}")
        print(f"Active TCOs: {active_tcos}")
        
        # 6. Data Quality Issues
        print("\n6. POTENTIAL DATA QUALITY ISSUES:")
        print("-" * 40)
        
        issues = []
        
        # Check for missing duty rates
        cursor.execute("""
            SELECT COUNT(*) FROM tariff_codes tc 
            LEFT JOIN duty_rates dr ON tc.hs_code = dr.hs_code 
            WHERE dr.hs_code IS NULL AND tc.level >= 4
        """)
        missing_duties = cursor.fetchone()[0]
        if missing_duties > 0:
            issues.append(f"❌ {missing_duties} detailed tariff codes missing duty rates")
        
        # Check for very low FTA coverage
        if codes_with_fta < 100:
            issues.append(f"⚠️  Very low FTA coverage ({codes_with_fta} codes)")
        
        # Check chapter notes coverage
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NULL OR chapter_notes = ''")
        missing_chapter_notes = cursor.fetchone()[0]
        if missing_chapter_notes > 0:
            issues.append(f"❌ {missing_chapter_notes} chapters missing notes")
        
        if not issues:
            print("✅ No major data quality issues detected!")
        else:
            for issue in issues:
                print(issue)
        
        # 7. Recommendations
        print("\n7. RECOMMENDATIONS FOR IMPROVEMENT:")
        print("-" * 40)
        
        recommendations = []
        
        if codes_with_fta < 1000:
            recommendations.append("📈 Expand FTA rates coverage - currently very limited")
        
        if missing_duties > 0:
            recommendations.append("📈 Add duty rates for all detailed tariff codes")
        
        # Check if we have recent data
        cursor.execute("SELECT COUNT(*) FROM news_items WHERE created_at > date('now', '-30 days')")
        recent_news = cursor.fetchone()[0]
        if recent_news == 0:
            recommendations.append("📰 Add recent trade news and updates")
        
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings")
        total_rulings = cursor.fetchone()[0]
        if total_rulings < 10:
            recommendations.append("⚖️ Add more customs classification rulings")
        
        if not recommendations:
            print("🎉 Database appears to be comprehensively populated!")
        else:
            for rec in recommendations:
                print(rec)
        
        print("\n" + "="*80)
        print("OVERALL ASSESSMENT:")
        print("="*80)
        
        # Calculate overall completeness score
        completeness_score = 0
        max_score = 0
        
        # Tariff codes (30 points)
        max_score += 30
        completeness_score += min(30, (codes_with_desc/total_codes) * 30)
        
        # Duty rates (25 points)
        max_score += 25
        if total_codes > 0:
            duty_coverage = codes_with_duties / total_codes
            completeness_score += min(25, duty_coverage * 25)
        
        # Special measures (20 points)
        max_score += 20
        if active_dumping > 500 and active_gst > 500 and active_tcos > 1000:
            completeness_score += 20
        elif active_dumping > 200 and active_gst > 200 and active_tcos > 500:
            completeness_score += 15
        else:
            completeness_score += 10
        
        # Export codes (15 points)
        max_score += 15
        if total_exports > 3000:
            completeness_score += 15
        elif total_exports > 1000:
            completeness_score += 10
        else:
            completeness_score += 5
        
        # Chapter notes (10 points)
        max_score += 10
        if missing_chapter_notes == 0:
            completeness_score += 10
        
        final_score = (completeness_score / max_score) * 100
        
        print(f"DATABASE COMPLETENESS SCORE: {final_score:.1f}/100")
        
        if final_score >= 90:
            print("🌟 EXCELLENT - Database is comprehensively populated!")
        elif final_score >= 80:
            print("✅ VERY GOOD - Database is well populated with minor gaps")
        elif final_score >= 70:
            print("👍 GOOD - Database is adequately populated")
        else:
            print("⚠️  NEEDS IMPROVEMENT - Significant data gaps remain")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data_completeness()
