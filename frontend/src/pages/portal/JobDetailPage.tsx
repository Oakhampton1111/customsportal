import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { jobsService } from '../../services/portal/jobsService';
import type { Job, Document, Activity } from '../../types/portal';

interface JobDetailState {
  job: Job | null;
  timeline: Array<{
    id: string;
    timestamp: string;
    event: string;
    description: string;
    actor: {
      name: string;
      type: 'customer' | 'system' | 'broker';
    };
    metadata?: Record<string, any>;
  }>;
  comments: Array<{
    id: string;
    comment: string;
    timestamp: string;
    author: {
      name: string;
      type: 'customer' | 'broker';
    };
  }>;
  loading: boolean;
  error: string | null;
}

const JobDetailPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [state, setState] = useState<JobDetailState>({
    job: null,
    timeline: [],
    comments: [],
    loading: true,
    error: null,
  });

  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'timeline' | 'comments'>('overview');

  useEffect(() => {
    if (jobId) {
      loadJobDetails();
    }
  }, [jobId]);

  const loadJobDetails = async () => {
    if (!jobId) return;

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      // Load job details, timeline, and comments in parallel
      const [jobResponse, timelineResponse, commentsResponse] = await Promise.all([
        jobsService.getJob(jobId),
        jobsService.getJobTimeline(jobId),
        jobsService.getJobComments(jobId),
      ]);

      if (jobResponse.success && jobResponse.data) {
        setState(prev => ({
          ...prev,
          job: jobResponse.data!,
          timeline: timelineResponse.success ? timelineResponse.data || [] : [],
          comments: commentsResponse.success ? commentsResponse.data || [] : [],
          loading: false,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: jobResponse.error || 'Failed to load job details',
          loading: false,
        }));
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to load job details',
        loading: false,
      }));
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId || !newComment.trim() || submittingComment) return;

    try {
      setSubmittingComment(true);
      const response = await jobsService.addJobComment(jobId, newComment.trim());

      if (response.success && response.data) {
        // Add the new comment to the list
        setState(prev => ({
          ...prev,
          comments: [
            ...prev.comments,
            {
              id: response.data!.id,
              comment: response.data!.comment,
              timestamp: response.data!.timestamp,
              author: {
                name: response.data!.author,
                type: 'customer' as const,
              },
            },
          ],
        }));
        setNewComment('');
      }
    } catch (err) {
      console.error('Failed to add comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDateShort = (dateString: string): string => {
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
          <p className="mt-4 text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (state.error || !state.job) {
    return (
      <div className="portal-card">
        <div className="portal-card-content">
          <div className="text-center text-red-600">
            <p className="text-lg font-medium">Error loading job details</p>
            <p className="mt-2">{state.error || 'Job not found'}</p>
            <div className="mt-4 space-x-4">
              <button
                onClick={loadJobDetails}
                className="portal-btn portal-btn-primary"
              >
                Try Again
              </button>
              <Link
                to="/portal/jobs"
                className="portal-btn portal-btn-outline"
              >
                Back to Jobs
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const job = state.job;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Link to="/portal/jobs" className="hover:text-blue-600">Jobs</Link>
            <span>/</span>
            <span>Job #{job.jobNumber}</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
          <div className="flex items-center gap-4 mt-2">
            <span className={`portal-status ${getStatusColor(job.status)}`}>
              {formatStatus(job.status)}
            </span>
            {job.priority !== 'normal' && (
              <span className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded-full">
                {job.priority.toUpperCase()} PRIORITY
              </span>
            )}
            <span className="text-sm text-gray-500">
              Updated {formatDateShort(job.updatedAt)}
            </span>
          </div>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => jobsService.requestStatusUpdate(job.id, 'Customer requested status update')}
            className="portal-btn portal-btn-outline"
          >
            📞 Request Update
          </button>
          <Link
            to={`/portal/jobs/${job.id}/edit`}
            className="portal-btn portal-btn-primary"
          >
            ✏️ Edit Job
          </Link>
        </div>
      </div>

      {/* Job Overview Card */}
      <div className="portal-card">
        <div className="portal-card-header">
          <h2 className="portal-card-title">Job Overview</h2>
        </div>
        <div className="portal-card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Shipment Details</h3>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-500">Job Number:</span> {job.jobNumber}</div>
                <div><span className="text-gray-500">Type:</span> {job.type.charAt(0).toUpperCase() + job.type.slice(1)}</div>
                <div><span className="text-gray-500">Value:</span> {formatCurrency(job.totalValue, job.currency)}</div>
                {job.estimatedDuties && (
                  <div><span className="text-gray-500">Est. Duties:</span> {formatCurrency(job.estimatedDuties, job.currency)}</div>
                )}
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Route</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-gray-500">From:</span>
                  <div className="font-medium">{job.origin.city}, {job.origin.country}</div>
                  {job.origin.port && <div className="text-gray-500">Port: {job.origin.port}</div>}
                </div>
                <div>
                  <span className="text-gray-500">To:</span>
                  <div className="font-medium">{job.destination.city}, {job.destination.country}</div>
                  {job.destination.port && <div className="text-gray-500">Port: {job.destination.port}</div>}
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Timeline</h3>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-500">Created:</span> {formatDateShort(job.createdAt)}</div>
                {job.estimatedArrival && (
                  <div><span className="text-gray-500">Est. Arrival:</span> {formatDateShort(job.estimatedArrival)}</div>
                )}
                {job.actualArrival && (
                  <div><span className="text-gray-500">Actual Arrival:</span> {formatDateShort(job.actualArrival)}</div>
                )}
                {job.completedAt && (
                  <div><span className="text-gray-500">Completed:</span> {formatDateShort(job.completedAt)}</div>
                )}
              </div>
            </div>
          </div>

          {job.description && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="font-medium text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700">{job.description}</p>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="portal-card">
        <div className="portal-card-header">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', count: null },
              { id: 'documents', label: 'Documents', count: job.documents.length },
              { id: 'timeline', label: 'Timeline', count: state.timeline.length },
              { id: 'comments', label: 'Comments', count: state.comments.length },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`pb-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
                {tab.count !== null && (
                  <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="portal-card-content">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-4">Recent Activity</h3>
                {state.timeline.slice(0, 5).map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{activity.description}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(activity.timestamp)} • {activity.actor.name}
                      </p>
                    </div>
                  </div>
                ))}
                {state.timeline.length > 5 && (
                  <button
                    onClick={() => setActiveTab('timeline')}
                    className="text-sm text-blue-600 hover:text-blue-800 mt-2"
                  >
                    View all activity →
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-gray-900">Documents</h3>
                <Link
                  to={`/portal/jobs/${job.id}/upload`}
                  className="portal-btn portal-btn-primary"
                >
                  📎 Upload Document
                </Link>
              </div>
              
              {job.documents.length > 0 ? (
                <div className="space-y-3">
                  {job.documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">📄</div>
                        <div>
                          <h4 className="font-medium text-gray-900">{doc.name}</h4>
                          <p className="text-sm text-gray-500">
                            {doc.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} • 
                            {(doc.size / 1024 / 1024).toFixed(1)} MB • 
                            Uploaded {formatDateShort(doc.uploadedAt)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`portal-status ${getStatusColor(doc.status)}`}>
                          {formatStatus(doc.status)}
                        </span>
                        <a
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="portal-btn portal-btn-outline"
                        >
                          View
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">📄</div>
                  <p className="text-gray-600">No documents uploaded yet</p>
                </div>
              )}
            </div>
          )}

          {/* Timeline Tab */}
          {activeTab === 'timeline' && (
            <div>
              <h3 className="font-medium text-gray-900 mb-4">Activity Timeline</h3>
              {state.timeline.length > 0 ? (
                <div className="space-y-4">
                  {state.timeline.map((activity) => (
                    <div key={activity.id} className="flex items-start gap-4">
                      <div className="w-3 h-3 bg-blue-500 rounded-full mt-1 flex-shrink-0"></div>
                      <div className="flex-1 pb-4">
                        <p className="text-sm text-gray-900">{activity.description}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatDate(activity.timestamp)} • {activity.actor.name}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">📅</div>
                  <p className="text-gray-600">No activity recorded yet</p>
                </div>
              )}
            </div>
          )}

          {/* Comments Tab */}
          {activeTab === 'comments' && (
            <div>
              <h3 className="font-medium text-gray-900 mb-4">Comments</h3>
              
              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} className="mb-6">
                <div className="portal-form-group">
                  <label className="portal-form-label">Add a comment</label>
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Ask a question or provide additional information..."
                    className="portal-form-input portal-form-textarea"
                    rows={3}
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={submittingComment || !newComment.trim()}
                  className="portal-btn portal-btn-primary disabled:opacity-50"
                >
                  {submittingComment ? 'Posting...' : 'Post Comment'}
                </button>
              </form>

              {/* Comments List */}
              {state.comments.length > 0 ? (
                <div className="space-y-4">
                  {state.comments.map((comment) => (
                    <div key={comment.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900">{comment.author.name}</span>
                        <span className="text-sm text-gray-500">{formatDate(comment.timestamp)}</span>
                      </div>
                      <p className="text-gray-700">{comment.comment}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">💬</div>
                  <p className="text-gray-600">No comments yet</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobDetailPage;