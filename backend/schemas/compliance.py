"""
Compliance Management Pydantic schemas for the Customs Broker Portal.

This module defines the request and response models for compliance-related API endpoints.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ComplianceAlert(BaseModel):
    """Base compliance alert model."""
    id: str
    type: str = Field(..., description="Alert type (warning, error, info, success)")
    title: str
    message: str
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    category: str = Field(..., description="Alert category")
    timestamp: str
    resolved: bool = False
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    affected_codes: List[str] = []
    action_required: Optional[str] = None
    priority: str = Field(default="normal", description="Priority level (low, normal, high, urgent)")


class ComplianceAlertResponse(ComplianceAlert):
    """Response model for compliance alerts."""
    pass


class ComplianceMetric(BaseModel):
    """Base compliance metric model."""
    name: str
    value: float
    unit: str
    trend: str = Field(..., description="Trend direction (up, down, stable)")
    change: Optional[float] = None
    target: Optional[float] = None
    status: str = Field(..., description="Status (good, warning, critical, excellent, improving)")


class ComplianceMetricResponse(ComplianceMetric):
    """Extended compliance metric with additional details."""
    category: Optional[str] = None
    change_percentage: Optional[float] = None
    description: Optional[str] = None
    last_updated: Optional[str] = None
    historical_data: List[Dict[str, Any]] = []


class ComplianceOverviewSummary(BaseModel):
    """Compliance overview summary information."""
    status: str
    trend: str
    last_updated: str
    key_issues: List[str] = []
    recommendations: List[str] = []


class ComplianceOverviewResponse(BaseModel):
    """Response model for compliance overview."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall compliance score (0-100)")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High, Critical)")
    last_assessment: str = Field(..., description="ISO timestamp of last assessment")
    next_review: str = Field(..., description="ISO timestamp of next scheduled review")
    total_requirements: int = Field(..., ge=0, description="Total number of compliance requirements")
    compliant_count: int = Field(..., ge=0, description="Number of compliant items")
    non_compliant_count: int = Field(..., ge=0, description="Number of non-compliant items")
    pending_review_count: int = Field(..., ge=0, description="Number of items pending review")
    recent_alerts: List[ComplianceAlert] = []
    compliance_metrics: List[ComplianceMetric] = []
    summary: ComplianceOverviewSummary


class ComplianceHistoryDetails(BaseModel):
    """Details for compliance history events."""
    pass  # Flexible dict structure


class ComplianceHistoryResponse(BaseModel):
    """Response model for compliance history records."""
    id: str
    event_type: str = Field(..., description="Type of event (assessment, alert, audit, training, violation)")
    title: str
    description: str
    timestamp: str
    user: str
    status: str
    details: Dict[str, Any] = {}
    affected_entities: List[str] = []
    severity: str = Field(..., description="Event severity (low, medium, high, info)")


class ComplianceAssessmentRequest(BaseModel):
    """Request model for creating compliance assessments."""
    assessment_type: str = Field(..., description="Type of assessment (risk, audit, comprehensive)")
    scope: Optional[List[str]] = Field(None, description="Areas to include in assessment")
    priority: str = Field(default="normal", description="Assessment priority (low, normal, high)")
    description: Optional[str] = None
    scheduled_date: Optional[str] = None
    
    @validator('assessment_type')
    def validate_assessment_type(cls, v):
        allowed_types = ['risk', 'audit', 'comprehensive']
        if v not in allowed_types:
            raise ValueError(f'Assessment type must be one of: {allowed_types}')
        return v


class ComplianceFinding(BaseModel):
    """Compliance assessment finding."""
    category: str
    severity: str = Field(..., description="Finding severity (low, medium, high, critical)")
    description: str
    recommendation: str


class ComplianceRecommendation(BaseModel):
    """Compliance improvement recommendation."""
    priority: str = Field(..., description="Recommendation priority (low, medium, high)")
    category: str
    description: str
    estimated_impact: Optional[str] = None
    implementation_effort: Optional[str] = None


class ComplianceAssessmentSummary(BaseModel):
    """Summary information for compliance assessment."""
    total_areas_reviewed: int
    compliant_areas: int
    areas_needing_attention: int
    overall_trend: str
    key_strengths: List[str] = []
    improvement_areas: List[str] = []


class ComplianceAssessmentResponse(BaseModel):
    """Response model for compliance assessments."""
    assessment_id: str
    assessment_type: str
    overall_score: float = Field(..., ge=0, le=100)
    risk_level: str
    status: str = Field(..., description="Assessment status (pending, in_progress, completed, failed)")
    created_at: str
    completed_at: Optional[str] = None
    findings: List[ComplianceFinding] = []
    recommendations: List[ComplianceRecommendation] = []
    next_assessment_due: Optional[str] = None
    summary: ComplianceAssessmentSummary


