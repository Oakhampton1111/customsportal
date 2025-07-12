import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { supportService } from '../../services/portal/supportService';
import { jobsService } from '../../services/portal/jobsService';
import type { SupportTicket, TicketStatus, TicketPriority, TicketCategory, Job } from '../../types/portal';

interface SupportPageState {
  tickets: SupportTicket[];
  jobs: Job[];
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  stats: {
    total: number;
    byStatus: Record<TicketStatus, number>;
    byPriority: Record<TicketPriority, number>;
  } | null;
}

const SupportPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [state, setState] = useState<SupportPageState>({
    tickets: [],
    jobs: [],
    loading: true,
    error: null,
    pagination: {
      page: 1,
      limit: 20,
      total: 0,
      totalPages: 0,
      hasNext: false,
      hasPrev: false,
    },
    stats: null,
  });

  // Filter states
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    status: searchParams.get('status') || '',
    priority: searchParams.get('priority') || '',
    category: searchParams.get('category') || '',
  });

  const [showFilters, setShowFilters] = useState(false);
  const [showCreateTicket, setShowCreateTicket] = useState(false);
  const [newTicket, setNewTicket] = useState({
    subject: '',
    description: '',
    priority: 'normal' as TicketPriority,
    category: 'general' as TicketCategory,
    jobId: '',
  });

  useEffect(() => {
    loadTickets();
    loadJobs();
    loadStats();
  }, [searchParams]);

  const loadTickets = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const params = {
        page: parseInt(searchParams.get('page') || '1'),
        limit: parseInt(searchParams.get('limit') || '20'),
        search: searchParams.get('search') || undefined,
        status: searchParams.get('status') as TicketStatus || undefined,
        priority: searchParams.get('priority') as TicketPriority || undefined,
        category: searchParams.get('category') as TicketCategory || undefined,
        sortBy: searchParams.get('sortBy') || 'createdAt',
        sortOrder: (searchParams.get('sortOrder') as 'asc' | 'desc') || 'desc',
      };

      const response = await supportService.getTickets(params);

      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          tickets: response.data || [],
          pagination: response.pagination || prev.pagination,
          loading: false,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Failed to load tickets',
          loading: false,
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to load tickets',
        loading: false,
      }));
    }
  };

  const loadJobs = async () => {
    try {
      const response = await jobsService.getJobs({ limit: 100 });
      if (response.success && response.data) {
        setState(prev => ({ ...prev, jobs: response.data || [] }));
      }
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  };

  const loadStats = async () => {
    try {
      const response = await supportService.getSupportStats();
      if (response.success && response.data) {
        setState(prev => ({ ...prev, stats: response.data || null }));
      }
    } catch (err) {
      console.error('Failed to load support stats:', err);
    }
  };

  const updateSearchParams = (newParams: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams);
    
    Object.entries(newParams).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });

    // Reset to page 1 when filters change
    if (Object.keys(newParams).some(key => key !== 'page')) {
      params.set('page', '1');
    }

    setSearchParams(params);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateSearchParams({ search: filters.search || null });
  };

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    updateSearchParams({ [key]: value || null });
  };

  const clearFilters = () => {
    setFilters({ search: '', status: '', priority: '', category: '' });
    setSearchParams(new URLSearchParams());
  };

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await supportService.createTicket({
        subject: newTicket.subject,
        description: newTicket.description,
        priority: newTicket.priority,
        category: newTicket.category,
        jobId: newTicket.jobId || undefined,
      });

      if (response.success) {
        setShowCreateTicket(false);
        setNewTicket({
          subject: '',
          description: '',
          priority: 'normal',
          category: 'general',
          jobId: '',
        });
        loadTickets();
        loadStats();
      }
    } catch (err) {
      console.error('Failed to create ticket:', err);
    }
  };

  const getStatusColor = (status: TicketStatus): string => {
    const colors: Record<TicketStatus, string> = {
      open: 'portal-status-warning',
      in_progress: 'portal-status-info',
      waiting_customer: 'portal-status-warning',
      resolved: 'portal-status-success',
      closed: 'portal-status-success',
    };
    return colors[status] || 'portal-status-info';
  };

  const getPriorityColor = (priority: TicketPriority): string => {
    const colors: Record<TicketPriority, string> = {
      low: 'text-green-600',
      normal: 'text-blue-600',
      high: 'text-orange-600',
      urgent: 'text-red-600',
    };
    return colors[priority] || 'text-gray-600';
  };

  const getCategoryIcon = (category: TicketCategory): string => {
    const icons: Record<TicketCategory, string> = {
      general: '💬',
      technical: '🔧',
      billing: '💰',
      documentation: '📄',
      customs: '🏛️',
      shipping: '🚛',
    };
    return icons[category] || '💬';
  };

  const formatStatus = (status: string): string => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (state.loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading support tickets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Center</h1>
          <p className="text-gray-600 mt-1">
            Get help from our customs experts and track your support requests
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/portal/support/knowledge-base"
            className="portal-btn portal-btn-outline"
          >
            📚 Knowledge Base
          </Link>
          <button
            onClick={() => setShowCreateTicket(true)}
            className="portal-btn portal-btn-primary"
          >
            🎫 Create Ticket
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="portal-card">
          <div className="portal-card-content">
            <div className="flex items-center gap-4">
              <div className="text-3xl">📞</div>
              <div>
                <h3 className="font-medium text-gray-900">Call Support</h3>
                <p className="text-sm text-gray-600">Speak with our experts</p>
                <p className="text-sm font-medium text-blue-600">+1 (555) 123-4567</p>
              </div>
            </div>
          </div>
        </div>

        <div className="portal-card">
          <div className="portal-card-content">
            <div className="flex items-center gap-4">
              <div className="text-3xl">💬</div>
              <div>
                <h3 className="font-medium text-gray-900">Live Chat</h3>
                <p className="text-sm text-gray-600">Chat with support now</p>
                <button className="text-sm font-medium text-blue-600 hover:text-blue-800">
                  Start Chat
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="portal-card">
          <div className="portal-card-content">
            <div className="flex items-center gap-4">
              <div className="text-3xl">📧</div>
              <div>
                <h3 className="font-medium text-gray-900">Email Support</h3>
                <p className="text-sm text-gray-600">Send us an email</p>
                <p className="text-sm font-medium text-blue-600">support@cargoclear.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Support Stats */}
      {state.stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Tickets</p>
                  <p className="text-2xl font-bold text-gray-900">{state.stats.total}</p>
                </div>
                <div className="text-3xl">🎫</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Open</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {state.stats.byStatus.open || 0}
                  </p>
                </div>
                <div className="text-3xl">📂</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {state.stats.byStatus.in_progress || 0}
                  </p>
                </div>
                <div className="text-3xl">⚙️</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Resolved</p>
                  <p className="text-2xl font-bold text-green-600">
                    {state.stats.byStatus.resolved || 0}
                  </p>
                </div>
                <div className="text-3xl">✅</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Ticket Modal */}
      {showCreateTicket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Create Support Ticket</h2>
              <button
                onClick={() => setShowCreateTicket(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div className="portal-form-group">
                <label className="portal-form-label">Subject *</label>
                <input
                  type="text"
                  value={newTicket.subject}
                  onChange={(e) => setNewTicket(prev => ({ ...prev, subject: e.target.value }))}
                  className="portal-form-input"
                  required
                  placeholder="Brief description of your issue"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="portal-form-group">
                  <label className="portal-form-label">Priority</label>
                  <select
                    value={newTicket.priority}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, priority: e.target.value as TicketPriority }))}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>

                <div className="portal-form-group">
                  <label className="portal-form-label">Category</label>
                  <select
                    value={newTicket.category}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, category: e.target.value as TicketCategory }))}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="general">General</option>
                    <option value="technical">Technical</option>
                    <option value="billing">Billing</option>
                    <option value="documentation">Documentation</option>
                    <option value="customs">Customs</option>
                    <option value="shipping">Shipping</option>
                  </select>
                </div>

                <div className="portal-form-group">
                  <label className="portal-form-label">Related Job</label>
                  <select
                    value={newTicket.jobId}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, jobId: e.target.value }))}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">No specific job</option>
                    {state.jobs.map(job => (
                      <option key={job.id} value={job.id}>
                        {job.jobNumber} - {job.title}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="portal-form-group">
                <label className="portal-form-label">Description *</label>
                <textarea
                  value={newTicket.description}
                  onChange={(e) => setNewTicket(prev => ({ ...prev, description: e.target.value }))}
                  className="portal-form-input portal-form-textarea"
                  rows={5}
                  required
                  placeholder="Please provide detailed information about your issue..."
                />
              </div>

              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreateTicket(false)}
                  className="portal-btn portal-btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="portal-btn portal-btn-primary"
                >
                  Create Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="portal-card">
        <div className="portal-card-content">
          <form onSubmit={handleSearch} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="portal-form-label">Search Tickets</label>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                placeholder="Search by subject, description, or ticket ID..."
                className="portal-form-input"
              />
            </div>
            <button type="submit" className="portal-btn portal-btn-primary">
              🔍 Search
            </button>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="portal-btn portal-btn-outline"
            >
              🔧 Filters
            </button>
          </form>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="portal-form-label">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="waiting_customer">Waiting Customer</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>

                <div>
                  <label className="portal-form-label">Priority</label>
                  <select
                    value={filters.priority}
                    onChange={(e) => handleFilterChange('priority', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Priorities</option>
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="portal-form-label">Category</label>
                  <select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Categories</option>
                    <option value="general">General</option>
                    <option value="technical">Technical</option>
                    <option value="billing">Billing</option>
                    <option value="documentation">Documentation</option>
                    <option value="customs">Customs</option>
                    <option value="shipping">Shipping</option>
                  </select>
                </div>
              </div>

              <div className="mt-4 flex gap-2">
                <button
                  onClick={clearFilters}
                  className="portal-btn portal-btn-ghost"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error State */}
      {state.error && (
        <div className="portal-card">
          <div className="portal-card-content">
            <div className="text-center text-red-600">
              <p className="text-lg font-medium">Error loading tickets</p>
              <p className="mt-2">{state.error}</p>
              <button
                onClick={loadTickets}
                className="portal-btn portal-btn-primary mt-4"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tickets List */}
      {!state.error && (
        <div className="portal-card">
          <div className="portal-card-header">
            <div className="flex items-center justify-between">
              <h2 className="portal-card-title">
                Support Tickets ({state.pagination.total})
              </h2>
              <div className="text-sm text-gray-500">
                Page {state.pagination.page} of {state.pagination.totalPages}
              </div>
            </div>
          </div>
          <div className="portal-card-content">
            {state.tickets.length > 0 ? (
              <div className="space-y-4">
                {state.tickets.map((ticket) => (
                  <div
                    key={ticket.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="text-3xl">
                          {getCategoryIcon(ticket.category)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-medium text-gray-900">
                              <Link
                                to={`/portal/support/tickets/${ticket.id}`}
                                className="hover:text-blue-600"
                              >
                                {ticket.subject}
                              </Link>
                            </h3>
                            <span className={`portal-status ${getStatusColor(ticket.status)}`}>
                              {formatStatus(ticket.status)}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(ticket.priority)}`}>
                              {ticket.priority.toUpperCase()}
                            </span>
                          </div>
                          
                          <div className="text-sm text-gray-600 mb-2">
                            <span className="font-medium">Category:</span> {formatStatus(ticket.category)}
                            {ticket.jobId && (
                              <>
                                <span className="mx-2">•</span>
                                <span className="font-medium">Job:</span> 
                                <Link 
                                  to={`/portal/jobs/${ticket.jobId}`}
                                  className="text-blue-600 hover:text-blue-800 ml-1"
                                >
                                  {state.jobs.find(j => j.id === ticket.jobId)?.jobNumber || ticket.jobId}
                                </Link>
                              </>
                            )}
                          </div>

                          <p className="text-sm text-gray-700 line-clamp-2 mb-2">
                            {ticket.description}
                          </p>

                          <div className="text-xs text-gray-500">
                            Created {formatDate(ticket.createdAt)}
                            {ticket.updatedAt !== ticket.createdAt && (
                              <span> • Updated {formatDate(ticket.updatedAt)}</span>
                            )}
                            {ticket.resolvedAt && (
                              <span> • Resolved {formatDate(ticket.resolvedAt)}</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">
                          {ticket.messages.length} message{ticket.messages.length !== 1 ? 's' : ''}
                        </span>
                        <Link
                          to={`/portal/support/tickets/${ticket.id}`}
                          className="portal-btn portal-btn-outline"
                        >
                          View Details
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🎫</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No support tickets found
                </h3>
                <p className="text-gray-600 mb-4">
                  {filters.search || filters.status || filters.priority || filters.category
                    ? 'Try adjusting your search criteria or filters.'
                    : 'Create your first support ticket to get help from our team.'}
                </p>
                {!filters.search && !filters.status && !filters.priority && !filters.category && (
                  <button
                    onClick={() => setShowCreateTicket(true)}
                    className="portal-btn portal-btn-primary"
                  >
                    Create Support Ticket
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pagination */}
      {state.pagination.totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {((state.pagination.page - 1) * state.pagination.limit) + 1} to{' '}
            {Math.min(state.pagination.page * state.pagination.limit, state.pagination.total)} of{' '}
            {state.pagination.total} results
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => updateSearchParams({ page: String(state.pagination.page - 1) })}
              disabled={!state.pagination.hasPrev}
              className="portal-btn portal-btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>
            
            <span className="flex items-center px-4 py-2 text-sm text-gray-700">
              Page {state.pagination.page} of {state.pagination.totalPages}
            </span>
            
            <button
              onClick={() => updateSearchParams({ page: String(state.pagination.page + 1) })}
              disabled={!state.pagination.hasNext}
              className="portal-btn portal-btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SupportPage;