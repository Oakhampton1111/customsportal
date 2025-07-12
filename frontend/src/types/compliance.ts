export interface ComplianceRequirement {
  id: number;
  requirement_code: string;
  title: string;
  description: string;
  category: ComplianceCategory;
  severity: ComplianceSeverity;
  applicable_to: string[];
  regulatory_body: string;
  effective_date: string;
  expiry_date?: string;
  documentation_required: string[];
  compliance_criteria: string[];
  penalties: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const ComplianceCategory = {
  CUSTOMS: "customs",
  TRADE: "trade",
  SECURITY: "security",
  ENVIRONMENTAL: "environmental",
  FINANCIAL: "financial",
  OPERATIONAL: "operational",
  DATA_PROTECTION: "data_protection"
} as const;

export type ComplianceCategory = typeof ComplianceCategory[keyof typeof ComplianceCategory];

export const ComplianceSeverity = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical"
} as const;

export type ComplianceSeverity = typeof ComplianceSeverity[keyof typeof ComplianceSeverity];

export interface ComplianceAudit {
  id: number;
  audit_number: string;
  audit_type: AuditType;
  status: AuditStatus;
  title: string;
  description: string;
  scope: string[];
  auditor_name: string;
  auditor_organization: string;
  scheduled_date: string;
  start_date?: string;
  completion_date?: string;
  findings: ComplianceFinding[];
  recommendations: string[];
  overall_score?: number;
  compliance_level: ComplianceLevel;
  follow_up_required: boolean;
  follow_up_date?: string;
  customer_id: string;
  created_at: string;
  updated_at: string;
}

export const AuditType = {
  INTERNAL: "internal",
  EXTERNAL: "external",
  REGULATORY: "regulatory",
  SELF_ASSESSMENT: "self_assessment"
} as const;

export type AuditType = typeof AuditType[keyof typeof AuditType];

export const AuditStatus = {
  SCHEDULED: "scheduled",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
  POSTPONED: "postponed"
} as const;

export type AuditStatus = typeof AuditStatus[keyof typeof AuditStatus];

export const ComplianceLevel = {
  FULLY_COMPLIANT: "fully_compliant",
  MOSTLY_COMPLIANT: "mostly_compliant",
  PARTIALLY_COMPLIANT: "partially_compliant",
  NON_COMPLIANT: "non_compliant"
} as const;

export type ComplianceLevel = typeof ComplianceLevel[keyof typeof ComplianceLevel];

export interface ComplianceFinding {
  id: number;
  finding_type: FindingType;
  severity: ComplianceSeverity;
  requirement_id: number;
  title: string;
  description: string;
  evidence: string[];
  impact_assessment: string;
  corrective_action_required: string;
  corrective_action_deadline?: string;
  status: FindingStatus;
  assigned_to?: string;
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
}

export const FindingType = {
  NON_COMPLIANCE: "non_compliance",
  OBSERVATION: "observation",
  BEST_PRACTICE: "best_practice",
  IMPROVEMENT_OPPORTUNITY: "improvement_opportunity"
} as const;

export type FindingType = typeof FindingType[keyof typeof FindingType];

export const FindingStatus = {
  OPEN: "open",
  IN_PROGRESS: "in_progress",
  RESOLVED: "resolved",
  CLOSED: "closed",
  DEFERRED: "deferred"
} as const;

export type FindingStatus = typeof FindingStatus[keyof typeof FindingStatus];

export interface ComplianceReport {
  id: number;
  report_number: string;
  report_type: ReportType;
  title: string;
  description: string;
  reporting_period_start: string;
  reporting_period_end: string;
  generated_date: string;
  generated_by: string;
  status: ReportStatus;
  executive_summary: string;
  key_metrics: Record<string, any>;
  compliance_score: number;
  violations_summary: ViolationSummary[];
  recommendations: string[];
  action_items: ActionItem[];
  attachments: string[];
  customer_id: string;
  is_confidential: boolean;
  distribution_list: string[];
  created_at: string;
}

