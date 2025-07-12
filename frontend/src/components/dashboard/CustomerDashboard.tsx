import React, { useState, useEffect } from 'react';
import type { Customer } from '../../types/customer';
import type { DocumentStats } from '../../types/documents';
import type { ComplianceStatistics } from '../../types/compliance';

interface CustomerDashboardProps {
  customer: Customer;
  onLogout: () => void;
}

interface DashboardStats {
  documents: DocumentStats;
  compliance: ComplianceStatistics;
  recentActivity: ActivityItem[];
}

interface ActivityItem {
  id: string;
  type: 'document' | 'loa' | 'edi' | 'compliance';
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

export const CustomerDashboard: React.FC<CustomerDashboardProps> = ({
  customer,
  onLogout
}) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      try {
        // This would be replaced with actual API calls
        const mockStats: DashboardStats = {
          documents: {
            total_documents: 45,
            total_size_bytes: 125000000,
            documents_by_type: {
              invoice: 15,
              packing_list: 12,
              certificate: 8,
              permit: 6,
              other: 4
            },
            documents_by_category: {
              import: 25,
              export: 15,
              compliance: 5
            },
            documents_by_status: {
              approved: 35,
              pending: 8,
              rejected: 2
            },
            documents_by_compliance: {
              compliant: 40,
              pending_review: 5
            },
            pending_review: 5,
            expiring_this_month: 3,
            compliance_issues: 2,
            recent_uploads: 8,
            top_uploaders: [],
            storage_by_type: {}
          },
          compliance: {
            total_requirements: 12,
            pending_requirements: 3,
            completed_requirements: 8,
            overdue_requirements: 1,
            compliance_rate: 75,
            upcoming_audits: 1,
            completed_audits: 2,
            open_findings: 2,
            critical_findings: 0,
            upcoming_assessments: 1,
            recent_reports: 3
          },
          recentActivity: [
            {
              id: '1',
              type: 'document',
              title: 'Invoice uploaded',
              description: 'Commercial invoice for shipment #SH001',
              timestamp: '2024-01-15T10:30:00Z',
              status: 'success'
            },
            {
              id: '2',
              type: 'compliance',
              title: 'Compliance requirement due',
              description: 'Annual security assessment due in 7 days',
              timestamp: '2024-01-14T15:45:00Z',
              status: 'warning'
            },
            {
              id: '3',
              type: 'loa',
              title: 'LOA signed',
              description: 'Digital Letter of Authority #LOA-2024-001',
              timestamp: '2024-01-13T09:15:00Z',
              status: 'success'
            }
          ]
        };

        setStats(mockStats);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-blue-600 bg-blue-100';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'document': return '📄';
      case 'loa': return '📝';
      case 'edi': return '🔄';
      case 'compliance': return '✅';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {customer.first_name}!
              </h1>
              <p className="text-gray-600">
                {customer.company_name && `${customer.company_name} • `}
                {customer.email}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <span className="text-2xl">📄</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Documents
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats?.documents.total_documents || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <span className="text-2xl">✅</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Compliance Rate
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats?.compliance.compliance_rate || 0}%
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <span className="text-2xl">⏰</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Pending Tasks
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats?.compliance.pending_requirements || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <span className="text-2xl">🚨</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Critical Issues
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats?.compliance.critical_findings || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Recent Activity
                </h3>
                <div className="space-y-4">
                  {stats?.recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <span className="text-xl">{getActivityIcon(activity.type)}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {activity.title}
                          </p>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                            {activity.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500">{activity.description}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Quick Actions
                </h3>
                <div className="space-y-3">
                  <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                    📄 Upload Document
                  </button>
                  <button className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                    📝 Create LOA
                  </button>
                  <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                    🔄 Register EDI Job
                  </button>
                  <button className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                    ✅ View Compliance
                  </button>
                </div>
              </div>
            </div>

            {/* Account Status */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Account Status
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Email Verified</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      customer.email_verified ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                    }`}>
                      {customer.email_verified ? 'Verified' : 'Pending'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Verification Status</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-blue-600 bg-blue-100">
                      {customer.verification_status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Member Since</span>
                    <span className="text-sm text-gray-900">
                      {new Date(customer.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};