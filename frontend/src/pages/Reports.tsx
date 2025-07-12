import React, { useState, useEffect } from 'react';
import { ProfessionalCard, ProfessionalCardHeader, ProfessionalCardContent } from '../components/ui/ProfessionalCard';
import { KPICard, KPIGrid } from '../components/ui/KPICard';
import { ActionToolbar } from '../components/ui/ActionToolbar';
import { ProfessionalTable } from '../components/ui/ProfessionalTable';
import { ProfessionalFilters, SearchBar } from '../components/ui/ProfessionalFilters';
import { reportsApi, type DashboardAnalytics, type TradeVolumeAnalytics, type DutySavingsAnalytics, type ClassificationAccuracyAnalytics, type Report } from '../services/reportsApi';

// Icon components for TypeScript compatibility
const ChartIcon: React.FC = () => <span>📊</span>;
const TrendIcon: React.FC = () => <span>📈</span>;
const DownloadIcon: React.FC = () => <span>⬇️</span>;
const CalendarIcon: React.FC = () => <span>📅</span>;
const FileIcon: React.FC = () => <span>📄</span>;
const AnalyticsIcon: React.FC = () => <span>📉</span>;

interface FilterValues {
  type: string;
  status: string;
  format: string;
}

const Reports: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'reports' | 'analytics' | 'templates'>('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [filterValues, setFilterValues] = useState<FilterValues>({
    type: '',
    status: '',
    format: ''
  });

  // Analytics data state
  const [dashboardAnalytics, setDashboardAnalytics] = useState<DashboardAnalytics | null>(null);
  const [tradeVolumeAnalytics, setTradeVolumeAnalytics] = useState<TradeVolumeAnalytics | null>(null);
  const [dutySavingsAnalytics, setDutySavingsAnalytics] = useState<DutySavingsAnalytics | null>(null);
  const [classificationAnalytics, setClassificationAnalytics] = useState<ClassificationAccuracyAnalytics | null>(null);
  const [reportsData, setReportsData] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load analytics data
  useEffect(() => {
    const loadAnalyticsData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [dashboard, tradeVolume, dutySavings, classification, reports] = await Promise.all([
          reportsApi.getDashboardAnalytics(),
          reportsApi.getTradeVolumeAnalytics(),
          reportsApi.getDutySavingsAnalytics(),
          reportsApi.getClassificationAccuracyAnalytics(),
          reportsApi.getReports(0, 50)
        ]);

        setDashboardAnalytics(dashboard);
        setTradeVolumeAnalytics(tradeVolume);
        setDutySavingsAnalytics(dutySavings);
        setClassificationAnalytics(classification);
        setReportsData(reports.reports);
      } catch (err) {
        console.error('Error loading analytics data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load analytics data');
        // Fallback to empty data for development
        setReportsData([]);
      } finally {
        setLoading(false);
      }
    };

    loadAnalyticsData();
  }, []);

  // Filter reports based on search and filters
  const filteredReports = reportsData.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !filterValues.type || report.type === filterValues.type;
    const matchesStatus = !filterValues.status || report.status === filterValues.status;
    const matchesFormat = !filterValues.format || report.format === filterValues.format;

    return matchesSearch && matchesType && matchesStatus && matchesFormat;
  });

  // Table columns configuration
  const columns = [
    {
      key: 'id',
      title: 'Report ID',
      width: '100px',
      sortable: true
    },
    {
      key: 'name',
      title: 'Name',
      width: '200px',
      sortable: true
    },
    {
      key: 'type',
      title: 'Type',
      width: '120px',
      sortable: true,
      render: (type: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          type === 'dashboard' ? 'bg-blue-100 text-blue-800' :
          type === 'trade_volume' ? 'bg-green-100 text-green-800' :
          type === 'duty_savings' ? 'bg-purple-100 text-purple-800' :
          type === 'classification_accuracy' ? 'bg-red-100 text-red-800' :
          'bg-orange-100 text-orange-800'
        }`}>
          {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </span>
      )
    },
    {
      key: 'status',
      title: 'Status',
      width: '120px',
      sortable: true,
      render: (status: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          status === 'generated' ? 'bg-green-100 text-green-800' :
          status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
          status === 'failed' ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      )
    },
    {
      key: 'created_at',
      title: 'Created',
      width: '150px',
      sortable: true,
      render: (date: string) => new Date(date).toLocaleDateString()
    },
    {
      key: 'format',
      title: 'Format',
      width: '80px',
      sortable: true,
      render: (format: string) => format.toUpperCase()
    },
    {
      key: 'file_size',
      title: 'Size',
      width: '80px',
      sortable: true,
      render: (size: number | undefined) => size ? `${(size / 1024).toFixed(1)} KB` : 'N/A'
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '120px',
      render: (value: any, record: Report) => (
        <div className="flex gap-2">
          <button
            className="text-blue-600 hover:text-blue-800 text-sm"
            onClick={() => handleDownloadReport(record.id)}
          >
            Download
          </button>
          <button
            className="text-green-600 hover:text-green-800 text-sm"
            onClick={() => handleViewReport(record.id)}
          >
            View
          </button>
        </div>
      )
    }
  ];

  // Action handlers
  const handleDownloadReport = async (reportId: string) => {
    try {
      await reportsApi.downloadReportAsFile(reportId);
    } catch (err) {
      console.error('Error downloading report:', err);
    }
  };

  const handleViewReport = (reportId: string) => {
    console.log('Viewing report:', reportId);
  };

  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      await reportsApi.generateQuickReport('dashboard');
      // Reload reports
      const reports = await reportsApi.getReports(0, 50);
      setReportsData(reports.reports);
    } catch (err) {
      console.error('Error generating report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleReport = () => {
    console.log('Scheduling report');
  };

  // Action toolbar configuration
  const toolbarActions = [
    {
      id: 'generate',
      label: 'Generate Report',
      onClick: handleGenerateReport,
      variant: 'primary' as const
    },
    {
      id: 'schedule',
      label: 'Schedule Report',
      onClick: handleScheduleReport,
      variant: 'default' as const
    },
    {
      id: 'export',
      label: 'Export List',
      onClick: () => console.log('Exporting report list'),
      variant: 'default' as const
    },
    {
      id: 'refresh',
      label: 'Refresh',
      onClick: () => window.location.reload(),
      variant: 'default' as const
    }
  ];

  // Filter options
  const filterOptions = [
    {
      key: 'type',
      label: 'Type',
      type: 'select' as const,
      options: [
        { label: 'All Types', value: '' },
        { label: 'Dashboard', value: 'dashboard' },
        { label: 'Trade Volume', value: 'trade_volume' },
        { label: 'Duty Savings', value: 'duty_savings' },
        { label: 'Classification Accuracy', value: 'classification_accuracy' },
        { label: 'Custom', value: 'custom' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select' as const,
      options: [
        { label: 'All Statuses', value: '' },
        { label: 'Generated', value: 'generated' },
        { label: 'Processing', value: 'processing' },
        { label: 'Failed', value: 'failed' },
        { label: 'Scheduled', value: 'scheduled' }
      ]
    },
    {
      key: 'format',
      label: 'Format',
      type: 'select' as const,
      options: [
        { label: 'All Formats', value: '' },
        { label: 'JSON', value: 'json' },
        { label: 'CSV', value: 'csv' },
        { label: 'PDF', value: 'pdf' }
      ]
    }
  ];

  // Calculate KPI data from analytics
  const totalReports = reportsData.length;
  const generatedReports = reportsData.filter(r => r.status === 'generated').length;
  const scheduledReports = 0; // Will be calculated from schedules API
  const successRate = totalReports > 0 ? ((generatedReports / totalReports) * 100) : 0;

  // Tab navigation styles
  const tabButtonClass = (tabName: string) => `
    px-4 py-2 font-medium text-sm border-b-2 transition-colors duration-200
    ${activeTab === tabName 
      ? 'border-blue-500 text-blue-600 bg-blue-50' 
      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
    }
  `;

  if (loading && !dashboardAnalytics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error && !dashboardAnalytics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error loading analytics data: {error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-gray-600 mt-1">Generate, schedule, and manage comprehensive business reports</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleGenerateReport}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <FileIcon />
            Generate Report
          </button>
          <button
            onClick={handleScheduleReport}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <CalendarIcon />
            Schedule Report
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={tabButtonClass('overview')}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={tabButtonClass('reports')}
          >
            Reports
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={tabButtonClass('analytics')}
          >
            Analytics
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={tabButtonClass('templates')}
          >
            Templates
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* KPI Grid */}
          <KPIGrid>
            <KPICard
              label="Total Reports"
              value={totalReports.toString()}
              icon={FileIcon}
              trend="+12%"
              subtitle="All time"
            />
            <KPICard
              label="Success Rate"
              value={`${successRate.toFixed(1)}%`}
              icon={TrendIcon}
              trend="+2.3%"
              subtitle="Last 30 days"
            />
            <KPICard
              label="Generated Today"
              value={generatedReports.toString()}
              icon={ChartIcon}
              trend="+5"
              subtitle="Completed reports"
            />
            <KPICard
              label="Scheduled Reports"
              value={scheduledReports.toString()}
              icon={CalendarIcon}
              trend="0"
              subtitle="Upcoming"
            />
          </KPIGrid>

          {/* Recent Reports */}
          <ProfessionalCard variant="default">
            <ProfessionalCardHeader>
              <h3 className="text-lg font-semibold">Recent Reports</h3>
              <p className="text-sm text-gray-600">Latest generated reports</p>
            </ProfessionalCardHeader>
            <ProfessionalCardContent>
              <div className="space-y-4">
                {reportsData.slice(0, 5).map((report) => (
                  <div key={report.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{report.name}</h4>
                      <p className="text-sm text-gray-600">Report ID: {report.id}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span>Type: {report.type.replace('_', ' ')}</span>
                        <span>Format: {report.format.toUpperCase()}</span>
                        <span>Size: {report.file_size ? `${(report.file_size / 1024).toFixed(1)} KB` : 'N/A'}</span>
                        <span>Created: {new Date(report.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        report.status === 'generated' ? 'bg-green-100 text-green-800' :
                        report.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        report.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                      </span>
                      <button
                        onClick={() => handleDownloadReport(report.id)}
                        className="text-blue-600 hover:text-blue-800 p-1"
                      >
                        <DownloadIcon />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </ProfessionalCardContent>
          </ProfessionalCard>
        </div>
      )}

      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Search and Filters */}
          <div className="space-y-4">
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Search reports by name or ID..."
            />
            <ProfessionalFilters
              filters={filterOptions}
              values={filterValues}
              onChange={(values) => setFilterValues(values as FilterValues)}
            />
          </div>

          {/* Action Toolbar */}
          <ActionToolbar
            actions={toolbarActions}
            selectedCount={selectedRowKeys.length}
            totalCount={filteredReports.length}
            showSelectionInfo={true}
            className="bg-white border border-gray-200 rounded-lg"
          />

          {/* Reports Table */}
          <ProfessionalCard variant="default">
            <ProfessionalCardContent>
              <ProfessionalTable
                columns={columns}
                data={filteredReports}
                rowKey="id"
                selection={{
                  selectedRowKeys,
                  onChange: setSelectedRowKeys
                }}
                pagination={{
                  current: 1,
                  pageSize: 10,
                  total: filteredReports.length,
                  onChange: (page: number, pageSize: number) => console.log('Page changed:', page, pageSize)
                }}
                scroll={{ x: 1200 }}
              />
            </ProfessionalCardContent>
          </ProfessionalCard>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* Analytics KPIs */}
          <KPIGrid>
            <KPICard
              label="Reports Generated"
              value={dashboardAnalytics?.total_shipments.value.toString() || "0"}
              icon={ChartIcon}
              trend={dashboardAnalytics?.total_shipments.change_percentage ? `+${dashboardAnalytics.total_shipments.change_percentage}%` : "+0%"}
              subtitle="Last 30 days"
            />
            <KPICard
              label="Compliance Rate"
              value={dashboardAnalytics?.compliance_rate.value ? `${dashboardAnalytics.compliance_rate.value.toFixed(1)}%` : "0%"}
              icon={TrendIcon}
              trend={dashboardAnalytics?.compliance_rate.change_percentage ? `+${dashboardAnalytics.compliance_rate.change_percentage}%` : "+0%"}
              subtitle="Performance metric"
            />
            <KPICard
              label="Cost Savings"
              value={dutySavingsAnalytics ? `$${dutySavingsAnalytics.total_savings.toLocaleString()}` : "$0"}
              icon={DownloadIcon}
              trend={dutySavingsAnalytics ? `${dutySavingsAnalytics.savings_rate.toFixed(1)}%` : "0%"}
              subtitle="Total savings"
            />
            <KPICard
              label="Classification Accuracy"
              value={classificationAnalytics ? `${classificationAnalytics.overall_accuracy.toFixed(1)}%` : "0%"}
              icon={AnalyticsIcon}
              trend={classificationAnalytics ? `${classificationAnalytics.total_classifications} items` : "0 items"}
              subtitle="Accuracy rate"
            />
          </KPIGrid>

          {/* Analytics Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ProfessionalCard variant="default">
              <ProfessionalCardHeader>
                <h3 className="text-lg font-semibold">Trade Volume Trends</h3>
                <p className="text-sm text-gray-600">Shipment volume over time</p>
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                  <div className="text-center">
                    <ChartIcon />
                    <p className="text-gray-500 mt-2">Chart visualization would be rendered here</p>
                    <p className="text-sm text-gray-400">
                      {tradeVolumeAnalytics ? 
                        `${tradeVolumeAnalytics.shipment_count} shipments, ${tradeVolumeAnalytics.growth_rate.toFixed(1)}% growth` :
                        'Loading trade volume data...'
                      }
                    </p>
                  </div>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>

            <ProfessionalCard variant="default">
              <ProfessionalCardHeader>
                <h3 className="text-lg font-semibold">Duty Savings Analysis</h3>
                <p className="text-sm text-gray-600">Savings breakdown by category</p>
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="space-y-4">
                  {dutySavingsAnalytics?.top_saving_products.slice(0, 5).map((product, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{product.product}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${product.percentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600 w-16">${product.savings.toLocaleString()}</span>
                      </div>
                    </div>
                  )) || (
                    <div className="text-center text-gray-500">
                      <p>Loading duty savings data...</p>
                    </div>
                  )}
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="space-y-6">
          {/* Template Categories */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <ProfessionalCard variant="default">
              <ProfessionalCardHeader>
                <h3 className="text-lg font-semibold">Analytics Templates</h3>
                <p className="text-sm text-gray-600">Pre-built analytics report templates</p>
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="space-y-3">
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Dashboard Analytics</div>
                    <div className="text-xs text-gray-600">Comprehensive dashboard overview</div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Trade Volume Analysis</div>
                    <div className="text-xs text-gray-600">Trade volume trends and insights</div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Duty Savings Report</div>
                    <div className="text-xs text-gray-600">Cost savings analysis</div>
                  </div>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>

            <ProfessionalCard variant="default">
              <ProfessionalCardHeader>
                <h3 className="text-lg font-semibold">Compliance Templates</h3>
                <p className="text-sm text-gray-600">Compliance and accuracy reporting</p>
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="space-y-3">
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Classification Accuracy</div>
                    <div className="text-xs text-gray-600">Accuracy metrics and insights</div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Compliance Audit</div>
                    <div className="text-xs text-gray-600">Compliance status overview</div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Risk Assessment</div>
                    <div className="text-xs text-gray-600">Risk evaluation report</div>
                  </div>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>

            <ProfessionalCard variant="default">
              <ProfessionalCardHeader>
                <h3 className="text-lg font-semibold">Custom Templates</h3>
                <p className="text-sm text-gray-600">User-defined report templates</p>
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="space-y-3">
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Custom Report 1</div>
                    <div className="text-xs text-gray-600">User-defined template</div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Custom Report 2</div>
                    <div className="text-xs text-gray-600">User-defined template</div>
                  </div>
                  <div className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <div className="font-medium text-sm">Custom Report 3</div>
                    <div className="text-xs text-gray-600">User-defined template</div>
                  </div>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>
          </div>

          {/* Template Actions */}
          <ProfessionalCard variant="default">
            <ProfessionalCardHeader>
              <h3 className="text-lg font-semibold">Template Management</h3>
              <p className="text-sm text-gray-600">Create and manage custom report templates</p>
            </ProfessionalCardHeader>
            <ProfessionalCardContent>
              <div className="flex gap-4">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  Create New Template
                </button>
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                  Import Template
                </button>
                <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                  Export Templates
                </button>
              </div>
            </ProfessionalCardContent>
          </ProfessionalCard>
        </div>
      )}
    </div>
  );
};

export default Reports;