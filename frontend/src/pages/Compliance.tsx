import React, { useState, useEffect } from 'react';
import { ProfessionalCard, ProfessionalCardHeader, ProfessionalCardContent, ProfessionalCardFooter } from '../components/ui/ProfessionalCard';
import { KPICard, KPIGrid } from '../components/ui/KPICard';
import { ActionToolbar } from '../components/ui/ActionToolbar';
import { ProfessionalTable } from '../components/ui/ProfessionalTable';
import { SearchBar, ProfessionalFilters } from '../components/ui/ProfessionalFilters';
import {
  complianceApi,
  formatDate,
  formatDateShort,
  getComplianceStatusColor,
  getComplianceStatusBadgeColor,
  getSeverityColor,
  getSeverityBadgeColor,
  formatComplianceScore
} from '../services/complianceApi';
import type {
  ComplianceOverview,
  ComplianceRequirement,
  ComplianceAlert,
  ComplianceAudit
} from '../services/complianceApi';

// Icon components for KPICard
const TargetIcon = ({ className }: { className?: string }) => <span className={className}>🎯</span>;
const CheckIcon = ({ className }: { className?: string }) => <span className={className}>✅</span>;
const XIcon = ({ className }: { className?: string }) => <span className={className}>❌</span>;
const ClockIcon = ({ className }: { className?: string }) => <span className={className}>🕐</span>;
const ChartIcon = ({ className }: { className?: string }) => <span className={className}>📊</span>;
const AlertIcon = ({ className }: { className?: string }) => <span className={className}>⚠️</span>;

