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
    console.log(`Export API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Export API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Export API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('Export API Response Error:', error);
    
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

// Type definitions matching backend models
export interface AHECCNode {
  code: string;
  description: string;
  level: string; // section, chapter, heading, subheading
  parent_code?: string;
  children: AHECCNode[];
  statistical_unit?: string;
  corresponding_import_code?: string;
  has_children: boolean;
}

export interface ExportRequirement {
  requirement_type: string; // permit, certificate, license
  description: string;
  issuing_authority: string;
  mandatory: boolean;
  processing_time?: string;
  cost?: string;
  documentation_required: string[];
}

export interface ExportDestination {
  country: string;
  value_aud: number;
  percentage: number;
}

export interface ExportStatistics {
  ahecc_code: string;
  export_value_aud: number;
  export_volume: number;
  unit: string;
  top_destinations: ExportDestination[];
  year_on_year_change: number;
  seasonal_pattern?: string;
}

export interface MarketAccessInfo {
  country: string;
  access_status: string;
  requirements: string[];
  restrictions?: string[];
  tariff_treatment?: string;
}

export interface MarketAccessInfoSummary {
  [key: string]: MarketAccessInfo;
}

export interface ExportCodeDetails {
  code: string;
  description: string;
  statistical_unit?: string;
  corresponding_import_code?: string;
  level: string;
  parent_code?: string;
  export_requirements: ExportRequirement[];
  market_access_summary: MarketAccessInfoSummary;
  trade_statistics?: ExportStatistics;
}

export const exportApi = {
  /**
   * Get AHECC tree structure
   */
  async getAHECCTree(section?: string, parentCode?: string): Promise<AHECCNode[]> {
    const params = new URLSearchParams();
    if (section) params.append('section', section);
    if (parentCode) params.append('parent_code', parentCode);

    const response = await apiClient.get<AHECCNode[]>(`/api/export/ahecc-tree?${params}`);
    return response.data;
  },

  /**
   * Search AHECC codes
   */
  async searchAHECCCodes(
    query: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<AHECCNode[]> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await apiClient.get<AHECCNode[]>(`/api/export/ahecc-search?${params}`);
    return response.data;
  },

  /**
   * Get detailed information for a specific AHECC code
   */
  async getExportCodeDetails(aheccCode: string): Promise<ExportCodeDetails> {
    const response = await apiClient.get<ExportCodeDetails>(`/api/export/code/${aheccCode}/details`);
    return response.data;
  },

  /**
   * Get export requirements for a specific AHECC code and country
   */
  async getExportRequirements(aheccCode: string, country: string): Promise<ExportRequirement[]> {
    const response = await apiClient.get<ExportRequirement[]>(`/api/export/code/${aheccCode}/requirements/${country}`);
    return response.data;
  },

  /**
   * Get market access information for a specific country
   */
  async getMarketAccessInfo(country: string): Promise<MarketAccessInfo> {
    const response = await apiClient.get<MarketAccessInfo>(`/api/export/market-access/${country}`);
    return response.data;
  },

  /**
   * Get export statistics for a specific AHECC code
   */
  async getExportStatistics(aheccCode: string): Promise<ExportStatistics> {
    const response = await apiClient.get<ExportStatistics>(`/api/export/statistics/${aheccCode}`);
    return response.data;
  },

  /**
   * Get export permits for a commodity group
   */
  async getExportPermits(commodityGroup: string): Promise<ExportRequirement[]> {
    const response = await apiClient.get<ExportRequirement[]>(`/api/export/permits/${commodityGroup}`);
    return response.data;
  },

  /**
   * Get quarantine requirements for a specific AHECC code
   */
  async getQuarantineRequirements(aheccCode: string): Promise<ExportRequirement[]> {
    const response = await apiClient.get<ExportRequirement[]>(`/api/export/quarantine/${aheccCode}`);
    return response.data;
  },

  /**
   * Health check for the export service
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/export/health');
    return response.data;
  },
};

// Export utility functions for formatting
export const formatAHECCCode = (code: string): string => {
  // Format AHECC code as XXXX.XX.XX.XX
  if (code.length === 10) {
    return `${code.slice(0, 4)}.${code.slice(4, 6)}.${code.slice(6, 8)}.${code.slice(8, 10)}`;
  }
  return code;
};

export const parseAHECCCode = (code: string): string => {
  // Remove dots and ensure proper format
  return code.replace(/\./g, '');
};

export const validateAHECCCode = (code: string): boolean => {
  // AHECC code should be 10 digits
  return /^\d{10}$/.test(code.replace(/\./g, ''));
};

export const getCodeLevel = (code: string): string => {
  const cleanCode = parseAHECCCode(code);
  if (cleanCode.length >= 2) return 'chapter';
  if (cleanCode.length >= 4) return 'heading';
  if (cleanCode.length >= 6) return 'subheading';
  if (cleanCode.length >= 8) return 'item';
  if (cleanCode.length === 10) return 'statistical';
  return 'unknown';
};

// Error types for better error handling
export class ExportApiError extends Error {
  public statusCode?: number;
  public errorCode?: string;

  constructor(
    message: string,
    statusCode?: number,
    errorCode?: string
  ) {
    super(message);
    this.name = 'ExportApiError';
    this.statusCode = statusCode;
    this.errorCode = errorCode;
  }
}

export class ValidationError extends ExportApiError {
  public field?: string;

  constructor(message: string, field?: string) {
    super(message, 400, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
    this.field = field;
  }
}

export class NetworkError extends ExportApiError {
  constructor(message: string = 'Network connection failed') {
    super(message, 0, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

export default exportApi;
