// Main type definitions for the Customs Broker Portal
// These types match the backend API schemas

// Common API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Duty Calculator Types
export interface DutyCalculationRequest {
  hs_code: string;
  country_code: string;
  customs_value: number;
  quantity?: number;
  calculation_date?: string;
  currency?: string;
  description?: string;
}

export interface DutyComponent {
  duty_type: string;
  rate: number;
  amount: number;
  description: string;
  basis: string;
  applicable: boolean;
}

export interface DutyCalculationResult {
  hs_code: string;
  country_code: string;
  customs_value: number;
  total_duty: number;
  total_gst: number;
  total_amount: number;
  components: DutyComponent[];
  calculation_date: string;
  currency: string;
  exchange_rate?: number;
  warnings?: string[];
  notes?: string[];
}

// Tariff Types
export interface TariffRate {
  id: string;
  hs_code: string;
  description: string;
  general_rate: number;
  unit: string;
  effective_date: string;
  expiry_date?: string;
  conditions?: string[];
}

export interface FtaRate {
  id: string;
  hs_code: string;
  country_code: string;
  country_name: string;
  rate: number;
  unit: string;
  agreement_name: string;
  effective_date: string;
  expiry_date?: string;
  conditions?: string[];
  origin_criteria?: string;
}

// Search Types
export interface SearchQuery {
  query: string;
  search_type: 'hs_code' | 'description' | 'all';
  filters?: {
    country_code?: string;
    rate_type?: 'general' | 'fta' | 'all';
    effective_date?: string;
  };
  pagination?: {
    page: number;
    limit: number;
  };
}

export interface SearchResult {
  id: string;
  type: 'tariff' | 'fta' | 'classification';
  hs_code: string;
  description: string;
  rate?: number;
  unit?: string;
  country_code?: string;
  country_name?: string;
  relevance_score: number;
  highlighted_text?: string;
}

// Classification Types
export interface HsClassification {
  hs_code: string;
  description: string;
  level: number;
  parent_code?: string;
  children?: HsClassification[];
  statistical_suffix?: string;
  unit_of_quantity?: string;
}

// Form Types
export interface DutyCalculationForm {
  hsCode: string;
  countryCode: string;
  customsValue: string;
  quantity?: string;
  currency: string;
  description?: string;
}

export interface SearchForm {
  query: string;
  searchType: 'hs_code' | 'description' | 'all';
  countryCode?: string;
  rateType?: 'general' | 'fta' | 'all';
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: string[];
}

// Navigation Types
export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon?: string;
  children?: NavigationItem[];
}

// Country Types
export interface Country {
  code: string;
  name: string;
  region?: string;
  fta_agreements?: string[];
}

// All types are defined above and exported individually