const Compliance: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterValues, setFilterValues] = useState({
    category: '',
    status: '',
    priority: '',
    riskLevel: ''
  });
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  
  // API data state
  const [overview, setOverview] = useState<ComplianceOverview | null>(null);
  const [requirements, setRequirements] = useState<ComplianceRequirement[]>([]);
  const [alerts, setAlerts] = useState<ComplianceAlert[]>([]);
  const [audits, setAudits] = useState<ComplianceAudit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load compliance data
  useEffect(() => {
    const loadComplianceData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Load all compliance data in parallel
        const [overviewData, requirementsData, alertsData] = await Promise.all([
          complianceApi.getOverview(),
          complianceApi.getRequirements(),
          complianceApi.getAlerts(10) // Get recent alerts
        ]);

        setOverview(overviewData);
        setRequirements(requirementsData);
        setAlerts(alertsData);

        console.log('✅ Compliance data loaded successfully');
      } catch (err) {
        console.error('❌ Error loading compliance data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load compliance data');
      } finally {
        setLoading(false);
      }
    };

    loadComplianceData();
  }, []);

  // Load audit data when audits tab is active
  useEffect(() => {
    if (activeTab === 'audits' && audits.length === 0) {
      const loadAudits = async () => {
        try {
          // For now, we'll use a mock audit ID since we don't have a list audits endpoint
          // In a real implementation, you'd have a getAudits() method
          const mockAuditId = 'audit-001';
          const auditData = await complianceApi.getAudit(mockAuditId);
          setAudits([auditData]);
        } catch (err) {
          console.error('Error loading audit data:', err);
          // Don't set error state for audits as it's not critical
        }
      };

      loadAudits();
    }
  }, [activeTab, audits.length]);

  // Filter compliance requirements based on search and filters
  const filteredRequirements = requirements.filter(req => {
    const matchesSearch = req.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         req.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (req.assigned_to && req.assigned_to.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = !filterValues.category || req.category === filterValues.category;
    const matchesStatus = !filterValues.status || req.status === filterValues.status;
    const matchesPriority = !filterValues.priority || req.priority === filterValues.priority;
    const matchesRiskLevel = !filterValues.riskLevel || req.risk_level === filterValues.riskLevel;

    return matchesSearch && matchesCategory && matchesStatus && matchesPriority && matchesRiskLevel;
  });

  // Calculate KPI data from real API data
  const totalRequirements = requirements.length;
  const compliantCount = requirements.filter(req => req.status.toLowerCase() === 'compliant').length;
  const nonCompliantCount = requirements.filter(req => req.status.toLowerCase() === 'non-compliant').length;
  const pendingCount = requirements.filter(req =>
    req.status.toLowerCase() === 'pending' ||
    req.status.toLowerCase() === 'under review' ||
    req.status.toLowerCase() === 'in progress'
  ).length;
  const averageScore = totalRequirements > 0
    ? Math.round(requirements.reduce((sum, req) => sum + req.compliance_score, 0) / totalRequirements)
    : 0;
  const highRiskCount = requirements.filter(req => req.risk_level.toLowerCase() === 'high').length;

  // Action toolbar configuration
  const toolbarActions = [
    {
      id: 'create',
      label: 'New Requirement',
      icon: '➕',
      onClick: () => {
        console.log('Creating new requirement...');
      },
      variant: 'primary' as const
    },
    {
      id: 'refresh',
      label: 'Refresh',
      icon: '🔄',
      onClick: async () => {
        console.log('Refreshing compliance data...');
        setLoading(true);
        try {
          const [overviewData, requirementsData, alertsData] = await Promise.all([
            complianceApi.getOverview(),
            complianceApi.getRequirements(),
            complianceApi.getAlerts(10)
          ]);
          setOverview(overviewData);
          setRequirements(requirementsData);
          setAlerts(alertsData);
          setError(null);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to refresh data');
        } finally {
          setLoading(false);
        }
      },
      variant: 'default' as const
    },
    {
      id: 'export',
      label: 'Export Report',
      icon: '📥',
      onClick: () => {
        console.log('Exporting compliance report...');
      },
      variant: 'default' as const
    },
    {
      id: 'import',
      label: 'Import Requirements',
      icon: '📤',
      onClick: () => {
        console.log('Importing requirements...');
      },
      variant: 'default' as const
    }
  ];

  // Table columns configuration
  const tableColumns = [
    {
      key: 'id',
      title: 'ID',
      dataIndex: 'id',
      width: '80px',
      sorter: true
    },
    {
      key: 'title',
      title: 'Requirement',
      dataIndex: 'title',
      sorter: true,
      render: (value: string, record: any) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{record.description}</div>
        </div>
      )
    },
    {
      key: 'category',
      title: 'Category',
      dataIndex: 'category',
      width: '120px',
      sorter: true,
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'Import' ? 'bg-blue-100 text-blue-800' :
          value === 'Export' ? 'bg-green-100 text-green-800' :
          value === 'Trade' ? 'bg-purple-100 text-purple-800' :
          value === 'Regulatory' ? 'bg-orange-100 text-orange-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'status',
      title: 'Status',
      dataIndex: 'status',
      width: '130px',
      sorter: true,
      render: (value: string) => {
        const statusConfig = {
          'Compliant': { color: 'text-green-800 bg-green-100', icon: '✅' },
          'Non-Compliant': { color: 'text-red-800 bg-red-100', icon: '❌' },
          'Under Review': { color: 'text-orange-800 bg-orange-100', icon: '🕐' },
          'Pending': { color: 'text-blue-800 bg-blue-100', icon: '⚠️' }
        };
        const config = statusConfig[value as keyof typeof statusConfig];
        const icon = config?.icon || '⚠️';
        
        return (
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config?.color || 'bg-gray-100 text-gray-800'}`}>
            <span className="mr-1">{icon}</span>
            {value}
          </span>
        );
      }
    },
    {
      key: 'priority',
      title: 'Priority',
      dataIndex: 'priority',
      width: '100px',
      sorter: true,
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'Critical' ? 'bg-red-100 text-red-800' :
          value === 'High' ? 'bg-orange-100 text-orange-800' :
          value === 'Medium' ? 'bg-orange-100 text-orange-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'compliance_score',
      title: 'Score',
      dataIndex: 'compliance_score',
      width: '80px',
      sorter: true,
      render: (value: number) => (
        <div className="text-center">
          <div className={`font-medium ${
            value >= 90 ? 'text-green-600' :
            value >= 80 ? 'text-orange-600' :
            'text-red-600'
          }`}>
            {value}%
          </div>
        </div>
      )
    },
    {
      key: 'assigned_to',
      title: 'Assigned To',
      dataIndex: 'assigned_to',
      width: '120px',
      sorter: true
    },
    {
      key: 'due_date',
      title: 'Due Date',
      dataIndex: 'due_date',
      width: '110px',
      sorter: true,
      render: (value: string) => {
        if (!value) return <span className="text-gray-400">-</span>;
        const dueDate = new Date(value);
        const today = new Date();
        const isOverdue = dueDate < today;
        const isDueSoon = (dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24) <= 7;
        
        return (
          <span className={`text-sm ${
            isOverdue ? 'text-red-600 font-medium' :
            isDueSoon ? 'text-orange-600 font-medium' :
            'text-gray-600'
          }`}>
            {formatDateShort(value)}
          </span>
        );
      }
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '120px',
      render: (record: any) => (
        <div className="flex space-x-2">
          <button
            onClick={() => console.log('View requirement:', record.id)}
            className="text-blue-600 hover:text-blue-800"
            title="View Details"
          >
            👁️
          </button>
          <button
            onClick={() => console.log('Edit requirement:', record.id)}
            className="text-green-600 hover:text-green-800"
            title="Edit"
          >
            ✏️
          </button>
          <button
            onClick={() => console.log('Delete requirement:', record.id)}
            className="text-red-600 hover:text-red-800"
            title="Delete"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  // Filter options
  const filterOptions = [
    {
      key: 'category',
      label: 'Category',
      type: 'select' as const,
      options: [
        { label: 'All Categories', value: '' },
        { label: 'Import', value: 'Import' },
        { label: 'Export', value: 'Export' },
        { label: 'Trade', value: 'Trade' },
        { label: 'Regulatory', value: 'Regulatory' },
        { label: 'Documentation', value: 'Documentation' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select' as const,
      options: [
        { label: 'All Statuses', value: '' },
        { label: 'Compliant', value: 'Compliant' },
        { label: 'Non-Compliant', value: 'Non-Compliant' },
        { label: 'Under Review', value: 'Under Review' },
        { label: 'Pending', value: 'Pending' }
      ]
    },
    {
      key: 'priority',
      label: 'Priority',
      type: 'select' as const,
      options: [
        { label: 'All Priorities', value: '' },
        { label: 'Critical', value: 'Critical' },
        { label: 'High', value: 'High' },
        { label: 'Medium', value: 'Medium' },
        { label: 'Low', value: 'Low' }
      ]
    },
    {
      key: 'riskLevel',
      label: 'Risk Level',
      type: 'select' as const,
      options: [
        { label: 'All Risk Levels', value: '' },
        { label: 'High', value: 'High' },
        { label: 'Medium', value: 'Medium' },
        { label: 'Low', value: 'Low' }
      ]
    }
  ];

  // Custom tab navigation component
  const TabNavigation = () => {
    const tabs = [
      { id: 'overview', label: 'Overview', icon: '📊' },
      { id: 'requirements', label: 'Requirements', icon: '📋' },
      { id: 'audits', label: 'Audits', icon: '🛡️' },
      { id: 'reports', label: 'Reports', icon: '📈' }
    ];

    return (
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    );
  };

  // Overview tab content
  const OverviewContent = () => (
    <div className="space-y-6">
      {/* KPI Grid */}
      <KPIGrid>
        <KPICard
          icon={TargetIcon}
          label="Total Requirements"
          value={totalRequirements.toString()}
          color="blue"
        />
        <KPICard
          icon={CheckIcon}
          label="Compliant"
          value={compliantCount.toString()}
          color="green"
        />
        <KPICard
          icon={XIcon}
          label="Non-Compliant"
          value={nonCompliantCount.toString()}
          color="red"
        />
        <KPICard
          icon={ClockIcon}
          label="Pending Review"
          value={pendingCount.toString()}
          color="orange"
        />
        <KPICard
          icon={ChartIcon}
          label="Average Score"
          value={`${averageScore}%`}
          color="purple"
        />
        <KPICard
          icon={AlertIcon}
          label="High Risk"
          value={highRiskCount.toString()}
          color="orange"
        />
      </KPIGrid>

      {/* Compliance Summary Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ProfessionalCard variant="default">
          <ProfessionalCardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Compliance Status Distribution</h3>
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-green-500 mr-2">✅</span>
                  <span className="text-sm font-medium">Compliant</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 mr-2">{compliantCount}</span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${(compliantCount / totalRequirements) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-red-500 mr-2">❌</span>
                  <span className="text-sm font-medium">Non-Compliant</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 mr-2">{nonCompliantCount}</span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full" 
                      style={{ width: `${(nonCompliantCount / totalRequirements) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-orange-500 mr-2">🕐</span>
                  <span className="text-sm font-medium">Under Review</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-gray-600 mr-2">{pendingCount}</span>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-orange-500 h-2 rounded-full" 
                      style={{ width: `${(pendingCount / totalRequirements) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>

        <ProfessionalCard variant="alert">
          <ProfessionalCardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Recent Audit Results</h3>
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="space-y-4">
              {audits.slice(0, 3).map((audit) => (
                <div key={audit.audit_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-sm">{audit.audit_type}</div>
                    <div className="text-xs text-gray-500">{audit.auditor}</div>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-medium ${
                      audit.overall_score >= 90 ? 'text-green-600' :
                      audit.overall_score >= 80 ? 'text-orange-600' :
                      'text-red-600'
                    }`}>
                      {audit.overall_score}%
                    </div>
                    <div className="text-xs text-gray-500">{audit.status}</div>
                  </div>
                </div>
              ))}
              {audits.length === 0 && !loading && (
                <div className="text-center text-gray-500 py-4">
                  No audit data available
                </div>
              )}
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>
      </div>
    </div>
  );

  // Requirements tab content
  const RequirementsContent = () => (
    <div className="space-y-6">
      <ActionToolbar
        actions={toolbarActions}
        selectedCount={selectedRowKeys.length}
        showSelectionInfo={true}
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-1">
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            placeholder="Search requirements..."
          />
        </div>
        <div className="lg:col-span-3">
          <ProfessionalFilters
            filters={filterOptions}
            values={filterValues}
            onChange={(values) => setFilterValues(prev => ({ ...prev, ...values }))}
          />
        </div>
      </div>

      <ProfessionalTable
        columns={tableColumns}
        data={filteredRequirements}
        loading={false}
        rowKey="id"
        pagination={{
          current: 1,
          pageSize: 10,
          total: filteredRequirements.length,
          onChange: (page: number, pageSize: number) => {
            console.log('Pagination changed:', page, pageSize);
          }
        }}
        selection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys
        }}
        scroll={{ x: 1200 }}
      />
    </div>
  );

  // Audits tab content
  const AuditsContent = () => (
    <div className="space-y-6">
      {loading && (
        <div className="text-center py-8">
          <div className="text-gray-500">Loading audit data...</div>
        </div>
      )}
      
      {error && (
        <div className="text-center py-8">
          <div className="text-red-500">Error loading audit data: {error}</div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {audits.map((audit) => (
          <ProfessionalCard key={audit.audit_id} variant="default">
            <ProfessionalCardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">{audit.audit_type}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getComplianceStatusBadgeColor(audit.status)}`}>
                  {audit.status}
                </span>
              </div>
            </ProfessionalCardHeader>
            <ProfessionalCardContent>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Auditor:</span>
                  <span className="font-medium">{audit.auditor}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Period:</span>
                  <span className="font-medium">{formatDateShort(audit.start_date)} - {audit.end_date ? formatDateShort(audit.end_date) : 'Ongoing'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Findings:</span>
                  <span className="font-medium">{audit.findings.length} total</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Score:</span>
                  <span className={`font-medium ${getComplianceStatusColor(audit.risk_level)}`}>
                    {formatComplianceScore(audit.overall_score)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Risk Level:</span>
                  <span className={`font-medium ${getComplianceStatusColor(audit.risk_level)}`}>
                    {audit.risk_level}
                  </span>
                </div>
              </div>
            </ProfessionalCardContent>
            <ProfessionalCardFooter>
              <button
                onClick={() => console.log('View audit details:', audit.audit_id)}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                View Details
              </button>
            </ProfessionalCardFooter>
          </ProfessionalCard>
        ))}
        
        {audits.length === 0 && !loading && !error && (
          <div className="col-span-full text-center py-8">
            <div className="text-gray-500">No audit data available</div>
          </div>
        )}
      </div>
    </div>
  );

  // Reports tab content
  const ReportsContent = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProfessionalCard variant="default">
          <ProfessionalCardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Compliance Summary Report</h3>
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <p className="text-sm text-gray-600 mb-4">
              Comprehensive overview of all compliance requirements and their current status.
            </p>
            <div className="flex items-center text-sm text-gray-500">
              <span className="mr-1">📅</span>
              Last generated: {new Date().toLocaleDateString()}
            </div>
          </ProfessionalCardContent>
          <ProfessionalCardFooter>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
              Generate Report
            </button>
          </ProfessionalCardFooter>
        </ProfessionalCard>

        <ProfessionalCard variant="default">
          <ProfessionalCardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Audit Trail Report</h3>
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <p className="text-sm text-gray-600 mb-4">
              Detailed audit trail showing all compliance activities and changes.
            </p>
            <div className="flex items-center text-sm text-gray-500">
              <span className="mr-1">📅</span>
              Last generated: {new Date().toLocaleDateString()}
            </div>
          </ProfessionalCardContent>
          <ProfessionalCardFooter>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
              Generate Report
            </button>
          </ProfessionalCardFooter>
        </ProfessionalCard>

        <ProfessionalCard variant="default">
          <ProfessionalCardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Risk Assessment Report</h3>
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <p className="text-sm text-gray-600 mb-4">
              Risk analysis and assessment of all compliance requirements.
            </p>
            <div className="flex items-center text-sm text-gray-500">
              <span className="mr-1">📅</span>
              Last generated: {new Date().toLocaleDateString()}
            </div>
          </ProfessionalCardContent>
          <ProfessionalCardFooter>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
              Generate Report
            </button>
          </ProfessionalCardFooter>
        </ProfessionalCard>
      </div>
    </div>
  );

  // Render tab content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewContent />;
      case 'requirements':
        return <RequirementsContent />;
      case 'audits':
        return <AuditsContent />;
      case 'reports':
        return <ReportsContent />;
      default:
        return <OverviewContent />;
    }
  };

  // Show loading state
  if (loading && !overview && requirements.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Compliance Management</h1>
            <p className="text-gray-600">Monitor and manage compliance requirements, audits, and reports</p>
          </div>
        </div>
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">Loading compliance data...</div>
          <div className="mt-2 text-sm text-gray-400">Please wait while we fetch your compliance information</div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !overview && requirements.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Compliance Management</h1>
            <p className="text-gray-600">Monitor and manage compliance requirements, audits, and reports</p>
          </div>
        </div>
        <div className="text-center py-12">
          <div className="text-red-500 text-lg">❌ Error Loading Compliance Data</div>
          <div className="mt-2 text-sm text-gray-600">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Compliance Management</h1>
          <p className="text-gray-600">Monitor and manage compliance requirements, audits, and reports</p>
        </div>
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <div className="text-red-800 text-sm">⚠️ {error}</div>
          </div>
        )}
      </div>

      <TabNavigation />
      {renderTabContent()}
    </div>
  );
};

export default Compliance;