class ComplianceRequirementResponse(BaseModel):
    """Response model for compliance requirements."""
    id: str
    title: str
    description: str
    category: str = Field(..., description="Requirement category (Import, Export, Trade, Documentation, etc.)")
    priority: str = Field(..., description="Priority level (Low, Medium, High, Critical)")
    status: str = Field(..., description="Compliance status (Compliant, Non-Compliant, Under Review, Pending)")
    compliance_score: int = Field(..., ge=0, le=100, description="Compliance score (0-100)")
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None
    last_review: Optional[str] = None
    next_review: Optional[str] = None
    documents_required: List[str] = []
    risk_level: str = Field(..., description="Risk level (Low, Medium, High)")
    regulatory_reference: Optional[str] = None
    implementation_status: str = Field(..., description="Implementation status (Not Started, In Progress, Implemented, Monitoring)")
    estimated_effort: Optional[str] = None


class ComplianceAuditFinding(BaseModel):
    """Audit finding details."""
    finding_id: str
    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    status: str = Field(..., description="Finding status (Open, In Progress, Resolved)")
    due_date: Optional[str] = None


class ComplianceAuditRecommendation(BaseModel):
    """Audit recommendation details."""
    priority: str
    category: str
    description: str
    estimated_cost: Optional[str] = None
    estimated_timeline: Optional[str] = None
    expected_benefit: Optional[str] = None


class ComplianceArea(BaseModel):
    """Compliance area assessment."""
    area: str
    score: int = Field(..., ge=0, le=100)
    status: str = Field(..., description="Area status (Poor, Fair, Good, Excellent)")


class ComplianceAuditSummary(BaseModel):
    """Audit summary information."""
    strengths: List[str] = []
    improvement_areas: List[str] = []
    overall_assessment: str


class ComplianceAuditResponse(BaseModel):
    """Response model for compliance audits."""
    audit_id: str
    audit_type: str = Field(..., description="Type of audit (Internal, External, Comprehensive)")
    status: str = Field(..., description="Audit status (Scheduled, In Progress, Completed, Cancelled)")
    overall_score: float = Field(..., ge=0, le=100)
    risk_level: str
    start_date: str
    end_date: Optional[str] = None
    auditor: str
    scope: List[str] = []
    findings: List[ComplianceAuditFinding] = []
    recommendations: List[ComplianceAuditRecommendation] = []
    compliance_areas: List[ComplianceArea] = []
    next_audit_date: Optional[str] = None
    certification_status: Optional[str] = None
    summary: ComplianceAuditSummary


# Request models for updates
class UpdateComplianceAlertRequest(BaseModel):
    """Request model for updating compliance alerts."""
    resolved: Optional[bool] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class UpdateComplianceRequirementRequest(BaseModel):
    """Request model for updating compliance requirements."""
    status: Optional[str] = None
    compliance_score: Optional[int] = Field(None, ge=0, le=100)
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    next_review: Optional[str] = None


# Validation models
class ComplianceValidationRequest(BaseModel):
    """Request model for compliance validation."""
    entity_type: str = Field(..., description="Type of entity to validate (shipment, document, process)")
    entity_id: str
    validation_rules: List[str] = []
    strict_mode: bool = Field(default=False, description="Enable strict validation mode")


class ComplianceValidationResult(BaseModel):
    """Result of compliance validation."""
    entity_id: str
    entity_type: str
    is_compliant: bool
    compliance_score: float = Field(..., ge=0, le=100)
    violations: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    validation_timestamp: str


class ComplianceValidationResponse(BaseModel):
    """Response model for compliance validation."""
    validation_id: str
    results: List[ComplianceValidationResult]
    overall_compliance: bool
    summary: Dict[str, Any]


# Bulk operation models
class BulkComplianceCheckRequest(BaseModel):
    """Request model for bulk compliance checks."""
    entity_ids: List[str] = Field(..., min_items=1, max_items=100)
    entity_type: str
    check_types: List[str] = []
    include_recommendations: bool = Field(default=True)


class BulkComplianceCheckResponse(BaseModel):
    """Response model for bulk compliance checks."""
    total_checked: int
    compliant_count: int
    non_compliant_count: int
    results: List[ComplianceValidationResult]
    summary_statistics: Dict[str, Any]


# Export models
class ComplianceReportRequest(BaseModel):
    """Request model for generating compliance reports."""
    report_type: str = Field(..., description="Type of report (overview, detailed, audit, metrics)")
    period: Optional[str] = Field(None, description="Time period (7d, 30d, 90d, 1y)")
    include_sections: List[str] = []
    format: str = Field(default="json", description="Report format (json, pdf, csv)")
    filters: Dict[str, Any] = {}


class ComplianceReportResponse(BaseModel):
    """Response model for compliance reports."""
    report_id: str
    report_type: str
    generated_at: str
    period: Optional[str] = None
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = {}