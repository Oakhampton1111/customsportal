"""
Reports and Analytics schemas for the Customs Broker Portal.

This module contains Pydantic schemas for reports and analytics API endpoints,
including request/response models, validation, and serialization.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from pydantic.types import PositiveInt

from schemas.common import BaseSchema, PaginationMeta, SearchParams


# Enums for report types and statuses
class ReportType(str, Enum):
    """Types of reports available in the system."""
    TRADE_VOLUME = "trade_volume"
    DUTY_SAVINGS = "duty_savings"
    CLASSIFICATION_ACCURACY = "classification_accuracy"
    COMPLIANCE_SUMMARY = "compliance_summary"
    DOCUMENT_ANALYTICS = "document_analytics"
    CLIENT_ACTIVITY = "client_activity"
    SHIPMENT_TRACKING = "shipment_tracking"
    FINANCIAL_SUMMARY = "financial_summary"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """Status of report generation."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReportFormat(str, Enum):
    """Available export formats for reports."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ScheduleFrequency(str, Enum):
    """Frequency options for scheduled reports."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MetricType(str, Enum):
    """Types of analytics metrics."""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    TREND = "trend"


# Base report schemas
class ReportBase(BaseModel):
    """Base report schema with common fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True,
        protected_namespaces=()
    )
    
    title: str = Field(..., max_length=255, description="Report title")
    description: Optional[str] = Field(None, description="Report description")
    report_type: ReportType = Field(..., description="Type of report")
    
    # Date range for report data
    date_from: Optional[date] = Field(None, description="Start date for report data")
    date_to: Optional[date] = Field(None, description="End date for report data")
    
    # Filters and parameters
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Report filters")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Report parameters")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Report tags")
    is_public: bool = Field(False, description="Whether report is publicly accessible")
    
    @field_validator('date_from', 'date_to')
    @classmethod
    def validate_dates(cls, v):
        """Validate date fields."""
        if v and isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
            return cleaned_tags
        return []


class ReportCreate(ReportBase):
    """Schema for creating a new report."""
    
    created_by: str = Field(..., max_length=100, description="User who created the report")
    auto_refresh: bool = Field(False, description="Whether to auto-refresh report data")
    refresh_interval_hours: Optional[int] = Field(None, ge=1, le=168, description="Auto-refresh interval in hours")


class ReportUpdate(BaseModel):
    """Schema for updating report metadata."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)
    date_from: Optional[date] = Field(None)
    date_to: Optional[date] = Field(None)
    filters: Optional[Dict[str, Any]] = Field(None)
    parameters: Optional[Dict[str, Any]] = Field(None)
    tags: Optional[List[str]] = Field(None)
    is_public: Optional[bool] = Field(None)
    auto_refresh: Optional[bool] = Field(None)
    refresh_interval_hours: Optional[int] = Field(None, ge=1, le=168)
    last_modified_by: Optional[str] = Field(None, max_length=100)


class ReportResponse(ReportBase):
    """Schema for report response."""
    
    id: int = Field(..., description="Report ID")
    status: ReportStatus = Field(..., description="Report generation status")
    
    # Generation info
    created_by: str = Field(..., description="User who created the report")
    last_modified_by: Optional[str] = Field(None, description="User who last modified")
    generated_at: Optional[datetime] = Field(None, description="When report was last generated")
    generation_time_ms: Optional[int] = Field(None, description="Generation time in milliseconds")
    
    # Data info
    data_points: Optional[int] = Field(None, description="Number of data points in report")
    file_size_bytes: Optional[int] = Field(None, description="Generated file size in bytes")
    
    # Auto-refresh
    auto_refresh: bool = Field(False, description="Whether auto-refresh is enabled")
    refresh_interval_hours: Optional[int] = Field(None, description="Auto-refresh interval")
    last_refreshed: Optional[datetime] = Field(None, description="Last refresh timestamp")
    next_refresh: Optional[datetime] = Field(None, description="Next scheduled refresh")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @computed_field
    @property
    def file_size_mb(self) -> Optional[float]:
        """File size in megabytes."""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return None
    
    @computed_field
    @property
    def is_stale(self) -> bool:
        """Whether report data is considered stale (older than 24 hours)."""
        if not self.generated_at:
            return True
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(hours=24)
        return self.generated_at < threshold
    
    @computed_field
    @property
    def needs_refresh(self) -> bool:
        """Whether report needs to be refreshed."""
        if not self.auto_refresh or not self.next_refresh:
            return False
        return datetime.utcnow() >= self.next_refresh


