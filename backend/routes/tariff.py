"""
Tariff API routes for the Customs Broker Portal.

This module implements comprehensive tariff code lookup, hierarchical navigation,
and search functionality for Australian HS codes with related duty information.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.exc import SQLAlchemyError

from database import get_async_session
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from schemas.tariff import (
    TariffTreeResponse, TariffDetailResponse, TariffSearchRequest,
    TariffSearchResponse, TariffTreeNode, TariffCodeResponse,
    TariffSearchResult, TariffCodeSummary
)
from schemas.common import PaginationMeta, PaginationParams

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/tariff", tags=["Tariff"])


@router.get("/sections", response_model=List[Dict[str, Any]])
async def get_tariff_sections(
    db: AsyncSession = Depends(get_async_session)
) -> List[Dict[str, Any]]:
    """
    Get all tariff sections.
    
    Returns a list of all tariff sections with basic information including
    section number, title, description, and chapter count.
    
    Returns:
        List of tariff sections with metadata
    """
    try:
        logger.info("Fetching all tariff sections")
        
        # Query sections with chapter count
        stmt = (
            select(
                TariffSection,
                func.count(TariffChapter.id).label("chapter_count")
            )
            .outerjoin(TariffChapter, TariffSection.id == TariffChapter.section_id)
            .group_by(TariffSection.id)
            .order_by(TariffSection.section_number)
        )
        
        result = await db.execute(stmt)
        sections_with_counts = result.all()
        
        sections = []
        for section, chapter_count in sections_with_counts:
            sections.append({
                "id": section.id,
                "section_number": section.section_number,
                "title": section.title,
                "description": section.description,
                "chapter_range": section.chapter_range,
                "chapter_count": chapter_count or 0
            })
        
        logger.info(f"Retrieved {len(sections)} tariff sections")
        return sections
        
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching tariff sections: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching tariff sections"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching tariff sections: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.get("/chapters/{section_id}", response_model=List[Dict[str, Any]])
async def get_chapters_by_section(
    section_id: int = Path(..., description="Section ID to get chapters for"),
    db: AsyncSession = Depends(get_async_session)
) -> List[Dict[str, Any]]:
    """
    Get chapters for a specific section.
    
    Returns all chapters belonging to the specified section with
    tariff code counts and metadata.
    
    Args:
        section_id: ID of the section to get chapters for
        
    Returns:
        List of chapters with metadata
        
    Raises:
        HTTPException: 404 if section not found
    """
    try:
        logger.info(f"Fetching chapters for section {section_id}")
        
        # First verify section exists
        section_stmt = select(TariffSection).where(TariffSection.id == section_id)
        section_result = await db.execute(section_stmt)
        section = section_result.scalar_one_or_none()
        
        if not section:
            raise HTTPException(
                status_code=404,
                detail=f"Section with ID {section_id} not found"
            )
        
        # Query chapters with tariff code count
        stmt = (
            select(
                TariffChapter,
                func.count(TariffCode.id).label("tariff_code_count")
            )
            .outerjoin(TariffCode)
            .where(TariffChapter.section_id == section_id)
            .group_by(TariffChapter.id)
            .order_by(TariffChapter.chapter_number)
        )
        
        result = await db.execute(stmt)
        chapters_with_counts = result.all()
        
        chapters = []
        for chapter, tariff_count in chapters_with_counts:
            chapters.append({
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "chapter_notes": chapter.chapter_notes,
                "section_id": chapter.section_id,
                "tariff_code_count": tariff_count or 0,
                "section_title": section.title
            })
        
        logger.info(f"Retrieved {len(chapters)} chapters for section {section_id}")
        return chapters
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching chapters for section {section_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching chapters"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching chapters for section {section_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.get("/tree/{section_id}", response_model=TariffTreeResponse)
async def get_tariff_tree(
    section_id: int = Path(..., description="Section ID to build tree for"),
    depth: int = Query(2, ge=1, le=5, description="Maximum tree depth to expand"),
    parent_code: Optional[str] = Query(None, description="Parent code to start tree from"),
    db: AsyncSession = Depends(get_async_session)
) -> TariffTreeResponse:
    """
    Get hierarchical tariff tree with lazy loading.
    
    Returns a hierarchical tree structure of tariff codes for the specified
    section with configurable depth and lazy loading support.
    
    Args:
        section_id: Section ID to build tree for
        depth: Maximum depth to expand (1-5)
        parent_code: Optional parent code to start tree from
        
    Returns:
        Hierarchical tariff tree with navigation metadata
        
    Raises:
        HTTPException: 404 if section or parent code not found
    """
    try:
        start_time = time.time()
        logger.info(f"Building tariff tree for section {section_id}, depth {depth}")
        
        # Verify section exists
        section_stmt = select(TariffSection).where(TariffSection.id == section_id)
        section_result = await db.execute(section_stmt)
        section = section_result.scalar_one_or_none()
        
        if not section:
            raise HTTPException(
                status_code=404,
                detail=f"Section with ID {section_id} not found"
            )
        
        # Build base query
        base_conditions = [TariffCode.section_id == section_id, TariffCode.is_active == True]
        
        if parent_code:
            # Verify parent code exists
            parent_stmt = select(TariffCode).where(TariffCode.hs_code == parent_code)
            parent_result = await db.execute(parent_stmt)
            parent = parent_result.scalar_one_or_none()
            
            if not parent:
                raise HTTPException(
                    status_code=404,
                    detail=f"Parent code {parent_code} not found"
                )
            
            # Get children of parent code
            base_conditions.append(TariffCode.parent_code == parent_code)
        else:
            # Get root level codes (level 2 - chapters)
            base_conditions.append(TariffCode.level == 2)
        
        # Query tariff codes with children count
        stmt = (
            select(TariffCode)
            .where(and_(*base_conditions))
            .order_by(TariffCode.hs_code)
        )
        
        result = await db.execute(stmt)
        codes = result.scalars().all()
        
        # Build tree nodes with children count calculated separately
        root_nodes = []
        for code in codes:
            # Count children for this code
            children_stmt = select(func.count(TariffCode.id)).where(
                TariffCode.parent_code == code.hs_code
            )
            children_result = await db.execute(children_stmt)
            children_count = children_result.scalar() or 0
            
            node = await _build_tree_node(code, children_count, depth - 1, db)
            root_nodes.append(node)
        
        # Calculate tree metadata
        total_nodes = len(root_nodes)
        max_depth = depth
        expanded_levels = list(range(1, depth + 1))
        
        execution_time = time.time() - start_time
        logger.info(f"Built tariff tree with {total_nodes} nodes in {execution_time:.3f}s")
        
        return TariffTreeResponse(
            root_nodes=root_nodes,
            total_nodes=total_nodes,
            max_depth=max_depth,
            expanded_levels=expanded_levels,
            section_id=section_id,
            parent_code=parent_code
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error building tariff tree: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while building tariff tree"
        )
    except Exception as e:
        logger.error(f"Unexpected error building tariff tree: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


async def _build_tree_node(
    code: TariffCode,
    children_count: int,
    remaining_depth: int,
    db: AsyncSession
) -> TariffTreeNode:
    """
    Build a tree node with optional children expansion.
    
    Args:
        code: TariffCode instance
        children_count: Number of direct children
        remaining_depth: Remaining depth to expand
        db: Database session
        
    Returns:
        TariffTreeNode with optional children
    """
    has_children = children_count > 0
    is_leaf = not has_children
    
    # Calculate depth from level
    depth = (code.level // 2) - 1
    
    # Get hierarchy path
    path = code.get_hierarchy_path() if hasattr(code, 'get_hierarchy_path') else [code.hs_code]
    
    node = TariffTreeNode(
        id=code.id,
        hs_code=code.hs_code,
        description=code.description,
        level=code.level,
        parent_code=code.parent_code,
        is_active=code.is_active,
        has_children=has_children,
        children_count=children_count,
        is_leaf=is_leaf,
        depth=depth,
        path=path
    )
    
    # Expand children if depth remaining and has children
    if remaining_depth > 0 and has_children:
        children_stmt = (
            select(TariffCode)
            .where(TariffCode.parent_code == code.hs_code)
            .order_by(TariffCode.hs_code)
        )
        
        children_result = await db.execute(children_stmt)
        children = children_result.scalars().all()
        
        children_nodes = []
        for child in children:
            # Count children for this child code
            child_children_stmt = select(func.count(TariffCode.id)).where(
                TariffCode.parent_code == child.hs_code
            )
            child_children_result = await db.execute(child_children_stmt)
            child_children_count = child_children_result.scalar() or 0
            
            child_node = await _build_tree_node(child, child_children_count, remaining_depth - 1, db)
            children_nodes.append(child_node)
        
        node.children = children_nodes
    
    return node


@router.get("/code/{hs_code}", response_model=TariffDetailResponse)
async def get_tariff_detail(
    hs_code: str = Path(..., description="HS code to get details for"),
    include_rates: bool = Query(True, description="Include duty and FTA rates"),
    include_children: bool = Query(True, description="Include direct child codes"),
    include_related: bool = Query(False, description="Include related codes"),
    db: AsyncSession = Depends(get_async_session)
) -> TariffDetailResponse:
    """
    Get detailed tariff information with all related data.
    
    Returns comprehensive tariff code information including duty rates,
    FTA rates, dumping duties, TCOs, GST provisions, and hierarchy context.
    
    Args:
        hs_code: HS code to get details for
        include_rates: Whether to include duty and FTA rates
        include_children: Whether to include direct child codes
        include_related: Whether to include related/similar codes
        
    Returns:
        Comprehensive tariff detail response
        
    Raises:
        HTTPException: 404 if HS code not found
    """
    try:
        start_time = time.time()
        logger.info(f"Fetching tariff details for HS code {hs_code}")
        
        # Clean HS code
        clean_hs_code = ''.join(c for c in hs_code if c.isdigit())
        
        # Build query with eager loading
        stmt = (
            select(TariffCode)
            .options(
                selectinload(TariffCode.section),
                selectinload(TariffCode.chapter),
                selectinload(TariffCode.parent)
            )
            .where(TariffCode.hs_code == clean_hs_code)
        )
        
        result = await db.execute(stmt)
        tariff = result.scalar_one_or_none()
        
        if not tariff:
            raise HTTPException(
                status_code=404,
                detail=f"Tariff code {clean_hs_code} not found"
            )
        
        # Build tariff response
        tariff_response = TariffCodeResponse(
            id=tariff.id,
            hs_code=tariff.hs_code,
            description=tariff.description,
            unit_description=tariff.unit_description,
            parent_code=tariff.parent_code,
            level=tariff.level,
            chapter_notes=tariff.chapter_notes,
            section_id=tariff.section_id,
            chapter_id=tariff.chapter_id,
            is_active=tariff.is_active,
            created_at=tariff.created_at,
            updated_at=tariff.updated_at,
            is_chapter_level=tariff.is_chapter_level,
            is_heading_level=tariff.is_heading_level,
            is_subheading_level=tariff.is_subheading_level,
            is_statistical_level=tariff.is_statistical_level,
            hierarchy_path=tariff.get_hierarchy_path(),
            chapter_code=tariff.get_chapter_code(),
            heading_code=tariff.get_heading_code()
        )
        
        # Initialize response
        detail_response = TariffDetailResponse(tariff=tariff_response)
        
        # Add section and chapter info
        if tariff.section:
            detail_response.section = {
                "id": tariff.section.id,
                "section_number": tariff.section.section_number,
                "title": tariff.section.title,
                "description": tariff.section.description
            }
        
        if tariff.chapter:
            detail_response.chapter = {
                "id": tariff.chapter.id,
                "chapter_number": tariff.chapter.chapter_number,
                "title": tariff.chapter.title,
                "chapter_notes": tariff.chapter.chapter_notes
            }
        
        # Add parent info
        if tariff.parent:
            detail_response.parent = TariffCodeSummary(
                id=tariff.parent.id,
                hs_code=tariff.parent.hs_code,
                description=tariff.parent.description,
                level=tariff.parent.level,
                is_active=tariff.parent.is_active,
                parent_code=tariff.parent.parent_code
            )
        
        # Include rates if requested
        if include_rates:
            detail_response.duty_rates = await _get_duty_rates(tariff.id, db)
            detail_response.fta_rates = await _get_fta_rates(tariff.id, db)
        
        # Include children if requested
        if include_children:
            detail_response.children = await _get_child_codes(tariff.hs_code, db)
        
        # Build breadcrumbs
        detail_response.breadcrumbs = _build_breadcrumbs(tariff)
        
        # Include related codes if requested
        if include_related:
            detail_response.related_codes = await _get_related_codes(tariff, db)
        
        execution_time = time.time() - start_time
        logger.info(f"Retrieved tariff details for {clean_hs_code} in {execution_time:.3f}s")
        
        return detail_response
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching tariff details for {hs_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching tariff details"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching tariff details for {hs_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


async def _get_duty_rates(tariff_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
    """Get duty rates for a tariff code."""
    stmt = select(DutyRate).where(DutyRate.tariff_code_id == tariff_id)
    result = await db.execute(stmt)
    rates = result.scalars().all()
    
    return [
        {
            "id": rate.id,
            "rate_type": rate.rate_type,
            "rate_value": float(rate.rate_value) if rate.rate_value else None,
            "rate_text": rate.rate_text,
            "unit_type": rate.unit_type,
            "effective_date": rate.effective_date.isoformat() if rate.effective_date else None,
            "expiry_date": rate.expiry_date.isoformat() if rate.expiry_date else None
        }
        for rate in rates
    ]


async def _get_fta_rates(tariff_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
    """Get FTA rates for a tariff code."""
    stmt = (
        select(FtaRate)
        .options(selectinload(FtaRate.trade_agreement))
        .where(FtaRate.tariff_code_id == tariff_id)
    )
    result = await db.execute(stmt)
    rates = result.scalars().all()
    
    return [
        {
            "id": rate.id,
            "fta_code": rate.fta_code,
            "preferential_rate": float(rate.preferential_rate) if rate.preferential_rate else None,
            "rate_text": rate.rate_text,
            "safeguard_rate": float(rate.safeguard_rate) if rate.safeguard_rate else None,
            "effective_date": rate.effective_date.isoformat() if rate.effective_date else None,
            "trade_agreement": {
                "fta_code": rate.trade_agreement.fta_code,
                "full_name": rate.trade_agreement.full_name
            } if rate.trade_agreement else None
        }
        for rate in rates
    ]


async def _get_child_codes(parent_hs_code: str, db: AsyncSession) -> List[TariffCodeSummary]:
    """Get direct child codes for a tariff code."""
    stmt = (
        select(TariffCode)
        .where(TariffCode.parent_code == parent_hs_code)
        .order_by(TariffCode.hs_code)
        .limit(50)  # Limit to prevent large responses
    )
    result = await db.execute(stmt)
    children = result.scalars().all()
    
    return [
        TariffCodeSummary(
            id=child.id,
            hs_code=child.hs_code,
            description=child.description,
            level=child.level,
            is_active=child.is_active,
            parent_code=child.parent_code
        )
        for child in children
    ]


def _build_breadcrumbs(tariff: TariffCode) -> List[Dict[str, str]]:
    """Build breadcrumb navigation for a tariff code."""
    breadcrumbs = []
    
    # Add section breadcrumb
    if tariff.section:
        breadcrumbs.append({
            "type": "section",
            "code": str(tariff.section.section_number),
            "title": tariff.section.title,
            "url": f"/api/tariff/sections"
        })
    
    # Add chapter breadcrumb
    if tariff.chapter:
        breadcrumbs.append({
            "type": "chapter",
            "code": f"{tariff.chapter.chapter_number:02d}",
            "title": tariff.chapter.title,
            "url": f"/api/tariff/chapters/{tariff.section_id}"
        })
    
    # Add hierarchy levels
    hierarchy_path = tariff.get_hierarchy_path()
    for i, code in enumerate(hierarchy_path[:-1]):  # Exclude current code
        level = len(code)
        breadcrumbs.append({
            "type": f"level_{level}",
            "code": code,
            "title": f"HS {code}",
            "url": f"/api/tariff/code/{code}"
        })
    
    return breadcrumbs


async def _get_related_codes(tariff: TariffCode, db: AsyncSession) -> List[TariffCodeSummary]:
    """Get related/similar codes for a tariff code."""
    # Get sibling codes (same parent)
    if tariff.parent_code:
        stmt = (
            select(TariffCode)
            .where(
                and_(
                    TariffCode.parent_code == tariff.parent_code,
                    TariffCode.hs_code != tariff.hs_code,
                    TariffCode.is_active == True
                )
            )
            .order_by(TariffCode.hs_code)
            .limit(10)
        )
        result = await db.execute(stmt)
        related = result.scalars().all()
        
        return [
            TariffCodeSummary(
                id=code.id,
                hs_code=code.hs_code,
                description=code.description,
                level=code.level,
                is_active=code.is_active,
                parent_code=code.parent_code
            )
            for code in related
        ]
    
    return []


@router.get("/search", response_model=TariffSearchResponse)
async def search_tariff_codes(
    query: Optional[str] = Query(None, description="Search query"),
    level: Optional[int] = Query(None, ge=2, le=10, description="Filter by level"),
    section_id: Optional[int] = Query(None, description="Filter by section"),
    chapter_id: Optional[int] = Query(None, description="Filter by chapter"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    hs_code_starts_with: Optional[str] = Query(None, description="HS code prefix filter"),
    limit: int = Query(50, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Results to skip"),
    sort_by: str = Query("hs_code", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_async_session)
) -> TariffSearchResponse:
    """
    Search tariff codes with filters and pagination.
    
    Provides comprehensive search functionality with full-text search,
    filters, sorting, and pagination for tariff codes.
    
    Args:
        query: Search query for description
        level: Filter by hierarchy level
        section_id: Filter by section ID
        chapter_id: Filter by chapter ID
        is_active: Filter by active status
        hs_code_starts_with: Filter by HS code prefix
        limit: Results per page (1-1000)
        offset: Results to skip
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Paginated search results with metadata
    """
    try:
        start_time = time.time()
        logger.info(f"Searching tariff codes with query: {query}")
        
        # Build base query
        base_stmt = select(TariffCode).options(
            selectinload(TariffCode.section),
            selectinload(TariffCode.chapter)
        )
        
        # Build conditions
        conditions = []
        
        if is_active is not None:
            conditions.append(TariffCode.is_active == is_active)
        
        if level:
            conditions.append(TariffCode.level == level)
        
        if section_id:
            conditions.append(TariffCode.section_id == section_id)
        
        if chapter_id:
            conditions.append(TariffCode.chapter_id == chapter_id)
        
        if hs_code_starts_with:
            clean_prefix = ''.join(c for c in hs_code_starts_with if c.isdigit())
            conditions.append(TariffCode.hs_code.like(f"{clean_prefix}%"))
        
        if query:
            # Full-text search on description
            search_condition = TariffCode.description.ilike(f"%{query}%")
            conditions.append(search_condition)
        
        # Apply conditions
        if conditions:
            base_stmt = base_stmt.where(and_(*conditions))
        
        # Get total count
        count_stmt = select(func.count()).select_from(
            base_stmt.subquery()
        )
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Apply sorting
        sort_column = getattr(TariffCode, sort_by, TariffCode.hs_code)
        if sort_order == "desc":
            sort_column = sort_column.desc()
        
        # Apply pagination
        search_stmt = (
            base_stmt
            .order_by(sort_column)
            .offset(offset)
            .limit(limit)
        )
        
        # Execute search
        search_result = await db.execute(search_stmt)
        tariff_codes = search_result.scalars().all()
        
        # Build search results
        results = []
        for code in tariff_codes:
            # Calculate relevance score (simple implementation)
            relevance_score = 1.0
            match_type = "description"
            
            if query and query.lower() in code.description.lower():
                relevance_score = 0.9
            
            if hs_code_starts_with and code.hs_code.startswith(hs_code_starts_with):
                relevance_score = 1.0
                match_type = "hs_code"
            
            # Highlight description (simple implementation)
            highlighted_description = code.description
            if query:
                highlighted_description = code.description.replace(
                    query, f"<mark>{query}</mark>"
                )
            
            result = TariffSearchResult(
                id=code.id,
                hs_code=code.hs_code,
                description=code.description,
                level=code.level,
                is_active=code.is_active,
                parent_code=code.parent_code,
                relevance_score=relevance_score,
                match_type=match_type,
                highlighted_description=highlighted_description,
                section_title=code.section.title if code.section else None,
                chapter_title=code.chapter.title if code.chapter else None
            )
            results.append(result)
        
        # Create pagination metadata
        pagination = PaginationMeta.create(total_count, limit, offset)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Search completed: {len(results)} results in {execution_time:.3f}s")
        
        return TariffSearchResponse(
            results=results,
            pagination=pagination,
            query=query,
            total_results=total_count,
            search_time_ms=execution_time * 1000
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during tariff search: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred during search"
        )
    except Exception as e:
        logger.error(f"Unexpected error during tariff search: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during search"
        )


@router.get("/compare", response_model=Dict[str, Any])
async def compare_tariff_codes(
    codes: str = Query(..., description="Comma-separated list of HS codes to compare"),
    include_duties: bool = Query(True, description="Include duty rate comparisons"),
    include_fta: bool = Query(True, description="Include FTA rate comparisons"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Compare multiple tariff codes side by side.
    
    Provides detailed comparison of tariff codes including descriptions,
    duty rates, FTA rates, and other relevant information for analysis.
    
    Args:
        codes: Comma-separated list of HS codes to compare (max 5)
        include_duties: Whether to include duty rate comparisons
        include_fta: Whether to include FTA rate comparisons
        
    Returns:
        Detailed comparison data for the specified codes
        
    Raises:
        HTTPException: 400 for invalid codes or too many codes
    """
    try:
        start_time = time.time()
        
        # Parse and validate codes
        code_list = [code.strip() for code in codes.split(',') if code.strip()]
        
        if not code_list:
            raise HTTPException(status_code=400, detail="No codes provided")
        
        if len(code_list) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 codes allowed for comparison")
        
        logger.info(f"Comparing tariff codes: {code_list}")
        
        # Fetch tariff codes with related data
        stmt = (
            select(TariffCode)
            .options(
                selectinload(TariffCode.section),
                selectinload(TariffCode.chapter),
                selectinload(TariffCode.duty_rates) if include_duties else selectinload(TariffCode.duty_rates).raiseload(),
                selectinload(TariffCode.fta_rates) if include_fta else selectinload(TariffCode.fta_rates).raiseload(),
                selectinload(TariffCode.dumping_duties),
                selectinload(TariffCode.tcos),
                selectinload(TariffCode.gst_provisions)
            )
            .where(TariffCode.hs_code.in_(code_list))
        )
        
        result = await db.execute(stmt)
        found_codes = result.scalars().all()
        
        # Check if all codes were found
        found_hs_codes = {code.hs_code for code in found_codes}
        missing_codes = set(code_list) - found_hs_codes
        
        if missing_codes:
            logger.warning(f"Some codes not found: {missing_codes}")
        
        # Build comparison data
        comparison_data = {
            "codes": [],
            "summary": {
                "total_codes": len(found_codes),
                "requested_codes": len(code_list),
                "missing_codes": list(missing_codes)
            },
            "comparison_matrix": {}
        }
        
        # Process each found code
        for code in found_codes:
            code_data = {
                "hs_code": code.hs_code,
                "description": code.description,
                "level": code.level,
                "is_active": code.is_active,
                "section": {
                    "number": code.section.section_number if code.section else None,
                    "title": code.section.title if code.section else None
                },
                "chapter": {
                    "number": code.chapter.chapter_number if code.chapter else None,
                    "title": code.chapter.title if code.chapter else None
                }
            }
            
            # Add duty rates if requested
            if include_duties and code.duty_rates:
                code_data["duty_rates"] = [
                    {
                        "rate_type": rate.rate_type,
                        "rate": rate.rate,
                        "unit": rate.unit,
                        "effective_from": rate.effective_from.isoformat() if rate.effective_from else None
                    }
                    for rate in code.duty_rates
                ]
            
            # Add FTA rates if requested
            if include_fta and code.fta_rates:
                code_data["fta_rates"] = [
                    {
                        "partner_country": rate.partner_country,
                        "agreement_name": rate.agreement_name,
                        "preferential_rate": rate.preferential_rate,
                        "effective_from": rate.effective_from.isoformat() if rate.effective_from else None
                    }
                    for rate in code.fta_rates
                ]
            
            # Add other relevant data
            code_data["has_dumping_duties"] = len(code.dumping_duties) > 0
            code_data["has_tcos"] = len(code.tcos) > 0
            code_data["has_gst_provisions"] = len(code.gst_provisions) > 0
            
            comparison_data["codes"].append(code_data)
        
        # Build comparison matrix for key differences
        if len(found_codes) > 1:
            comparison_data["comparison_matrix"] = _build_comparison_matrix(found_codes)
        
        execution_time = time.time() - start_time
        comparison_data["execution_time_ms"] = execution_time * 1000
        
        logger.info(f"Comparison completed for {len(found_codes)} codes in {execution_time:.3f}s")
        
        return comparison_data
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during tariff comparison: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred during comparison"
        )
    except Exception as e:
        logger.error(f"Unexpected error during tariff comparison: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during comparison"
        )


