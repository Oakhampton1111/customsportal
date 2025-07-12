// AI Document Processing API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  public status: number;
  public response?: any;

  constructor(message: string, status: number, response?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}

class HttpClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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
}

const httpClient = new HttpClient(API_BASE_URL);

// AI Document Processing API
export const aiApi = {
  async getProcessingStats(): Promise<{
    total_documents: number;
    pending_review: number;
    completed_today: number;
    accuracy_rate: number;
    avg_processing_time: number;
  }> {
    return httpClient.get('/ai/documents/stats');
  },

  async getPendingDocuments(): Promise<Array<{
    id: number;
    document_id: number;
    document_name: string;
    processing_status: 'pending' | 'processing' | 'completed' | 'failed';
    detected_document_type: string;
    extraction_confidence: 'high' | 'medium' | 'low';
    requires_manual_review: boolean;
    created_at: string;
    processing_duration_seconds?: number;
  }>> {
    return httpClient.get('/ai/documents/pending');
  },

  async getDocumentProcessing(id: number): Promise<{
    id: number;
    document_id: number;
    document_name: string;
    processing_status: string;
    detected_document_type: string;
    extraction_confidence: string;
    extracted_fields: Record<string, any>;
    ocr_results: Array<{
      page_number: number;
      text_content: string;
      confidence_score: number;
      bounding_boxes: Array<{
        text: string;
        x: number;
        y: number;
        width: number;
        height: number;
      }>;
    }>;
    validation_errors: string[];
    requires_manual_review: boolean;
    created_at: string;
    updated_at: string;
  }> {
    return httpClient.get(`/ai/documents/processing/${id}`);
  },

  async updateExtractedFields(id: number, fields: Record<string, any>): Promise<void> {
    return httpClient.put(`/ai/documents/processing/${id}/fields`, { extracted_fields: fields });
  },

  async approveProcessing(id: number): Promise<void> {
    return httpClient.post(`/ai/documents/processing/${id}/approve`);
  },

  async rejectProcessing(id: number, reason: string): Promise<void> {
    return httpClient.post(`/ai/documents/processing/${id}/reject`, { reason });
  },

  async reprocessDocument(id: number): Promise<void> {
    return httpClient.post(`/ai/documents/processing/${id}/reprocess`);
  },

  async generateCustomsEntry(documentId: number, extractedData: Record<string, any>): Promise<{
    entry_id: string;
    declaration_data: Record<string, any>;
    calculated_duties: Array<{
      item_number: string;
      hs_code: string;
      description: string;
      quantity: number;
      unit_value: number;
      total_value: number;
      duty_rate: number;
      duty_amount: number;
      gst_amount: number;
      total_charges: number;
    }>;
    compliance_checks: Array<{
      check_type: string;
      status: 'pass' | 'fail' | 'warning';
      message: string;
      required_documents?: string[];
    }>;
    estimated_clearance_time: string;
  }> {
    return httpClient.post('/ai/customs/generate-entry', {
      document_id: documentId,
      extracted_data: extractedData
    });
  },

  async validateHSCode(code: string, description: string): Promise<{
    is_valid: boolean;
    suggested_codes: Array<{
      code: string;
      description: string;
      confidence: number;
    }>;
    duty_rates: {
      general: number;
      preferential?: Record<string, number>;
    };
  }> {
    return httpClient.post('/ai/hs-codes/validate', {
      hs_code: code,
      description
    });
  },

  async calculateDuties(items: Array<{
    hs_code: string;
    description: string;
    quantity: number;
    unit_value: number;
    country_of_origin: string;
  }>): Promise<{
    total_customs_value: number;
    total_duty: number;
    total_gst: number;
    total_charges: number;
    item_breakdown: Array<{
      item_number: number;
      customs_value: number;
      duty_rate: number;
      duty_amount: number;
      gst_rate: number;
      gst_amount: number;
      total_item_charges: number;
      applicable_concessions: string[];
    }>;
  }> {
    return httpClient.post('/ai/duties/calculate', { items });
  },

  async checkCompliance(entryData: Record<string, any>): Promise<{
    overall_status: 'compliant' | 'non_compliant' | 'requires_review';
    checks: Array<{
      category: string;
      requirement: string;
      status: 'pass' | 'fail' | 'warning';
      message: string;
      severity: 'low' | 'medium' | 'high' | 'critical';
      required_action?: string;
      supporting_documents?: string[];
    }>;
    required_permits: Array<{
      permit_type: string;
      issuing_authority: string;
      estimated_processing_time: string;
      application_url?: string;
    }>;
    recommendations: string[];
  }> {
    return httpClient.post('/ai/compliance/check', entryData);
  }
};

export { ApiError };
export default aiApi;