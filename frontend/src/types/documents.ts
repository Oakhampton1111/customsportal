export interface Document {
  id: number;
  filename: string;
  original_name: string;
  title: string;
  description?: string;
  document_type: DocumentType;
  category: DocumentCategory;
  file_size: number;
  mime_type: string;
  file_hash: string;
  client_id?: string;
  client_name?: string;
  hs_code?: string;
  shipment_ref?: string;
  tags: string[];
  is_confidential: boolean;
  compliance_status: ComplianceStatus;
  compliance_notes?: string;
  expiry_date?: string;
  uploaded_by: string;
  upload_date: string;
  last_accessed?: string;
  last_modified_by?: string;
  updated_at: string;
  status: DocumentStatus;
  is_active: boolean;
}

export const DocumentType = {
  INVOICE: "invoice",
  PACKING_LIST: "packing_list",
  CERTIFICATE: "certificate",
  PERMIT: "permit",
  DECLARATION: "declaration",
  CORRESPONDENCE: "correspondence",
  REPORT: "report",
  OTHER: "other"
} as const;

export type DocumentType = typeof DocumentType[keyof typeof DocumentType];

export const DocumentCategory = {
  IMPORT: "import",
  EXPORT: "export",
  COMPLIANCE: "compliance",
  FINANCIAL: "financial",
  LEGAL: "legal",
  OPERATIONAL: "operational",
  ARCHIVE: "archive"
} as const;

export type DocumentCategory = typeof DocumentCategory[keyof typeof DocumentCategory];

export const DocumentStatus = {
  DRAFT: "draft",
  PENDING: "pending",
  APPROVED: "approved",
  REJECTED: "rejected",
  ARCHIVED: "archived"
} as const;

export type DocumentStatus = typeof DocumentStatus[keyof typeof DocumentStatus];

export const ComplianceStatus = {
  COMPLIANT: "compliant",
  NON_COMPLIANT: "non_compliant",
  PENDING_REVIEW: "pending_review",
  NOT_APPLICABLE: "not_applicable"
} as const;

export type ComplianceStatus = typeof ComplianceStatus[keyof typeof ComplianceStatus];

export interface DocumentUploadRequest {
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

export interface DocumentUploadResponse {
  document_id: number;
  filename: string;
  original_name: string;
  file_size: number;
  upload_url: string;
}

export interface DocumentSearchParams {
  query?: string;
  document_type?: DocumentType;
  category?: DocumentCategory;
  status?: DocumentStatus;
  compliance_status?: ComplianceStatus;
  client_id?: string;
  client_name?: string;
  hs_code?: string;
  shipment_ref?: string;
  is_confidential?: boolean;
  uploaded_by?: string;
  upload_date_from?: string;
  upload_date_to?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}

export interface DocumentStats {
  total_documents: number;
  total_size_bytes: number;
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