def _build_comparison_matrix(codes: List[TariffCode]) -> Dict[str, Any]:
    """
    Build a comparison matrix highlighting key differences between codes.
    
    Args:
        codes: List of TariffCode objects to compare
        
    Returns:
        Dictionary containing comparison analysis
    """
    matrix = {
        "levels": {},
        "sections": {},
        "chapters": {},
        "duty_complexity": {},
        "fta_coverage": {}
    }
    
    for code in codes:
        # Level distribution
        level = code.level
        matrix["levels"][level] = matrix["levels"].get(level, 0) + 1
        
        # Section distribution
        section_title = code.section.title if code.section else "Unknown"
        matrix["sections"][section_title] = matrix["sections"].get(section_title, 0) + 1
        
        # Chapter distribution
        chapter_title = code.chapter.title if code.chapter else "Unknown"
        matrix["chapters"][chapter_title] = matrix["chapters"].get(chapter_title, 0) + 1
        
        # Duty complexity (number of different duty rates)
        duty_count = len(code.duty_rates) if code.duty_rates else 0
        matrix["duty_complexity"][code.hs_code] = duty_count
        
        # FTA coverage (number of FTA agreements)
        fta_count = len(code.fta_rates) if code.fta_rates else 0
        matrix["fta_coverage"][code.hs_code] = fta_count
    
    return matrix