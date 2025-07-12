/**
 * Documents API service for the Customs Broker Portal.
 * 
 * This service provides comprehensive document management functionality including:
 * - File upload and storage
 * - Document metadata management
 * - Search and filtering
 * - Sharing and permissions
 * - Category management
 * - Bulk operations
 */

import axios from 'axios';
import type { AxiosProgressEvent } from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const DOCUMENTS_API_URL = `${API_BASE_URL}/api/documents`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: DOCUMENTS_API_URL,
  timeout: 30000, // 30 seconds for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// String literal types (replacing enums)
export type DocumentType = 
  | 'INVOICE'
  | 'PACKING_LIST'
  | 'BILL_OF_LADING'
  | 'CERTIFICATE_OF_ORIGIN'
  | 'COMMERCIAL_INVOICE'
  | 'CUSTOMS_DECLARATION'
  | 'IMPORT_PERMIT'
  | 'EXPORT_PERMIT'
  | 'INSURANCE_CERTIFICATE'
  | 'INSPECTION_CERTIFICATE'
  | 'PHYTOSANITARY_CERTIFICATE'
  | 'HEALTH_CERTIFICATE'
  | 'FUMIGATION_CERTIFICATE'
  | 'WEIGHT_CERTIFICATE'
  | 'QUALITY_CERTIFICATE'
  | 'DANGEROUS_GOODS_DECLARATION'
  | 'CARNET'
  | 'TEMPORARY_ADMISSION'
  | 'TRANSIT_DOCUMENT'
  | 'WAREHOUSE_RECEIPT'
  | 'DELIVERY_ORDER'
  | 'FREIGHT_INVOICE'
  | 'DUTY_PAYMENT_RECEIPT'
  | 'CUSTOMS_BOND'
  | 'POWER_OF_ATTORNEY'
  | 'CORRESPONDENCE'
  | 'INTERNAL_MEMO'
  | 'CLIENT_COMMUNICATION'
  | 'REGULATORY_NOTICE'
  | 'TARIFF_CLASSIFICATION'
  | 'VALUATION_DOCUMENT'
  | 'RULING_REQUEST'
  | 'RULING_RESPONSE'
  | 'AUDIT_DOCUMENT'
  | 'COMPLIANCE_REPORT'
  | 'TRAINING_MATERIAL'
  | 'PROCEDURE_DOCUMENT'
  | 'CONTRACT'
  | 'AGREEMENT'
  | 'OTHER';

export type DocumentCategory = 
  | 'IMPORT'
  | 'EXPORT'
  | 'TRANSIT'
  | 'WAREHOUSE'
  | 'COMPLIANCE'
  | 'FINANCIAL'
  | 'LEGAL'
  | 'OPERATIONAL'
  | 'REGULATORY'
  | 'CLIENT'
  | 'INTERNAL'
  | 'ARCHIVE';

export type DocumentStatus = 
  | 'DRAFT'
  | 'PENDING_REVIEW'
  | 'APPROVED'
  | 'REJECTED'
  | 'SUBMITTED'
  | 'PROCESSED'
  | 'ARCHIVED'
  | 'EXPIRED';

export type ComplianceStatus = 
  | 'NOT_APPLICABLE'
  | 'COMPLIANT'
  | 'NON_COMPLIANT'
  | 'NEEDS_REVIEW'
  | 'PENDING_VERIFICATION'
  | 'VERIFIED'
  | 'REJECTED';

export type SharePermission = 
  | 'VIEW'
  | 'COMMENT'
  | 'EDIT'
  | 'ADMIN';

// Type definitions
export interface Document {
  id: number;
  filename: string;
  original_name: string;
  title?: string;
  description?: string;
  document_type: DocumentType;
  category: DocumentCategory;
  status: DocumentStatus;
  file_size: number;
  file_size_mb: number;
  mime_type: string;
  file_hash?: string;
  version: number;
  parent_document_id?: number;
  
  // Business context
  client_id?: string;
  client_name?: string;
  hs_code?: string;
  shipment_ref?: string;
  
  // Tags and metadata
  tags: string[];
  metadata: Record<string, any>;
  
  // Compliance
  is_confidential: boolean;
  compliance_status: ComplianceStatus;
  compliance_notes?: string;
  
  // Dates
  upload_date: string;
  last_accessed?: string;
  expiry_date?: string;
  
  // Users
  uploaded_by: string;
  last_modified_by?: string;
  
  // Status
  is_active: boolean;
  created_at: string;
  updated_at: string;
  
  // Computed properties
  is_expired: boolean;
  is_expiring_soon: boolean;
  display_name: string;
}

export interface DocumentSummary {
  id: number;
  filename: string;
  original_name: string;
  title?: string;
  document_type: DocumentType;
  category: DocumentCategory;
  status: DocumentStatus;
  file_size: number;
  file_size_mb: number;
  upload_date: string;
  uploaded_by: string;
  is_confidential: boolean;
  compliance_status: ComplianceStatus;
  display_name: string;
}

