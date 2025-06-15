"""
Export classification and requirements API routes.
Provides endpoints for AHECC codes, export requirements, and market access information.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from database import get_async_session
from models.export import ExportCode
from models.tariff import TariffCode
from models.fta import FtaRate, TradeAgreement
from models.hierarchy import TariffSection, TariffChapter

router = APIRouter(prefix="/api/export", tags=["export"])

# Response models
class AHECCNode(BaseModel):
    code: str
    description: str
    level: str  # section, chapter, heading, subheading
    parent_code: Optional[str] = None
    children: List['AHECCNode'] = []
    statistical_unit: Optional[str] = None
    corresponding_import_code: Optional[str] = None
    has_children: bool = False

class ExportRequirement(BaseModel):
    requirement_type: str  # permit, certificate, license
    description: str
    issuing_authority: str
    mandatory: bool
    processing_time: Optional[str] = None
    cost: Optional[str] = None
    documentation_required: List[str] = []

class MarketAccessInfo(BaseModel):
    country: str
    tariff_rate: Optional[str] = None
    preferential_rate: Optional[str] = None
    fta_eligible: bool = False
    quota_restrictions: Optional[str] = None
    prohibited_goods: List[str] = []
    technical_requirements: List[str] = []
    phytosanitary_required: bool = False
    health_certificate_required: bool = False

class ExportStatistics(BaseModel):
    ahecc_code: str
    export_value_aud: float
    export_volume: float
    unit: str
    top_destinations: List[Dict[str, Any]]
    year_on_year_change: float
    seasonal_pattern: Optional[str] = None

class ExportCodeDetails(BaseModel):
    code: str
    description: str
    statistical_unit: Optional[str]
    corresponding_import_code: Optional[str]
    level: str
    parent_code: Optional[str]
    export_requirements: List[ExportRequirement]
    market_access_summary: Dict[str, Any]
    trade_statistics: Optional[ExportStatistics]

# Fix forward reference
AHECCNode.model_rebuild()

@router.get("/ahecc-tree", response_model=List[AHECCNode])
async def get_ahecc_tree(
    section: Optional[str] = None,
    parent_code: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get AHECC hierarchical structure.
    If section specified, return only that section's tree.
    If parent_code specified, return children of that code.
    """
    try:
        if section:
            # Get specific section tree
            section_codes = await db.execute(
                select(ExportCode)
                .where(ExportCode.ahecc_code.like(f"{section}%"))
                .order_by(ExportCode.ahecc_code)
            )
            codes = section_codes.scalars().all()
        elif parent_code:
            # Get children of specific parent
            parent_len = len(parent_code)
            child_len = parent_len + 2 if parent_len < 8 else parent_len + 2
            
            children = await db.execute(
                select(ExportCode)
                .where(
                    and_(
                        ExportCode.ahecc_code.like(f"{parent_code}%"),
                        func.length(ExportCode.ahecc_code) == child_len
                    )
                )
                .order_by(ExportCode.ahecc_code)
            )
            codes = children.scalars().all()
        else:
            # Get top-level sections (2-digit codes)
            sections = await db.execute(
                select(ExportCode)
                .where(func.length(ExportCode.ahecc_code) == 2)
                .order_by(ExportCode.ahecc_code)
            )
            codes = sections.scalars().all()

        # Convert to tree structure
        tree_nodes = []
        for code in codes:
            # Determine level based on code length
            code_len = len(code.ahecc_code)
            if code_len == 2:
                level = "section"
                parent = None
            elif code_len == 4:
                level = "chapter"
                parent = code.ahecc_code[:2]
            elif code_len == 6:
                level = "heading"
                parent = code.ahecc_code[:4]
            else:
                level = "subheading"
                parent = code.ahecc_code[:6]

            # Check if has children
            next_level_len = code_len + 2 if code_len < 8 else code_len + 2
            has_children_result = await db.execute(
                select(func.count(ExportCode.id))
                .where(
                    and_(
                        ExportCode.ahecc_code.like(f"{code.ahecc_code}%"),
                        func.length(ExportCode.ahecc_code) == next_level_len
                    )
                )
            )
            has_children = has_children_result.scalar() > 0

            tree_nodes.append(AHECCNode(
                code=code.ahecc_code,
                description=code.description,
                level=level,
                parent_code=parent,
                statistical_unit=code.statistical_unit,
                corresponding_import_code=code.corresponding_import_code,
                has_children=has_children
            ))

        return tree_nodes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AHECC tree: {str(e)}")

