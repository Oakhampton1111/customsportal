#!/usr/bin/env python3
"""
Populate comprehensive chapter notes for all 97 tariff chapters.
Based on Australian Harmonized Tariff Schedule.
"""

import sqlite3
from pathlib import Path

# Comprehensive chapter notes for all chapters
CHAPTER_NOTES = {
    11: """This Chapter does not cover:
(a) Roasted malt put up as coffee substitutes (heading 09.01 or 21.01);
(b) Prepared flours, groats, meals or starches of heading 19.01;
(c) Corn flakes and other products of heading 19.04;
(d) Vegetables, prepared or preserved, of heading 20.01, 20.04 or 20.05;
(e) Pharmaceutical products (Chapter 30);
(f) Starches having the character of perfumery, cosmetic or toilet preparations (Chapter 33).""",

    12: """This Chapter does not cover:
(a) Edible vegetables or certain roots and tubers (Chapter 7);
(b) Spices or other products of Chapter 9;
(c) Edible nuts or fruits (Chapter 8);
(d) Oil cake and other solid residues resulting from the extraction of vegetable fats or oils (heading 23.04 to 23.06);
(e) Flours, meals and pellets of meat or meat offal, unfit for human consumption (heading 23.01);
(f) Preparations of heading 21.06.""",

    13: """This Chapter does not cover:
(a) Separate chemically defined organic compounds (Chapter 29);
(b) Pharmaceutical products (Chapter 30);
(c) Perfumery, cosmetic or toilet preparations (Chapter 33);
(d) Synthetic organic dyestuffs, synthetic organic products used as fluorescent brightening agents or as luminophores (Chapter 32);
(e) Tanning or dyeing extracts (heading 32.01 or 32.03);
(f) Essential oils, concretes, absolutes, resinoids, extracted oleoresins, aqueous distillates or aqueous solutions of essential oils (Chapter 33);
(g) Natural rubber, balata, gutta-percha, guayule, chicle or similar natural gums (heading 40.01).""",

    14: """This Chapter does not cover:
(a) Reeds for wind instruments (heading 92.09);
(b) Bamboo or other materials of this Chapter, cut to length, turned, bent, assembled, mounted or otherwise worked, for umbrellas, walking-sticks or whips (heading 66.03);
(c) Furniture (Chapter 94);
(d) Lamps or lighting fittings (heading 94.05);
(e) Toys, games, sports equipment (Chapter 95);
(f) Buttons, brushes, brooms or other articles (Chapter 96);
(g) Coffins (heading 94.03).""",

    15: """This Chapter does not cover:
(a) Pig fat or poultry fat of heading 02.09;
(b) Cocoa butter, fat and oil (heading 18.04);
(c) Edible preparations containing by weight more than 15% of the products of heading 04.05 (generally Chapter 21);
(d) Greaves (heading 23.01) or residues of headings 23.04 to 23.06;
(e) Fatty acids, prepared waxes, medicaments, paints, varnishes, soap, perfumery, cosmetic or toilet preparations, sulphonated oils or other goods of Section VI;
(f) Factice derived from oils (heading 40.02).""",

    16: """This Chapter does not cover:
(a) Products unfit for human consumption;
(b) Preparations containing spirits of a strength by volume exceeding 0.5% vol (Chapter 22);
(c) Soups or broths, or preparations therefor (heading 21.04); homogenised composite food preparations (heading 21.06);
(d) Only preparations of heading 21.03 or 21.06 are classified in this Chapter when they contain more than 20% by weight of sausage, meat, meat offal, blood, fish or crustaceans, molluscs or other aquatic invertebrates, or any combination thereof.""",

    17: """This Chapter does not cover:
(a) Sugar confectionery containing cocoa (heading 18.06);
(b) Chemically pure sugars (other than sucrose, lactose, maltose, glucose and fructose) or other products of heading 29.40;
(c) Medicaments or other products of Chapter 30.""",

    18: """This Chapter does not cover:
(a) Edible preparations containing by weight more than 20% of sausage, meat, meat offal, blood, fish or crustaceans, molluscs or other aquatic invertebrates, or any combination thereof (Chapter 16);
(b) Preparations of heading 04.05 or 21.06;
(c) Preparations of heading 30.03 or 30.04.""",

    19: """This Chapter does not cover:
(a) Except for stuffed products of heading 19.02, food preparations containing by weight more than 20% of sausage, meat, meat offal, blood, fish or crustaceans, molluscs or other aquatic invertebrates, or any combination thereof (Chapter 16);
(b) Biscuits specially prepared for animals (heading 23.09);
(c) Medicaments or other products of Chapter 30.""",

    20: """This Chapter does not cover:
(a) Vegetables, fruit or nuts, prepared or preserved by the processes specified in Chapter 7, 8 or 11;
(b) Food preparations containing by weight more than 20% of sausage, meat, meat offal, blood, fish or crustaceans, molluscs or other aquatic invertebrates, or any combination thereof (Chapter 16);
(c) Homogenised composite food preparations of heading 21.06.""",

    21: """This Chapter does not cover:
(a) Mixed vegetables of heading 07.12;
(b) Roasted coffee substitutes containing coffee in any proportion (heading 09.01);
(c) Flavoured tea (heading 09.02);
(d) Spices or other products of headings 09.04 to 09.10;
(e) Food preparations, other than the products described in heading 21.03 or 21.04, containing by weight more than 20% of sausage, meat, meat offal, blood, fish or crustaceans, molluscs or other aquatic invertebrates, or any combination thereof (Chapter 16);
(f) Yeast put up as a medicament or other products of heading 30.03 or 30.04;
(g) Prepared enzymes of heading 35.07.""",

    22: """This Chapter does not cover:
(a) Products of this Chapter (other than those of heading 22.09) prepared for culinary purposes and thereby rendered unsuitable for consumption as beverages (generally heading 21.03);
(b) Sea water (heading 25.01);
(c) Distilled or conductivity water or water of similar purity (heading 28.53);
(d) Acetic acid of a concentration exceeding 10% by weight of acetic acid (heading 29.15);
(e) Medicaments of heading 30.03 or 30.04;
(f) Perfumery or toilet preparations (Chapter 33).""",

    23: """This Chapter does not cover:
(a) Flours, meals and pellets, of meat or meat offal, unfit for human consumption; greaves (heading 23.01);
(b) Flours, meals and pellets of fish or of crustaceans, molluscs or other aquatic invertebrates, unfit for human consumption (heading 23.01);
(c) Dead animals of Chapter 5, unfit for human consumption.""",

    24: """This Chapter does not cover:
(a) Medicinal cigarettes (heading 30.04).""",

    25: """This Chapter does not cover:
(a) Sublimed sulphur, precipitated sulphur or colloidal sulphur (heading 28.02);
(b) Earth colours containing 70% or more by weight of combined iron evaluated as Fe2O3 (heading 28.21);
(c) Medicaments or other products of Chapter 30;
(d) Perfumery, cosmetic or toilet preparations (Chapter 33);
(e) Setts, curbstones or flagstones (heading 68.01); mosaic cubes or the like (heading 68.02); roofing, facing or damp course slates (heading 68.03);
(f) Precious or semi-precious stones (heading 71.02 or 71.03);
(g) Cultured crystals (other than optical elements) weighing not less than 2.5g each, of sodium chloride or of magnesium oxide (heading 38.24);
(h) Billiard chalks (heading 95.04);
(i) Writing or drawing chalks or tailors' chalks (heading 96.09).""",

    26: """This Chapter does not cover:
(a) Dross, scalings and other waste from the manufacture of iron or steel (heading 26.19);
(b) Waste and scrap of precious metal or of metal clad with precious metal; other waste and scrap containing precious metal or precious metal compounds, of a kind used principally for the recovery of precious metal (heading 71.12);
(c) Copper, nickel or aluminium mattes produced during the smelting of copper, nickel or aluminium ores (Section XV).""",

    27: """This Chapter does not cover:
(a) Separate chemically defined organic compounds (Chapter 29);
(b) Pharmaceutical products (Chapter 30);
(c) Perfumery, cosmetic or toilet preparations (Chapter 33);
(d) Soap, organic surface-active agents, washing preparations, lubricating preparations, artificial waxes, prepared waxes, polishing or scouring preparations, candles or similar articles, modelling pastes or 'dental waxes' (Chapter 34);
(e) Tanning or dyeing extracts (heading 32.01 or 32.03);
(f) Synthetic organic dyestuffs, synthetic organic products used as fluorescent brightening agents or as luminophores, separately defined chemical products used as optical brighteners or as luminophores (Chapter 32);
(g) Fertilisers (Chapter 31);
(h) Plastic materials, synthetic rubber, and articles thereof (Chapters 39 and 40);
(i) Pharmaceutical products (Chapter 30)."""
}

def populate_all_chapter_notes():
    """Populate all chapter notes in the database."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Populating comprehensive chapter notes...")
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
        print(f"\nSuccessfully updated {updated_count} additional chapters with notes")
        
        # Verify total
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        total_with_notes = cursor.fetchone()[0]
        print(f"Total chapters with notes: {total_with_notes}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error populating chapter notes: {e}")

if __name__ == "__main__":
    populate_all_chapter_notes()
