import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Compliance API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Compliance API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Compliance API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('Compliance API Response Error:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      const errorData = data as { detail?: string; message?: string };
      throw new Error(errorData?.detail || errorData?.message || `HTTP ${status} Error`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// Type definitions matching backend schemas
export interface ComplianceAlert {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  category: string;
  timestamp: string;
  resolved: boolean;
  assigned_to?: string;
  due_date?: string;
  affected_codes: string[];
  action_required?: string;
  priority: string;
}

export interface ComplianceMetric {
  name: string;
  value: number;
  unit: string;
  trend: string;
  change?: number;
  target?: number;
  status: string;
  category?: string;
  change_percentage?: number;
  description?: string;
  last_updated?: string;
  historical_data?: Array<{ date: string; value: number }>;
}

export interface ComplianceOverviewSummary {
  status: string;
  trend: string;
  last_updated: string;
  key_issues: string[];
  recommendations: string[];
}

export interface ComplianceOverview {
  overall_score: number;
  risk_level: string;
  last_assessment: string;
  next_review: string;
  total_requirements: number;
  compliant_count: number;
  non_compliant_count: number;
  pending_review_count: number;
  recent_alerts: ComplianceAlert[];
  compliance_metrics: ComplianceMetric[];
  summary: ComplianceOverviewSummary;
}

export interface ComplianceHistoryRecord {
  id: string;
  event_type: string;
  title: string;
  description: string;
  timestamp: string;
  user: string;
  status: string;
  details: Record<string, any>;
  affected_entities: string[];
  severity: string;
}

export interface ComplianceFinding {
  category: string;
  severity: string;
  description: string;
  recommendation: string;
}

export interface ComplianceRecommendation {
  priority: string;
  category: string;
  description: string;
  estimated_impact?: string;
  implementation_effort?: string;
}

export interface ComplianceAssessmentSummary {
  total_areas_reviewed: number;
  compliant_areas: number;
  areas_needing_attention: number;
  overall_trend: string;
  key_strengths: string[];
  improvement_areas: string[];
}

export interface ComplianceAssessment {
  assessment_id: string;
  assessment_type: string;
  overall_score: number;
  risk_level: string;
  status: string;
  created_at: string;
  completed_at?: string;
  findings: ComplianceFinding[];
  recommendations: ComplianceRecommendation[];
  next_assessment_due?: string;
  summary: ComplianceAssessmentSummary;
}

export interface ComplianceRequirement {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  compliance_score: number;
  due_date?: string;
  assigned_to?: string;
  last_review?: string;
  next_review?: string;
  documents_required: string[];
  risk_level: string;
  regulatory_reference?: string;
  implementation_status: string;
  estimated_effort?: string;
}

export interface ComplianceAuditFinding {
  finding_id: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string;
  status: string;
  due_date?: string;
}

export interface ComplianceAuditRecommendation {
  priority: string;
  category: string;
  description: string;
  estimated_cost?: string;
  estimated_timeline?: string;
  expected_benefit?: string;
}

export interface ComplianceArea {
  area: string;
  score: number;
  status: string;
}

export interface ComplianceAuditSummary {
  strengths: string[];
  improvement_areas: string[];
  overall_assessment: string;
}

export interface ComplianceAudit {
  audit_id: string;
  audit_type: string;
  status: string;
  overall_score: number;
  risk_level: string;
  start_date: string;
  end_date?: string;
  auditor: string;
  scope: string[];
  findings: ComplianceAuditFinding[];
  recommendations: ComplianceAuditRecommendation[];
  compliance_areas: ComplianceArea[];
  next_audit_date?: string;
  certification_status?: string;
  summary: ComplianceAuditSummary;
}

export interface ComplianceAssessmentRequest {
  assessment_type: string;
  scope?: string[];
  priority?: string;
  description?: string;
  scheduled_date?: string;
}

export const complianceApi = {
  /**
   * Get compliance dashboard overview
   */
  async getOverview(): Promise<ComplianceOverview> {
    const response = await apiClient.get<ComplianceOverview>('/api/compliance/overview');
    return response.data;
  },

  /**
   * Get compliance alerts with filtering
   */
  async getAlerts(
    limit: number = 50,
    severity?: string,
    category?: string,
    resolved?: boolean
  ): Promise<ComplianceAlert[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (severity) params.append('severity', severity);
    if (category) params.append('category', category);
    if (resolved !== undefined) params.append('resolved', resolved.toString());

    const response = await apiClient.get<ComplianceAlert[]>(`/api/compliance/alerts?${params}`);
    return response.data;
  },

  /**
   * Get compliance metrics
   */
  async getMetrics(
    period: string = '30d',
    category?: string
  ): Promise<ComplianceMetric[]> {
    const params = new URLSearchParams();
    params.append('period', period);
    if (category) params.append('category', category);

    const response = await apiClient.get<ComplianceMetric[]>(`/api/compliance/metrics?${params}`);
    return response.data;
  },

  /**
   * Get compliance history
   */
  async getHistory(
    limit: number = 50,
    startDate?: string,
    endDate?: string,
    eventType?: string
  ): Promise<ComplianceHistoryRecord[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (eventType) params.append('event_type', eventType);

    const response = await apiClient.get<ComplianceHistoryRecord[]>(`/api/compliance/history?${params}`);
    return response.data;
  },

  /**
   * Create compliance assessment
   */
  async createAssessment(request: ComplianceAssessmentRequest): Promise<ComplianceAssessment> {
    const response = await apiClient.post<ComplianceAssessment>('/api/compliance/assessment', request);
    return response.data;
  },

  /**
   * Get compliance requirements
   */
  async getRequirements(
    category?: string,
    status?: string,
    priority?: string,
    limit: number = 50
  ): Promise<ComplianceRequirement[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (category) params.append('category', category);
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);

    const response = await apiClient.get<ComplianceRequirement[]>(`/api/compliance/requirements?${params}`);
    return response.data;
  },

  /**
   * Get compliance audit details
   */
  async getAudit(auditId: string): Promise<ComplianceAudit> {
    const response = await apiClient.get<ComplianceAudit>(`/api/compliance/audit/${auditId}`);
    return response.data;
  },

  /**
   * Health check for compliance service
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string; version: string }> {
    const response = await apiClient.get('/api/compliance/health');
    return response.data;
  },
};

// Export utility functions
export const formatComplianceScore = (score: number): string => {
  return `${score.toFixed(1)}%`;
};

export const getComplianceStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'compliant':
    case 'excellent':
    case 'good':
      return 'text-green-600';
    case 'under review':
    case 'pending':
    case 'improving':
      return 'text-yellow-600';
    case 'non-compliant':
    case 'critical':
    case 'high':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

export const getComplianceStatusBadgeColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'compliant':
    case 'excellent':
    case 'good':
      return 'bg-green-100 text-green-800';
    case 'under review':
    case 'pending':
    case 'improving':
      return 'bg-yellow-100 text-yellow-800';
    case 'non-compliant':
    case 'critical':
    case 'high':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getSeverityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'low':
    case 'info':
      return 'text-blue-600';
    case 'medium':
      return 'text-yellow-600';
    case 'high':
      return 'text-orange-600';
    case 'critical':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

export const getSeverityBadgeColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'low':
    case 'info':
      return 'bg-blue-100 text-blue-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'high':
      return 'bg-orange-100 text-orange-800';
    case 'critical':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-AU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDateShort = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-AU', {
    month: 'short',
    day: 'numeric'
  });
};

// Error types for better error handling
export class ComplianceApiError extends Error {
  public statusCode?: number;
  public errorCode?: string;

  constructor(
    message: string,
    statusCode?: number,
    errorCode?: string
  ) {
    super(message);
    this.name = 'ComplianceApiError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
  }
}

export class ValidationError extends ComplianceApiError {
  public field?: string;

  constructor(message: string, field?: string) {
    super(message, 400, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
    this.field = field;
  }
}

export class NetworkError extends ComplianceApiError {
  constructor(message: string = 'Network connection failed') {
    super(message, 0, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

export default complianceApi;