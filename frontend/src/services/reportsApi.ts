import { apiClient } from './api';

// Types matching the backend schemas
export interface AnalyticsMetric {
  name: string;
  value: number;
  unit: string;
  change_percentage?: number;
  trend?: 'up' | 'down' | 'stable';
  period?: string;
}

export interface DashboardAnalytics {
  total_shipments: AnalyticsMetric;
  compliance_rate: AnalyticsMetric;
  avg_processing_time: AnalyticsMetric;
  cost_savings: AnalyticsMetric;
  active_alerts: AnalyticsMetric;
  pending_reviews: AnalyticsMetric;
  recent_activity: Array<{
    type: string;
    description: string;
    timestamp: string;
    status: string;
  }>;
  top_countries: Array<{
    country: string;
    shipment_count: number;
    percentage: number;
  }>;
  period: string;
}

export interface TradeVolumeAnalytics {
  shipment_count: number;
  total_value: number;
  growth_rate: number;
  avg_shipment_value: number;
  top_products: Array<{
    product: string;
    count: number;
    value: number;
    percentage: number;
  }>;
  monthly_trends: Array<{
    month: string;
    shipments: number;
    value: number;
    growth_rate: number;
  }>;
  country_breakdown: Array<{
    country: string;
    shipments: number;
    value: number;
    percentage: number;
  }>;
  period: string;
}

export interface DutySavingsAnalytics {
  total_savings: number;
  savings_rate: number;
  fta_utilization: number;
  top_saving_products: Array<{
    product: string;
    savings: number;
    percentage: number;
  }>;
  savings_by_country: Array<{
    country: string;
    savings: number;
    percentage: number;
  }>;
  missed_opportunities: Array<{
    product: string;
    potential_savings: number;
    reason: string;
  }>;
  optimization_recommendations: Array<{
    recommendation: string;
    potential_savings: number;
    implementation_effort: string;
  }>;
  period: string;
}

export interface ClassificationAccuracyAnalytics {
  overall_accuracy: number;
  total_classifications: number;
  manual_review_rate: number;
  accuracy_by_category: Array<{
    category: string;
    accuracy: number;
    count: number;
  }>;
  common_errors: Array<{
    error_type: string;
    frequency: number;
    impact: string;
  }>;
  low_confidence_items: Array<{
    item: string;
    confidence_score: number;
    suggested_classification: string;
  }>;
  training_recommendations: Array<{
    area: string;
    priority: string;
    description: string;
  }>;
  period: string;
}

