import axios, { AxiosError } from 'axios';
import type { DutyCalculationRequest, DutyCalculationResult } from '../types';

// Type alias for consistency with backend
export type DutyCalculationResponse = DutyCalculationResult;

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
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('API Response Error:', error);
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      throw new Error(data?.detail || data?.message || `HTTP ${status} Error`);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export interface DutyRatesResponse {
  hs_code: string;
  general_rate: number;
  general_rate_description: string;
  unit: string;
  statistical_code?: string;
  last_updated: string;
}

export interface DutyBreakdownResponse {
  hs_code: string;
  country_code: string;
  customs_value: number;
  breakdown: {
    general_duty: {
      rate: number;
      amount: number;
      description: string;
    };
    fta_duty?: {
      rate: number;
      amount: number;
      description: string;
      agreement: string;
    };
    anti_dumping?: {
      rate: number;
      amount: number;
      description: string;
    };
    gst: {
      rate: number;
      amount: number;
      description: string;
    };
    total_duty: number;
    total_taxes: number;
    total_amount: number;
  };
}

export interface FtaRatesResponse {
  hs_code: string;
  country_code: string;
  fta_agreements: Array<{
    agreement_name: string;
    agreement_code: string;
    rate: number;
    rate_description: string;
    effective_date: string;
    conditions?: string[];
  }>;
}

export interface TcoCheckResponse {
  hs_code: string;
  tco_eligible: boolean;
  tco_orders?: Array<{
    order_number: string;
    description: string;
    effective_date: string;
    expiry_date?: string;
    conditions?: string[];
  }>;
}

export const dutyCalculatorApi = {
  /**
   * Calculate comprehensive duty for goods
   */
  async calculateDuty(request: DutyCalculationRequest): Promise<DutyCalculationResponse> {
    const response = await apiClient.post<DutyCalculationResponse>('/api/duty/calculate', request);
    return response.data;
  },

  /**
   * Get duty rates for a specific HS code
   */
  async getDutyRates(hsCode: string): Promise<DutyRatesResponse> {
    const response = await apiClient.get<DutyRatesResponse>(`/api/duty/rates/${hsCode}`);
    return response.data;
  },

  /**
   * Get detailed duty breakdown
   */
  async getDutyBreakdown(
    hsCode: string,
    countryCode: string,
    customsValue: number,
    quantity: number = 1
  ): Promise<DutyBreakdownResponse> {
    const params = new URLSearchParams({
      hs_code: hsCode,
      country_code: countryCode,
      customs_value: customsValue.toString(),
      quantity: quantity.toString(),
    });

    const response = await apiClient.get<DutyBreakdownResponse>(`/api/duty/breakdown?${params}`);
    return response.data;
  },

  /**
   * Get FTA rates for specific HS code and country
   */
  async getFtaRates(hsCode: string, countryCode: string): Promise<FtaRatesResponse> {
    const response = await apiClient.get<FtaRatesResponse>(`/api/duty/fta-rates/${hsCode}/${countryCode}`);
    return response.data;
  },

  /**
   * Check TCO exemption eligibility
   */
  async checkTcoExemption(hsCode: string): Promise<TcoCheckResponse> {
    const response = await apiClient.get<TcoCheckResponse>(`/api/duty/tco-check/${hsCode}`);
    return response.data;
  },

  /**
   * Health check for the duty calculator service
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/duty/health');
    return response.data;
  },
};

// Export utility functions for formatting
export const formatCurrency = (amount: number, currency: string = 'AUD'): string => {
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatPercentage = (rate: number): string => {
  return new Intl.NumberFormat('en-AU', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  }).format(rate / 100);
};

export const formatHsCode = (hsCode: string): string => {
  // Format HS code as XXXX.XX.XX
  if (hsCode.length === 10) {
    return `${hsCode.slice(0, 4)}.${hsCode.slice(4, 6)}.${hsCode.slice(6, 8)}`;
  }
  return hsCode;
};

export const validateHsCode = (hsCode: string): boolean => {
  // HS code should be 10 digits
  return /^\d{10}$/.test(hsCode.replace(/\./g, ''));
};

export const parseHsCode = (hsCode: string): string => {
  // Remove dots and ensure 10 digits
  return hsCode.replace(/\./g, '').padEnd(10, '0').slice(0, 10);
};

// Error types for better error handling
export class DutyCalculatorApiError extends Error {
  public statusCode?: number;
  public errorCode?: string;

  constructor(
    message: string,
    statusCode?: number,
    errorCode?: string
  ) {
    super(message);
    this.name = 'DutyCalculatorApiError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
  }
}

export class ValidationError extends DutyCalculatorApiError {
  public field?: string;

  constructor(message: string, field?: string) {
    super(message, 400, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
    this.field = field;
  }
}

export class NetworkError extends DutyCalculatorApiError {
  constructor(message: string = 'Network connection failed') {
    super(message, 0, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

export default dutyCalculatorApi;