// Portal Type Definitions
// Core types for the customer portal system

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  company: string;
  phone?: string;
  role: 'customer' | 'admin';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Job {
  id: string;
  jobNumber: string;
  customerId: string;
  title: string;
  description?: string;
  type: JobType;
  status: JobStatus;
  priority: JobPriority;
  
  // Shipment details
  origin: Location;
  destination: Location;
  estimatedArrival?: string;
  actualArrival?: string;
  
  // Financial
  totalValue: number;
  currency: string;
  estimatedDuties?: number;
  actualDuties?: number;
  
  // Documents
  documents: Document[];
  
  // Timeline
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  
  // Metadata
  metadata?: Record<string, any>;
}

export type JobType = 
  | 'import'
  | 'export'
  | 'transit'
  | 'warehouse'
  | 'consultation';

export type JobStatus = 
  | 'pending'
  | 'in_progress'
  | 'customs_review'
  | 'awaiting_payment'
  | 'completed'
  | 'cancelled'
  | 'on_hold';

export type JobPriority = 
  | 'low'
  | 'normal'
  | 'high'
  | 'urgent';

export interface Location {
  country: string;
  city: string;
  port?: string;
  address?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
}

export interface Document {
  id: string;
  jobId: string;
  name: string;
  type: DocumentType;
  url: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
  uploadedBy: string;
  status: DocumentStatus;
  metadata?: Record<string, any>;
}

export type DocumentType = 
  | 'invoice'
  | 'packing_list'
  | 'bill_of_lading'
  | 'certificate_of_origin'
  | 'customs_declaration'
  | 'permit'
  | 'insurance'
  | 'other';

export type DocumentStatus = 
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'requires_revision';

export interface Payment {
  id: string;
  jobId: string;
  customerId: string;
  amount: number;
  currency: string;
  type: PaymentType;
  status: PaymentStatus;
  method?: PaymentMethod;
  description: string;
  dueDate?: string;
  paidAt?: string;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

export type PaymentType = 
  | 'duties'
  | 'fees'
  | 'storage'
  | 'consultation'
  | 'other';

export type PaymentStatus = 
  | 'pending'
  | 'paid'
  | 'overdue'
  | 'cancelled'
  | 'refunded';

export type PaymentMethod = 
  | 'credit_card'
  | 'bank_transfer'
  | 'check'
  | 'cash'
  | 'other';

export interface Activity {
  id: string;
  jobId?: string;
  customerId: string;
  type: ActivityType;
  title: string;
  description: string;
  timestamp: string;
  actor: {
    id: string;
    name: string;
    type: 'user' | 'system' | 'broker';
  };
  metadata?: Record<string, any>;
}

export type ActivityType = 
  | 'job_created'
  | 'job_updated'
  | 'job_completed'
  | 'document_uploaded'
  | 'document_approved'
  | 'document_rejected'
  | 'payment_created'
  | 'payment_completed'
  | 'status_changed'
  | 'comment_added'
  | 'system_notification';

export interface SupportTicket {
  id: string;
  customerId: string;
  jobId?: string;
  subject: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;
  assignedTo?: string;
  messages: TicketMessage[];
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  metadata?: Record<string, any>;
}

export type TicketStatus = 
  | 'open'
  | 'in_progress'
  | 'waiting_customer'
  | 'resolved'
  | 'closed';

export type TicketPriority = 
  | 'low'
  | 'normal'
  | 'high'
  | 'urgent';

export type TicketCategory = 
  | 'general'
  | 'technical'
  | 'billing'
  | 'documentation'
  | 'customs'
  | 'shipping';

export interface TicketMessage {
  id: string;
  ticketId: string;
  content: string;
  author: {
    id: string;
    name: string;
    type: 'customer' | 'support' | 'system';
  };
  attachments?: Document[];
  createdAt: string;
  isInternal: boolean;
}

export interface Notification {
  id: string;
  customerId: string;
  jobId?: string;
  type: NotificationType;
  title: string;
  message: string;
  isRead: boolean;
  priority: NotificationPriority;
  actionUrl?: string;
  createdAt: string;
  readAt?: string;
  metadata?: Record<string, any>;
}

export type NotificationType = 
  | 'job_update'
  | 'payment_due'
  | 'document_required'
  | 'customs_clearance'
  | 'shipment_arrival'
  | 'system_maintenance'
  | 'general';

export type NotificationPriority = 
  | 'low'
  | 'normal'
  | 'high'
  | 'urgent';

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  pagination?: PaginationInfo;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface ListParams {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}

// Portal UI types
export interface SidebarItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: string | number;
  children?: SidebarItem[];
  isActive?: boolean;
  permissions?: string[];
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
  isActive?: boolean;
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
}

export interface FilterOption {
  label: string;
  value: string | number;
  count?: number;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  metadata?: Record<string, any>;
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'file' | 'date' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: string | number }[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    custom?: (value: any) => string | null;
  };
}

export interface FormData {
  [key: string]: any;
}

export interface FormErrors {
  [key: string]: string;
}

// Portal configuration
export interface PortalConfig {
  branding: {
    companyName: string;
    logo: string;
    primaryColor: string;
    secondaryColor: string;
  };
  features: {
    enablePayments: boolean;
    enableSupport: boolean;
    enableNotifications: boolean;
    enableDocumentUpload: boolean;
  };
  limits: {
    maxFileSize: number;
    maxFilesPerJob: number;
    supportedFileTypes: string[];
  };
  api: {
    baseUrl: string;
    timeout: number;
  };
}

// Error types
export interface PortalError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}