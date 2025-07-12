import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { paymentsService } from '../../services/portal/paymentsService';
import { jobsService } from '../../services/portal/jobsService';
import type { Payment, PaymentType, PaymentStatus, PaymentMethod, Job } from '../../types/portal';

interface PaymentsPageState {
  payments: Payment[];
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
    totalPaid: number;
    totalPending: number;
    totalOverdue: number;
    currency: string;
  } | null;
}

const PaymentsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [state, setState] = useState<PaymentsPageState>({
    payments: [],
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
    type: searchParams.get('type') || '',
    status: searchParams.get('status') || '',
    jobId: searchParams.get('jobId') || '',
  });

  const [showFilters, setShowFilters] = useState(false);
  const [processingPayment, setProcessingPayment] = useState<string | null>(null);

  useEffect(() => {
    loadPayments();
    loadJobs();
    loadStats();
  }, [searchParams]);

  const loadPayments = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const params = {
        page: parseInt(searchParams.get('page') || '1'),
        limit: parseInt(searchParams.get('limit') || '20'),
        search: searchParams.get('search') || undefined,
        type: searchParams.get('type') as PaymentType || undefined,
        status: searchParams.get('status') as PaymentStatus || undefined,
        jobId: searchParams.get('jobId') || undefined,
        sortBy: searchParams.get('sortBy') || 'createdAt',
        sortOrder: (searchParams.get('sortOrder') as 'asc' | 'desc') || 'desc',
      };

      const response = await paymentsService.getPayments(params);

      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          payments: response.data || [],
          pagination: response.pagination || prev.pagination,
          loading: false,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Failed to load payments',
          loading: false,
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to load payments',
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
      const response = await paymentsService.getPaymentStats();
      if (response.success && response.data) {
        setState(prev => ({ ...prev, stats: response.data || null }));
      }
    } catch (err) {
      console.error('Failed to load payment stats:', err);
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
    setFilters({ search: '', type: '', status: '', jobId: '' });
    setSearchParams(new URLSearchParams());
  };

  const handlePayNow = async (payment: Payment) => {
    setProcessingPayment(payment.id);
    try {
      // In a real implementation, this would open a payment modal or redirect to payment processor
      const response = await paymentsService.processPayment({
        paymentId: payment.id,
        method: 'credit_card', // This would be selected by user
        paymentDetails: {
          // Payment details would be collected from user
        },
      });

      if (response.success) {
        // Refresh payments list
        loadPayments();
        loadStats();
      }
    } catch (err) {
      console.error('Payment failed:', err);
    } finally {
      setProcessingPayment(null);
    }
  };

  const getStatusColor = (status: PaymentStatus): string => {
    const colors: Record<PaymentStatus, string> = {
      pending: 'portal-status-warning',
      paid: 'portal-status-success',
      overdue: 'portal-status-error',
      cancelled: 'portal-status-error',
      refunded: 'portal-status-info',
    };
    return colors[status] || 'portal-status-info';
  };

  const getTypeIcon = (type: PaymentType): string => {
    const icons: Record<PaymentType, string> = {
      duties: '🏛️',
      fees: '💰',
      storage: '📦',
      consultation: '💼',
      other: '💳',
    };
    return icons[type] || '💳';
  };

  const formatStatus = (status: string): string => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatCurrency = (amount: number, currency: string = 'USD'): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const isOverdue = (payment: Payment): boolean => {
    return payment.status === 'pending' && !!payment.dueDate && new Date(payment.dueDate) < new Date();
  };

  if (state.loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading payments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
          <p className="text-gray-600 mt-1">
            Manage your payments, invoices, and billing
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/portal/payments/autopay"
            className="portal-btn portal-btn-outline"
          >
            ⚙️ Auto-Pay Settings
          </Link>
          <Link
            to="/portal/payments/history"
            className="portal-btn portal-btn-outline"
          >
            📊 Payment History
          </Link>
        </div>
      </div>

      {/* Payment Stats */}
      {state.stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Paid</p>
                  <p className="text-2xl font-bold text-green-600">
                    {formatCurrency(state.stats.totalPaid, state.stats.currency)}
                  </p>
                </div>
                <div className="text-3xl">✅</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {formatCurrency(state.stats.totalPending, state.stats.currency)}
                  </p>
                </div>
                <div className="text-3xl">⏳</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Overdue</p>
                  <p className="text-2xl font-bold text-red-600">
                    {formatCurrency(state.stats.totalOverdue, state.stats.currency)}
                  </p>
                </div>
                <div className="text-3xl">⚠️</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="portal-card">
        <div className="portal-card-content">
          <form onSubmit={handleSearch} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="portal-form-label">Search Payments</label>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                placeholder="Search by description, job number, or amount..."
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
                  <label className="portal-form-label">Payment Type</label>
                  <select
                    value={filters.type}
                    onChange={(e) => handleFilterChange('type', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Types</option>
                    <option value="duties">Duties</option>
                    <option value="fees">Fees</option>
                    <option value="storage">Storage</option>
                    <option value="consultation">Consultation</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="portal-form-label">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Statuses</option>
                    <option value="pending">Pending</option>
                    <option value="paid">Paid</option>
                    <option value="overdue">Overdue</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="refunded">Refunded</option>
                  </select>
                </div>

                <div>
                  <label className="portal-form-label">Job</label>
                  <select
                    value={filters.jobId}
                    onChange={(e) => handleFilterChange('jobId', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Jobs</option>
                    {state.jobs.map(job => (
                      <option key={job.id} value={job.id}>
                        {job.jobNumber} - {job.title}
                      </option>
                    ))}
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
              <p className="text-lg font-medium">Error loading payments</p>
              <p className="mt-2">{state.error}</p>
              <button
                onClick={loadPayments}
                className="portal-btn portal-btn-primary mt-4"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Payments List */}
      {!state.error && (
        <div className="portal-card">
          <div className="portal-card-header">
            <div className="flex items-center justify-between">
              <h2 className="portal-card-title">
                Payments ({state.pagination.total})
              </h2>
              <div className="text-sm text-gray-500">
                Page {state.pagination.page} of {state.pagination.totalPages}
              </div>
            </div>
          </div>
          <div className="portal-card-content">
            {state.payments.length > 0 ? (
              <div className="space-y-4">
                {state.payments.map((payment) => (
                  <div
                    key={payment.id}
                    className={`border rounded-lg p-4 transition-colors ${
                      isOverdue(payment) 
                        ? 'border-red-200 bg-red-50' 
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="text-3xl">
                          {getTypeIcon(payment.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-medium text-gray-900">
                              {payment.description}
                            </h3>
                            <span className={`portal-status ${getStatusColor(payment.status)}`}>
                              {formatStatus(payment.status)}
                            </span>
                            {isOverdue(payment) && (
                              <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded-full">
                                OVERDUE
                              </span>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <div>
                              <span className="font-medium">Amount:</span> {formatCurrency(payment.amount, payment.currency)}
                            </div>
                            <div>
                              <span className="font-medium">Type:</span> {formatStatus(payment.type)}
                            </div>
                            <div>
                              <span className="font-medium">Job:</span> 
                              <Link 
                                to={`/portal/jobs/${payment.jobId}`}
                                className="text-blue-600 hover:text-blue-800 ml-1"
                              >
                                {state.jobs.find(j => j.id === payment.jobId)?.jobNumber || payment.jobId}
                              </Link>
                            </div>
                          </div>

                          <div className="text-sm text-gray-500 mt-2">
                            <span className="font-medium">Created:</span> {formatDate(payment.createdAt)}
                            {payment.dueDate && (
                              <>
                                <span className="mx-2">•</span>
                                <span className="font-medium">Due:</span> {formatDate(payment.dueDate)}
                              </>
                            )}
                            {payment.paidAt && (
                              <>
                                <span className="mx-2">•</span>
                                <span className="font-medium">Paid:</span> {formatDate(payment.paidAt)}
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {payment.status === 'pending' && (
                          <button
                            onClick={() => handlePayNow(payment)}
                            disabled={processingPayment === payment.id}
                            className="portal-btn portal-btn-primary disabled:opacity-50"
                          >
                            {processingPayment === payment.id ? 'Processing...' : '💳 Pay Now'}
                          </button>
                        )}
                        
                        {payment.status === 'paid' && (
                          <button
                            onClick={() => paymentsService.getPaymentReceipt(payment.id)}
                            className="portal-btn portal-btn-outline"
                          >
                            📄 Receipt
                          </button>
                        )}

                        <button
                          onClick={() => paymentsService.downloadInvoice(payment.id)}
                          className="portal-btn portal-btn-outline"
                          title="Download Invoice"
                        >
                          📥 Invoice
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">💳</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No payments found
                </h3>
                <p className="text-gray-600 mb-4">
                  {filters.search || filters.type || filters.status || filters.jobId
                    ? 'Try adjusting your search criteria or filters.'
                    : 'No payments have been created yet.'}
                </p>
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

export default PaymentsPage;