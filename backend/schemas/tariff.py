"""
Tariff code schemas for the Customs Broker Portal.

This module contains Pydantic schemas for TariffCode model validation,
including request/response schemas, tree navigation, and search functionality.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import (
    BaseSchema, HSCodeValidator, PaginationMeta, SearchParams
)


class TariffCodeBase(BaseModel):
    """
    Base schema for TariffCode with core fields.
    
    Contains the essential fields shared across create, update, and response schemas.
    """
    
    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="HS code (2-10 digits)",
        example="0101210000"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Description of the tariff code",
        example="Live horses - Pure-bred breeding animals"
    )
    unit_description: Optional[str] = Field(
        None,
        max_length=100,
        description="Unit of measurement description",
        example="Number (No.)"
    )
    parent_code: Optional[str] = Field(
        None,
        min_length=2,
        max_length=8,
        description="Parent HS code for hierarchy",
        example="01012100"
    )
    level: int = Field(
        ...,
        ge=2,
        le=10,
        description="Hierarchy level (2, 4, 6, 8, or 10 digits)",
        example=10
    )
    chapter_notes: Optional[str] = Field(
        None,
        description="Additional notes for the chapter"
    )
    section_id: Optional[int] = Field(
        None,
        description="Foreign key to tariff_sections"
    )
    chapter_id: Optional[int] = Field(
        None,
        description="Foreign key to tariff_chapters"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the code is currently active"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('parent_code')
    @classmethod
    def validate_parent_code(cls, v):
        """Validate parent code format if provided."""
        if v:
            return HSCodeValidator.validate_hs_code(v)
        return v
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        """Validate level is one of the allowed values."""
        if v not in [2, 4, 6, 8, 10]:
            raise ValueError("Level must be 2, 4, 6, 8, or 10")
        return v
    
    @model_validator(mode='after')
    def validate_hierarchy_consistency(self):
        """Validate HS code and level consistency."""
        hs_code = self.hs_code
        level = self.level
        parent_code = self.parent_code
        
        if hs_code and level:
            # Check HS code length matches level
            if len(hs_code) != level:
                raise ValueError(f"HS code length ({len(hs_code)}) must match level ({level})")
            
            # Check parent code relationship
            if parent_code and level > 2:
                if not hs_code.startswith(parent_code):
                    raise ValueError("HS code must start with parent code")
                if len(parent_code) >= len(hs_code):
                    raise ValueError("Parent code must be shorter than HS code")
        
        return self


class TariffCodeCreate(TariffCodeBase):
    """
    Schema for creating new tariff codes.
    
    Inherits from TariffCodeBase with any creation-specific validations.
    """
    pass


class TariffCodeUpdate(BaseModel):
    """
    Schema for updating existing tariff codes.
    
    All fields are optional to support partial updates.
    """
    
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=2000,
        description="Description of the tariff code"
    )
    unit_description: Optional[str] = Field(
        None,
        max_length=100,
        description="Unit of measurement description"
    )
    chapter_notes: Optional[str] = Field(
        None,
        description="Additional notes for the chapter"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the code is currently active"
    )


class TariffCodeSummary(BaseModel):
    """
    Summary schema for tariff codes in lists.
    
    Contains minimal fields for efficient list responses.
    """
    
    model_config = {"from_attributes": True}
    
    id: int = Field(description="Primary key")
    hs_code: str = Field(description="HS code")
    description: str = Field(description="Description of the tariff code")
    level: int = Field(description="Hierarchy level")
    is_active: bool = Field(description="Whether the code is currently active")
    parent_code: Optional[str] = Field(None, description="Parent HS code")
    
    # Computed properties
    has_children: Optional[bool] = Field(
        None,
        description="Whether this code has child codes"
    )


class TariffTreeNode(BaseModel):
    """
    Schema for hierarchical tree navigation.
    
    Represents a node in the tariff code tree with navigation metadata.
    """
    
    model_config = {"from_attributes": True}
    
    id: int = Field(description="Primary key")
    hs_code: str = Field(description="HS code")
    description: str = Field(description="Description of the tariff code")
    level: int = Field(description="Hierarchy level")
    parent_code: Optional[str] = Field(None, description="Parent HS code")
    is_active: bool = Field(description="Whether the code is currently active")
    
    # Tree navigation metadata
    has_children: bool = Field(
        default=False,
        description="Whether this node has child nodes"
    )
    children_count: int = Field(
        default=0,
        description="Number of direct child nodes"
    )
    is_leaf: bool = Field(
        default=True,
        description="Whether this is a leaf node (no children)"
    )
    depth: int = Field(
        default=0,
        description="Depth in the tree (0 = root)"
    )
    path: List[str] = Field(
        default_factory=list,
        description="Full path from root to this node"
    )
    
    # Optional child nodes for expanded tree
    children: Optional[List["TariffTreeNode"]] = Field(
        None,
        description="Child nodes (if expanded)"
    )


class TariffCodeResponse(TariffCodeBase, BaseSchema):
    """
    Complete response schema for tariff codes.
    
    Includes all fields plus computed properties and relationships.
    """
    
    id: int = Field(description="Primary key")
    
    # Computed properties from the model
    is_chapter_level: Optional[bool] = Field(
        None,
        description="Whether this is a chapter-level code (2 digits)"
    )
    is_heading_level: Optional[bool] = Field(
        None,
        description="Whether this is a heading-level code (4 digits)"
    )
    is_subheading_level: Optional[bool] = Field(
        None,
        description="Whether this is a subheading-level code (6 digits)"
    )
    is_statistical_level: Optional[bool] = Field(
        None,
        description="Whether this is a statistical-level code (8 or 10 digits)"
    )
    
    # Hierarchy information
    hierarchy_path: Optional[List[str]] = Field(
        None,
        description="Full hierarchy path from root to this code"
    )
    chapter_code: Optional[str] = Field(
        None,
        description="Chapter-level code (2 digits)"
    )
    heading_code: Optional[str] = Field(
        None,
        description="Heading-level code (4 digits)"
    )
    
    # Relationship counts (for lazy loading)
    duty_rates_count: Optional[int] = Field(
        None,
        description="Number of associated duty rates"
    )
    fta_rates_count: Optional[int] = Field(
        None,
        description="Number of associated FTA rates"
    )
    children_count: Optional[int] = Field(
        None,
        description="Number of direct child codes"
    )


class TariffSearchRequest(SearchParams):
    """
    Search request schema for tariff codes.
    
    Extends base search parameters with tariff-specific filters.
    """
    
    # Hierarchy filters
    level: Optional[int] = Field(
        None,
        ge=2,
        le=10,
        description="Filter by hierarchy level"
    )
    section_id: Optional[int] = Field(
        None,
        description="Filter by section ID"
    )
    chapter_id: Optional[int] = Field(
        None,
        description="Filter by chapter ID"
    )
    parent_code: Optional[str] = Field(
        None,
        description="Filter by parent code"
    )
    
    # Status filters
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status"
    )
    
    # Content filters
    description_contains: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Filter by description content"
    )
    hs_code_starts_with: Optional[str] = Field(
        None,
        min_length=1,
        max_length=8,
        description="Filter by HS code prefix"
    )
    
    # Advanced filters
    has_duty_rates: Optional[bool] = Field(
        None,
        description="Filter codes that have duty rates"
    )
    has_fta_rates: Optional[bool] = Field(
        None,
        description="Filter codes that have FTA rates"
    )
    has_children: Optional[bool] = Field(
        None,
        description="Filter codes that have child codes"
    )
    
    @field_validator('hs_code_starts_with')
    @classmethod
    def validate_hs_code_prefix(cls, v):
        """Validate HS code prefix format."""
        if v:
            # Allow partial HS codes for prefix search
            cleaned = ''.join(c for c in v if c.isdigit())
            if not cleaned or len(cleaned) > 8:
                raise ValueError("HS code prefix must be 1-8 digits")
            return cleaned
        return v


class TariffSearchResult(TariffCodeSummary):
    """
    Search result schema for individual tariff codes.
    
    Extends summary with search-specific metadata.
    """
    
    # Search relevance
    relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Search relevance score (0.0-1.0)"
    )
    match_type: Optional[str] = Field(
        None,
        description="Type of match (exact, prefix, description, etc.)"
    )
    highlighted_description: Optional[str] = Field(
        None,
        description="Description with search terms highlighted"
    )
    
    # Additional context
    section_title: Optional[str] = Field(
        None,
        description="Title of the parent section"
    )
    chapter_title: Optional[str] = Field(
        None,
        description="Title of the parent chapter"
    )


class TariffSearchResponse(BaseModel):
    """
    Complete search response with results and metadata.
    
    Contains search results, pagination, and search statistics.
    """
    
    results: List[TariffSearchResult] = Field(
        description="Search results"
    )
    pagination: PaginationMeta = Field(
        description="Pagination metadata"
    )
    
    # Search metadata
    query: Optional[str] = Field(
        None,
        description="Original search query"
    )
    total_results: int = Field(
        description="Total number of matching results"
    )
    search_time_ms: Optional[float] = Field(
        None,
        description="Search execution time in milliseconds"
    )
    
    # Search statistics
    facets: Optional[Dict[str, Any]] = Field(
        None,
        description="Search facets for filtering"
    )
    suggestions: Optional[List[str]] = Field(
        None,
        description="Search suggestions for query improvement"
    )


class TariffTreeResponse(BaseModel):
    """
    Response schema for hierarchical tariff tree.
    
    Contains tree structure with navigation metadata.
    """
    
    root_nodes: List[TariffTreeNode] = Field(
        description="Root nodes of the tree"
    )
    
    # Tree metadata
    total_nodes: int = Field(
        description="Total number of nodes in the tree"
    )
    max_depth: int = Field(
        description="Maximum depth of the tree"
    )
    expanded_levels: List[int] = Field(
        default_factory=list,
        description="Levels that are expanded in this response"
    )
    
    # Navigation context
    section_id: Optional[int] = Field(
        None,
        description="Section ID if tree is filtered by section"
    )
    chapter_id: Optional[int] = Field(
        None,
        description="Chapter ID if tree is filtered by chapter"
    )
    parent_code: Optional[str] = Field(
        None,
        description="Parent code if tree shows children of specific code"
    )


class TariffDetailResponse(BaseModel):
    """
    Comprehensive tariff detail response.
    
    Contains complete tariff information with all related data.
    """
    
    model_config = {"from_attributes": True}
    
    # Core tariff information
    tariff: TariffCodeResponse = Field(
        description="Core tariff code information"
    )
    
    # Related data (optional for lazy loading)
    duty_rates: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Associated duty rates"
    )
    fta_rates: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Associated FTA rates"
    )
    children: Optional[List[TariffCodeSummary]] = Field(
        None,
        description="Direct child codes"
    )
    
    # Hierarchy context
    section: Optional[Dict[str, Any]] = Field(
        None,
        description="Parent section information"
    )
    chapter: Optional[Dict[str, Any]] = Field(
        None,
        description="Parent chapter information"
    )
    parent: Optional[TariffCodeSummary] = Field(
        None,
        description="Parent code information"
    )
    
    # Navigation aids
    breadcrumbs: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Breadcrumb navigation path"
    )
    related_codes: Optional[List[TariffCodeSummary]] = Field(
        None,
        description="Related or similar codes"
    )


# Update forward references for recursive models
TariffTreeNode.model_rebuild()