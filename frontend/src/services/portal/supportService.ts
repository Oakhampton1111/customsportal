// Support Service for Portal
// Handles all support ticket-related API operations

import { portalApi } from './api';
import type { 
  SupportTicket, 
  TicketStatus, 
  TicketPriority,
  TicketCategory,
  TicketMessage,
  ApiResponse, 
  ListParams,
  PaginationInfo 
} from '../../types/portal';

export interface SupportListParams extends ListParams {
  status?: TicketStatus;
  priority?: TicketPriority;
  category?: TicketCategory;
  jobId?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface CreateTicketData {
  subject: string;
  description: string;
  priority: TicketPriority;
  category: TicketCategory;
  jobId?: string;
  attachments?: File[];
}

export interface CreateMessageData {
  ticketId: string;
  content: string;
  attachments?: File[];
}

export class SupportService {
  /**
   * Get list of support tickets for the current customer
   */
  async getTickets(params: SupportListParams = {}): Promise<ApiResponse<SupportTicket[]> & { pagination: PaginationInfo }> {
    const queryParams = {
      ...params,
      ...(params.status && { status: params.status }),
      ...(params.priority && { priority: params.priority }),
      ...(params.category && { category: params.category }),
      ...(params.jobId && { jobId: params.jobId }),
      ...(params.dateFrom && { dateFrom: params.dateFrom }),
      ...(params.dateTo && { dateTo: params.dateTo }),
    };

    return portalApi.getList<SupportTicket>('/portal/support/tickets', queryParams);
  }

  /**
   * Get a specific ticket by ID
   */
  async getTicket(ticketId: string): Promise<ApiResponse<SupportTicket>> {
    return portalApi.get<SupportTicket>(`/portal/support/tickets/${ticketId}`);
  }

  /**
   * Create a new support ticket
   */
  async createTicket(data: CreateTicketData): Promise<ApiResponse<SupportTicket>> {
    if (data.attachments && data.attachments.length > 0) {
      // Handle file uploads separately for now
      const ticketData = {
        subject: data.subject,
        description: data.description,
        priority: data.priority,
        category: data.category,
        jobId: data.jobId,
      };

      const response = await portalApi.post<SupportTicket>('/portal/support/tickets', ticketData);
      
      // Upload attachments if ticket creation was successful
      if (response.success && response.data && data.attachments.length > 0) {
        for (const file of data.attachments) {
          try {
            await portalApi.upload(`/portal/support/tickets/${response.data.id}/attachments`, file);
          } catch (error) {
            console.error('Failed to upload attachment:', error);
          }
        }
      }

      return response;
    } else {
      return portalApi.post<SupportTicket>('/portal/support/tickets', {
        subject: data.subject,
        description: data.description,
        priority: data.priority,
        category: data.category,
        jobId: data.jobId,
      });
    }
  }

  /**
   * Update a ticket
   */
  async updateTicket(ticketId: string, updates: {
    subject?: string;
    priority?: TicketPriority;
    category?: TicketCategory;
  }): Promise<ApiResponse<SupportTicket>> {
    return portalApi.patch<SupportTicket>(`/portal/support/tickets/${ticketId}`, updates);
  }

  /**
   * Close a ticket
   */
  async closeTicket(ticketId: string, reason?: string): Promise<ApiResponse<SupportTicket>> {
    return portalApi.patch<SupportTicket>(`/portal/support/tickets/${ticketId}/close`, { reason });
  }

  /**
   * Reopen a ticket
   */
  async reopenTicket(ticketId: string, reason?: string): Promise<ApiResponse<SupportTicket>> {
    return portalApi.patch<SupportTicket>(`/portal/support/tickets/${ticketId}/reopen`, { reason });
  }

