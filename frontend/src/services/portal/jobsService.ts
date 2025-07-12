// Jobs Service for Portal
// Handles all job-related API operations

import { portalApi } from './api';
import type { 
  Job, 
  JobStatus, 
  JobType, 
  JobPriority,
  ApiResponse, 
  ListParams,
  PaginationInfo 
} from '../../types/portal';

export interface JobsListParams extends ListParams {
  status?: JobStatus;
  type?: JobType;
  priority?: JobPriority;
  dateFrom?: string;
  dateTo?: string;
}

export interface CreateJobData {
  title: string;
  description?: string;
  type: JobType;
  priority?: JobPriority;
  origin: {
    country: string;
    city: string;
    port?: string;
    address?: string;
  };
  destination: {
    country: string;
    city: string;
    port?: string;
    address?: string;
  };
  estimatedArrival?: string;
  totalValue: number;
  currency: string;
  metadata?: Record<string, any>;
}

export interface UpdateJobData {
  title?: string;
  description?: string;
  priority?: JobPriority;
  estimatedArrival?: string;
  totalValue?: number;
  currency?: string;
  metadata?: Record<string, any>;
}

export class JobsService {
  /**
   * Get list of jobs for the current customer
   */
  async getJobs(params: JobsListParams = {}): Promise<ApiResponse<Job[]> & { pagination: PaginationInfo }> {
    const queryParams = {
      ...params,
      ...(params.status && { status: params.status }),
      ...(params.type && { type: params.type }),
      ...(params.priority && { priority: params.priority }),
      ...(params.dateFrom && { dateFrom: params.dateFrom }),
      ...(params.dateTo && { dateTo: params.dateTo }),
    };

    return portalApi.getList<Job>('/portal/jobs', queryParams);
  }

  /**
   * Get a specific job by ID
   */
  async getJob(jobId: string): Promise<ApiResponse<Job>> {
    return portalApi.get<Job>(`/portal/jobs/${jobId}`);
  }

  /**
   * Create a new job
   */
  async createJob(data: CreateJobData): Promise<ApiResponse<Job>> {
    return portalApi.post<Job>('/portal/jobs', data);
  }

  /**
   * Update an existing job
   */
  async updateJob(jobId: string, data: UpdateJobData): Promise<ApiResponse<Job>> {
    return portalApi.patch<Job>(`/portal/jobs/${jobId}`, data);
  }

  /**
   * Cancel a job
   */
  async cancelJob(jobId: string, reason?: string): Promise<ApiResponse<Job>> {
    return portalApi.patch<Job>(`/portal/jobs/${jobId}/cancel`, { reason });
  }

  /**
   * Get job statistics for dashboard
   */
  async getJobStats(): Promise<ApiResponse<{
    total: number;
    byStatus: Record<JobStatus, number>;
    byType: Record<JobType, number>;
    byPriority: Record<JobPriority, number>;
    recentActivity: number;
    pendingPayments: number;
  }>> {
    return portalApi.get('/portal/jobs/stats');
  }

  /**
   * Get recent jobs activity
   */
  async getRecentActivity(limit: number = 10): Promise<ApiResponse<Array<{
    jobId: string;
    jobNumber: string;
    title: string;
    action: string;
    timestamp: string;
    actor: string;
  }>>> {
    return portalApi.get('/portal/jobs/recent-activity', { limit });
  }

  /**
   * Search jobs by various criteria
   */
  async searchJobs(query: string, filters?: {
    status?: JobStatus[];
    type?: JobType[];
    priority?: JobPriority[];
    dateRange?: {
      from: string;
      to: string;
    };
  }): Promise<ApiResponse<Job[]>> {
    const params = {
      q: query,
      ...(filters?.status && { status: filters.status.join(',') }),
      ...(filters?.type && { type: filters.type.join(',') }),
      ...(filters?.priority && { priority: filters.priority.join(',') }),
      ...(filters?.dateRange && {
        dateFrom: filters.dateRange.from,
        dateTo: filters.dateRange.to,
      }),
    };

    return portalApi.get<Job[]>('/portal/jobs/search', params);
  }

  /**
   * Get jobs that need attention (pending actions, overdue, etc.)
   */
  async getJobsNeedingAttention(): Promise<ApiResponse<Job[]>> {
    return portalApi.get<Job[]>('/portal/jobs/needs-attention');
  }

  /**
   * Get job timeline/history
   */
  async getJobTimeline(jobId: string): Promise<ApiResponse<Array<{
    id: string;
    timestamp: string;
    event: string;
    description: string;
    actor: {
      name: string;
      type: 'customer' | 'broker' | 'system';
    };
    metadata?: Record<string, any>;
  }>>> {
    return portalApi.get(`/portal/jobs/${jobId}/timeline`);
  }

  /**
   * Add a comment to a job
   */
  async addJobComment(jobId: string, comment: string): Promise<ApiResponse<{
    id: string;
    comment: string;
    timestamp: string;
    author: string;
  }>> {
    return portalApi.post(`/portal/jobs/${jobId}/comments`, { comment });
  }

  /**
   * Get job comments
   */
  async getJobComments(jobId: string): Promise<ApiResponse<Array<{
    id: string;
    comment: string;
    timestamp: string;
    author: {
      name: string;
      type: 'customer' | 'broker';
    };
  }>>> {
    return portalApi.get(`/portal/jobs/${jobId}/comments`);
  }

  /**
   * Request job status update from broker
   */
  async requestStatusUpdate(jobId: string, message?: string): Promise<ApiResponse<void>> {
    return portalApi.post(`/portal/jobs/${jobId}/request-update`, { message });
  }

  /**
   * Mark job as reviewed by customer
   */
  async markJobAsReviewed(jobId: string): Promise<ApiResponse<Job>> {
    return portalApi.patch(`/portal/jobs/${jobId}/mark-reviewed`);
  }

  /**
   * Get jobs summary for a date range
   */
  async getJobsSummary(dateFrom: string, dateTo: string): Promise<ApiResponse<{
    totalJobs: number;
    completedJobs: number;
    pendingJobs: number;
    totalValue: number;
    averageProcessingTime: number;
    topDestinations: Array<{
      country: string;
      count: number;
    }>;
    topOrigins: Array<{
      country: string;
      count: number;
    }>;
  }>> {
    return portalApi.get('/portal/jobs/summary', { dateFrom, dateTo });
  }

  /**
   * Export jobs data
   */
  async exportJobs(params: {
    format: 'csv' | 'excel' | 'pdf';
    dateFrom?: string;
    dateTo?: string;
    status?: JobStatus[];
    type?: JobType[];
  }): Promise<ApiResponse<{
    downloadUrl: string;
    filename: string;
    expiresAt: string;
  }>> {
    const queryParams = {
      format: params.format,
      ...(params.dateFrom && { dateFrom: params.dateFrom }),
      ...(params.dateTo && { dateTo: params.dateTo }),
      ...(params.status && { status: params.status.join(',') }),
      ...(params.type && { type: params.type.join(',') }),
    };

    return portalApi.get('/portal/jobs/export', queryParams);
  }
}

// Create and export default instance
export const jobsService = new JobsService();
export default JobsService;