class ReportSummary(BaseModel):
    """Summary schema for report lists."""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: int
    title: str
    report_type: ReportType
    status: ReportStatus
    created_by: str
    generated_at: Optional[datetime]
    data_points: Optional[int]
    is_public: bool
    created_at: datetime
    
    @computed_field
    @property
    def is_stale(self) -> bool:
        """Whether report data is stale."""
        if not self.generated_at:
            return True
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(hours=24)
        return self.generated_at < threshold


# Report template schemas
class ReportTemplateBase(BaseModel):
    """Base schema for report templates."""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    name: str = Field(..., max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    report_type: ReportType = Field(..., description="Type of report")
    category: str = Field(..., max_length=100, description="Template category")
    
    # Template configuration
    default_filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Default filters")
    default_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Default parameters")
    required_fields: Optional[List[str]] = Field(default_factory=list, description="Required fields")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Template tags")
    is_system_template: bool = Field(False, description="Whether this is a system template")
    is_active: bool = Field(True, description="Whether template is active")


class ReportTemplateCreate(ReportTemplateBase):
    """Schema for creating report templates."""
    
    created_by: str = Field(..., max_length=100, description="User who created the template")


class ReportTemplateResponse(ReportTemplateBase):
    """Schema for report template response."""
    
    id: int = Field(..., description="Template ID")
    created_by: str = Field(..., description="User who created the template")
    usage_count: int = Field(0, description="Number of times template has been used")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# Report scheduling schemas
class ReportScheduleBase(BaseModel):
    """Base schema for report scheduling."""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    name: str = Field(..., max_length=255, description="Schedule name")
    report_template_id: int = Field(..., description="Report template to use")
    frequency: ScheduleFrequency = Field(..., description="Schedule frequency")
    
    # Schedule timing
    start_date: date = Field(..., description="When to start the schedule")
    end_date: Optional[date] = Field(None, description="When to end the schedule")
    time_of_day: str = Field("09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Time to run (HH:MM)")
    
    # Recipients
    email_recipients: Optional[List[str]] = Field(default_factory=list, description="Email recipients")
    
    # Options
    export_format: ReportFormat = Field(ReportFormat.PDF, description="Export format")
    include_charts: bool = Field(True, description="Include charts in export")
    is_active: bool = Field(True, description="Whether schedule is active")
    
    @field_validator('email_recipients')
    @classmethod
    def validate_emails(cls, v):
        """Validate email addresses."""
        if v:
            for email in v:
                if '@' not in email:
                    raise ValueError(f"Invalid email format: {email}")
        return v


class ReportScheduleCreate(ReportScheduleBase):
    """Schema for creating report schedules."""
    
    created_by: str = Field(..., max_length=100, description="User who created the schedule")


class ReportScheduleResponse(ReportScheduleBase):
    """Schema for report schedule response."""
    
    id: int = Field(..., description="Schedule ID")
    created_by: str = Field(..., description="User who created the schedule")
    last_run: Optional[datetime] = Field(None, description="Last execution time")
    next_run: Optional[datetime] = Field(None, description="Next scheduled execution")
    run_count: int = Field(0, description="Number of times executed")
    success_count: int = Field(0, description="Number of successful executions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @computed_field
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.run_count == 0:
            return 0.0
        return round((self.success_count / self.run_count) * 100, 2)


# Analytics schemas
class AnalyticsMetric(BaseModel):
    """Schema for analytics metrics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., description="Metric name")
    value: Union[int, float, Decimal] = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Type of metric")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    description: Optional[str] = Field(None, description="Metric description")
    
    # Comparison data
    previous_value: Optional[Union[int, float, Decimal]] = Field(None, description="Previous period value")
    change_percentage: Optional[float] = Field(None, description="Percentage change from previous period")
    trend: Optional[str] = Field(None, description="Trend direction (up/down/stable)")
    
    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="When metric was calculated")
    data_points: Optional[int] = Field(None, description="Number of data points used")
    
    @computed_field
    @property
    def formatted_value(self) -> str:
        """Formatted value with unit."""
        if self.unit:
            return f"{self.value} {self.unit}"
        return str(self.value)


class DashboardAnalytics(BaseModel):
    """Schema for dashboard analytics data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Key Performance Indicators
    total_shipments: AnalyticsMetric = Field(..., description="Total shipments processed")
    total_duty_paid: AnalyticsMetric = Field(..., description="Total duty payments")
    duty_savings: AnalyticsMetric = Field(..., description="Total duty savings from FTAs")
    classification_accuracy: AnalyticsMetric = Field(..., description="Classification accuracy rate")
    
    # Volume metrics
    monthly_volume: AnalyticsMetric = Field(..., description="Monthly trade volume")
    document_processing: AnalyticsMetric = Field(..., description="Documents processed")
    compliance_rate: AnalyticsMetric = Field(..., description="Compliance success rate")
    
    # Trends
    volume_trend: List[Dict[str, Any]] = Field(..., description="Volume trend data")
    duty_trend: List[Dict[str, Any]] = Field(..., description="Duty payments trend")
    savings_trend: List[Dict[str, Any]] = Field(..., description="Savings trend data")
    
    # Generated metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When analytics were generated")
    data_period_start: date = Field(..., description="Start of data period")
    data_period_end: date = Field(..., description="End of data period")


class TradeVolumeAnalytics(BaseModel):
    """Schema for trade volume analytics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Volume metrics
    total_value: Decimal = Field(..., description="Total trade value")
    total_weight: Decimal = Field(..., description="Total weight")
    shipment_count: int = Field(..., description="Number of shipments")
    
    # Breakdowns
    by_country: List[Dict[str, Any]] = Field(..., description="Volume by country")
    by_hs_code: List[Dict[str, Any]] = Field(..., description="Volume by HS code")
    by_month: List[Dict[str, Any]] = Field(..., description="Volume by month")
    by_client: List[Dict[str, Any]] = Field(..., description="Volume by client")
    
    # Trends
    growth_rate: float = Field(..., description="Year-over-year growth rate")
    seasonal_patterns: List[Dict[str, Any]] = Field(..., description="Seasonal pattern analysis")
    
    # Metadata
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


class DutySavingsAnalytics(BaseModel):
    """Schema for duty savings analytics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Savings metrics
    total_savings: Decimal = Field(..., description="Total duty savings")
    potential_savings: Decimal = Field(..., description="Potential additional savings")
    savings_rate: float = Field(..., description="Savings rate percentage")
    
    # FTA utilization
    fta_utilization: List[Dict[str, Any]] = Field(..., description="FTA utilization rates")
    top_saving_products: List[Dict[str, Any]] = Field(..., description="Products with highest savings")
    savings_by_country: List[Dict[str, Any]] = Field(..., description="Savings by origin country")
    
    # Opportunities
    missed_opportunities: List[Dict[str, Any]] = Field(..., description="Missed savings opportunities")
    optimization_recommendations: List[str] = Field(..., description="Optimization recommendations")
    
    # Metadata
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


class ClassificationAccuracyAnalytics(BaseModel):
    """Schema for classification accuracy analytics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Accuracy metrics
    overall_accuracy: float = Field(..., description="Overall classification accuracy")
    confidence_distribution: List[Dict[str, Any]] = Field(..., description="Confidence score distribution")
    accuracy_by_category: List[Dict[str, Any]] = Field(..., description="Accuracy by product category")
    
    # Error analysis
    common_errors: List[Dict[str, Any]] = Field(..., description="Most common classification errors")
    low_confidence_items: List[Dict[str, Any]] = Field(..., description="Items with low confidence scores")
    manual_review_rate: float = Field(..., description="Rate of manual reviews required")
    
    # Improvements
    accuracy_trend: List[Dict[str, Any]] = Field(..., description="Accuracy improvement over time")
    training_recommendations: List[str] = Field(..., description="Model training recommendations")
    
    # Metadata
    total_classifications: int = Field(..., description="Total classifications analyzed")
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


# Search and filter schemas
class ReportSearchParams(SearchParams):
    """Extended search parameters for reports."""
    
    report_type: Optional[ReportType] = Field(None, description="Filter by report type")
    status: Optional[ReportStatus] = Field(None, description="Filter by status")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    
    date_from: Optional[date] = Field(None, description="Filter by creation date from")
    date_to: Optional[date] = Field(None, description="Filter by creation date to")
    
    is_public: Optional[bool] = Field(None, description="Filter by public status")
    is_stale: Optional[bool] = Field(None, description="Filter by stale status")
    
    tags: Optional[List[str]] = Field(None, description="Filter by tags")


# Export schemas
class ReportExportRequest(BaseModel):
    """Schema for report export requests."""
    
    model_config = ConfigDict(from_attributes=True)
    
    report_id: int = Field(..., description="Report ID to export")
    format: ReportFormat = Field(..., description="Export format")
    include_charts: bool = Field(True, description="Include charts in export")
    include_raw_data: bool = Field(False, description="Include raw data")
    
    # Customization options
    title_override: Optional[str] = Field(None, description="Override report title")
    watermark: Optional[str] = Field(None, description="Watermark text")
    custom_footer: Optional[str] = Field(None, description="Custom footer text")


class ReportExportResponse(BaseModel):
    """Schema for report export response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(..., description="Export success status")
    download_url: Optional[str] = Field(None, description="Download URL for exported file")
    filename: str = Field(..., description="Generated filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    expires_at: datetime = Field(..., description="Download link expiry")
    
    @computed_field
    @property
    def file_size_mb(self) -> float:
        """File size in megabytes."""
        return round(self.file_size_bytes / (1024 * 1024), 2)


# List response schemas
class ReportListResponse(BaseModel):
    """Response schema for report lists."""
    
    reports: List[ReportSummary] = Field(..., description="List of reports")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    filters: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    total_count: int = Field(..., description="Total number of reports")


class ReportTemplateListResponse(BaseModel):
    """Response schema for report template lists."""
    
    templates: List[ReportTemplateResponse] = Field(..., description="List of templates")
    categories: List[str] = Field(..., description="Available categories")
    total_count: int = Field(..., description="Total number of templates")


class ReportScheduleListResponse(BaseModel):
    """Response schema for report schedule lists."""
    
    schedules: List[ReportScheduleResponse] = Field(..., description="List of schedules")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    total_count: int = Field(..., description="Total number of schedules")


# Generation request schemas
class ReportGenerationRequest(BaseModel):
    """Schema for report generation requests."""
    
    model_config = ConfigDict(from_attributes=True)
    
    title: str = Field(..., max_length=255, description="Report title")
    report_type: ReportType = Field(..., description="Type of report to generate")
    
    # Date range
    date_from: Optional[date] = Field(None, description="Start date for data")
    date_to: Optional[date] = Field(None, description="End date for data")
    
    # Filters and parameters
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Data filters")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Generation parameters")
    
    # Options
    include_charts: bool = Field(True, description="Include charts")
    include_summary: bool = Field(True, description="Include executive summary")
    export_format: Optional[ReportFormat] = Field(None, description="Export format (if immediate export)")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Report tags")
    is_public: bool = Field(False, description="Make report public")


class ReportGenerationResponse(BaseModel):
    """Schema for report generation response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(..., description="Generation success status")
    report_id: int = Field(..., description="Generated report ID")
    status: ReportStatus = Field(..., description="Current generation status")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    message: str = Field(..., description="Status message")