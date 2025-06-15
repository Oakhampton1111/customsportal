import axios, { AxiosError } from 'axios';

// Temporarily hardcode to test
const API_BASE_URL = 'http://127.0.0.1:8000';

// Debug logging
console.log('Rulings API - Environment variable VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
console.log('Rulings API - Using API_BASE_URL:', API_BASE_URL);

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
    console.log(`Rulings API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Rulings API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Rulings API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('Rulings API Response Error:', error);
    
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

// TypeScript interfaces for Rulings API
export interface TariffRuling {
  ruling_number: string;
  title: string;
  description: string;
  hs_code: string;
  commodity_description: string;
  ruling_date: string;
  effective_date: string;
  status: 'active' | 'superseded' | 'revoked';
  tariff_classification: string;
  duty_rate: string;
  origin_country?: string;
  applicant?: string;
  ruling_text: string;
  references: string[];
  related_rulings: string[];
}

export interface AntiDumpingDecision {
  id: string;
  case_number: string;
  title: string;
  product_description: string;
  hs_codes: string[];
  countries_involved: string[];
  decision_type: 'initiation' | 'preliminary' | 'final' | 'review' | 'termination';
  decision_date: string;
  effective_date: string;
  duty_rate?: string;
  status: 'active' | 'expired' | 'revoked';
  summary: string;
  document_url?: string;
}

export interface RegulatoryUpdate {
  id: string;
  title: string;
  description: string;
  category: 'tariff' | 'customs' | 'trade_agreement' | 'regulation' | 'procedure';
  update_type: 'new' | 'amendment' | 'repeal' | 'clarification';
  published_date: string;
  effective_date: string;
  affected_codes: string[];
  impact_level: 'low' | 'medium' | 'high' | 'critical';
  summary: string;
  full_text?: string;
  document_url?: string;
  contact_info?: string;
}

export interface RulingSearchQuery {
  query: string;
  ruling_type?: 'tariff' | 'anti_dumping' | 'regulatory';
  hs_code?: string;
  date_from?: string;
  date_to?: string;
  status?: string;
  page?: number;
  limit?: number;
}

export interface RulingSearchResult {
  id: string;
  type: 'tariff_ruling' | 'anti_dumping' | 'regulatory_update';
  title: string;
  summary: string;
  ruling_number?: string;
  date: string;
  status: string;
  relevance_score: number;
  hs_codes: string[];
}

export interface RulingStatistics {
  total_rulings: number;
  recent_rulings: number;
  by_category: Record<string, number>;
  by_status: Record<string, number>;
  monthly_trends: {
    month: string;
    count: number;
  }[];
  top_hs_codes: {
    hs_code: string;
    count: number;
    description: string;
  }[];
}

export const rulingsApi = {
  /**
   * Get recent rulings
   */
  async getRecentRulings(limit: number = 10): Promise<TariffRuling[]> {
    const response = await apiClient.get<TariffRuling[]>(`/api/rulings/recent?limit=${limit}`);
    return response.data;
  },

  /**
   * Get specific tariff ruling by ruling number
   */
  async getTariffRuling(rulingNumber: string): Promise<TariffRuling> {
    const response = await apiClient.get<TariffRuling>(`/api/rulings/tariff/${rulingNumber}`);
    return response.data;
  },

  /**
   * Get recent anti-dumping decisions
   */
  async getRecentAntiDumpingDecisions(limit: number = 10): Promise<AntiDumpingDecision[]> {
    const response = await apiClient.get<AntiDumpingDecision[]>(`/api/rulings/anti-dumping/recent?limit=${limit}`);
    return response.data;
  },

  /**
   * Get regulatory updates
   */
  async getRegulatoryUpdates(limit: number = 10): Promise<RegulatoryUpdate[]> {
    const response = await apiClient.get<RegulatoryUpdate[]>(`/api/rulings/regulatory/updates?limit=${limit}`);
    return response.data;
  },

  /**
   * Search rulings
   */
  async searchRulings(query: RulingSearchQuery): Promise<{
    results: RulingSearchResult[];
    total: number;
    page: number;
    limit: number;
  }> {
    const params = new URLSearchParams({
      q: query.query,
      page: query.page?.toString() || '1',
      limit: query.limit?.toString() || '20',
    });

    // Add optional filters
    if (query.ruling_type) {
      params.append('ruling_type', query.ruling_type);
    }
    if (query.hs_code) {
      params.append('hs_code', query.hs_code);
    }
    if (query.date_from) {
      params.append('date_from', query.date_from);
    }
    if (query.date_to) {
      params.append('date_to', query.date_to);
    }
    if (query.status) {
      params.append('status', query.status);
    }

    const response = await apiClient.get(`/api/rulings/search?${params}`);
    return response.data;
  },

  /**
   * Get ruling statistics
   */
  async getStatistics(): Promise<RulingStatistics> {
    const response = await apiClient.get<RulingStatistics>('/api/rulings/statistics');
    return response.data;
  },

  /**
   * Health check for the rulings service
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/rulings/health');
    return response.data;
  },
};

export default rulingsApi;
