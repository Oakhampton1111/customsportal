// Payments Service for Portal
// Handles all payment-related API operations

import { portalApi } from './api';
import type { 
  Payment, 
  PaymentType, 
  PaymentStatus,
  PaymentMethod,
  ApiResponse, 
  ListParams,
  PaginationInfo 
} from '../../types/portal';

export interface PaymentsListParams extends ListParams {
  jobId?: string;
  type?: PaymentType;
  status?: PaymentStatus;
  method?: PaymentMethod;
  dateFrom?: string;
  dateTo?: string;
  dueDateFrom?: string;
  dueDateTo?: string;
}

export interface CreatePaymentData {
  jobId: string;
  amount: number;
  currency: string;
  type: PaymentType;
  description: string;
  dueDate?: string;
  metadata?: Record<string, any>;
}

export interface ProcessPaymentData {
  paymentId: string;
  method: PaymentMethod;
  paymentDetails?: {
    cardToken?: string;
    bankAccount?: string;
    checkNumber?: string;
    reference?: string;
  };
}

export interface PaymentSummary {
  totalPaid: number;
  totalPending: number;
  totalOverdue: number;
  currency: string;
  byType: Record<PaymentType, number>;
  byStatus: Record<PaymentStatus, number>;
  recentPayments: number;
}

export class PaymentsService {
  /**
   * Get list of payments for the current customer
   */
  async getPayments(params: PaymentsListParams = {}): Promise<ApiResponse<Payment[]> & { pagination: PaginationInfo }> {
    const queryParams = {
      ...params,
      ...(params.jobId && { jobId: params.jobId }),
      ...(params.type && { type: params.type }),
      ...(params.status && { status: params.status }),
      ...(params.method && { method: params.method }),
      ...(params.dateFrom && { dateFrom: params.dateFrom }),
      ...(params.dateTo && { dateTo: params.dateTo }),
      ...(params.dueDateFrom && { dueDateFrom: params.dueDateFrom }),
      ...(params.dueDateTo && { dueDateTo: params.dueDateTo }),
    };

    return portalApi.getList<Payment>('/portal/payments', queryParams);
  }

  /**
   * Get a specific payment by ID
   */
  async getPayment(paymentId: string): Promise<ApiResponse<Payment>> {
    return portalApi.get<Payment>(`/portal/payments/${paymentId}`);
  }

  /**
   * Create a new payment request
   */
  async createPayment(data: CreatePaymentData): Promise<ApiResponse<Payment>> {
    return portalApi.post<Payment>('/portal/payments', data);
  }

  /**
   * Process a payment
   */
  async processPayment(data: ProcessPaymentData): Promise<ApiResponse<{
    payment: Payment;
    transactionId: string;
    status: 'success' | 'pending' | 'failed';
    message: string;
  }>> {
    return portalApi.post(`/portal/payments/${data.paymentId}/process`, {
      method: data.method,
      paymentDetails: data.paymentDetails,
    });
  }

  /**
   * Cancel a payment
   */
  async cancelPayment(paymentId: string, reason?: string): Promise<ApiResponse<Payment>> {
    return portalApi.patch<Payment>(`/portal/payments/${paymentId}/cancel`, { reason });
  }

  /**
   * Get payment statistics for dashboard
   */
  async getPaymentStats(): Promise<ApiResponse<PaymentSummary>> {
    return portalApi.get('/portal/payments/stats');
  }

  /**
   * Get payments for a specific job
   */
  async getJobPayments(jobId: string): Promise<ApiResponse<Payment[]>> {
    return portalApi.get<Payment[]>(`/portal/jobs/${jobId}/payments`);
  }

  /**
   * Get overdue payments
   */
  async getOverduePayments(): Promise<ApiResponse<Payment[]>> {
    return portalApi.get<Payment[]>('/portal/payments/overdue');
  }

  /**
   * Get upcoming payments (due soon)
   */
  async getUpcomingPayments(days: number = 7): Promise<ApiResponse<Payment[]>> {
    return portalApi.get<Payment[]>('/portal/payments/upcoming', { days });
  }

  /**
   * Search payments
   */
  async searchPayments(query: string, filters?: {
    type?: PaymentType[];
    status?: PaymentStatus[];
    jobId?: string;
    dateRange?: {
      from: string;
      to: string;
    };
  }): Promise<ApiResponse<Payment[]>> {
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

    return portalApi.get<Payment[]>('/portal/payments/search', params);
  }

  /**
   * Get payment methods available for customer
   */
  async getPaymentMethods(): Promise<ApiResponse<Array<{
    method: PaymentMethod;
    label: string;
    enabled: boolean;
    fees?: {
      fixed?: number;
      percentage?: number;
      currency: string;
    };
    limits?: {
      min?: number;
      max?: number;
      currency: string;
    };
  }>>> {
    return portalApi.get('/portal/payments/methods');
  }

