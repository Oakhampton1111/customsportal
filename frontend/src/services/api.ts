import type {
  Customer,
  CustomerRegistration,
  CustomerLogin,
  TokenResponse,
  SSOProvider,
  SSOInitiateResponse,
  LinkedSSOAccount
} from '../types/customer';
import type {
  Document,
  DocumentUploadRequest,
  DocumentCategory,
  DocumentSearchParams,
  DocumentStats
} from '../types/documents';
import type {
  DigitalLOA,
  LOACreateRequest,
  LOASignRequest,
  LOATemplate,
  LOAStats
} from '../types/loa';
import type {
  EDIJob,
  JobRegistrationRequest,
  EDIMessage,
  JobStatusResponse,
  CustomsDeclaration
} from '../types/edi';
import type {
  ComplianceRequirement,
  ComplianceAudit,
  ComplianceReport
} from '../types/compliance';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  public status: number;
  public response?: any;

  constructor(
    message: string,
    status: number,
    response?: any
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}

// HTTP Client utility
class HttpClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('auth_token');

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return response as unknown as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Network error occurred', 0, error);
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async upload<T>(endpoint: string, formData: FormData): Promise<T> {
    const token = localStorage.getItem('auth_token');
    
    const config: RequestInit = {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  }
}

const httpClient = new HttpClient(API_BASE_URL);

// Authentication API
export const authApi = {
  async login(credentials: CustomerLogin): Promise<TokenResponse> {
    return httpClient.post<TokenResponse>('/auth/login', credentials);
  },

  async register(data: CustomerRegistration): Promise<TokenResponse> {
    return httpClient.post<TokenResponse>('/auth/register', data);
  },

  async logout(): Promise<void> {
    await httpClient.post<void>('/auth/logout');
    localStorage.removeItem('auth_token');
  },

  async refreshToken(): Promise<TokenResponse> {
    return httpClient.post<TokenResponse>('/auth/refresh');
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    return httpClient.post<{ message: string }>('/auth/forgot-password', { email });
  },

  async resetPassword(token: string, password: string): Promise<{ message: string }> {
    return httpClient.post<{ message: string }>('/auth/reset-password', { token, password });
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    return httpClient.post<{ message: string }>('/auth/verify-email', { token });
  },
};

// Customer API
export const customerApi = {
  async getProfile(): Promise<Customer> {
    return httpClient.get<Customer>('/customer/profile');
  },

  async updateProfile(data: Partial<Customer>): Promise<Customer> {
    return httpClient.put<Customer>('/customer/profile', data);
  },

  async getDashboardStats(): Promise<{
    totalDocuments: number;
    pendingLOAs: number;
    activeEDIJobs: number;
    complianceScore: number;
  }> {
    return httpClient.get('/customer/dashboard/stats');
  },

  async getRecentActivity(): Promise<Array<{
    id: string;
    type: string;
    description: string;
    timestamp: string;
    status: string;
  }>> {
    return httpClient.get('/customer/activity');
  },
};

// Documents API
export const documentsApi = {
  async getDocuments(filters?: DocumentSearchParams): Promise<Document[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return httpClient.get<Document[]>(`/documents${query}`);
  },

  async getDocument(id: string): Promise<Document> {
    return httpClient.get<Document>(`/documents/${id}`);
  },

  async uploadDocument(data: DocumentUploadRequest, file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(data));
    return httpClient.upload<Document>('/documents/upload', formData);
  },

  async updateDocument(id: string, data: Partial<Document>): Promise<Document> {
    return httpClient.put<Document>(`/documents/${id}`, data);
  },

  async deleteDocument(id: string): Promise<void> {
    return httpClient.delete<void>(`/documents/${id}`);
  },

  async downloadDocument(id: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/documents/${id}/download`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (!response.ok) {
      throw new ApiError('Failed to download document', response.status);
    }
    
    return response.blob();
  },

  async getCategories(): Promise<DocumentCategory[]> {
    return httpClient.get<DocumentCategory[]>('/documents/categories');
  },

  async shareDocument(id: string, email: string, permissions: string[]): Promise<{ message: string }> {
    return httpClient.post<{ message: string }>(`/documents/${id}/share`, {
      email,
      permissions,
    });
  },
};

// LOA API
export const loaApi = {
  async getLOAs(): Promise<DigitalLOA[]> {
    return httpClient.get<DigitalLOA[]>('/loa');
  },

  async getLOA(id: string): Promise<DigitalLOA> {
    return httpClient.get<DigitalLOA>(`/loa/${id}`);
  },

  async createLOA(data: LOACreateRequest): Promise<DigitalLOA> {
    return httpClient.post<DigitalLOA>('/loa', data);
  },

  async updateLOA(id: string, data: Partial<LOACreateRequest>): Promise<DigitalLOA> {
    return httpClient.put<DigitalLOA>(`/loa/${id}`, data);
  },

  async signLOA(id: string, data: LOASignRequest): Promise<DigitalLOA> {
    return httpClient.post<DigitalLOA>(`/loa/${id}/sign`, data);
  },

  async deleteLOA(id: string): Promise<void> {
    return httpClient.delete<void>(`/loa/${id}`);
  },

  async downloadLOA(id: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/loa/${id}/download`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      },
    });
    
    if (!response.ok) {
      throw new ApiError('Failed to download LOA', response.status);
    }
    
    return response.blob();
  },

  async getTemplates(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    fields: string[];
  }>> {
    return httpClient.get('/loa/templates');
  },
};