export interface DocumentUploadData {
  title?: string;
  description?: string;
  document_type: DocumentType;
  category: DocumentCategory;
  client_id?: string;
  client_name?: string;
  hs_code?: string;
  shipment_ref?: string;
  tags?: string[];
  is_confidential?: boolean;
  compliance_status?: ComplianceStatus;
  compliance_notes?: string;
  expiry_date?: string;
}

export interface DocumentUpdateData {
  title?: string;
  description?: string;
  document_type?: DocumentType;
  category?: DocumentCategory;
  status?: DocumentStatus;
  client_id?: string;
  client_name?: string;
  hs_code?: string;
  shipment_ref?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  is_confidential?: boolean;
  compliance_status?: ComplianceStatus;
  compliance_notes?: string;
  expiry_date?: string;
}

export interface DocumentSearchParams {
  query?: string;
  page?: number;
  limit?: number;
  document_type?: DocumentType;
  category?: DocumentCategory;
  status?: DocumentStatus;
  compliance_status?: ComplianceStatus;
  client_id?: string;
  client_name?: string;
  hs_code?: string;
  shipment_ref?: string;
  is_confidential?: boolean;
  is_expired?: boolean;
  is_expiring_soon?: boolean;
  uploaded_by?: string;
  upload_date_from?: string;
  upload_date_to?: string;
  tags?: string[];
}

