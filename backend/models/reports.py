"""
Reports and Analytics models for the Customs Broker Portal.

This module contains models for report generation, scheduling, templates,
and analytics data storage for the customs broker reporting system.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, CheckConstraint, Index,
    ForeignKey, func, BigInteger, JSON, Date, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


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


class Report(Base):
    """
    Report model for storing report metadata and generation information.
    
    This model stores comprehensive report information including generation status,
    parameters, data, and metadata for business intelligence reports.
    """
    
    __tablename__ = "reports"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Report metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_type: Mapped[ReportType] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[ReportStatus] = mapped_column(String(50), nullable=False, index=True, default=ReportStatus.PENDING)
    
    # Date range for report data
    date_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    date_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    
    # Report configuration
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Generated data and files
    report_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Generation info
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    data_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Auto-refresh configuration
    auto_refresh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    refresh_interval_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_refreshed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    next_refresh: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # User tracking
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_modified_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Tags and metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    report_schedules: Mapped[List["ReportSchedule"]] = relationship(
        "ReportSchedule",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid report types
        CheckConstraint(
            f"report_type IN {tuple(rt.value for rt in ReportType)}",
            name="ck_reports_type"
        ),
        
        # Ensure valid status
        CheckConstraint(
            f"status IN {tuple(status.value for status in ReportStatus)}",
            name="ck_reports_status"
        ),
        
        # Date range validation
        CheckConstraint(
            "date_from IS NULL OR date_to IS NULL OR date_from <= date_to",
            name="ck_reports_date_range"
        ),
        
        # File size constraint
        CheckConstraint(
            "file_size_bytes IS NULL OR file_size_bytes > 0",
            name="ck_reports_file_size"
        ),
        
        # Generation time constraint
        CheckConstraint(
            "generation_time_ms IS NULL OR generation_time_ms >= 0",
            name="ck_reports_generation_time"
        ),
        
        # Data points constraint
        CheckConstraint(
            "data_points IS NULL OR data_points >= 0",
            name="ck_reports_data_points"
        ),
        
        # Refresh interval constraint
        CheckConstraint(
            "refresh_interval_hours IS NULL OR (refresh_interval_hours >= 1 AND refresh_interval_hours <= 168)",
            name="ck_reports_refresh_interval"
        ),
        
        # Composite indexes for performance
        Index("ix_reports_type_status", "report_type", "status"),
        Index("ix_reports_date_range", "date_from", "date_to"),
        Index("ix_reports_created_status", "created_at", "status"),
        Index("ix_reports_public_active", "is_public", "is_active"),
        Index("ix_reports_auto_refresh", "auto_refresh", "next_refresh"),
    )
    
    def __repr__(self) -> str:
        """String representation of Report."""
        return (
            f"<Report(id={self.id}, title='{self.title}', "
            f"type='{self.report_type}', status='{self.status}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.title} ({self.report_type})"
    
    @property
    def file_size_mb(self) -> Optional[float]:
        """Get file size in megabytes."""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return None
    
    @property
    def is_stale(self) -> bool:
        """Check if report data is considered stale (older than 24 hours)."""
        if not self.generated_at:
            return True
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(hours=24)
        return self.generated_at < threshold
    
    @property
    def needs_refresh(self) -> bool:
        """Check if report needs to be refreshed."""
        if not self.auto_refresh or not self.next_refresh:
            return False
        return datetime.utcnow() >= self.next_refresh
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the report."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the report."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if report has a specific tag."""
        return self.tags is not None and tag in self.tags


