#!/usr/bin/env python3
"""
Populate chapter notes for all tariff chapters.
Chapter notes provide important guidance for customs classification.
"""

import sqlite3
from pathlib import Path

# Chapter notes based on Australian Harmonized Tariff Schedule
CHAPTER_NOTES = {
    1: """This Chapter covers all live animals except:
(a) Fish and crustaceans, molluscs and other aquatic invertebrates (Chapter 3);
(b) Cultures of micro-organisms and other products of heading 30.02;
(c) Animals of heading 95.08.""",
    
    2: """This Chapter does not cover:
(a) Products unfit for human consumption;
(b) Guts, bladders or stomachs of animals (heading 05.04) or blood (heading 05.11 or 30.02);
(c) Animal fats, other than products of heading 02.09 (Chapter 15).""",
    
    3: """This Chapter does not cover:
(a) Marine mammals (heading 01.06);
(b) Meat of marine mammals (heading 02.08 or 02.09);
(c) Fish (including livers and roes) and crustaceans, molluscs and other aquatic invertebrates, dead and unfit for human consumption by reason of either their species or their condition (Chapter 5);
(d) Caviar and caviar substitutes prepared from fish eggs (heading 16.04).""",
    
    4: """This Chapter does not cover:
(a) Butter (heading 04.05);
(b) Cheese and curd (heading 04.06);
(c) Preparations containing cocoa (Chapter 18);
(d) Preparations containing coffee (heading 21.01);
(e) Flavoured or coloured sugar syrups (heading 21.06);
(f) Pharmaceutical products (Chapter 30);
(g) Cosmetic or toilet preparations (Chapter 33);
(h) Albumins (heading 35.02) or gelatin (heading 35.03).""",
    
    5: """This Chapter does not cover:
(a) Edible products (other than guts, bladders and stomachs of animals, whole and pieces thereof, and animal blood, liquid or dried);
(b) Hides or skins (including furskins) other than goods of heading 05.05 and parings and similar waste of raw hides or skins of heading 05.11 (Chapter 41 or 43);
(c) Animal textile materials, other than horsehair and horsehair waste (Section XI);
(d) Prepared knots or tufts for broom or brush making (heading 96.03).""",
    
    6: """This Chapter covers only live trees and goods (including seedlings, plants, roots, cut flowers and ornamental foliage) of a kind commonly supplied by nursery gardeners or florists for planting or for ornamental use; nevertheless it does not cover potatoes, onions, shallots, garlic or other products of Chapter 7.""",
    
    7: """This Chapter does not cover forage products of heading 12.14.
In this Chapter the term "vegetables" includes edible mushrooms, truffles, olives, capers, marrows, pumpkins, aubergines, sweet corn (Zea mays var. saccharata), fruits of the genus Capsicum or of the genus Pimenta, fennel, parsley, chervil, tarragon, cress and sweet marjoram (Majorana hortensis or Origanum majorana).""",
    
    8: """This Chapter does not cover nuts or fruits used primarily for the extraction of oil (Chapter 12).
In this Chapter the term "nuts" means coconuts, Brazil nuts, cashew nuts, hazelnuts or filberts, walnuts, chestnuts, pistachios, macadamia nuts, kola nuts, areca nuts, pine nuts and similar nuts, whether or not shelled or peeled.""",
    
    9: """Mixtures of the products of headings 09.04 to 09.10 are to be classified as follows:
(a) Mixtures of two or more of the products of the same heading are to be classified in that heading;
(b) Mixtures of products of different headings are to be classified in heading 09.10.
The products of heading 09.10 may contain added flavouring.""",
    
    10: """This Chapter does not cover:
(a) Vegetables of the leguminous species (Chapter 7);
(b) Sweet corn (Chapter 7);
(c) Cereal straw and husks, unprepared, whether or not chopped, ground, pressed or in the form of pellets (heading 12.13);
(d) Cereal straw and husks, prepared, or cereal straw prepared as stuffing for mattresses (heading 14.01)."""
}

def populate_chapter_notes():
    """Populate chapter notes in the database."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Populating chapter notes...")
        updated_count = 0
        
        for chapter_num, notes in CHAPTER_NOTES.items():
            cursor.execute("""
                UPDATE tariff_chapters 
                SET chapter_notes = ? 
                WHERE chapter_number = ?
            """, (notes, chapter_num))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"Updated Chapter {chapter_num:02d}")
        
        conn.commit()
        print(f"\nSuccessfully updated {updated_count} chapters with notes")
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        total_with_notes = cursor.fetchone()[0]
        print(f"Total chapters with notes: {total_with_notes}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error populating chapter notes: {e}")

if __name__ == "__main__":
    populate_chapter_notes()
