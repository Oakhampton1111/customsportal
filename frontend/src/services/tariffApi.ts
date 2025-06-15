import axios, { AxiosError, type AxiosResponse } from 'axios';
import type { TariffRate, FtaRate, HsClassification } from '../types';

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
    console.log(`Tariff API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Tariff API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`Tariff API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('Tariff API Response Error:', error);
    
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

export interface TariffSection {
  id: number;
  section_number: number;
  title: string;
  description?: string;
  chapter_range?: string;
}

export interface TariffChapter {
  id: number;
  chapter_number: number;
  title: string;
  description?: string;
  section_id: number;
}

export interface TariffCodeDetails {
  id: number;
  hs_code: string;
  description: string;
  unit_description?: string;
  parent_code?: string;
  level: number;
  chapter_notes?: string;
  section_id?: number;
  chapter_id?: number;
  is_active: boolean;
  children?: TariffCodeDetails[];
}

export interface TariffHierarchyResponse {
  sections: TariffSection[];
  chapters: TariffChapter[];
  codes: TariffCodeDetails[];
}

export interface TariffTreeNode {
  id: number;
  hs_code: string;
  description: string;
  level: number;
  parent_code?: string;
  has_children: boolean;
  is_leaf: boolean;
  children?: TariffTreeNode[];
  depth: number;
  expanded: boolean;
}

export interface TariffTreeResponse {
  nodes: TariffTreeNode[];
  section?: TariffSection;
  chapter?: TariffChapter;
  total_nodes: number;
  max_depth: number;
  expanded_levels: number[];
  root_level: number;
  show_inactive: boolean;
  load_time_ms?: number;
}

export const tariffApi = {
  /**
   * Get tariff rate information for a specific HS code
   */
  async getTariffRate(hsCode: string): Promise<TariffRate> {
    const response = await apiClient.get<TariffRate>(`/api/tariff/rates/${hsCode}`);
    return response.data;
  },

  /**
   * Get FTA rates for a specific HS code and country
   */
  async getFtaRates(hsCode: string, countryCode?: string): Promise<FtaRate[]> {
    const url = countryCode 
      ? `/api/tariff/fta-rates/${hsCode}/${countryCode}`
      : `/api/tariff/fta-rates/${hsCode}`;
    
    const response = await apiClient.get<FtaRate[]>(url);
    return response.data;
  },

  /**
   * Get HS code classification hierarchy
   */
  async getClassification(hsCode: string): Promise<HsClassification> {
    const response = await apiClient.get<HsClassification>(`/api/tariff/classification/${hsCode}`);
    return response.data;
  },

  /**
   * Get complete tariff hierarchy (sections, chapters, codes)
   */
  async getHierarchy(level?: number, parentCode?: string): Promise<TariffHierarchyResponse> {
    const params = new URLSearchParams();
    if (level) params.append('level', level.toString());
    if (parentCode) params.append('parent_code', parentCode);

    const response = await apiClient.get<TariffHierarchyResponse>(`/api/tariff/hierarchy?${params}`);
    return response.data;
  },

  /**
   * Get all tariff sections
   */
  async getSections(): Promise<TariffSection[]> {
    const response = await apiClient.get<TariffSection[]>('/api/tariff/sections');
    return response.data;
  },

  /**
   * Get chapters for a specific section
   */
  async getChapters(sectionId?: number): Promise<TariffChapter[]> {
    const url = sectionId 
      ? `/api/tariff/chapters/${sectionId}`
      : '/api/tariff/chapters';
    
    const response = await apiClient.get<TariffChapter[]>(url);
    return response.data;
  },

  /**
   * Get tariff codes for a specific chapter or parent code
   */
  async getCodes(chapterId?: number, parentCode?: string, level?: number): Promise<TariffCodeDetails[]> {
    const params = new URLSearchParams();
    if (chapterId) params.append('chapter_id', chapterId.toString());
    if (parentCode) params.append('parent_code', parentCode);
    if (level) params.append('level', level.toString());

    const response = await apiClient.get<TariffCodeDetails[]>(`/api/tariff/codes?${params}`);
    return response.data;
  },

  /**
   * Get detailed information for a specific HS code including children
   */
  async getCodeDetails(hsCode: string): Promise<TariffCodeDetails> {
    const response = await apiClient.get<TariffCodeDetails>(`/api/tariff/codes/${hsCode}`);
    return response.data;
  },

  /**
   * Validate HS code format and existence
   */
  async validateHsCode(hsCode: string): Promise<{ valid: boolean; exists: boolean; message?: string }> {
    const response = await apiClient.get<{ valid: boolean; exists: boolean; message?: string }>(`/api/tariff/validate/${hsCode}`);
    return response.data;
  },

  /**
   * Health check for the tariff service
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/tariff/health');
    return response.data;
  },

  /**
   * Get hierarchical tariff tree with lazy loading
   */
  async getTariffTree(
    sectionId: number, 
    depth: number = 2, 
    parentCode?: string
  ): Promise<TariffTreeResponse> {
    const params = new URLSearchParams();
    params.append('depth', depth.toString());
    if (parentCode) params.append('parent_code', parentCode);

    const response = await apiClient.get<TariffTreeResponse>(`/api/tariff/tree/${sectionId}?${params}`);
    return response.data;
  },

  /**
   * Search tariff codes by query string
   */
  async searchTariffCodes(
    query: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<{
    results: TariffCodeDetails[];
    total: number;
    limit: number;
    offset: number;
  }> {
    const params = new URLSearchParams();
    params.append('q', query);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await apiClient.get(`/api/tariff/search?${params}`);
    return response.data;
  },

  /**
   * Compare multiple tariff codes
   */
  async compareTariffCodes(hsCodes: string[]): Promise<{
    codes: Array<{
      hs_code: string;
      description: string;
      duty_rate: string;
      unit: string;
      fta_rates: FtaRate[];
    }>;
    comparison_matrix: Record<string, Record<string, string>>;
  }> {
    const response = await apiClient.post('/api/tariff/compare', {
      hs_codes: hsCodes
    });
    return response.data;
  },

  // Aliases for backward compatibility
  searchCodes: function(query: string, limit?: number, offset?: number) {
    return this.searchTariffCodes(query, limit, offset);
  },

  compareCodes: function(hsCodes: string[]) {
    return this.compareTariffCodes(hsCodes);
  },
};

export default tariffApi;