class ReportTemplate(Base):
    """
    Report template model for storing reusable report configurations.
    
    Templates allow users to create standardized reports with predefined
    parameters, filters, and formatting options.
    """
    
    __tablename__ = "report_templates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Template metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_type: Mapped[ReportType] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Template configuration
    default_filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    default_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    required_fields: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # User tracking
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Tags and metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    is_system_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    report_schedules: Mapped[List["ReportSchedule"]] = relationship(
        "ReportSchedule",
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid report types
        CheckConstraint(
            f"report_type IN {tuple(rt.value for rt in ReportType)}",
            name="ck_report_templates_type"
        ),
        
        # Usage count constraint
        CheckConstraint(
            "usage_count >= 0",
            name="ck_report_templates_usage_count"
        ),
        
        # Unique constraint for name within category
        Index("ix_report_templates_name_category", "name", "category", unique=True),
        
        # Composite indexes
        Index("ix_report_templates_type_category", "report_type", "category"),
        Index("ix_report_templates_system_active", "is_system_template", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of ReportTemplate."""
        return (
            f"<ReportTemplate(id={self.id}, name='{self.name}', "
            f"type='{self.report_type}', category='{self.category}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.category})"
    
    def increment_usage(self) -> None:
        """Increment usage count."""
        self.usage_count += 1


class ReportSchedule(Base):
    """
    Report schedule model for automated report generation.
    
    Manages scheduled report generation with configurable frequency,
    recipients, and delivery options.
    """
    
    __tablename__ = "report_schedules"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Schedule metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    frequency: Mapped[ScheduleFrequency] = mapped_column(String(20), nullable=False, index=True)
    
    # Foreign keys
    report_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("reports.id", ondelete="SET NULL"),
        nullable=True
    )
    report_template_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("report_templates.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Schedule timing
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    time_of_day: Mapped[str] = mapped_column(String(5), nullable=False, default="09:00")  # HH:MM format
    
    # Execution tracking
    last_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    next_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    run_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Recipients and delivery
    email_recipients: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    export_format: Mapped[ReportFormat] = mapped_column(String(20), nullable=False, default=ReportFormat.PDF)
    include_charts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # User tracking
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        back_populates="report_schedules",
        lazy="select"
    )
    
    template: Mapped["ReportTemplate"] = relationship(
        "ReportTemplate",
        back_populates="report_schedules",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid frequency
        CheckConstraint(
            f"frequency IN {tuple(freq.value for freq in ScheduleFrequency)}",
            name="ck_report_schedules_frequency"
        ),
        
        # Ensure valid export format
        CheckConstraint(
            f"export_format IN {tuple(fmt.value for fmt in ReportFormat)}",
            name="ck_report_schedules_export_format"
        ),
        
        # Date range validation
        CheckConstraint(
            "end_date IS NULL OR start_date <= end_date",
            name="ck_report_schedules_date_range"
        ),
        
        # Time format validation (SQLite compatible)
        CheckConstraint(
            "time_of_day GLOB '[0-2][0-9]:[0-5][0-9]' AND length(time_of_day) = 5",
            name="ck_report_schedules_time_format"
        ),
        
        # Count constraints
        CheckConstraint(
            "run_count >= 0",
            name="ck_report_schedules_run_count"
        ),
        
        CheckConstraint(
            "success_count >= 0 AND success_count <= run_count",
            name="ck_report_schedules_success_count"
        ),
        
        # Composite indexes
        Index("ix_report_schedules_frequency_active", "frequency", "is_active"),
        Index("ix_report_schedules_next_run_active", "next_run", "is_active"),
        Index("ix_report_schedules_template_active", "report_template_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of ReportSchedule."""
        return (
            f"<ReportSchedule(id={self.id}, name='{self.name}', "
            f"frequency='{self.frequency}', active={self.is_active})>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.frequency})"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.run_count == 0:
            return 0.0
        return round((self.success_count / self.run_count) * 100, 2)
    
    def record_execution(self, success: bool = True) -> None:
        """Record execution of the schedule."""
        self.run_count += 1
        if success:
            self.success_count += 1
        self.last_run = datetime.utcnow()


class AnalyticsMetric(Base):
    """
    Analytics metric model for storing calculated business intelligence metrics.
    
    Stores time-series analytics data for dashboards and reporting.
    """
    
    __tablename__ = "analytics_metrics"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Metric identification
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_type: Mapped[MetricType] = mapped_column(String(20), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Metric value
    value: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=4), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Comparison data
    previous_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=20, scale=4), nullable=True)
    change_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=8, scale=4), nullable=True)
    trend: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # up/down/stable
    
    # Time period
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    calculation_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid metric types
        CheckConstraint(
            f"metric_type IN {tuple(mt.value for mt in MetricType)}",
            name="ck_analytics_metrics_type"
        ),
        
        # Period validation
        CheckConstraint(
            "period_start <= period_end",
            name="ck_analytics_metrics_period"
        ),
        
        # Data points constraint
        CheckConstraint(
            "data_points IS NULL OR data_points >= 0",
            name="ck_analytics_metrics_data_points"
        ),
        
        # Trend validation
        CheckConstraint(
            "trend IS NULL OR trend IN ('up', 'down', 'stable')",
            name="ck_analytics_metrics_trend"
        ),
        
        # Unique constraint for metric per period
        Index("ix_analytics_metrics_unique", "name", "category", "period_start", "period_end", unique=True),
        
        # Composite indexes
        Index("ix_analytics_metrics_name_period", "name", "period_start", "period_end"),
        Index("ix_analytics_metrics_category_calculated", "category", "calculated_at"),
        Index("ix_analytics_metrics_type_period", "metric_type", "period_start"),
    )
    
    def __repr__(self) -> str:
        """String representation of AnalyticsMetric."""
        return (
            f"<AnalyticsMetric(id={self.id}, name='{self.name}', "
            f"value={self.value}, period='{self.period_start}' to '{self.period_end}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        unit_str = f" {self.unit}" if self.unit else ""
        return f"{self.name}: {self.value}{unit_str}"
    
    @property
    def formatted_value(self) -> str:
        """Get formatted value with unit."""
        unit_str = f" {self.unit}" if self.unit else ""
        return f"{self.value}{unit_str}"
    
    @property
    def period_days(self) -> int:
        """Get number of days in the period."""
        return (self.period_end - self.period_start).days + 1