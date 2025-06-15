/**
 * Real API client for integration tests
 * This client makes actual HTTP requests to the backend server
 */

import { getApiBaseUrl, getAuthHeaders, retryOperation } from '../config/test-environment';

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

/**
 * Real API client for integration testing
 */
export class IntegrationApiClient {
  private baseUrl: string;
  private defaultTimeout: number;
  private authToken?: string;

  constructor() {
    this.baseUrl = getApiBaseUrl();
    this.defaultTimeout = 30000; // 30 seconds
  }

  /**
   * Set authentication token for subsequent requests
   */
  setAuthToken(token: string): void {
    this.authToken = token;
  }

  /**
   * Clear authentication token
   */
  clearAuthToken(): void {
    this.authToken = undefined;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    timeout: number = this.defaultTimeout
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const requestOptions: RequestInit = {
      ...options,
      headers: {
        ...getAuthHeaders(this.authToken),
        ...options.headers,
      },
    };

    return retryOperation(async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        const responseHeaders: Record<string, string> = {};
        response.headers.forEach((value, key) => {
          responseHeaders[key] = value;
        });

        let data: T;
        const contentType = response.headers.get('content-type');
        
        if (contentType?.includes('application/json')) {
          data = await response.json();
        } else {
          data = (await response.text()) as unknown as T;
        }

        if (!response.ok) {
          const error: ApiError = {
            message: typeof data === 'object' && data && 'message' in data 
              ? (data as any).message 
              : `HTTP ${response.status}`,
            status: response.status,
            details: data,
          };
          throw error;
        }

        return {
          data,
          status: response.status,
          headers: responseHeaders,
        };
      } catch (error) {
        clearTimeout(timeoutId);
        
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error(`Request timeout after ${timeout}ms`);
        }
        
        throw error;
      }
    });
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, timeout?: number): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, { method: 'GET' }, timeout);
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any, timeout?: number): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }, timeout);
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any, timeout?: number): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }, timeout);
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, timeout?: number): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, { method: 'DELETE' }, timeout);
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: any, timeout?: number): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }, timeout);
  }

  // Authentication methods
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.post<{ access_token: string; user: any }>('/auth/login', {
      email,
      password,
    });
    
    const token = response.data.access_token;
    this.setAuthToken(token);
    
    return {
      token,
      user: response.data.user,
    };
  }

  async register(email: string, password: string, fullName: string): Promise<{ token: string; user: any }> {
    const response = await this.post<{ access_token: string; user: any }>('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    
    const token = response.data.access_token;
    this.setAuthToken(token);
    
    return {
      token,
      user: response.data.user,
    };
  }

  async logout(): Promise<void> {
    try {
      await this.post('/auth/logout');
    } finally {
      this.clearAuthToken();
    }
  }

  // Tariff API methods
  async getTariffSections(): Promise<any[]> {
    const response = await this.get<any[]>('/tariff/sections');
    return response.data;
  }

  async getTariffChapters(sectionId: string): Promise<any[]> {
    const response = await this.get<any[]>(`/tariff/chapters/${sectionId}`);
    return response.data;
  }

  async getTariffCode(hsCode: string): Promise<any> {
    const response = await this.get<any>(`/tariff/code/${hsCode}`);
    return response.data;
  }

  async searchTariffs(query: string, filters?: any): Promise<any> {
    const params = new URLSearchParams({ q: query });
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await this.get<any>(`/tariff/search?${params.toString()}`);
    return response.data;
  }

  // Duty Calculator API methods
  async calculateDuty(hsCode: string, value: number, countryCode: string, options?: any): Promise<any> {
    const response = await this.post<any>('/duty/calculate', {
      hs_code: hsCode,
      value,
      country_code: countryCode,
      ...options,
    });
    return response.data;
  }

  async getDutyRates(hsCode: string): Promise<any> {
    const response = await this.get<any>(`/duty/rates/${hsCode}`);
    return response.data;
  }

  async getFtaRates(hsCode: string, countryCode: string): Promise<any> {
    const response = await this.get<any>(`/duty/fta-rates/${hsCode}/${countryCode}`);
    return response.data;
  }

  async checkTco(hsCode: string): Promise<any> {
    const response = await this.get<any>(`/duty/tco-check/${hsCode}`);
    return response.data;
  }

  // Search API methods
  async classifyProduct(description: string, options?: any): Promise<any> {
    const response = await this.post<any>('/search/classify', {
      description,
      ...options,
    });
    return response.data;
  }

  async batchClassifyProducts(descriptions: string[], options?: any): Promise<any> {
    const response = await this.post<any>('/search/classify/batch', {
      descriptions,
      ...options,
    });
    return response.data;
  }

  async searchProducts(query: string, filters?: any): Promise<any> {
    const params = new URLSearchParams({ q: query });
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await this.get<any>(`/search/products?${params.toString()}`);
    return response.data;
  }

  async submitFeedback(classificationId: string, feedback: any): Promise<any> {
    const response = await this.post<any>('/search/feedback', {
      classification_id: classificationId,
      ...feedback,
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.get<any>('/health', 5000); // 5 second timeout for health check
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new IntegrationApiClient();