  /**
   * Add a message to a ticket
   */
  async addMessage(data: CreateMessageData): Promise<ApiResponse<TicketMessage>> {
    if (data.attachments && data.attachments.length > 0) {
      // Create message first
      const messageResponse = await portalApi.post<TicketMessage>(
        `/portal/support/tickets/${data.ticketId}/messages`, 
        { content: data.content }
      );

      // Upload attachments if message creation was successful
      if (messageResponse.success && messageResponse.data && data.attachments.length > 0) {
        for (const file of data.attachments) {
          try {
            await portalApi.upload(
              `/portal/support/tickets/${data.ticketId}/messages/${messageResponse.data.id}/attachments`, 
              file
            );
          } catch (error) {
            console.error('Failed to upload message attachment:', error);
          }
        }
      }

      return messageResponse;
    } else {
      return portalApi.post<TicketMessage>(
        `/portal/support/tickets/${data.ticketId}/messages`, 
        { content: data.content }
      );
    }
  }

  /**
   * Get messages for a ticket
   */
  async getTicketMessages(ticketId: string): Promise<ApiResponse<TicketMessage[]>> {
    return portalApi.get<TicketMessage[]>(`/portal/support/tickets/${ticketId}/messages`);
  }

  /**
   * Search tickets
   */
  async searchTickets(query: string, filters?: {
    status?: TicketStatus[];
    priority?: TicketPriority[];
    category?: TicketCategory[];
    jobId?: string;
    dateRange?: {
      from: string;
      to: string;
    };
  }): Promise<ApiResponse<SupportTicket[]>> {
    const params = {
      q: query,
      ...(filters?.status && { status: filters.status.join(',') }),
      ...(filters?.priority && { priority: filters.priority.join(',') }),
      ...(filters?.category && { category: filters.category.join(',') }),
      ...(filters?.jobId && { jobId: filters.jobId }),
      ...(filters?.dateRange && {
        dateFrom: filters.dateRange.from,
        dateTo: filters.dateRange.to,
      }),
    };

    return portalApi.get<SupportTicket[]>('/portal/support/tickets/search', params);
  }

  /**
   * Get support statistics
   */
  async getSupportStats(): Promise<ApiResponse<{
    total: number;
    byStatus: Record<TicketStatus, number>;
    byPriority: Record<TicketPriority, number>;
    byCategory: Record<TicketCategory, number>;
    averageResponseTime: number;
    averageResolutionTime: number;
    satisfactionRating: number;
  }>> {
    return portalApi.get('/portal/support/stats');
  }

  /**
   * Get frequently asked questions
   */
  async getFAQs(category?: TicketCategory): Promise<ApiResponse<Array<{
    id: string;
    question: string;
    answer: string;
    category: TicketCategory;
    helpful: number;
    notHelpful: number;
    tags: string[];
  }>>> {
    const params = category ? { category } : {};
    return portalApi.get('/portal/support/faqs', params);
  }

  /**
   * Rate FAQ helpfulness
   */
  async rateFAQ(faqId: string, helpful: boolean): Promise<ApiResponse<void>> {
    return portalApi.post(`/portal/support/faqs/${faqId}/rate`, { helpful });
  }

  /**
   * Get support contact information
   */
  async getContactInfo(): Promise<ApiResponse<{
    phone: string;
    email: string;
    hours: {
      timezone: string;
      weekdays: string;
      weekends: string;
    };
    emergencyContact?: {
      phone: string;
      email: string;
      available: string;
    };
  }>> {
    return portalApi.get('/portal/support/contact');
  }

  /**
   * Request callback
   */
  async requestCallback(data: {
    phone: string;
    preferredTime: string;
    timezone: string;
    reason: string;
    urgency: 'low' | 'normal' | 'high' | 'urgent';
  }): Promise<ApiResponse<{
    callbackId: string;
    scheduledTime: string;
    confirmationNumber: string;
  }>> {
    return portalApi.post('/portal/support/callback', data);
  }

