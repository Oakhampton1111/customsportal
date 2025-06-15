#!/usr/bin/env python3
"""Complete chapter notes population for chapters 42-97."""

import sqlite3
from pathlib import Path

# Final batch of chapter notes (42-97)
FINAL_NOTES = {
    42: "This Chapter covers all leather goods, travel goods, handbags and similar containers, regardless of the material from which they are made.",
    43: "This Chapter covers furskins and artificial fur, whether raw, tanned or dressed, and articles made therefrom.",
    44: "This Chapter covers wood and articles of wood, including wood charcoal.",
    45: "This Chapter covers cork and articles of cork.",
    46: "This Chapter covers manufactures of straw, esparto or other plaiting materials; basketware and wickerwork.",
    47: "This Chapter covers pulp of wood or of other fibrous cellulosic material; recovered (waste and scrap) paper or paperboard.",
    48: "This Chapter covers paper and paperboard; articles of paper pulp, of paper or of paperboard.",
    49: "This Chapter covers printed books, newspapers, pictures and other products of the printing industry; manuscripts, typescripts and plans.",
    50: "This Chapter covers silk, including silk waste and silk yarn.",
    51: "This Chapter covers wool, fine or coarse animal hair; horsehair yarn and woven fabric.",
    52: "This Chapter covers cotton.",
    53: "This Chapter covers other vegetable textile fibres; paper yarn and woven fabrics of paper yarn.",
    54: "This Chapter covers man-made filaments; strip and the like of man-made textile materials.",
    55: "This Chapter covers man-made staple fibres.",
    56: "This Chapter covers wadding, felt and nonwovens; special yarns; twine, cordage, ropes and cables and articles thereof.",
    57: "This Chapter covers carpets and other textile floor coverings.",
    58: "This Chapter covers special woven fabrics; tufted textile fabrics; lace; tapestries; trimmings; embroidery.",
    59: "This Chapter covers impregnated, coated, covered or laminated textile fabrics; textile articles of a kind suitable for industrial use.",
    60: "This Chapter covers knitted or crocheted fabrics.",
    61: "This Chapter covers articles of apparel and clothing accessories, knitted or crocheted.",
    62: "This Chapter covers articles of apparel and clothing accessories, not knitted or crocheted.",
    63: "This Chapter covers other made up textile articles; sets; worn clothing and worn textile articles; rags.",
    64: "This Chapter covers footwear, gaiters and the like; parts of such articles.",
    65: "This Chapter covers headgear and parts thereof.",
    66: "This Chapter covers umbrellas, sun umbrellas, walking-sticks, seat-sticks, whips, riding-crops and parts thereof.",
    67: "This Chapter covers prepared feathers and down and articles made of feathers or of down; artificial flowers; articles of human hair.",
    68: "This Chapter covers articles of stone, plaster, cement, asbestos, mica or similar materials.",
    69: "This Chapter covers ceramic products.",
    70: "This Chapter covers glass and glassware.",
    71: "This Chapter covers natural or cultured pearls, precious or semi-precious stones, precious metals, metals clad with precious metal, and articles thereof; imitation jewellery; coin.",
    72: "This Chapter covers iron and steel.",
    73: "This Chapter covers articles of iron or steel.",
    74: "This Chapter covers copper and articles thereof.",
    75: "This Chapter covers nickel and articles thereof.",
    76: "This Chapter covers aluminium and articles thereof.",
    78: "This Chapter covers lead and articles thereof.",
    79: "This Chapter covers zinc and articles thereof.",
    80: "This Chapter covers tin and articles thereof.",
    81: "This Chapter covers other base metals; cermets; articles thereof.",
    82: "This Chapter covers tools, implements, cutlery, spoons and forks, of base metal; parts thereof of base metal.",
    83: "This Chapter covers miscellaneous articles of base metal.",
    84: "This Chapter covers nuclear reactors, boilers, machinery and mechanical appliances; parts thereof.",
    85: "This Chapter covers electrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles.",
    86: "This Chapter covers railway or tramway locomotives, rolling-stock and parts thereof; railway or tramway track fixtures and fittings and parts thereof; mechanical (including electro-mechanical) traffic signalling equipment of all kinds.",
    87: "This Chapter covers vehicles other than railway or tramway rolling-stock, and parts and accessories thereof.",
    88: "This Chapter covers aircraft, spacecraft, and parts thereof.",
    89: "This Chapter covers ships, boats and floating structures.",
    90: "This Chapter covers optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; parts and accessories thereof.",
    91: "This Chapter covers clocks and watches and parts thereof.",
    92: "This Chapter covers musical instruments; parts and accessories of such articles.",
    93: "This Chapter covers arms and ammunition; parts and accessories thereof.",
    94: "This Chapter covers furniture; bedding, mattresses, mattress supports, cushions and similar stuffed furnishings; lamps and lighting fittings, not elsewhere specified or included; illuminated signs, illuminated name-plates and the like; prefabricated buildings.",
    95: "This Chapter covers toys, games and sports requisites; parts and accessories thereof.",
    96: "This Chapter covers miscellaneous manufactured articles.",
    97: "This Chapter covers works of art, collectors' pieces and antiques."
}

def complete_chapter_notes():
    """Complete all remaining chapter notes."""
    db_path = Path("customs_portal.db")
    
    if not db_path.exists():
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("Completing final chapter notes (42-97)...")
        updated_count = 0
        
        for chapter_num, notes in FINAL_NOTES.items():
            cursor.execute("""
                UPDATE tariff_chapters 
                SET chapter_notes = ? 
                WHERE chapter_number = ?
            """, (notes, chapter_num))
            
            if cursor.rowcount > 0:
                updated_count += 1
                if chapter_num % 10 == 0:
                    print(f"Updated Chapter {chapter_num:02d}")
        
        conn.commit()
        print(f"\nSuccessfully updated {updated_count} final chapters")
        
        # Final verification
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters WHERE chapter_notes IS NOT NULL AND chapter_notes != ''")
        total_with_notes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tariff_chapters")
        total_chapters = cursor.fetchone()[0]
        
        print(f"COMPLETE: {total_with_notes}/{total_chapters} chapters now have notes")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    complete_chapter_notes()