  /**
   * Get payment history for a date range
   */
  async getPaymentHistory(dateFrom: string, dateTo: string): Promise<ApiResponse<{
    payments: Payment[];
    summary: {
      totalAmount: number;
      totalCount: number;
      averageAmount: number;
      currency: string;
      byMonth: Array<{
        month: string;
        amount: number;
        count: number;
      }>;
    };
  }>> {
    return portalApi.get('/portal/payments/history', { dateFrom, dateTo });
  }

  /**
   * Request payment plan for large amounts
   */
  async requestPaymentPlan(paymentId: string, plan: {
    installments: number;
    frequency: 'weekly' | 'monthly';
    startDate: string;
    reason?: string;
  }): Promise<ApiResponse<{
    planId: string;
    installments: Array<{
      amount: number;
      dueDate: string;
      description: string;
    }>;
    status: 'pending_approval' | 'approved' | 'rejected';
  }>> {
    return portalApi.post(`/portal/payments/${paymentId}/payment-plan`, plan);
  }

  /**
   * Get payment receipts
   */
  async getPaymentReceipt(paymentId: string): Promise<ApiResponse<{
    receiptUrl: string;
    receiptNumber: string;
    expiresAt: string;
  }>> {
    return portalApi.get(`/portal/payments/${paymentId}/receipt`);
  }

  /**
   * Download payment invoice
   */
  async downloadInvoice(paymentId: string): Promise<ApiResponse<{
    invoiceUrl: string;
    invoiceNumber: string;
    expiresAt: string;
  }>> {
    return portalApi.get(`/portal/payments/${paymentId}/invoice`);
  }

  /**
   * Set up automatic payment for recurring charges
   */
  async setupAutoPay(data: {
    jobId?: string;
    paymentMethod: PaymentMethod;
    paymentDetails: {
      cardToken?: string;
      bankAccount?: string;
    };
    maxAmount?: number;
    enabled: boolean;
  }): Promise<ApiResponse<{
    autoPayId: string;
    status: 'active' | 'inactive';
    nextPaymentDate?: string;
  }>> {
    return portalApi.post('/portal/payments/autopay', data);
  }

  /**
   * Get auto-pay settings
   */
  async getAutoPaySettings(): Promise<ApiResponse<Array<{
    id: string;
    jobId?: string;
    paymentMethod: PaymentMethod;
    maxAmount?: number;
    enabled: boolean;
    createdAt: string;
    lastPaymentAt?: string;
    nextPaymentDate?: string;
  }>>> {
    return portalApi.get('/portal/payments/autopay');
  }

  /**
   * Update auto-pay settings
   */
  async updateAutoPay(autoPayId: string, updates: {
    enabled?: boolean;
    maxAmount?: number;
    paymentMethod?: PaymentMethod;
  }): Promise<ApiResponse<void>> {
    return portalApi.patch(`/portal/payments/autopay/${autoPayId}`, updates);
  }

  /**
   * Delete auto-pay setup
   */
  async deleteAutoPay(autoPayId: string): Promise<ApiResponse<void>> {
    return portalApi.delete(`/portal/payments/autopay/${autoPayId}`);
  }

  /**
   * Get payment disputes
   */
  async getPaymentDisputes(): Promise<ApiResponse<Array<{
    id: string;
    paymentId: string;
    reason: string;
    status: 'open' | 'investigating' | 'resolved' | 'closed';
    amount: number;
    currency: string;
    createdAt: string;
    resolvedAt?: string;
  }>>> {
    return portalApi.get('/portal/payments/disputes');
  }

  /**
   * Create payment dispute
   */
  async createPaymentDispute(paymentId: string, data: {
    reason: string;
    description: string;
    evidence?: string[];
  }): Promise<ApiResponse<{
    disputeId: string;
    status: string;
    referenceNumber: string;
  }>> {
    return portalApi.post(`/portal/payments/${paymentId}/dispute`, data);
  }

  /**
   * Export payment data
   */
  async exportPayments(params: {
    format: 'csv' | 'excel' | 'pdf';
    dateFrom?: string;
    dateTo?: string;
    status?: PaymentStatus[];
    type?: PaymentType[];
  }): Promise<ApiResponse<{
    downloadUrl: string;
    filename: string;
    expiresAt: string;
  }>> {
    const queryParams = {
      format: params.format,
      ...(params.dateFrom && { dateFrom: params.dateFrom }),
      ...(params.dateTo && { dateTo: params.dateTo }),
      ...(params.status && { status: params.status.join(',') }),
      ...(params.type && { type: params.type.join(',') }),
    };

    return portalApi.get('/portal/payments/export', queryParams);
  }
}

// Create and export default instance
export const paymentsService = new PaymentsService();
export default PaymentsService;