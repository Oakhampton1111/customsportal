export interface EDIJob {
  id: number;
  job_number: string;
  job_type: string;
  status: JobStatus;
  consignment_reference: string;
  cargo_description: string;
  port_of_discharge: string;
  estimated_arrival?: string;
  vessel_voyage?: string;
  port_of_loading?: string;
  total_packages?: number;
  total_weight_kg?: string;
  total_value_aud?: string;
  clearance_deadline?: string;
  priority: string;
  customer_id: string;
  created_at: string;
  updated_at: string;
}

export const JobStatus = {
  REGISTERED: "registered",
  IN_PROGRESS: "in_progress",
  PENDING_DOCUMENTS: "pending_documents",
  UNDER_EXAMINATION: "under_examination",
  CLEARED: "cleared",
  DELIVERED: "delivered",
  CANCELLED: "cancelled"
} as const;

export type JobStatus = typeof JobStatus[keyof typeof JobStatus];

export interface JobRegistrationRequest {
  job_type: string;
  consignment_reference: string;
  cargo_description: string;
  port_of_discharge: string;
  estimated_arrival?: string;
  vessel_voyage?: string;
  port_of_loading?: string;
  total_packages?: number;
  total_weight_kg?: string;
  total_value_aud?: string;
  clearance_deadline?: string;
  priority?: string;
}

export interface CustomsDeclaration {
  id: number;
  declaration_number: string;
  declaration_type: DeclarationType;
  status: DeclarationStatus;
  job_id: number;
  consignment_reference: string;
  importer_name: string;
  importer_abn?: string;
  exporter_name?: string;
  exporter_address?: string;
  total_invoice_value: string;
  currency: string;
  vessel_name?: string;
  voyage_number?: string;
  port_of_loading?: string;
  port_of_discharge?: string;
  commercial_reference?: string;
  submitted_at?: string;
  assessed_at?: string;
  cleared_at?: string;
  created_at: string;
  declaration_items: DeclarationItem[];
}

export const DeclarationType = {
  IMPORT: "import",
  EXPORT: "export",
  TRANSIT: "transit",
  WAREHOUSE: "warehouse"
} as const;

export type DeclarationType = typeof DeclarationType[keyof typeof DeclarationType];

export const DeclarationStatus = {
  DRAFT: "draft",
  SUBMITTED: "submitted",
  UNDER_ASSESSMENT: "under_assessment",
  ASSESSED: "assessed",
  CLEARED: "cleared",
  REJECTED: "rejected"
} as const;

export type DeclarationStatus = typeof DeclarationStatus[keyof typeof DeclarationStatus];

export interface DeclarationItem {
  id: number;
  declaration_id: number;
  item_number: number;
  description: string;
  hs_code: string;
  country_of_origin: string;
  quantity: string;
  unit_of_measure: string;
  unit_price: string;
  total_value: string;
  currency: string;
  net_weight_kg?: string;
  gross_weight_kg?: string;
  duty_rate?: string;
  duty_amount?: string;
  gst_amount?: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  is_examined: boolean;
  examination_notes?: string;
}

export interface DeclarationRequest {
  job_id: number;
  declaration_type: string;
  importer_name: string;
  importer_abn?: string;
  exporter_name?: string;
  exporter_address?: string;
  total_invoice_value: string;
  currency?: string;
  vessel_name?: string;
  voyage_number?: string;
  port_of_loading?: string;
  commercial_reference?: string;
}

export interface DeclarationItemRequest {
  item_number: number;
  description: string;
  hs_code: string;
  country_of_origin: string;
  quantity: string;
  unit_of_measure: string;
  unit_price: string;
  currency?: string;
  net_weight_kg?: string;
  gross_weight_kg?: string;
  brand?: string;
  model?: string;
  serial_number?: string;
}

export interface EDIMessage {
  id: number;
  message_id: string;
  message_type: EDIMessageType;
  direction: MessageDirection;
  status: EDIMessageStatus;
  job_id?: number;
  declaration_id?: number;
  customer_id?: string;
  raw_message: string;
  parsed_data?: Record<string, any>;
  received_at: string;
  processed_at?: string;
  error_message?: string;
  external_reference?: string;
}

export const EDIMessageType = {
  CUSCAR: "CUSCAR",
  CUSRES: "CUSRES",
  CUSDEC: "CUSDEC",
  CUSREP: "CUSREP",
  APERAK: "APERAK"
} as const;

export type EDIMessageType = typeof EDIMessageType[keyof typeof EDIMessageType];

export const MessageDirection = {
  INBOUND: "inbound",
  OUTBOUND: "outbound"
} as const;

export type MessageDirection = typeof MessageDirection[keyof typeof MessageDirection];

export const EDIMessageStatus = {
  RECEIVED: "received",
  PROCESSING: "processing",
  PROCESSED: "processed",
  ERROR: "error",
  ACKNOWLEDGED: "acknowledged"
} as const;

export type EDIMessageStatus = typeof EDIMessageStatus[keyof typeof EDIMessageStatus];

export interface JobStatusResponse {
  job: EDIJob;
  messages: EDIMessage[];
  declarations: CustomsDeclaration[];
}