export interface Report {
  id: string;
  name: string;
  type: 'dashboard' | 'trade_volume' | 'duty_savings' | 'classification_accuracy' | 'custom';
  status: 'generated' | 'processing' | 'failed' | 'scheduled';
  format: 'json' | 'csv' | 'pdf';
  created_at: string;
  updated_at: string;
  generated_at?: string;
  file_path?: string;
  file_size?: number;
  metadata?: Record<string, any>;
  config?: Record<string, any>;
  template_id?: string;
  schedule_id?: string;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description?: string;
  report_type: string;
  config: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface ReportSchedule {
  id: string;
  name: string;
  description?: string;
  template_id: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  is_active: boolean;
  next_run: string;
  last_run?: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateReportRequest {
  name: string;
  type: 'dashboard' | 'trade_volume' | 'duty_savings' | 'classification_accuracy' | 'custom';
  format?: 'json' | 'csv' | 'pdf';
  config?: Record<string, any>;
  template_id?: string;
}

export interface CreateTemplateRequest {
  name: string;
  description?: string;
  report_type: string;
  config: Record<string, any>;
}

export interface CreateScheduleRequest {
  name: string;
  description?: string;
  template_id: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  config?: Record<string, any>;
}

// API Service Class
export class ReportsApiService {
  // Analytics endpoints
  async getDashboardAnalytics(period?: string): Promise<DashboardAnalytics> {
    const params = period ? { period } : {};
    const response = await apiClient.get('/api/reports/analytics/dashboard', { params });
    return response.data;
  }

  async getTradeVolumeAnalytics(period?: string): Promise<TradeVolumeAnalytics> {
    const params = period ? { period } : {};
    const response = await apiClient.get('/api/reports/analytics/trade-volume', { params });
    return response.data;
  }

  async getDutySavingsAnalytics(period?: string): Promise<DutySavingsAnalytics> {
    const params = period ? { period } : {};
    const response = await apiClient.get('/api/reports/analytics/duty-savings', { params });
    return response.data;
  }

  async getClassificationAccuracyAnalytics(period?: string): Promise<ClassificationAccuracyAnalytics> {
    const params = period ? { period } : {};
    const response = await apiClient.get('/api/reports/analytics/classification-accuracy', { params });
    return response.data;
  }

  // Report management endpoints
  async getReports(
    skip?: number,
    limit?: number,
    type?: string,
    status?: string
  ): Promise<{ reports: Report[]; total: number }> {
    const params: Record<string, any> = {};
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;
    if (type) params.type = type;
    if (status) params.status = status;

    const response = await apiClient.get('/api/reports/', { params });
    return response.data;
  }

  async getReport(reportId: string): Promise<Report> {
    const response = await apiClient.get(`/api/reports/${reportId}`);
    return response.data;
  }

  async createReport(reportData: CreateReportRequest): Promise<Report> {
    const response = await apiClient.post('/api/reports/', reportData);
    return response.data;
  }

  async updateReport(reportId: string, reportData: Partial<CreateReportRequest>): Promise<Report> {
    const response = await apiClient.put(`/api/reports/${reportId}`, reportData);
    return response.data;
  }

  async deleteReport(reportId: string): Promise<void> {
    await apiClient.delete(`/api/reports/${reportId}`);
  }

  async downloadReport(reportId: string): Promise<Blob> {
    const response = await apiClient.get(`/api/reports/${reportId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  }

  async exportReport(reportId: string, format: 'csv' | 'pdf'): Promise<Blob> {
    const response = await apiClient.post(`/api/reports/${reportId}/export`,
      { format },
      { responseType: 'blob' }
    );
    return response.data;
  }

  // Template management endpoints
  async getTemplates(skip?: number, limit?: number): Promise<{ templates: ReportTemplate[]; total: number }> {
    const params: Record<string, any> = {};
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get('/api/reports/templates/', { params });
    return response.data;
  }

  async getTemplate(templateId: string): Promise<ReportTemplate> {
    const response = await apiClient.get(`/api/reports/templates/${templateId}`);
    return response.data;
  }

  async createTemplate(templateData: CreateTemplateRequest): Promise<ReportTemplate> {
    const response = await apiClient.post('/api/reports/templates/', templateData);
    return response.data;
  }

  async updateTemplate(templateId: string, templateData: Partial<CreateTemplateRequest>): Promise<ReportTemplate> {
    const response = await apiClient.put(`/api/reports/templates/${templateId}`, templateData);
    return response.data;
  }

  async deleteTemplate(templateId: string): Promise<void> {
    await apiClient.delete(`/api/reports/templates/${templateId}`);
  }

  // Schedule management endpoints
  async getSchedules(skip?: number, limit?: number): Promise<{ schedules: ReportSchedule[]; total: number }> {
    const params: Record<string, any> = {};
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;

    const response = await apiClient.get('/api/reports/schedules/', { params });
    return response.data;
  }

  async getSchedule(scheduleId: string): Promise<ReportSchedule> {
    const response = await apiClient.get(`/api/reports/schedules/${scheduleId}`);
    return response.data;
  }

  async createSchedule(scheduleData: CreateScheduleRequest): Promise<ReportSchedule> {
    const response = await apiClient.post('/api/reports/schedules/', scheduleData);
    return response.data;
  }

  async updateSchedule(scheduleId: string, scheduleData: Partial<CreateScheduleRequest>): Promise<ReportSchedule> {
    const response = await apiClient.put(`/api/reports/schedules/${scheduleId}`, scheduleData);
    return response.data;
  }

  async deleteSchedule(scheduleId: string): Promise<void> {
    await apiClient.delete(`/api/reports/schedules/${scheduleId}`);
  }

  async toggleSchedule(scheduleId: string, isActive: boolean): Promise<ReportSchedule> {
    const response = await apiClient.patch(`/api/reports/schedules/${scheduleId}/toggle`, { is_active: isActive });
    return response.data;
  }

  // Utility methods for frontend integration
  async generateQuickReport(type: 'dashboard' | 'trade_volume' | 'duty_savings' | 'classification_accuracy'): Promise<Report> {
    return this.createReport({
      name: `Quick ${type.replace('_', ' ')} Report - ${new Date().toLocaleDateString()}`,
      type,
      format: 'json'
    });
  }

  async downloadReportAsFile(reportId: string, filename?: string): Promise<void> {
    try {
      const blob = await this.downloadReport(reportId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `report-${reportId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading report:', error);
      throw error;
    }
  }

  async exportReportAsFile(reportId: string, format: 'csv' | 'pdf', filename?: string): Promise<void> {
    try {
      const blob = await this.exportReport(reportId, format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `report-${reportId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting report:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const reportsApi = new ReportsApiService();

// Export individual functions for convenience
export const {
  getDashboardAnalytics,
  getTradeVolumeAnalytics,
  getDutySavingsAnalytics,
  getClassificationAccuracyAnalytics,
  getReports,
  getReport,
  createReport,
  updateReport,
  deleteReport,
  downloadReport,
  exportReport,
  getTemplates,
  getTemplate,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  getSchedules,
  getSchedule,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  toggleSchedule,
  generateQuickReport,
  downloadReportAsFile,
  exportReportAsFile
} = reportsApi;