@router.get("/ahecc-search", response_model=List[AHECCNode])
async def search_ahecc_codes(
    query: str = Query(..., min_length=2),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    """Search AHECC codes by description or code."""
    try:
        search_results = await db.execute(
            select(ExportCode)
            .where(
                or_(
                    ExportCode.description.ilike(f"%{query}%"),
                    ExportCode.ahecc_code.ilike(f"%{query}%")
                )
            )
            .order_by(ExportCode.ahecc_code)
            .limit(limit)
        )
        codes = search_results.scalars().all()

        results = []
        for code in codes:
            code_len = len(code.ahecc_code)
            if code_len == 2:
                level = "section"
                parent = None
            elif code_len == 4:
                level = "chapter"
                parent = code.ahecc_code[:2]
            elif code_len == 6:
                level = "heading"
                parent = code.ahecc_code[:4]
            else:
                level = "subheading"
                parent = code.ahecc_code[:6]

            results.append(AHECCNode(
                code=code.ahecc_code,
                description=code.description,
                level=level,
                parent_code=parent,
                statistical_unit=code.statistical_unit,
                corresponding_import_code=code.corresponding_import_code
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching AHECC codes: {str(e)}")

@router.get("/code/{ahecc_code}/details", response_model=ExportCodeDetails)
async def get_export_code_details(
    ahecc_code: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Get comprehensive export information for specific AHECC code."""
    try:
        # Get the export code
        result = await db.execute(
            select(ExportCode)
            .where(ExportCode.ahecc_code == ahecc_code)
        )
        export_code = result.scalar_one_or_none()
        
        if not export_code:
            raise HTTPException(status_code=404, detail="AHECC code not found")

        # Determine level and parent
        code_len = len(ahecc_code)
        if code_len == 2:
            level = "section"
            parent = None
        elif code_len == 4:
            level = "chapter"
            parent = ahecc_code[:2]
        elif code_len == 6:
            level = "heading"
            parent = ahecc_code[:4]
        else:
            level = "subheading"
            parent = ahecc_code[:6]

        # Get export requirements based on commodity type
        requirements = get_export_requirements_by_code(ahecc_code)
        
        # Get market access summary
        market_access = get_market_access_summary(ahecc_code)
        
        # Get trade statistics from database patterns
        statistics = await get_export_statistics_from_db(db, ahecc_code, export_code)
        
        return ExportCodeDetails(
            code=export_code.ahecc_code,
            description=export_code.description,
            statistical_unit=export_code.statistical_unit,
            corresponding_import_code=export_code.corresponding_import_code,
            level=level,
            parent_code=parent,
            export_requirements=requirements,
            market_access_summary=market_access,
            trade_statistics=statistics
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching export code details: {str(e)}")

@router.get("/code/{ahecc_code}/requirements/{country}", response_model=List[ExportRequirement])
async def get_export_requirements(ahecc_code: str, country: str):
    """Get country-specific export requirements for AHECC code."""
    try:
        # Get requirements based on commodity type and destination
        requirements = get_country_specific_requirements(ahecc_code, country)
        return requirements
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching export requirements: {str(e)}")

@router.get("/market-access/{country}", response_model=MarketAccessInfo)
async def get_market_access_info(
    country: str, 
    ahecc_code: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Get market access information for destination country."""
    try:
        # Get FTA information if available
        fta_info = None
        if ahecc_code:
            # Check for corresponding import code and FTA rates
            export_result = await db.execute(
                select(ExportCode)
                .where(ExportCode.ahecc_code == ahecc_code)
            )
            export_code = export_result.scalar_one_or_none()
            
            if export_code and export_code.corresponding_import_code:
                fta_result = await db.execute(
                    select(FtaRate)
                    .join(TradeAgreement)
                    .where(
                        and_(
                            FtaRate.hs_code == export_code.corresponding_import_code,
                            TradeAgreement.partner_country.ilike(f"%{country}%")
                        )
                    )
                )
                fta_info = fta_result.scalar_one_or_none()

        return MarketAccessInfo(
            country=country,
            tariff_rate="5.0%" if not fta_info else "MFN Rate",
            preferential_rate="0.0%" if fta_info else None,
            fta_eligible=fta_info is not None,
            quota_restrictions=None,
            prohibited_goods=[],
            technical_requirements=get_technical_requirements(country, ahecc_code),
            phytosanitary_required=requires_phytosanitary(ahecc_code),
            health_certificate_required=requires_health_certificate(ahecc_code)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market access info: {str(e)}")

@router.get("/statistics/{ahecc_code}", response_model=ExportStatistics)
async def get_export_statistics(ahecc_code: str):
    """Get export statistics and trade performance data."""
    try:
        # Mock statistics - in production would query ABS export data
        mock_stats = ExportStatistics(
            ahecc_code=ahecc_code,
            export_value_aud=25000000.0,
            export_volume=1500.0,
            unit="tonnes",
            top_destinations=[
                {"country": "China", "value_aud": 12000000, "percentage": 48.0},
                {"country": "Japan", "value_aud": 6000000, "percentage": 24.0},
                {"country": "South Korea", "value_aud": 4000000, "percentage": 16.0},
                {"country": "United States", "value_aud": 3000000, "percentage": 12.0}
            ],
            year_on_year_change=8.5,
            seasonal_pattern="Peak exports in Q1 and Q3"
        )
        return mock_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching export statistics: {str(e)}")

@router.get("/permits/{commodity_group}", response_model=List[ExportRequirement])
async def get_export_permits(commodity_group: str):
    """Get required permits and licenses for commodity group."""
    try:
        permits = []
        
        # Determine permits based on commodity group
        if commodity_group.lower() in ["live_animals", "animal_products"]:
            permits.extend([
                ExportRequirement(
                    requirement_type="permit",
                    description="Export permit for live animals",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=True,
                    processing_time="10-15 business days",
                    cost="$200-500 AUD",
                    documentation_required=["Health certificates", "Veterinary inspection", "Transport arrangements"]
                ),
                ExportRequirement(
                    requirement_type="certificate",
                    description="AQIS health certificate",
                    issuing_authority="Australian Quarantine and Inspection Service",
                    mandatory=True,
                    processing_time="5-10 business days",
                    cost="$150-300 AUD",
                    documentation_required=["Veterinary health check", "Laboratory test results"]
                )
            ])
        
        elif commodity_group.lower() in ["plant_products", "agricultural"]:
            permits.extend([
                ExportRequirement(
                    requirement_type="certificate",
                    description="Phytosanitary certificate",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=True,
                    processing_time="3-7 business days",
                    cost="$50-150 AUD",
                    documentation_required=["Plant health inspection", "Treatment records", "Origin verification"]
                ),
                ExportRequirement(
                    requirement_type="permit",
                    description="Export permit for controlled plants",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=False,
                    processing_time="7-14 business days",
                    cost="$100-250 AUD",
                    documentation_required=["Species identification", "CITES permit (if applicable)"]
                )
            ])
        
        elif commodity_group.lower() in ["chemicals", "hazardous"]:
            permits.extend([
                ExportRequirement(
                    requirement_type="permit",
                    description="Chemical export permit",
                    issuing_authority="Australian Industrial Chemicals Introduction Scheme (AICIS)",
                    mandatory=True,
                    processing_time="15-30 business days",
                    cost="$500-2000 AUD",
                    documentation_required=["Safety data sheets", "Chemical composition", "End-use declaration"]
                ),
                ExportRequirement(
                    requirement_type="license",
                    description="Dangerous goods transport license",
                    issuing_authority="Australian Transport Safety Bureau",
                    mandatory=True,
                    processing_time="10-20 business days",
                    cost="$300-800 AUD",
                    documentation_required=["Transport plan", "Emergency response procedures", "Driver certification"]
                )
            ])
        
        elif commodity_group.lower() in ["food", "beverages"]:
            permits.extend([
                ExportRequirement(
                    requirement_type="certificate",
                    description="Export food safety certificate",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=True,
                    processing_time="5-10 business days",
                    cost="$100-300 AUD",
                    documentation_required=["HACCP certification", "Laboratory test results", "Facility inspection"]
                ),
                ExportRequirement(
                    requirement_type="permit",
                    description="Organic certification (if applicable)",
                    issuing_authority="Australian Certified Organic",
                    mandatory=False,
                    processing_time="14-21 business days",
                    cost="$200-600 AUD",
                    documentation_required=["Organic production records", "Chain of custody documentation"]
                )
            ])
        
        elif commodity_group.lower() in ["minerals", "resources"]:
            permits.extend([
                ExportRequirement(
                    requirement_type="permit",
                    description="Mineral export permit",
                    issuing_authority="Department of Industry, Science and Resources",
                    mandatory=True,
                    processing_time="20-40 business days",
                    cost="$1000-5000 AUD",
                    documentation_required=["Mining lease documentation", "Environmental impact assessment", "Royalty payments"]
                ),
                ExportRequirement(
                    requirement_type="license",
                    description="Export license for strategic minerals",
                    issuing_authority="Department of Foreign Affairs and Trade",
                    mandatory=False,
                    processing_time="30-60 business days",
                    cost="$500-2000 AUD",
                    documentation_required=["End-user certificate", "Strategic assessment", "National interest evaluation"]
                )
            ])
        
        else:
            # General export requirements
            permits.append(
                ExportRequirement(
                    requirement_type="permit",
                    description="General export permit",
                    issuing_authority="Australian Border Force",
                    mandatory=False,
                    processing_time="5-10 business days",
                    cost="$50-200 AUD",
                    documentation_required=["Commercial invoice", "Packing list", "Export declaration"]
                )
            )
        
        return permits
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching export permits: {str(e)}")

@router.get("/quarantine/{ahecc_code}", response_model=List[ExportRequirement])
async def get_quarantine_requirements(ahecc_code: str):
    """Get AQIS quarantine requirements for specific AHECC code."""
    try:
        requirements = []
        
        # Determine quarantine requirements based on AHECC code
        if requires_phytosanitary(ahecc_code):
            requirements.extend([
                ExportRequirement(
                    requirement_type="certificate",
                    description="Phytosanitary certificate",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=True,
                    processing_time="3-7 business days",
                    cost="$50-150 AUD",
                    documentation_required=["Plant health inspection", "Treatment records", "Pest-free area certification"]
                ),
                ExportRequirement(
                    requirement_type="inspection",
                    description="Pre-export plant inspection",
                    issuing_authority="Australian Quarantine and Inspection Service",
                    mandatory=True,
                    processing_time="1-3 business days",
                    cost="$100-250 AUD",
                    documentation_required=["Sampling protocols", "Visual inspection", "Laboratory testing"]
                )
            ])
        
        if requires_health_certificate(ahecc_code):
            requirements.extend([
                ExportRequirement(
                    requirement_type="certificate",
                    description="Health certificate for animal products",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=True,
                    processing_time="5-10 business days",
                    cost="$150-400 AUD",
                    documentation_required=["Veterinary health check", "Laboratory test results", "Slaughter facility certification"]
                ),
                ExportRequirement(
                    requirement_type="inspection",
                    description="Pre-export veterinary inspection",
                    issuing_authority="Australian Quarantine and Inspection Service",
                    mandatory=True,
                    processing_time="1-2 business days",
                    cost="$200-500 AUD",
                    documentation_required=["Animal health records", "Feed certification", "Transport arrangements"]
                )
            ])
        
        # Food products
        if any(ahecc_code.startswith(ch) for ch in ["16", "17", "18", "19", "20", "21", "22"]):
            requirements.append(
                ExportRequirement(
                    requirement_type="certificate",
                    description="Food safety certificate",
                    issuing_authority="Department of Agriculture, Fisheries and Forestry",
                    mandatory=True,
                    processing_time="5-10 business days",
                    cost="$100-300 AUD",
                    documentation_required=["HACCP certification", "Microbiological testing", "Facility inspection"]
                )
            )
        
        # Dairy products
        if ahecc_code.startswith("04"):
            requirements.append(
                ExportRequirement(
                    requirement_type="permit",
                    description="Dairy export permit",
                    issuing_authority="Dairy Australia",
                    mandatory=True,
                    processing_time="7-14 business days",
                    cost="$200-500 AUD",
                    documentation_required=["Dairy facility registration", "Quality assurance certification", "Pasteurization records"]
                )
            )
        
        # Organic products
        if "organic" in ahecc_code.lower():
            requirements.append(
                ExportRequirement(
                    requirement_type="certificate",
                    description="Organic certification",
                    issuing_authority="Australian Certified Organic",
                    mandatory=True,
                    processing_time="14-21 business days",
                    cost="$200-600 AUD",
                    documentation_required=["Organic production records", "Chain of custody documentation", "Annual inspection reports"]
                )
            )
        
        # If no specific requirements, provide general guidance
        if not requirements:
            requirements.append(
                ExportRequirement(
                    requirement_type="guidance",
                    description="General quarantine compliance",
                    issuing_authority="Australian Quarantine and Inspection Service",
                    mandatory=False,
                    processing_time="N/A",
                    cost="No cost",
                    documentation_required=["Commercial documentation", "Country of origin verification"]
                )
            )
        
        return requirements
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quarantine requirements: {str(e)}")

# Helper functions for export requirements
def get_export_requirements_by_code(ahecc_code: str) -> List[ExportRequirement]:
    """Get export requirements based on AHECC code."""
    requirements = []
    
    # Live animals (Chapter 01)
    if ahecc_code.startswith("01"):
        requirements.extend([
            ExportRequirement(
                requirement_type="permit",
                description="Export permit for live animals",
                issuing_authority="Department of Agriculture, Fisheries and Forestry",
                mandatory=True,
                processing_time="10-15 business days",
                cost="$200-500 AUD",
                documentation_required=["Health certificate", "Breeding records", "Transport arrangements"]
            ),
            ExportRequirement(
                requirement_type="certificate",
                description="Veterinary health certificate",
                issuing_authority="Australian Government Veterinarian",
                mandatory=True,
                processing_time="5-7 business days",
                cost="$150-300 AUD",
                documentation_required=["Animal health records", "Vaccination certificates"]
            )
        ])
    
    # Food products (Chapters 02-24)
    elif any(ahecc_code.startswith(ch) for ch in ["02", "03", "04", "07", "08", "09", "10", "11", "12", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]):
        requirements.extend([
            ExportRequirement(
                requirement_type="certificate",
                description="Export health certificate",
                issuing_authority="Department of Agriculture, Fisheries and Forestry",
                mandatory=True,
                processing_time="3-5 business days",
                cost="$50-150 AUD",
                documentation_required=["Product analysis", "Manufacturing records", "HACCP certification"]
            )
        ])
    
    # Chemicals and pharmaceuticals
    elif ahecc_code.startswith("29") or ahecc_code.startswith("30"):
        requirements.extend([
            ExportRequirement(
                requirement_type="permit",
                description="Chemical export permit",
                issuing_authority="Australian Industrial Chemicals Introduction Scheme (AICIS)",
                mandatory=True,
                processing_time="15-30 business days",
                cost="$500-2000 AUD",
                documentation_required=["Safety data sheets", "Chemical composition", "End-use declaration"]
            )
        ])
    
    return requirements

def get_country_specific_requirements(ahecc_code: str, country: str) -> List[ExportRequirement]:
    """Get country-specific export requirements."""
    base_requirements = get_export_requirements_by_code(ahecc_code)
    
    # Add country-specific requirements
    country_requirements = []
    
    if country.upper() in ["CHINA", "CN"]:
        if ahecc_code.startswith("01") or ahecc_code.startswith("02"):
            country_requirements.append(
                ExportRequirement(
                    requirement_type="certificate",
                    description="CNCA registration certificate",
                    issuing_authority="China National Certification and Accreditation Administration",
                    mandatory=True,
                    processing_time="30-60 business days",
                    cost="Varies",
                    documentation_required=["Facility registration", "Product certification"]
                )
            )
    
    elif country.upper() in ["JAPAN", "JP"]:
        if any(ahecc_code.startswith(ch) for ch in ["07", "08", "20"]):
            country_requirements.append(
                ExportRequirement(
                    requirement_type="certificate",
                    description="Plant quarantine certificate",
                    issuing_authority="Plant Protection Station (Japan)",
                    mandatory=True,
                    processing_time="5-10 business days",
                    cost="$100-200 AUD",
                    documentation_required=["Phytosanitary certificate", "Treatment records"]
                )
            )
    
    return base_requirements + country_requirements

def get_market_access_summary(ahecc_code: str) -> Dict[str, Any]:
    """Get market access summary for AHECC code."""
    return {
        "major_markets": ["China", "Japan", "South Korea", "United States", "European Union"],
        "fta_benefits": ["CPTPP", "KAFTA", "JAEPA", "ChAFTA"],
        "common_barriers": ["Phytosanitary requirements", "Technical standards", "Labeling requirements"],
        "growth_markets": ["India", "Indonesia", "Vietnam"]
    }

def get_technical_requirements(country: str, ahecc_code: Optional[str]) -> List[str]:
    """Get technical requirements for specific country."""
    requirements = []
    
    if country.upper() in ["EUROPEAN UNION", "EU"]:
        requirements.extend(["CE marking", "REACH compliance", "RoHS compliance"])
    elif country.upper() in ["UNITED STATES", "USA", "US"]:
        requirements.extend(["FDA registration", "FCC certification", "UL listing"])
    elif country.upper() in ["JAPAN", "JP"]:
        requirements.extend(["JIS standards", "PSE marking", "Telec certification"])
    
    return requirements

def requires_phytosanitary(ahecc_code: Optional[str]) -> bool:
    """Check if phytosanitary certificate is required."""
    if not ahecc_code:
        return False
    
    # Plant and plant products
    phyto_chapters = ["06", "07", "08", "09", "10", "11", "12", "13", "14"]
    return any(ahecc_code.startswith(ch) for ch in phyto_chapters)

def requires_health_certificate(ahecc_code: Optional[str]) -> bool:
    """Check if health certificate is required."""
    if not ahecc_code:
        return False
    
    # Animal products and food
    health_chapters = ["01", "02", "03", "04", "15", "16", "17", "18", "19", "20", "21", "22"]
    return any(ahecc_code.startswith(ch) for ch in health_chapters)

async def get_export_statistics_from_db(db: AsyncSession, ahecc_code: str, export_code: ExportCode) -> ExportStatistics:
    """Get trade statistics from database patterns."""
    # TO DO: implement database query to fetch trade statistics
    # For now, return mock statistics
    return ExportStatistics(
        ahecc_code=ahecc_code,
        export_value_aud=25000000.0,
        export_volume=1500.0,
        unit=export_code.statistical_unit or "kg",
        top_destinations=[
            {"country": "China", "value_aud": 12000000, "percentage": 48.0},
            {"country": "Japan", "value_aud": 6000000, "percentage": 24.0},
            {"country": "South Korea", "value_aud": 4000000, "percentage": 16.0},
            {"country": "United States", "value_aud": 3000000, "percentage": 12.0}
        ],
        year_on_year_change=8.5,
        seasonal_pattern="Peak exports in Q1 and Q3"
    )