// EDI API
export const ediApi = {
  async getJobs(): Promise<EDIJob[]> {
    return httpClient.get<EDIJob[]>('/edi/jobs');
  },

  async getJob(id: string): Promise<EDIJob> {
    return httpClient.get<EDIJob>(`/edi/jobs/${id}`);
  },

  async createJob(data: JobRegistrationRequest): Promise<EDIJob> {
    return httpClient.post<EDIJob>('/edi/jobs', data);
  },

  async updateJob(id: string, data: Partial<JobRegistrationRequest>): Promise<EDIJob> {
    return httpClient.put<EDIJob>(`/edi/jobs/${id}`, data);
  },

  async deleteJob(id: string): Promise<void> {
    return httpClient.delete<void>(`/edi/jobs/${id}`);
  },

  async getJobMessages(jobId: string): Promise<EDIMessage[]> {
    return httpClient.get<EDIMessage[]>(`/edi/jobs/${jobId}/messages`);
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    return httpClient.get<JobStatusResponse>(`/edi/jobs/${jobId}/status`);
  },

  async retryJob(jobId: string): Promise<EDIJob> {
    return httpClient.post<EDIJob>(`/edi/jobs/${jobId}/retry`);
  },

  async cancelJob(jobId: string): Promise<EDIJob> {
    return httpClient.post<EDIJob>(`/edi/jobs/${jobId}/cancel`);
  },

  async getPartners(): Promise<Array<{
    id: string;
    name: string;
    type: string;
    capabilities: string[];
  }>> {
    return httpClient.get('/edi/partners');
  },
};

// Compliance API
export const complianceApi = {
  async getRequirements(): Promise<ComplianceRequirement[]> {
    return httpClient.get<ComplianceRequirement[]>('/compliance/requirements');
  },

  async getRequirement(id: string): Promise<ComplianceRequirement> {
    return httpClient.get<ComplianceRequirement>(`/compliance/requirements/${id}`);
  },

  async getAudits(): Promise<ComplianceAudit[]> {
    return httpClient.get<ComplianceAudit[]>('/compliance/audits');
  },

  async getAudit(id: string): Promise<ComplianceAudit> {
    return httpClient.get<ComplianceAudit>(`/compliance/audits/${id}`);
  },

  async createAudit(data: {
    name: string;
    description: string;
    scope: string[];
    scheduledDate: string;
  }): Promise<ComplianceAudit> {
    return httpClient.post<ComplianceAudit>('/compliance/audits', data);
  },

  async getReports(): Promise<ComplianceReport[]> {
    return httpClient.get<ComplianceReport[]>('/compliance/reports');
  },

  async getReport(id: string): Promise<ComplianceReport> {
    return httpClient.get<ComplianceReport>(`/compliance/reports/${id}`);
  },

  async generateReport(data: {
    type: string;
    dateRange: { start: string; end: string };
    scope: string[];
  }): Promise<ComplianceReport> {
    return httpClient.post<ComplianceReport>('/compliance/reports/generate', data);
  },

  async getComplianceScore(): Promise<{
    overall: number;
    categories: Record<string, number>;
    trends: Array<{ date: string; score: number }>;
  }> {
    return httpClient.get('/compliance/score');
  },

  async getViolations(): Promise<Array<{
    id: string;
    type: string;
    severity: string;
    description: string;
    date: string;
    status: string;
    resolution?: string;
  }>> {
    return httpClient.get('/compliance/violations');
  },
};

// Notifications API
export const notificationsApi = {
  async getNotifications(): Promise<Array<{
    id: string;
    type: string;
    title: string;
    message: string;
    timestamp: string;
    read: boolean;
    priority: string;
  }>> {
    return httpClient.get('/notifications');
  },

  async markAsRead(id: string): Promise<void> {
    return httpClient.put<void>(`/notifications/${id}/read`);
  },

  async markAllAsRead(): Promise<void> {
    return httpClient.put<void>('/notifications/read-all');
  },

  async deleteNotification(id: string): Promise<void> {
    return httpClient.delete<void>(`/notifications/${id}`);
  },

  async getPreferences(): Promise<{
    email: boolean;
    push: boolean;
    sms: boolean;
    categories: Record<string, boolean>;
  }> {
    return httpClient.get('/notifications/preferences');
  },

  async updatePreferences(preferences: {
    email?: boolean;
    push?: boolean;
    sms?: boolean;
    categories?: Record<string, boolean>;
  }): Promise<void> {
    return httpClient.put<void>('/notifications/preferences', preferences);
  },
};

// Export the ApiError for error handling
export { ApiError };

// Export a default object with all APIs
export default {
  auth: authApi,
  customer: customerApi,
  documents: documentsApi,
  loa: loaApi,
  edi: ediApi,
  compliance: complianceApi,
  notifications: notificationsApi,
};