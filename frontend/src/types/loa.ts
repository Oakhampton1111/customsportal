export interface DigitalLOA {
  id: number;
  loa_number: string;
  customer_id: string;
  company_name: string;
  company_abn: string;
  authorized_person_name: string;
  authorized_person_title: string;
  authorized_person_email: string;
  authorized_person_phone?: string;
  customs_broker_license: string;
  authority_scope: string;
  reference_number?: string;
  loa_content: string;
  status: LOAStatus;
  created_at: string;
  updated_at: string;
  signed_at?: string;
  signed_by?: string;
  signature_data?: string;
  verification_code?: string;
  signed_pdf_path?: string;
  expires_at?: string;
  revoked_at?: string;
  revoked_by?: string;
  revocation_reason?: string;
  audit_trail: LOAAuditEntry[];
}

export const LOAStatus = {
  DRAFT: "draft",
  SIGNED: "signed",
  ACTIVE: "active",
  REVOKED: "revoked",
  EXPIRED: "expired"
} as const;

export type LOAStatus = typeof LOAStatus[keyof typeof LOAStatus];

export interface LOAAuditEntry {
  id: number;
  action: string;
  actor_name: string;
  actor_type: string;
  timestamp: string;
  details?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
}

export interface LOACreateRequest {
  company_name: string;
  company_abn: string;
  authorized_person_name: string;
  authorized_person_title: string;
  authorized_person_email: string;
  authorized_person_phone?: string;
  customs_broker_license: string;
  authority_scope: string;
  reference_number?: string;
  loa_content?: string;
}

export interface LOAUpdateRequest {
  company_name?: string;
  company_abn?: string;
  authorized_person_name?: string;
  authorized_person_title?: string;
  authorized_person_email?: string;
  authorized_person_phone?: string;
  customs_broker_license?: string;
  authority_scope?: string;
  reference_number?: string;
  loa_content?: string;
}

export interface LOASignRequest {
  signature_method: string;
  signature_data: string;
  certificate_data?: string;
  timestamp: string;
}

export interface LOAVerificationRequest {
  loa_number: string;
  verification_code: string;
}

export interface LOAVerificationResponse {
  valid: boolean;
  loa_number?: string;
  company_name?: string;
  authorized_person_name?: string;
  status?: string;
  signed_at?: string;
  expires_at?: string;
  verification_timestamp: string;
  error?: string;
}

export interface LOATemplate {
  id: number;
  template_name: string;
  template_code: string;
  description: string;
  template_content: string;
  legal_text: string;
  terms_conditions?: string;
  required_fields: string[];
  optional_fields: string[];
  is_active: boolean;
  is_default: boolean;
  version: string;
  created_at: string;
}

export interface LOAStats {
  total_loas: number;
  draft_count: number;
  signed_count: number;
  active_count: number;
  revoked_count: number;
  expired_count: number;
}