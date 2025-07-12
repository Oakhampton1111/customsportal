// Documents Service for Portal
// Handles all document-related API operations

import { portalApi } from './api';
import type { 
  Document, 
  DocumentType, 
  DocumentStatus,
  ApiResponse, 
  ListParams,
  PaginationInfo 
} from '../../types/portal';

export interface DocumentsListParams extends ListParams {
  jobId?: string;
  type?: DocumentType;
  status?: DocumentStatus;
  dateFrom?: string;
  dateTo?: string;
}

export interface UploadDocumentData {
  jobId: string;
  name: string;
  type: DocumentType;
  file: File;
  metadata?: Record<string, any>;
}

export interface UpdateDocumentData {
  name?: string;
  type?: DocumentType;
  metadata?: Record<string, any>;
}

export class DocumentsService {
  /**
   * Get list of documents for the current customer
   */
  async getDocuments(params: DocumentsListParams = {}): Promise<ApiResponse<Document[]> & { pagination: PaginationInfo }> {
    const queryParams = {
      ...params,
      ...(params.jobId && { jobId: params.jobId }),
      ...(params.type && { type: params.type }),
      ...(params.status && { status: params.status }),
      ...(params.dateFrom && { dateFrom: params.dateFrom }),
      ...(params.dateTo && { dateTo: params.dateTo }),
    };

    return portalApi.getList<Document>('/portal/documents', queryParams);
  }

  /**
   * Get a specific document by ID
   */
  async getDocument(documentId: string): Promise<ApiResponse<Document>> {
    return portalApi.get<Document>(`/portal/documents/${documentId}`);
  }

  /**
   * Upload a new document
   */
  async uploadDocument(data: UploadDocumentData): Promise<ApiResponse<Document>> {
    const additionalData = {
      jobId: data.jobId,
      name: data.name,
      type: data.type,
      ...(data.metadata && { metadata: JSON.stringify(data.metadata) }),
    };

    return portalApi.upload<Document>('/portal/documents/upload', data.file, additionalData);
  }

  /**
   * Update document metadata
   */
  async updateDocument(documentId: string, data: UpdateDocumentData): Promise<ApiResponse<Document>> {
    return portalApi.patch<Document>(`/portal/documents/${documentId}`, data);
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: string): Promise<ApiResponse<void>> {
    return portalApi.delete(`/portal/documents/${documentId}`);
  }

  /**
   * Download a document
   */
  async downloadDocument(documentId: string): Promise<ApiResponse<{
    url: string;
    filename: string;
    expiresAt: string;
  }>> {
    return portalApi.get(`/portal/documents/${documentId}/download`);
  }

  /**
   * Get document preview URL
   */
  async getDocumentPreview(documentId: string): Promise<ApiResponse<{
    previewUrl: string;
    expiresAt: string;
  }>> {
    return portalApi.get(`/portal/documents/${documentId}/preview`);
  }

  /**
   * Get documents for a specific job
   */
  async getJobDocuments(jobId: string): Promise<ApiResponse<Document[]>> {
    return portalApi.get<Document[]>(`/portal/jobs/${jobId}/documents`);
  }

  /**
   * Get document statistics
   */
  async getDocumentStats(): Promise<ApiResponse<{
    total: number;
    byType: Record<DocumentType, number>;
    byStatus: Record<DocumentStatus, number>;
    totalSize: number;
    recentUploads: number;
  }>> {
    return portalApi.get('/portal/documents/stats');
  }

  /**
   * Search documents
   */
  async searchDocuments(query: string, filters?: {
    type?: DocumentType[];
    status?: DocumentStatus[];
    jobId?: string;
    dateRange?: {
      from: string;
      to: string;
    };
  }): Promise<ApiResponse<Document[]>> {
    const params = {
      q: query,
      ...(filters?.type && { type: filters.type.join(',') }),
      ...(filters?.status && { status: filters.status.join(',') }),
      ...(filters?.jobId && { jobId: filters.jobId }),
      ...(filters?.dateRange && {
        dateFrom: filters.dateRange.from,
        dateTo: filters.dateRange.to,
      }),
    };

    return portalApi.get<Document[]>('/portal/documents/search', params);
  }

  /**
   * Get documents that need attention (pending approval, rejected, etc.)
   */
  async getDocumentsNeedingAttention(): Promise<ApiResponse<Document[]>> {
    return portalApi.get<Document[]>('/portal/documents/needs-attention');
  }

  /**
   * Request document review
   */
  async requestDocumentReview(documentId: string, message?: string): Promise<ApiResponse<void>> {
    return portalApi.post(`/portal/documents/${documentId}/request-review`, { message });
  }

  /**
   * Get supported file types and size limits
   */
  async getUploadLimits(): Promise<ApiResponse<{
    maxFileSize: number;
    maxFilesPerJob: number;
    supportedTypes: string[];
    supportedExtensions: string[];
  }>> {
    return portalApi.get('/portal/documents/upload-limits');
  }

  /**
   * Bulk upload documents
   */
  async bulkUploadDocuments(uploads: Array<{
    jobId: string;
    name: string;
    type: DocumentType;
    file: File;
    metadata?: Record<string, any>;
  }>): Promise<ApiResponse<{
    successful: Document[];
    failed: Array<{
      filename: string;
      error: string;
    }>;
  }>> {
    // For bulk upload, we'll upload files one by one for now
    // In a real implementation, this would be a single multipart request
    const results = {
      successful: [] as Document[],
      failed: [] as Array<{ filename: string; error: string; }>,
    };

    for (const upload of uploads) {
      try {
        const response = await this.uploadDocument(upload);
        if (response.success && response.data) {
          results.successful.push(response.data);
        } else {
          results.failed.push({
            filename: upload.file.name,
            error: response.error || 'Upload failed',
          });
        }
      } catch (error) {
        results.failed.push({
          filename: upload.file.name,
          error: error instanceof Error ? error.message : 'Upload failed',
        });
      }
    }

    return {
      success: true,
      data: results,
    };
  }

  /**
   * Get document sharing link
   */
  async createSharingLink(documentId: string, options?: {
    expiresIn?: number; // hours
    password?: string;
    allowDownload?: boolean;
  }): Promise<ApiResponse<{
    shareUrl: string;
    expiresAt: string;
    shareId: string;
  }>> {
    return portalApi.post(`/portal/documents/${documentId}/share`, options);
  }

  /**
   * Revoke document sharing link
   */
  async revokeSharingLink(documentId: string, shareId: string): Promise<ApiResponse<void>> {
    return portalApi.delete(`/portal/documents/${documentId}/share/${shareId}`);
  }

  /**
   * Get document version history
   */
  async getDocumentVersions(documentId: string): Promise<ApiResponse<Array<{
    id: string;
    version: number;
    uploadedAt: string;
    uploadedBy: string;
    size: number;
    changes: string;
  }>>> {
    return portalApi.get(`/portal/documents/${documentId}/versions`);
  }

  /**
   * Upload new version of existing document
   */
  async uploadDocumentVersion(documentId: string, file: File, changes: string): Promise<ApiResponse<Document>> {
    return portalApi.upload(`/portal/documents/${documentId}/versions`, file, { changes });
  }
}

// Create and export default instance
export const documentsService = new DocumentsService();
export default DocumentsService;