  /**
   * Get callback requests
   */
  async getCallbackRequests(): Promise<ApiResponse<Array<{
    id: string;
    phone: string;
    scheduledTime: string;
    status: 'pending' | 'scheduled' | 'completed' | 'cancelled';
    reason: string;
    urgency: string;
    createdAt: string;
  }>>> {
    return portalApi.get('/portal/support/callbacks');
  }

  /**
   * Cancel callback request
   */
  async cancelCallback(callbackId: string): Promise<ApiResponse<void>> {
    return portalApi.delete(`/portal/support/callbacks/${callbackId}`);
  }

  /**
   * Submit feedback
   */
  async submitFeedback(data: {
    type: 'bug' | 'feature' | 'improvement' | 'general';
    subject: string;
    description: string;
    rating?: number; // 1-5 stars
    page?: string;
    attachments?: File[];
  }): Promise<ApiResponse<{
    feedbackId: string;
    referenceNumber: string;
  }>> {
    const feedbackData = {
      type: data.type,
      subject: data.subject,
      description: data.description,
      rating: data.rating,
      page: data.page,
    };

    const response = await portalApi.post<{
      feedbackId: string;
      referenceNumber: string;
    }>('/portal/support/feedback', feedbackData);

    // Upload attachments if feedback submission was successful
    if (response.success && response.data && data.attachments && data.attachments.length > 0) {
      for (const file of data.attachments) {
        try {
          await portalApi.upload(`/portal/support/feedback/${response.data.feedbackId}/attachments`, file);
        } catch (error) {
          console.error('Failed to upload feedback attachment:', error);
        }
      }
    }

    return response;
  }

  /**
   * Get knowledge base articles
   */
  async getKnowledgeBase(params?: {
    category?: TicketCategory;
    search?: string;
    tags?: string[];
  }): Promise<ApiResponse<Array<{
    id: string;
    title: string;
    summary: string;
    content: string;
    category: TicketCategory;
    tags: string[];
    views: number;
    helpful: number;
    notHelpful: number;
    lastUpdated: string;
  }>>> {
    const queryParams = {
      ...(params?.category && { category: params.category }),
      ...(params?.search && { search: params.search }),
      ...(params?.tags && { tags: params.tags.join(',') }),
    };

    return portalApi.get('/portal/support/knowledge-base', queryParams);
  }

  /**
   * Get specific knowledge base article
   */
  async getKnowledgeBaseArticle(articleId: string): Promise<ApiResponse<{
    id: string;
    title: string;
    content: string;
    category: TicketCategory;
    tags: string[];
    views: number;
    helpful: number;
    notHelpful: number;
    lastUpdated: string;
    relatedArticles: Array<{
      id: string;
      title: string;
      summary: string;
    }>;
  }>> {
    return portalApi.get(`/portal/support/knowledge-base/${articleId}`);
  }

  /**
   * Rate knowledge base article
   */
  async rateKnowledgeBaseArticle(articleId: string, helpful: boolean): Promise<ApiResponse<void>> {
    return portalApi.post(`/portal/support/knowledge-base/${articleId}/rate`, { helpful });
  }

  /**
   * Get ticket satisfaction survey
   */
  async getTicketSurvey(ticketId: string): Promise<ApiResponse<{
    surveyId: string;
    questions: Array<{
      id: string;
      question: string;
      type: 'rating' | 'text' | 'choice';
      options?: string[];
      required: boolean;
    }>;
  }>> {
    return portalApi.get(`/portal/support/tickets/${ticketId}/survey`);
  }

  /**
   * Submit ticket satisfaction survey
   */
  async submitTicketSurvey(ticketId: string, surveyId: string, responses: Array<{
    questionId: string;
    answer: string | number;
  }>): Promise<ApiResponse<void>> {
    return portalApi.post(`/portal/support/tickets/${ticketId}/survey/${surveyId}`, { responses });
  }
}

// Create and export default instance
export const supportService = new SupportService();
export default SupportService;