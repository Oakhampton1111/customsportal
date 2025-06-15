-- Fix Tariff Hierarchy Data
-- =====================================================
-- This script fixes the tariff sections and chapters data
-- to ensure proper hierarchy for the frontend tree functionality
-- =====================================================

-- First, let's add the missing sections that the sample_data.sql expects
INSERT OR IGNORE INTO tariff_sections (section_number, title, description, chapter_range) VALUES
(6, 'Products of the Chemical or Allied Industries', 'Chemicals, pharmaceuticals, plastics, rubber', '28-40'),
(7, 'Plastics and Articles Thereof; Rubber and Articles Thereof', 'Plastics and rubber products', '39-40'),
(8, 'Raw Hides and Skins, Leather, Furskins and Articles Thereof', 'Leather goods and furskins', '41-43'),
(9, 'Wood and Articles of Wood; Wood Charcoal', 'Wood products and charcoal', '44-46'),
(10, 'Pulp of Wood or Other Fibrous Cellulosic Material; Paper and Paperboard', 'Paper and pulp products', '47-49'),
(11, 'Textiles and Textile Articles', 'Textiles, clothing and textile articles', '50-63'),
(12, 'Footwear, Headgear, Umbrellas, Walking-Sticks', 'Footwear and accessories', '64-67'),
(13, 'Articles of Stone, Plaster, Cement, Asbestos, Mica', 'Stone, ceramic and glass products', '68-70'),
(14, 'Natural or Cultured Pearls, Precious Stones and Metals', 'Precious stones, metals and jewelry', '71-71'),
(15, 'Base Metals and Articles of Base Metal', 'Iron, steel, aluminum and other base metals', '72-83'),
(16, 'Machinery and Mechanical Appliances; Electrical Equipment', 'Machinery, mechanical and electrical equipment', '84-85'),
(17, 'Vehicles, Aircraft, Vessels and Transport Equipment', 'Transport equipment and parts', '86-89'),
(18, 'Optical, Photographic, Cinematographic, Medical Instruments', 'Precision instruments and apparatus', '90-92'),
(19, 'Arms and Ammunition; Parts and Accessories Thereof', 'Weapons and ammunition', '93-93'),
(20, 'Miscellaneous Manufactured Articles', 'Furniture, toys, miscellaneous articles', '94-96'),
(21, 'Works of Art, Collectors Pieces and Antiques', 'Art, antiques and collectors items', '97-99');

-- Now add the missing chapters with correct section_id references
INSERT OR IGNORE INTO tariff_chapters (chapter_number, title, chapter_notes, section_id) VALUES
-- Live Animals and Animal Products (Section 1)
(4, 'Dairy Produce; Birds Eggs; Natural Honey', 'Dairy products, eggs and honey for human consumption', 1),
(5, 'Products of Animal Origin, Not Elsewhere Specified', 'Other animal products including gut, bladders, hair', 1),

-- Vegetable Products (Section 2)
(6, 'Live Trees and Other Plants; Bulbs, Roots; Cut Flowers', 'Live plants, bulbs, cut flowers and foliage', 2),
(7, 'Edible Vegetables and Certain Roots and Tubers', 'Fresh, chilled, frozen or dried vegetables', 2),
(8, 'Edible Fruit and Nuts; Peel of Citrus Fruit or Melons', 'Fresh, dried or prepared fruits and nuts', 2),
(9, 'Coffee, Tea, Mate and Spices', 'Coffee, tea, spices and culinary herbs', 2),
(10, 'Cereals', 'Wheat, rice, barley, oats, corn and other cereals', 2),

-- Textiles (Section 11)
(50, 'Silk', 'Silk yarn, woven fabrics and silk waste', 11),
(51, 'Wool, Fine or Coarse Animal Hair; Horsehair Yarn and Woven Fabric', 'Wool and animal hair products', 11),
(52, 'Cotton', 'Cotton yarn, thread and woven fabrics', 11),
(53, 'Other Vegetable Textile Fibres; Paper Yarn and Woven Fabrics', 'Jute, flax, hemp and other vegetable fibres', 11),
(54, 'Man-Made Filaments; Strip of Man-Made Textile Materials', 'Synthetic filament yarns and fabrics', 11),
(55, 'Man-Made Staple Fibres', 'Synthetic staple fibres and yarns', 11),
(56, 'Wadding, Felt and Nonwovens; Special Yarns; Twine, Cordage', 'Wadding, felt, nonwovens and cordage', 11),
(57, 'Carpets and Other Textile Floor Coverings', 'Carpets, rugs and textile floor coverings', 11),
(58, 'Special Woven Fabrics; Tufted Textile Fabrics; Lace; Tapestries', 'Special woven fabrics and lace', 11),
(59, 'Impregnated, Coated, Covered or Laminated Textile Fabrics', 'Coated and laminated textile fabrics', 11),
(60, 'Knitted or Crocheted Fabrics', 'Knitted and crocheted fabrics', 11),
(61, 'Articles of Apparel and Clothing Accessories, Knitted or Crocheted', 'Knitted clothing and accessories', 11),
(62, 'Articles of Apparel and Clothing Accessories, Not Knitted or Crocheted', 'Woven clothing and accessories', 11),
(63, 'Other Made-up Textile Articles; Sets; Worn Clothing', 'Made-up textile articles and worn clothing', 11),

-- Base Metals (Section 15)
(72, 'Iron and Steel', 'Iron, steel products and semi-finished steel', 15),
(73, 'Articles of Iron or Steel', 'Manufactured articles of iron or steel', 15),
(74, 'Copper and Articles Thereof', 'Copper and copper alloy products', 15),
(75, 'Nickel and Articles Thereof', 'Nickel and nickel alloy products', 15),
(76, 'Aluminium and Articles Thereof', 'Aluminum and aluminum alloy products', 15),

-- Vehicles (Section 17)
(87, 'Vehicles Other Than Railway or Tramway Rolling Stock', 'Motor vehicles, tractors and parts', 17),
(88, 'Aircraft, Spacecraft, and Parts Thereof', 'Aircraft, spacecraft and related parts', 17),
(89, 'Ships, Boats and Floating Structures', 'Ships, boats and marine vessels', 17);