export interface DocumentListParams {
  page?: number;
  limit?: number;
  document_type?: DocumentType;
  category?: DocumentCategory;
  status?: DocumentStatus;
  compliance_status?: ComplianceStatus;
  client_id?: string;
  is_confidential?: boolean;
  uploaded_by?: string;
  search?: string;
  sort_by?: 'upload_date' | 'title' | 'file_size' | 'status';
  sort_order?: 'asc' | 'desc';
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface DocumentListResponse {
  documents: DocumentSummary[];
  pagination: PaginationMeta;
  filters?: Record<string, any>;
  total_count: number;
}

export interface DocumentSearchResult extends DocumentSummary {
  relevance_score: number;
  match_type: string;
  highlighted_text?: string;
}

export interface DocumentSearchResponse {
  results: DocumentSearchResult[];
  pagination: PaginationMeta;
  query?: string;
  filters?: Record<string, any>;
  total_results: number;
  search_time_ms: number;
}

export interface DocumentUploadResponse {
  success: boolean;
  document_id: number;
  filename: string;
  original_name: string;
  file_size: number;
  upload_url?: string;
  message: string;
}

export interface DocumentStats {
  total_documents: number;
  total_size_bytes: number;
  total_size_mb: number;
  total_size_gb: number;
  documents_by_type: Record<string, number>;
  documents_by_category: Record<string, number>;
  documents_by_status: Record<string, number>;
  documents_by_compliance: Record<string, number>;
  pending_review: number;
  expiring_this_month: number;
  compliance_issues: number;
  recent_uploads: number;
  top_uploaders: Array<{ user: string; count: number }>;
  storage_by_type: Record<string, number>;
}

export interface DocumentCategoryData {
  id: number;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  parent_category_id?: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  document_count?: number;
  child_categories?: DocumentCategoryData[];
}

export interface DocumentShare {
  id: number;
  document_id: number;
  shared_with_user?: string;
  shared_with_group?: string;
  shared_with_email?: string;
  permission: SharePermission;
  can_download: boolean;
  can_share: boolean;
  expires_at?: string;
  access_count: number;
  max_access_count?: number;
  shared_by: string;
  last_accessed?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  is_expired: boolean;
  is_access_limit_reached: boolean;
  can_access: boolean;
}

export interface BulkOperationResponse {
  success: boolean;
  processed_count: number;
  success_count: number;
  error_count: number;
  errors: Array<{ document_id: number; error: string }>;
  message: string;
}

// API Service Class
export class DocumentsApiService {
  /**
   * Upload a new document
   */
  static async uploadDocument(
    file: File,
    metadata: DocumentUploadData,
    onProgress?: (progress: number) => void
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add metadata fields
    Object.entries(metadata).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (key === 'tags' && Array.isArray(value)) {
          formData.append(key, JSON.stringify(value));
        } else {
          formData.append(key, String(value));
        }
      }
    });

    const response = await apiClient.post<DocumentUploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  }

  /**
   * Get list of documents with filtering and pagination
   */
  static async getDocuments(params: DocumentListParams = {}): Promise<DocumentListResponse> {
    const response = await apiClient.get<DocumentListResponse>('/', { params });
    return response.data;
  }

  /**
   * Get a specific document by ID
   */
  static async getDocument(documentId: number): Promise<Document> {
    const response = await apiClient.get<Document>(`/${documentId}`);
    return response.data;
  }

  /**
   * Update document metadata
   */
  static async updateDocument(documentId: number, updateData: DocumentUpdateData): Promise<Document> {
    const response = await apiClient.put<Document>(`/${documentId}`, updateData);
    return response.data;
  }

  /**
   * Delete a document (soft delete by default)
   */
  static async deleteDocument(documentId: number, permanent: boolean = false): Promise<{ message: string }> {
    const response = await apiClient.delete(`/${documentId}`, {
      params: { permanent }
    });
    return response.data;
  }

  /**
   * Download a document file
   */
  static async downloadDocument(documentId: number, inline: boolean = false): Promise<Blob> {
    const response = await apiClient.get(`/${documentId}/download`, {
      params: { inline },
      responseType: 'blob'
    });
    return response.data;
  }

  /**
   * Get download URL for a document
   */
  static getDownloadUrl(documentId: number, inline: boolean = false): string {
    const params = inline ? '?inline=true' : '';
    return `${DOCUMENTS_API_URL}/${documentId}/download${params}`;
  }

  /**
   * Search documents with advanced filtering
   */
  static async searchDocuments(searchParams: DocumentSearchParams): Promise<DocumentSearchResponse> {
    const response = await apiClient.post<DocumentSearchResponse>('/search', searchParams);
    return response.data;
  }

  /**
   * Get document statistics and analytics
   */
  static async getDocumentStats(): Promise<DocumentStats> {
    const response = await apiClient.get<DocumentStats>('/stats');
    return response.data;
  }

  /**
   * Perform bulk operations on documents
   */
  static async bulkOperation(
    documentIds: number[],
    operation: string,
    parameters?: Record<string, any>
  ): Promise<BulkOperationResponse> {
    const response = await apiClient.post<BulkOperationResponse>('/bulk', {
      document_ids: documentIds,
      operation,
      parameters
    });
    return response.data;
  }

  /**
   * Get document categories
   */
  static async getCategories(includeInactive: boolean = false): Promise<DocumentCategoryData[]> {
    const response = await apiClient.get<DocumentCategoryData[]>('/categories', {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  }

  /**
   * Create a new document category
   */
  static async createCategory(categoryData: {
    name: string;
    description?: string;
    color?: string;
    icon?: string;
    parent_category_id?: number;
    sort_order?: number;
  }): Promise<DocumentCategoryData> {
    const response = await apiClient.post<DocumentCategoryData>('/categories', categoryData);
    return response.data;
  }

  /**
   * Share a document
   */
  static async shareDocument(
    documentId: number,
    shareData: {
      shared_with_user?: string;
      shared_with_group?: string;
      shared_with_email?: string;
      permission: SharePermission;
      can_download?: boolean;
      can_share?: boolean;
      expires_at?: string;
      max_access_count?: number;
    }
  ): Promise<DocumentShare> {
    const response = await apiClient.post<DocumentShare>(`/${documentId}/share`, shareData);
    return response.data;
  }

  /**
   * Get document shares
   */
  static async getDocumentShares(documentId: number): Promise<DocumentShare[]> {
    const response = await apiClient.get<DocumentShare[]>(`/${documentId}/shares`);
    return response.data;
  }

  /**
   * Revoke a document share
   */
  static async revokeShare(shareId: number): Promise<{ message: string }> {
    const response = await apiClient.delete(`/shares/${shareId}`);
    return response.data;
  }

  /**
   * Bulk delete documents
   */
  static async bulkDelete(documentIds: number[]): Promise<BulkOperationResponse> {
    return this.bulkOperation(documentIds, 'delete');
  }

  /**
   * Bulk update document status
   */
  static async bulkUpdateStatus(documentIds: number[], status: DocumentStatus): Promise<BulkOperationResponse> {
    return this.bulkOperation(documentIds, 'update_status', { status });
  }

  /**
   * Bulk update document category
   */
  static async bulkUpdateCategory(documentIds: number[], category: DocumentCategory): Promise<BulkOperationResponse> {
    return this.bulkOperation(documentIds, 'update_category', { category });
  }
}

// Export default instance
export default DocumentsApiService;

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getDocumentTypeLabel = (type: DocumentType): string => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
};

export const getCategoryLabel = (category: DocumentCategory): string => {
  return category.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
};

export const getStatusLabel = (status: DocumentStatus): string => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
};

export const getComplianceStatusLabel = (status: ComplianceStatus): string => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
};

export const isDocumentExpired = (expiryDate?: string): boolean => {
  if (!expiryDate) return false;
  return new Date(expiryDate) < new Date();
};

export const isDocumentExpiringSoon = (expiryDate?: string, days: number = 30): boolean => {
  if (!expiryDate) return false;
  const expiry = new Date(expiryDate);
  const threshold = new Date();
  threshold.setDate(threshold.getDate() + days);
  return expiry <= threshold && expiry >= new Date();
};