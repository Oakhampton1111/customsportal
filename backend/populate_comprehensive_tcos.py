"""
Comprehensive TCO (Tariff Concession Orders) Population Script
============================================================
Populates the database with a comprehensive, realistic dataset of Australian TCOs
based on actual Australian Border Force TCO patterns and industry requirements.
"""

import asyncio
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, func

from database import get_async_session
from models import TariffCode
from models.tco import Tco

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TCOPopulator:
    """Comprehensive TCO data populator."""
    
    def __init__(self):
        self.session: AsyncSession = None
        self.available_hs_codes: List[str] = []
        self.tco_counter = 1
        
        # TCO categories based on Australian industry patterns
        self.tco_categories = {
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
    
    async def initialize_session(self):
        """Initialize database session."""
        self.session = await anext(get_async_session())
        
    async def get_available_hs_codes(self) -> List[str]:
        """Get available HS codes from tariff_codes table."""
        logger.info("Fetching available HS codes...")
        
        result = await self.session.execute(
            select(TariffCode.hs_code)
            .where(TariffCode.is_active == True)
            .order_by(TariffCode.hs_code)
        )
        
        codes = [row[0] for row in result.fetchall()]
        logger.info(f"Found {len(codes)} available HS codes")
        return codes
    
    def generate_tco_number(self, year: int) -> str:
        """Generate realistic TCO number."""
        tco_num = f"TCO-{year}-{self.tco_counter:04d}"
        self.tco_counter += 1
        return tco_num
    
    def get_random_dates(self, year: int) -> Tuple[date, date, date]:
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
        
        return effective_date, expiry_date, gazette_date
    
    def get_gazette_number(self, gazette_date: date) -> str:
        """Generate realistic gazette number."""
        year = gazette_date.year
        week = gazette_date.isocalendar()[1]
        return f"C{year}G{week:02d}"
    
    def generate_substitutable_goods_text(self, category: str) -> str:
        """Generate realistic substitutable goods determination text."""
        templates = [
            f"No substitutable goods of Australian origin are commercially available that are suitable for the intended use in {category} applications.",
            f"Goods of Australian origin that are substitutable are not available in commercial quantities or within a reasonable time for {category} requirements.",
            f"The applicant has demonstrated that no Australian-made goods are suitable substitutes for the specific {category} application requirements.",
            f"Technical specifications require goods not available from Australian manufacturers for {category} industry use.",
            f"Specialized {category} equipment with no commercially viable Australian alternatives available."
        ]
        return random.choice(templates)
    
    async def clear_existing_tcos(self):
        """Clear existing TCO data."""
        logger.info("Clearing existing TCO data...")
        
        result = await self.session.execute(text("DELETE FROM tcos"))
        await self.session.commit()
        
        logger.info(f"Cleared existing TCO records")
    
    async def generate_tcos_for_category(self, category: str, config: Dict, target_count: int) -> List[Tco]:
        """Generate TCOs for a specific category."""
        logger.info(f"Generating {target_count} TCOs for {category} category...")
        
        tcos = []
        category_hs_codes = []
        
        # Filter HS codes by chapter
        for chapter in config["chapters"]:
            chapter_codes = [code for code in self.available_hs_codes if code.startswith(chapter)]
            category_hs_codes.extend(chapter_codes)
        
        if not category_hs_codes:
            logger.warning(f"No HS codes found for {category} chapters: {config['chapters']}")
            return []
        
        for i in range(target_count):
            # Generate TCO for different years (2020-2024)
            year = random.choice([2020, 2021, 2022, 2023, 2024])
            
            # Select random HS code from category
            hs_code = random.choice(category_hs_codes)
            
            # Generate dates
            effective_date, expiry_date, gazette_date = self.get_random_dates(year)
            
            # Determine if TCO is current (90% chance for recent years)
            is_current = True
            if year < 2022:
                is_current = random.choice([True, False])
            elif year == 2022:
                is_current = random.choice([True, True, True, False])  # 75% chance
            
            # If expired, mark as not current
            if expiry_date < date.today():
                is_current = False
            
            tco = Tco(
                tco_number=self.generate_tco_number(year),
                hs_code=hs_code,
                description=f"{random.choice(config['descriptions'])}, {self._generate_technical_specs()}",
                applicant_name=random.choice(config["applicants"]),
                effective_date=effective_date,
                expiry_date=expiry_date,
                gazette_date=gazette_date,
                gazette_number=self.get_gazette_number(gazette_date),
                substitutable_goods_determination=self.generate_substitutable_goods_text(category),
                is_current=is_current,
                created_at=datetime.now()
            )
            
            tcos.append(tco)
        
        return tcos
    
    def _generate_technical_specs(self) -> str:
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
    
    async def populate_comprehensive_tcos(self):
        """Populate comprehensive TCO dataset."""
        logger.info("Starting comprehensive TCO population...")
        
        # Initialize session
        await self.initialize_session()
        
        try:
            # Get available HS codes
            self.available_hs_codes = await self.get_available_hs_codes()
            
            if not self.available_hs_codes:
                logger.error("No HS codes available for TCO generation")
                return
            
            # Clear existing data
            await self.clear_existing_tcos()
            
            # Define target counts per category (total ~2000 TCOs)
            category_targets = {
                "automotive": 300,
                "mining": 280,
                "manufacturing": 250,
                "telecommunications": 200,
                "renewable_energy": 180,
                "aerospace": 150,
                "medical": 140,
                "agriculture": 120
            }
            
            all_tcos = []
            
            # Generate TCOs for each category
            for category, target_count in category_targets.items():
                if category in self.tco_categories:
                    category_tcos = await self.generate_tcos_for_category(
                        category, 
                        self.tco_categories[category], 
                        target_count
                    )
                    all_tcos.extend(category_tcos)
                    logger.info(f"Generated {len(category_tcos)} TCOs for {category}")
            
            # Batch insert TCOs
            logger.info(f"Inserting {len(all_tcos)} TCOs into database...")
            
            batch_size = 100
            for i in range(0, len(all_tcos), batch_size):
                batch = all_tcos[i:i + batch_size]
                self.session.add_all(batch)
                await self.session.commit()
                logger.info(f"Inserted batch {i//batch_size + 1}/{(len(all_tcos) + batch_size - 1)//batch_size}")
            
            # Verify insertion
            result = await self.session.execute(select(func.count(Tco.id)))
            total_count = result.scalar()
            
            result = await self.session.execute(
                select(func.count(Tco.id)).where(Tco.is_current == True)
            )
            active_count = result.scalar()
            
            logger.info(f"✅ Successfully populated {total_count} TCOs ({active_count} active)")
            
            # Generate summary statistics
            await self.generate_summary_statistics()
            
        except Exception as e:
            logger.error(f"Error during TCO population: {e}")
            await self.session.rollback()
            raise
        finally:
            await self.session.close()
    
    async def generate_summary_statistics(self):
        """Generate and display summary statistics."""
        logger.info("Generating TCO summary statistics...")
        
        # Total counts
        result = await self.session.execute(select(func.count(Tco.id)))
        total_count = result.scalar()
        
        result = await self.session.execute(
            select(func.count(Tco.id)).where(Tco.is_current == True)
        )
        active_count = result.scalar()
        
        # Chapter distribution
        result = await self.session.execute(
            text("""
                SELECT SUBSTR(hs_code, 1, 2) as chapter, COUNT(*) as count
                FROM tcos 
                GROUP BY SUBSTR(hs_code, 1, 2)
                ORDER BY count DESC
                LIMIT 10
            """)
        )
        chapter_stats = result.fetchall()
        
        # Year distribution
        result = await self.session.execute(
            text("""
                SELECT strftime('%Y', effective_date) as year, COUNT(*) as count
                FROM tcos 
                WHERE effective_date IS NOT NULL
                GROUP BY strftime('%Y', effective_date)
                ORDER BY year DESC
            """)
        )
        year_stats = result.fetchall()
        
        # Sample TCOs
        result = await self.session.execute(
            select(Tco.tco_number, Tco.hs_code, Tco.description, Tco.applicant_name)
            .order_by(Tco.tco_number)
            .limit(10)
        )
        samples = result.fetchall()
        
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
        for tco_num, hs_code, desc, applicant in samples:
            desc_short = desc[:50] + "..." if len(desc) > 50 else desc
            print(f"   {tco_num}: {hs_code} - {desc_short}")
            print(f"      Applicant: {applicant}")
        
        print("=" * 80)

async def main():
    """Main execution function."""
    populator = TCOPopulator()
    await populator.populate_comprehensive_tcos()

if __name__ == "__main__":
    asyncio.run(main())
