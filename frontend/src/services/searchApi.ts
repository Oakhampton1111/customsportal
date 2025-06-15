import axios, { AxiosError } from 'axios';
import type { SearchQuery, SearchResult, PaginatedResponse } from '../types';

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
    console.log(`Search API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Search API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Search API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('Search API Response Error:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      throw new Error((data as { detail?: string; message?: string })?.detail || (data as { detail?: string; message?: string })?.message || `HTTP ${status} Error`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export interface SearchApiResponse {
  results: SearchResult[];
  total: number;
  page: number;
  limit: number;
  query: string;
  search_type: string;
  execution_time: number;
}

// Additional interfaces for new endpoints
export interface ClassificationRequest {
  product_description: string;
  additional_info?: string;
  country_of_origin?: string;
  intended_use?: string;
}

export interface ClassificationResult {
  hs_code: string;
  description: string;
  confidence_score: number;
  reasoning: string;
  alternative_codes?: {
    hs_code: string;
    description: string;
    confidence_score: number;
  }[];
}

export interface BatchClassificationRequest {
  products: ClassificationRequest[];
}

export interface BatchClassificationResult {
  results: (ClassificationResult & { product_index: number })[];
  total_processed: number;
  processing_time: number;
}

export interface ClassificationFeedback {
  product_description: string;
  suggested_hs_code: string;
  actual_hs_code: string;
  feedback_type: 'correct' | 'incorrect' | 'partial';
  comments?: string;
}

export interface ProductSearchQuery {
  query: string;
  hs_code_filter?: string;
  country_filter?: string;
  page?: number;
  limit?: number;
}

export interface ProductSearchResult {
  product_name: string;
  hs_code: string;
  description: string;
  tariff_rate: string;
  country_of_origin?: string;
  manufacturer?: string;
  relevance_score: number;
}

export interface ClassificationStats {
  total_classifications: number;
  accuracy_rate: number;
  top_classified_codes: {
    hs_code: string;
    count: number;
    description: string;
  }[];
  classification_trends: {
    date: string;
    count: number;
    accuracy: number;
  }[];
  feedback_summary: {
    total_feedback: number;
    correct_percentage: number;
    incorrect_percentage: number;
    partial_percentage: number;
  };
}

export const searchApi = {
  /**
   * Search across tariff codes, descriptions, and classifications
   */
  async search(query: SearchQuery): Promise<PaginatedResponse<SearchResult>> {
    const params = new URLSearchParams({
      q: query.query,
      search_type: query.search_type,
      page: query.pagination?.page?.toString() || '1',
      limit: query.pagination?.limit?.toString() || '20',
    });

    // Add optional filters
    if (query.filters?.country_code) {
      params.append('country_code', query.filters.country_code);
    }
    if (query.filters?.rate_type) {
      params.append('rate_type', query.filters.rate_type);
    }
    if (query.filters?.effective_date) {
      params.append('effective_date', query.filters.effective_date);
    }

    const response = await apiClient.get<SearchApiResponse>(`/api/search?${params}`);
    
    // Transform backend response to frontend format
    return {
      success: true,
      data: response.data.results,
      pagination: {
        page: response.data.page,
        limit: response.data.limit,
        total: response.data.total,
        totalPages: Math.ceil(response.data.total / response.data.limit),
      },
    };
  },

  /**
   * Get search suggestions for autocomplete
   */
  async getSuggestions(query: string, type: 'hs_code' | 'description' = 'description'): Promise<string[]> {
    const params = new URLSearchParams({
      q: query,
      type,
      limit: '10',
    });

    const response = await apiClient.get<{ suggestions: string[] }>(`/api/search/suggestions?${params}`);
    return response.data.suggestions;
  },

  /**
   * Classify a product to get HS code recommendations
   */
  async classify(request: ClassificationRequest): Promise<ClassificationResult> {
    const response = await apiClient.post<ClassificationResult>('/api/search/classify', request);
    return response.data;
  },

  /**
   * Batch classify multiple products
   */
  async batchClassify(request: BatchClassificationRequest): Promise<BatchClassificationResult> {
    const response = await apiClient.post<BatchClassificationResult>('/api/search/classify/batch', request);
    return response.data;
  },

  /**
   * Submit classification feedback
   */
  async submitFeedback(feedback: ClassificationFeedback): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/api/search/feedback', feedback);
    return response.data;
  },

  /**
   * Search for products
   */
  async searchProducts(query: ProductSearchQuery): Promise<{
    results: ProductSearchResult[];
    total: number;
    page: number;
    limit: number;
  }> {
    const params = new URLSearchParams({
      q: query.query,
      page: query.page?.toString() || '1',
      limit: query.limit?.toString() || '20',
    });

    if (query.hs_code_filter) {
      params.append('hs_code', query.hs_code_filter);
    }
    if (query.country_filter) {
      params.append('country', query.country_filter);
    }

    const response = await apiClient.get(`/api/search/products?${params}`);
    return response.data;
  },

  /**
   * Get classification statistics
   */
  async getClassificationStats(): Promise<ClassificationStats> {
    const response = await apiClient.get<ClassificationStats>('/api/search/stats');
    return response.data;
  },

  /**
   * Health check for the search service
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/search/health');
    return response.data;
  },
};

export default searchApi;
