import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { documentsService } from '../../services/portal/documentsService';
import { jobsService } from '../../services/portal/jobsService';
import DocumentUpload from '../../components/portal/shared/DocumentUpload';
import type { Document, DocumentType, DocumentStatus, Job } from '../../types/portal';

interface DocumentsPageState {
  documents: Document[];
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

const DocumentsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [state, setState] = useState<DocumentsPageState>({
    documents: [],
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
    type: searchParams.get('type') || '',
    status: searchParams.get('status') || '',
    jobId: searchParams.get('jobId') || '',
  });

  const [showFilters, setShowFilters] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string>('');

  useEffect(() => {
    loadDocuments();
    loadJobs();
  }, [searchParams]);

  const loadDocuments = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const params = {
        page: parseInt(searchParams.get('page') || '1'),
        limit: parseInt(searchParams.get('limit') || '20'),
        search: searchParams.get('search') || undefined,
        type: searchParams.get('type') as DocumentType || undefined,
        status: searchParams.get('status') as DocumentStatus || undefined,
        jobId: searchParams.get('jobId') || undefined,
        sortBy: searchParams.get('sortBy') || 'uploadedAt',
        sortOrder: (searchParams.get('sortOrder') as 'asc' | 'desc') || 'desc',
      };

      const response = await documentsService.getDocuments(params);

      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          documents: response.data || [],
          pagination: response.pagination || prev.pagination,
          loading: false,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.error || 'Failed to load documents',
          loading: false,
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to load documents',
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

  const handleUploadComplete = (documents: Document[]) => {
    setState(prev => ({
      ...prev,
      documents: [...documents, ...prev.documents],
    }));
    setShowUpload(false);
    setSelectedJobId('');
  };

  const handleDownload = async (doc: Document) => {
    try {
      const response = await documentsService.downloadDocument(doc.id);
      if (response.success && response.data) {
        // Create a temporary link to download the file
        const link = document.createElement('a');
        link.href = response.data.url;
        link.download = response.data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const getStatusColor = (status: DocumentStatus): string => {
    const colors: Record<DocumentStatus, string> = {
      pending: 'portal-status-warning',
      approved: 'portal-status-success',
      rejected: 'portal-status-error',
      requires_revision: 'portal-status-warning',
    };
    return colors[status] || 'portal-status-info';
  };

  const formatStatus = (status: string): string => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

  const getDocumentIcon = (type: DocumentType): string => {
    const icons: Record<DocumentType, string> = {
      invoice: '🧾',
      packing_list: '📋',
      bill_of_lading: '🚢',
      certificate_of_origin: '📜',
      customs_declaration: '🏛️',
      permit: '📝',
      insurance: '🛡️',
      other: '📄',
    };
    return icons[type] || '📄';
  };

  if (state.loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">
            Manage your shipping documents and paperwork
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="portal-btn portal-btn-primary"
        >
          📎 Upload Documents
        </button>
      </div>

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Upload Documents</h2>
              <button
                onClick={() => setShowUpload(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="mb-4">
              <label className="portal-form-label">Select Job</label>
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                className="portal-form-input portal-form-select"
                required
              >
                <option value="">Choose a job...</option>
                {state.jobs.map(job => (
                  <option key={job.id} value={job.id}>
                    {job.jobNumber} - {job.title}
                  </option>
                ))}
              </select>
            </div>

            {selectedJobId && (
              <DocumentUpload
                jobId={selectedJobId}
                onUploadComplete={handleUploadComplete}
                onUploadError={(error) => console.error('Upload error:', error)}
              />
            )}
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="portal-card">
        <div className="portal-card-content">
          <form onSubmit={handleSearch} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="portal-form-label">Search Documents</label>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                placeholder="Search by document name or job number..."
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
                  <label className="portal-form-label">Document Type</label>
                  <select
                    value={filters.type}
                    onChange={(e) => handleFilterChange('type', e.target.value)}
                    className="portal-form-input portal-form-select"
                  >
                    <option value="">All Types</option>
                    <option value="invoice">Invoice</option>
                    <option value="packing_list">Packing List</option>
                    <option value="bill_of_lading">Bill of Lading</option>
                    <option value="certificate_of_origin">Certificate of Origin</option>
                    <option value="customs_declaration">Customs Declaration</option>
                    <option value="permit">Permit</option>
                    <option value="insurance">Insurance</option>
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
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                    <option value="requires_revision">Requires Revision</option>
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
              <p className="text-lg font-medium">Error loading documents</p>
              <p className="mt-2">{state.error}</p>
              <button
                onClick={loadDocuments}
                className="portal-btn portal-btn-primary mt-4"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Documents List */}
      {!state.error && (
        <div className="portal-card">
          <div className="portal-card-header">
            <div className="flex items-center justify-between">
              <h2 className="portal-card-title">
                Documents ({state.pagination.total})
              </h2>
              <div className="text-sm text-gray-500">
                Page {state.pagination.page} of {state.pagination.totalPages}
              </div>
            </div>
          </div>
          <div className="portal-card-content">
            {state.documents.length > 0 ? (
              <div className="space-y-4">
                {state.documents.map((document) => (
                  <div
                    key={document.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="text-3xl">
                        {getDocumentIcon(document.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="font-medium text-gray-900">
                            {document.name}
                          </h3>
                          <span className={`portal-status ${getStatusColor(document.status)}`}>
                            {formatStatus(document.status)}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Type:</span> {formatStatus(document.type)} • 
                          <span className="font-medium ml-2">Size:</span> {formatFileSize(document.size)} • 
                          <span className="font-medium ml-2">Job:</span> 
                          <Link 
                            to={`/portal/jobs/${document.jobId}`}
                            className="text-blue-600 hover:text-blue-800 ml-1"
                          >
                            {state.jobs.find(j => j.id === document.jobId)?.jobNumber || document.jobId}
                          </Link>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Uploaded {formatDate(document.uploadedAt)} by {document.uploadedBy}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownload(document)}
                        className="portal-btn portal-btn-outline"
                        title="Download"
                      >
                        📥 Download
                      </button>
                      <a
                        href={document.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="portal-btn portal-btn-outline"
                        title="View"
                      >
                        👁️ View
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No documents found
                </h3>
                <p className="text-gray-600 mb-4">
                  {filters.search || filters.type || filters.status || filters.jobId
                    ? 'Try adjusting your search criteria or filters.'
                    : 'Upload your first document to get started.'}
                </p>
                {!filters.search && !filters.type && !filters.status && !filters.jobId && (
                  <button
                    onClick={() => setShowUpload(true)}
                    className="portal-btn portal-btn-primary"
                  >
                    Upload Documents
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

export default DocumentsPage;