export const ReportType = {
  MONTHLY: "monthly",
  QUARTERLY: "quarterly",
  ANNUAL: "annual",
  AD_HOC: "ad_hoc",
  INCIDENT: "incident",
  REGULATORY_FILING: "regulatory_filing"
} as const;

export type ReportType = typeof ReportType[keyof typeof ReportType];

export const ReportStatus = {
  DRAFT: "draft",
  UNDER_REVIEW: "under_review",
  APPROVED: "approved",
  PUBLISHED: "published",
  ARCHIVED: "archived"
} as const;

export type ReportStatus = typeof ReportStatus[keyof typeof ReportStatus];

export interface ViolationSummary {
  category: string;
  count: number;
  severity_breakdown: Record<string, number>;
  trend: string;
}

export interface ActionItem {
  id: number;
  title: string;
  description: string;
  priority: string;
  assigned_to: string;
  due_date: string;
  status: string;
  completion_date?: string;
}

export interface ComplianceMetrics {
  overall_score: number;
  category_scores: Record<string, number>;
  trend_data: Array<{
    date: string;
    score: number;
    category_scores: Record<string, number>;
  }>;
  violation_counts: Record<string, number>;
  audit_frequency: Record<string, number>;
  improvement_rate: number;
  risk_level: string;
}

export interface ComplianceStatistics {
  overall_score: number;
  total_requirements: number;
  compliant_requirements: number;
  pending_audits: number;
  open_violations: number;
  recent_improvements: number;
  risk_level: string;
  last_audit_date?: string;
  next_audit_date?: string;
}

export interface ComplianceViolation {
  id: number;
  violation_number: string;
  requirement_id: number;
  violation_type: ViolationType;
  severity: ComplianceSeverity;
  title: string;
  description: string;
  detected_date: string;
  reported_date: string;
  status: ViolationStatus;
  root_cause_analysis?: string;
  corrective_actions: CorrectiveAction[];
  preventive_actions: string[];
  financial_impact?: string;
  regulatory_impact?: string;
  customer_id: string;
  assigned_to?: string;
  resolution_deadline?: string;
  resolved_date?: string;
  created_at: string;
  updated_at: string;
}

export const ViolationType = {
  PROCEDURAL: "procedural",
  DOCUMENTATION: "documentation",
  TRAINING: "training",
  SYSTEM: "system",
  REGULATORY: "regulatory",
  CONTRACTUAL: "contractual"
} as const;

export type ViolationType = typeof ViolationType[keyof typeof ViolationType];

export const ViolationStatus = {
  IDENTIFIED: "identified",
  INVESTIGATING: "investigating",
  CORRECTING: "correcting",
  MONITORING: "monitoring",
  CLOSED: "closed",
  ESCALATED: "escalated"
} as const;

export type ViolationStatus = typeof ViolationStatus[keyof typeof ViolationStatus];

export interface CorrectiveAction {
  id: number;
  action_type: string;
  description: string;
  assigned_to: string;
  due_date: string;
  status: string;
  completion_date?: string;
  effectiveness_review?: string;
}

export interface ComplianceTraining {
  id: number;
  training_code: string;
  title: string;
  description: string;
  category: string;
  required_for: string[];
  duration_hours: number;
  validity_period_months: number;
  training_materials: string[];
  assessment_required: boolean;
  passing_score?: number;
  is_mandatory: boolean;
  created_at: string;
}

export interface TrainingRecord {
  id: number;
  training_id: number;
  employee_id: string;
  employee_name: string;
  completion_date: string;
  score?: number;
  status: TrainingStatus;
  certificate_issued: boolean;
  certificate_number?: string;
  expiry_date?: string;
  renewal_required: boolean;
  notes?: string;
}

export const TrainingStatus = {
  NOT_STARTED: "not_started",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  FAILED: "failed",
  EXPIRED: "expired"
} as const;

export type TrainingStatus = typeof TrainingStatus[keyof typeof TrainingStatus];