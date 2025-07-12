import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { jobsService } from '../../services/portal/jobsService';
import type { Job, JobStatus, JobType, JobPriority } from '../../types/portal';

interface JobsPageState {
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
}

const JobsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [state, setState] = useState<JobsPageState>({
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
  });

  // Filter states
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    status: searchParams.get('status') || '',
    type: searchParams.get('type') || '',
    priority: searchParams.get('priority') || '',
  });

  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadJobs();
  }, [searchParams]);

  const loadJobs = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const params = {
        page: parseInt(searchParams.get('page') || '1'),
        limit: parseInt(searchParams.get('limit') || '20'),
        search: searchParams.get('search') || undefined,
        status: searchParams.get('status') as JobStatus || undefined,
        type: searchParams.get('type') as JobType || undefined,
        priority: searchParams.get('priority') as JobPriority || undefined,
        sortBy: searchParams.get('sortBy') || 'updatedAt',
        sortOrder: (searchParams.get('sortOrder') as 'asc' | 'desc') || 'desc',
      };

      const response = await jobsService.getJobs(params);

      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          jobs: response.data || [],
          pagination: response.pagination || prev.pagination,
          loading: false,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Failed to load jobs',
          loading: false,
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to load jobs',
        loading: false,
      }));
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
    setFilters({ search: '', status: '', type: '', priority: '' });
    setSearchParams(new URLSearchParams());
  };

  const getStatusColor = (status: JobStatus): string => {
    const colors: Record<JobStatus, string> = {
      pending: 'portal-status-warning',
      in_progress: 'portal-status-info',
      customs_review: 'portal-status-warning',
      awaiting_payment: 'portal-status-error',
      completed: 'portal-status-success',
      cancelled: 'portal-status-error',
      on_hold: 'portal-status-warning',
    };
    return colors[status] || 'portal-status-info';
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

  if (state.loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Jobs</h1>
          <p className="text-gray-600 mt-1">
            Track and manage your shipment jobs
          </p>
        </div>
        <Link
          to="/portal/jobs/new"
          className="portal-btn portal-btn-primary"
        >
          ➕ Create New Job
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="portal-card">
        <div className="portal-card-content">
          <form onSubmit={handleSearch} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="portal-form-label">Search Jobs</label>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                placeholder="Search by job number, title, or destination..."
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
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="customs_review">Customs Review</option>
                    <option value="awaiting_payment">Awaiting Payment</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="on_hold">On Hold</option>
                  </select>
                </div>

                <div>
                  <label className="portal-form-label">Type</label>
                  <select
                    value={filters.type}
                    onChange={(e) => handleFilterChange('type', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Types</option>
                    <option value="import">Import</option>
                    <option value="export">Export</option>
                    <option value="transit">Transit</option>
                    <option value="warehouse">Warehouse</option>
                    <option value="consultation">Consultation</option>
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
              <p className="text-lg font-medium">Error loading jobs</p>
              <p className="mt-2">{state.error}</p>
              <button
                onClick={loadJobs}
                className="portal-btn portal-btn-primary mt-4"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Jobs List */}
      {!state.error && (
        <div className="portal-card">
          <div className="portal-card-header">
            <div className="flex items-center justify-between">
              <h2 className="portal-card-title">
                Jobs ({state.pagination.total})
              </h2>
              <div className="text-sm text-gray-500">
                Page {state.pagination.page} of {state.pagination.totalPages}
              </div>
            </div>
          </div>
          <div className="portal-card-content">
            {state.jobs.length > 0 ? (
              <div className="space-y-4">
                {state.jobs.map((job) => (
                  <div
                    key={job.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-medium text-gray-900">
                            <Link
                              to={`/portal/jobs/${job.id}`}
                              className="hover:text-blue-600"
                            >
                              {job.title}
                            </Link>
                          </h3>
                          <span className={`portal-status ${getStatusColor(job.status)}`}>
                            {formatStatus(job.status)}
                          </span>
                          {job.priority !== 'normal' && (
                            <span className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded-full">
                              {job.priority.toUpperCase()}
                            </span>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Job #:</span> {job.jobNumber}
                          </div>
                          <div>
                            <span className="font-medium">Route:</span> {job.origin.country} → {job.destination.country}
                          </div>
                          <div>
                            <span className="font-medium">Value:</span> {formatCurrency(job.totalValue, job.currency)}
                          </div>
                        </div>

                        {job.description && (
                          <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                            {job.description}
                          </p>
                        )}
                      </div>

                      <div className="text-right text-sm text-gray-500 ml-4">
                        <div>Updated {formatDate(job.updatedAt)}</div>
                        {job.estimatedArrival && (
                          <div className="mt-1">
                            ETA: {formatDate(job.estimatedArrival)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📦</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No jobs found
                </h3>
                <p className="text-gray-600 mb-4">
                  {filters.search || filters.status || filters.type || filters.priority
                    ? 'Try adjusting your search criteria or filters.'
                    : 'Get started by creating your first shipment job.'}
                </p>
                {!filters.search && !filters.status && !filters.type && !filters.priority && (
                  <Link
                    to="/portal/jobs/new"
                    className="portal-btn portal-btn-primary"
                  >
                    Create New Job
                  </Link>
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

export default JobsPage;