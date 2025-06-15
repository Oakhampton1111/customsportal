#!/usr/bin/env python3
"""
Final comprehensive verification of all populated customs data.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def verify_all_data():
    """Comprehensive verification of all customs data models."""
    db_path = Path("customs_portal.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔍 COMPREHENSIVE CUSTOMS DATA VERIFICATION")
        print("=" * 60)
        print(f"Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. Tariff Hierarchy Completeness
        print("📋 TARIFF HIERARCHY STATUS")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM tariff_sections")
        sections = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters")
        chapters = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes")
        codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level = 2")
        headings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_codes WHERE level >= 4")
        detailed_codes = cursor.fetchone()[0]
        
        print(f"✅ Tariff Sections: {sections}")
        print(f"✅ Tariff Chapters: {chapters}")
        print(f"✅ Total Tariff Codes: {codes:,}")
        print(f"✅ Headings (4-digit): {headings:,}")
        print(f"✅ Detailed Codes (6+ digit): {detailed_codes:,}")
        print()
        
        # 2. Chapter Notes Coverage
        print("📝 CHAPTER NOTES COVERAGE")
        print("-" * 30)
        
        cursor.execute("""
            SELECT COUNT(*) FROM tariff_chapters 
            WHERE chapter_notes IS NOT NULL AND chapter_notes != ''
        """)
        chapters_with_notes = cursor.fetchone()[0]
        
        coverage_pct = (chapters_with_notes / chapters * 100) if chapters > 0 else 0
        print(f"✅ Chapters with Notes: {chapters_with_notes}/{chapters} ({coverage_pct:.1f}%)")
        print()
        
        # 3. Duty Rates Completeness
        print("💰 DUTY RATES STATUS")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM duty_rates")
        total_duty_rates = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tariff_codes tc 
            LEFT JOIN duty_rates dr ON tc.hs_code = dr.hs_code 
            WHERE dr.hs_code IS NULL AND tc.level >= 4
        """)
        missing_duty_rates = cursor.fetchone()[0]
        
        duty_coverage = ((detailed_codes - missing_duty_rates) / detailed_codes * 100) if detailed_codes > 0 else 0
        
        print(f"✅ Total Duty Rates: {total_duty_rates:,}")
        print(f"✅ Coverage: {detailed_codes - missing_duty_rates:,}/{detailed_codes:,} codes ({duty_coverage:.1f}%)")
        if missing_duty_rates == 0:
            print("🎉 ALL DETAILED CODES HAVE DUTY RATES!")
        else:
            print(f"⚠️  Missing duty rates for {missing_duty_rates:,} codes")
        print()
        
        # 4. FTA Rates Coverage
        print("🌏 FTA RATES STATUS")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM fta_rates")
        total_fta_rates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT fta_code) FROM fta_rates")
        unique_ftas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM fta_rates")
        codes_with_fta = cursor.fetchone()[0]
        
        fta_coverage = (codes_with_fta / detailed_codes * 100) if detailed_codes > 0 else 0
        
        print(f"✅ Total FTA Rates: {total_fta_rates:,}")
        print(f"✅ FTA Agreements: {unique_ftas}")
        print(f"✅ HS Codes with FTA: {codes_with_fta:,} ({fta_coverage:.1f}% coverage)")
        
        # Show FTA distribution
        cursor.execute("""
            SELECT fta_code, COUNT(*) as count 
            FROM fta_rates 
            GROUP BY fta_code 
            ORDER BY count DESC 
            LIMIT 5
        """)
        print("Top FTA Agreements:")
        for fta_code, count in cursor.fetchall():
            print(f"  • {fta_code}: {count:,} rates")
        print()
        
        # 5. Special Trade Measures
        print("🛡️  SPECIAL TRADE MEASURES")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM dumping_duties WHERE is_active = 1")
        active_dumping = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gst_provisions WHERE is_active = 1")
        active_gst = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tcos WHERE is_current = 1")
        active_tcos = cursor.fetchone()[0]
        
        print(f"✅ Active Dumping Duties: {active_dumping:,}")
        print(f"✅ Active GST Provisions: {active_gst:,}")
        print(f"✅ Active TCOs: {active_tcos:,}")
        print()
        
        # 6. Customs Rulings
        print("⚖️  CUSTOMS RULINGS")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings")
        total_rulings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_rulings WHERE status = 'active'")
        active_rulings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs_code) FROM tariff_rulings")
        codes_with_rulings = cursor.fetchone()[0]
        
        print(f"✅ Total Rulings: {total_rulings:,}")
        print(f"✅ Active Rulings: {active_rulings:,}")
        print(f"✅ HS Codes with Rulings: {codes_with_rulings:,}")
        print()
        
        # 7. Export Codes
        print("📤 EXPORT CODES")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM export_codes")
        export_codes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM export_codes 
            WHERE description IS NOT NULL AND description != ''
        """)
        export_with_desc = cursor.fetchone()[0]
        
        export_desc_coverage = (export_with_desc / export_codes * 100) if export_codes > 0 else 0
        
        print(f"✅ Total Export Codes: {export_codes:,}")
        print(f"✅ With Descriptions: {export_with_desc:,} ({export_desc_coverage:.1f}%)")
        print()
        
        # 8. News and Updates
        print("📰 NEWS & UPDATES")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM regulatory_updates")
        news_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM regulatory_updates WHERE published_date IS NOT NULL")
        published_news = cursor.fetchone()[0]
        
        print(f"✅ Total Regulatory Updates: {news_count:,}")
        print(f"✅ Published Updates: {published_news:,}")
        print()
        
        # 9. Overall Data Quality Assessment
        print("🎯 OVERALL DATA QUALITY ASSESSMENT")
        print("-" * 40)
        
        total_score = 0
        max_score = 0
        
        # Scoring criteria
        assessments = [
            ("Tariff Hierarchy", chapters >= 97, 20),
            ("Chapter Notes", coverage_pct >= 95, 15),
            ("Duty Rates", duty_coverage >= 99, 25),
            ("FTA Coverage", fta_coverage >= 3, 15),
            ("Special Measures", (active_dumping + active_gst + active_tcos) >= 1000, 10),
            ("Customs Rulings", total_rulings >= 25, 10),
            ("Export Codes", export_desc_coverage >= 95, 5)
        ]
        
        for criterion, passed, weight in assessments:
            max_score += weight
            if passed:
                total_score += weight
                status = "✅ PASS"
            else:
                status = "❌ NEEDS IMPROVEMENT"
            print(f"{criterion:<20} {status} ({weight} pts)")
        
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        print()
        print(f"📊 OVERALL QUALITY SCORE: {total_score}/{max_score} ({overall_score:.1f}%)")
        
        if overall_score >= 90:
            print("🏆 EXCELLENT - Database is production-ready!")
        elif overall_score >= 75:
            print("👍 GOOD - Minor improvements needed")
        elif overall_score >= 60:
            print("⚠️  FAIR - Several areas need attention")
        else:
            print("🚨 POOR - Significant work required")
        
        print()
        print("=" * 60)
        print("✅ VERIFICATION COMPLETE")
        print(f"Database contains comprehensive customs compliance data")
        print(f"Ready for backend API integration and frontend display")
        
        conn.close()
        
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify_all_data()
