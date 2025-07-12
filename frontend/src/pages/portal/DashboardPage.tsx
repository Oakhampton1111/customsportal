import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsService } from '../../services/portal/jobsService';
import type { Job } from '../../types/portal';

interface DashboardStats {
  total: number;
  byStatus: Record<string, number>;
  byType: Record<string, number>;
  byPriority: Record<string, number>;
  recentActivity: number;
  pendingPayments: number;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load stats and recent jobs in parallel
      const [statsResponse, jobsResponse] = await Promise.all([
        jobsService.getJobStats(),
        jobsService.getJobs({ limit: 5, sortBy: 'updatedAt', sortOrder: 'desc' })
      ]);

      if (statsResponse.success && statsResponse.data) {
        setStats(statsResponse.data);
      }

      if (jobsResponse.success && jobsResponse.data) {
        setRecentJobs(jobsResponse.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portal-card">
        <div className="portal-card-content">
          <div className="text-center text-red-600">
            <p className="text-lg font-medium">Error loading dashboard</p>
            <p className="mt-2">{error}</p>
            <button
              onClick={loadDashboardData}
              className="portal-btn portal-btn-primary mt-4"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="portal-card">
        <div className="portal-card-content">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to Your Portal
          </h1>
          <p className="text-gray-600">
            Track your shipments, manage documents, and stay updated on your customs clearance progress.
          </p>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Jobs</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                </div>
                <div className="text-3xl">📦</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {stats.byStatus.in_progress || 0}
                  </p>
                </div>
                <div className="text-3xl">🚛</div>
              </div>
            </div>
          </div>

          <div className="portal-card">
            <div className="portal-card-content">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.byStatus.completed || 0}
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
                  <p className="text-sm font-medium text-gray-600">Pending Payments</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {stats.pendingPayments}
                  </p>
                </div>
                <div className="text-3xl">💳</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Jobs */}
      <div className="portal-card">
        <div className="portal-card-header">
          <div className="flex items-center justify-between">
            <h2 className="portal-card-title">Recent Jobs</h2>
            <Link
              to="/portal/jobs"
              className="portal-btn portal-btn-outline"
            >
              View All
            </Link>
          </div>
        </div>
        <div className="portal-card-content">
          {recentJobs.length > 0 ? (
            <div className="space-y-4">
              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
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
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Job #{job.jobNumber} • {job.origin.country} → {job.destination.country}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Value: {formatCurrency(job.totalValue, job.currency)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">
                      Updated {new Date(job.updatedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No jobs yet
              </h3>
              <p className="text-gray-600 mb-4">
                Get started by creating your first shipment job.
              </p>
              <Link
                to="/portal/jobs/new"
                className="portal-btn portal-btn-primary"
              >
                Create New Job
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="portal-card">
        <div className="portal-card-header">
          <h2 className="portal-card-title">Quick Actions</h2>
        </div>
        <div className="portal-card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/portal/jobs/new"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors"
            >
              <div className="text-2xl mr-3">➕</div>
              <div>
                <h3 className="font-medium text-gray-900">Create New Job</h3>
                <p className="text-sm text-gray-600">Start a new shipment</p>
              </div>
            </Link>

            <Link
              to="/portal/documents"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors"
            >
              <div className="text-2xl mr-3">📄</div>
              <div>
                <h3 className="font-medium text-gray-900">Upload Documents</h3>
                <p className="text-sm text-gray-600">Add required paperwork</p>
              </div>
            </Link>

            <Link
              to="/portal/support"
              className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors"
            >
              <div className="text-2xl mr-3">🎧</div>
              <div>
                <h3 className="font-medium text-gray-900">Get Support</h3>
                <p className="text-sm text-gray-600">Contact our team</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;