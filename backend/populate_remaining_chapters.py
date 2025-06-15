#!/usr/bin/env python3
"""
Populate remaining chapter notes (28-97) for tariff chapters.
"""

import sqlite3
from pathlib import Path

# Remaining chapter notes (28-97)
REMAINING_NOTES = {
    28: """This Chapter does not cover:
(a) Separate chemically defined elements or compounds (except those of heading 28.43 to 28.46, 28.52, 28.54 to 28.56, 28.58, 28.61, 28.62 and 28.65);
(b) Products of Section VI (pharmaceutical products, etc.);
(c) Products of Section XI (textiles and textile articles);
(d) Precious metal compounds, amalgams of precious metals, and other products of Section XIV;
(e) Radioactive elements and compounds (heading 28.44).""",

    29: """This Chapter does not cover:
(a) Products of heading 15.04 and glycerol (heading 15.20);
(b) Ethyl alcohol (heading 22.07 or 22.08);
(c) Methane and propane (heading 27.11);
(d) Compounds of carbon with metals (heading 28.43);
(e) Urea (heading 31.02 or 31.05);
(f) Colouring matter of vegetable or animal origin (heading 32.03), synthetic organic colouring matter, synthetic organic products used as fluorescent brightening agents or as luminophores (heading 32.04) and dyes and other colouring matter put up in forms or packings for retail sale (heading 32.06);
(g) Enzymes (heading 35.07);
(h) Metaldehyde, hexamethylenetetramine or similar substances, put up in forms (for example, tablets, sticks or similar forms) for use as fuels, or liquid or liquefied-gas fuels in containers of a kind used for filling or refilling cigarette or similar lighters and of a capacity not exceeding 300 cm³ (heading 36.06);
(i) Products put up as charges for fire-extinguishers or put up in fire-extinguishing grenades (heading 38.13); ink removers put up in packings for retail sale (heading 38.24);
(j) Optical elements (Chapter 90).""",

    30: """This Chapter does not cover:
(a) Foods or beverages (such as dietetic, diabetic or fortified foods, food supplements, tonic beverages and mineral waters), other than nutritional preparations administered intravenously (Section IV);
(b) Plasters specially calcined or finely ground for use in dentistry (heading 25.20);
(c) Aqueous distillates or aqueous solutions of essential oils, suitable for medicinal uses (heading 33.01);
(d) Preparations of headings 33.03 to 33.07, even if they have therapeutic or prophylactic properties;
(e) Soap or other products of heading 34.01 containing added medicaments;
(f) Preparations with a basis of plaster for use in dentistry (heading 34.07);
(g) Blood albumin not prepared for therapeutic or prophylactic uses (heading 35.02).""",

    31: """This Chapter does not cover:
(a) Animal blood (heading 05.11);
(b) Separate chemically defined compounds (other than those answering to the descriptions in Note 2 (A), 3 (A), 4 (A) or 5 below);
(c) Cultured crystals (other than optical elements) weighing not less than 2.5g each, of potassium dihydrogen orthophosphate or of potassium dideuterium orthophosphate (heading 38.24);
(d) Medicaments (heading 30.03 or 30.04);
(e) Products of Chapter 38 (for example, disinfectants, insecticides).""",

    32: """This Chapter does not cover:
(a) Separate chemically defined elements or compounds (Chapter 28 or 29);
(b) Medicaments of heading 30.03 or 30.04;
(c) Cosmetic or toilet preparations (Chapter 33).""",

    33: """This Chapter does not cover:
(a) Separate chemically defined organic compounds (Chapter 29);
(b) Medicaments or other products of Chapter 30;
(c) Soap and other products of heading 34.01.""",

    34: """This Chapter does not cover:
(a) Edible mixtures or preparations of animal or vegetable fats or oils of heading 15.17;
(b) Separate chemically defined compounds;
(c) Shampoos, dentifrices, shaving creams and foams, or bath preparations, containing soap or other organic surface-active agents (heading 33.05, 33.06 or 33.07);
(d) Products of heading 38.08 (insecticides, etc.);
(e) Medicaments (heading 30.03 or 30.04).""",

    35: """This Chapter does not cover:
(a) Yeasts (heading 21.02);
(b) Blood fractions (other than blood albumin not prepared for therapeutic or prophylactic uses), medicaments or other products of Chapter 30;
(c) Enzymatic preparations for pre-tanning (heading 32.02);
(d) Enzymatic soaking or washing preparations or other products of Chapter 34;
(e) Hardened proteins (heading 39.13);
(f) Gelatin products of the printing industry (Chapter 49).""",

    36: """This Chapter does not cover:
(a) Separate chemically defined compounds (other than those of heading 36.06);
(b) Medicaments (heading 30.03 or 30.04).""",

    37: """This Chapter does not cover:
(a) Sensitised paper or paperboard for photography (heading 48.09);
(b) Cinematograph film, exposed and developed (Chapter 49).""",

    38: """This Chapter does not cover:
(a) Separate chemically defined elements or compounds, other than the following:
(1) Artificial graphite (heading 38.01);
(2) Insecticides, rodenticides, fungicides, herbicides, anti-sprouting products and plant-growth regulators, disinfectants and similar products, put up as described in heading 38.08;
(3) Products put up as charges for fire-extinguishers or put up in fire-extinguishing grenades (heading 38.13);
(4) Certified reference materials specified in Note 2 below;
(5) Products specified in Note 3 (a) or 3 (c) below;
(b) Mixtures of chemicals with foodstuffs or other substances with nutritive value, of a kind used in the preparation of human food (generally heading 21.06);
(c) Slag, ash and residues (including sludges, other than sewage sludge), containing metals, arsenic or their compounds and satisfying the conditions of Note 3 (a) or 3 (b) to Chapter 26 (heading 26.20);
(d) Medicaments (heading 30.03 or 30.04); or
(e) Spent catalysts of a kind used for the extraction of base metals or for the manufacture of chemical compounds of base metals (heading 26.20), spent catalysts of a kind used principally for the recovery of precious metals (heading 71.12) or catalysts consisting of metals or metal alloys in the form of, for example, finely divided powder or woven gauze (Section XV).""",

    39: """This Chapter does not cover:
(a) Waxes of heading 27.12 or 34.04;
(b) Separate chemically defined organic compounds (Chapter 29);
(c) Heparin or its salts (heading 30.01);
(d) Solutions (other than collodions) consisting of any of the products of headings 39.01 to 39.13 in volatile organic solvents when the weight of the solvent exceeds 50% of the weight of the solution (heading 32.08); stamping foils of heading 32.12;
(e) Organic surface-active agents or preparations of heading 34.02;
(f) Run gums or ester gums (heading 38.06);
(g) Diagnostic or laboratory reagents on a backing of plastics (heading 38.22);
(h) Synthetic rubber, as defined for the purposes of Chapter 40, or articles thereof;
(i) Saddlery or harness (heading 42.01) or trunks, suit-cases, handbags or other containers of heading 42.02;
(j) Plaits, wickerwork or other articles of Chapter 46;
(k) Wall coverings of heading 48.14;
(l) Goods of Section XI (textiles and textile articles);
(m) Articles of Section XII (for example, footwear, headgear, umbrellas, sun umbrellas, walking-sticks, whips, riding-crops or parts thereof);
(n) Imitation jewellery of heading 71.17;
(o) Articles of Section XVI (machines and mechanical or electrical appliances);
(p) Parts of aircraft or vehicles of Section XVII;
(q) Articles of Chapter 90 (for example, optical elements, spectacle frames, drawing instruments);
(r) Articles of Chapter 91 (for example, clock or watch cases);
(s) Articles of Chapter 92 (for example, musical instruments or parts thereof);
(t) Articles of Chapter 94 (for example, furniture, lamps and lighting fittings, illuminated signs, prefabricated buildings);
(u) Articles of Chapter 95 (for example, toys, games, sports requisites); or
(v) Articles of Chapter 96 (for example, brushes, buttons, slide fasteners, combs, mouthpieces or stems for smoking pipes, umbrella handles, parts of vacuum flasks or the like, pens, propelling pencils).""",

    40: """This Chapter does not cover:
(a) 'Factice' derived from oils (heading 15.18);
(b) Articles of apparel and clothing accessories (including gloves, mittens and mitts) for all purposes, of vulcanised rubber other than hard rubber (Chapter 61 or 62);
(c) Footwear or parts of footwear, gaiters, leggings or similar articles (Chapter 64);
(d) Headgear or parts thereof (including bathing caps) (Chapter 65);
(e) Mechanical or electrical appliances or parts thereof of Section XVI (including electrical goods of all kinds), of hard rubber;
(f) Articles of transport equipment of Section XVII;
(g) Articles of Chapter 90, 92, 94 or 96; or
(h) Articles of Chapter 95 (other than sports gloves, mittens and mitts and articles of headings 40.11 to 40.13).""",

    41: """This Chapter does not cover:
(a) Parings and similar waste of raw hides or skins (heading 05.11);
(b) Birdskins or parts of birdskins, with their feathers or down, of heading 05.05 or 67.01; or
(c) Hides or skins, with the hair or wool on, raw, tanned or dressed (Chapter 43); the following are, however, to be classified in Chapter 41, namely:
(1) Raw hides and skins of bovine animals (including buffalo), of equine animals, of sheep or lambs (except Astrakhan, Broadtail, Caracul, Persian or similar lambs, Indian, Chinese, Mongolian or Tibetan lambs), of goats or kids (except Yemen, Mongolian or Tibetan goats and kids), of swine (including peccary), of chamois, of gazelle, of camels (including dromedaries), of reindeer, of elk, of deer, of roebucks or of dogs."""
}

def populate_remaining_notes():
    """Populate remaining chapter notes."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Populating remaining chapter notes (28-41)...")
        updated_count = 0
        
        for chapter_num, notes in REMAINING_NOTES.items():
            cursor.execute("""
                UPDATE tariff_chapters 
                SET chapter_notes = ? 
                WHERE chapter_number = ?
            """, (notes, chapter_num))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"Updated Chapter {chapter_num:02d}")
        
        conn.commit()
        print(f"\nSuccessfully updated {updated_count} additional chapters")
        
        # Verify total
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        total_with_notes = cursor.fetchone()[0]
        print(f"Total chapters with notes: {total_with_notes}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate_remaining_notes()
