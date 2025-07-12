import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FiFileText,
  FiUpload,
  FiDownload,
  FiEye,
  FiEdit3,
  FiTrash2,
  FiShare2,
  FiClock,
  FiCheckCircle,
  FiAlertCircle,
  FiXCircle,
  FiFilter,
  FiSearch,
  FiPlus,
  FiFolder,
  FiArchive,
  FiShield,
  FiGlobe,
  FiCalendar,
  FiUser,
  FiTag,
  FiRefreshCw,
  FiMoreHorizontal
} from 'react-icons/fi';

// Import Professional Components
import {
  ProfessionalCard,
  ProfessionalCardHeader,
  ProfessionalCardContent,
  ProfessionalCardFooter
} from '../components/ui/ProfessionalCard';
import { KPICard, KPIGrid } from '../components/ui/KPICard';
import { ActionToolbar } from '../components/ui/ActionToolbar';
import { ProfessionalTable } from '../components/ui/ProfessionalTable';
import { ProfessionalFilters, SearchBar, QuickFilters } from '../components/ui/ProfessionalFilters';

// Import API Service
import { DocumentsApiService, type Document, type DocumentSummary, type DocumentStats as APIDocumentStats, type DocumentCategoryData } from '../services/documentsApi';

// Document Types and Interfaces - Use API types
type DocumentType = DocumentSummary; // Use DocumentSummary for list display

interface DocumentStats {
  totalDocuments: number;
  pendingReview: number;
  expiringThisMonth: number;
  complianceIssues: number;
  storageUsed: number;
  recentUploads: number;
}

const Documents: React.FC = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterValues, setFilterValues] = useState<any>({});
  const [stats, setStats] = useState<DocumentStats>({
    totalDocuments: 0,
    pendingReview: 0,
    expiringThisMonth: 0,
    complianceIssues: 0,
    storageUsed: 0,
    recentUploads: 0
  });
  const [categories, setCategories] = useState<DocumentCategoryData[]>([]);

  // Load data on component mount
  useEffect(() => {
    loadDocuments();
    loadCategories();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      
      // Load documents from API
      const documentsResponse = await DocumentsApiService.getDocuments();
      const documents = documentsResponse.documents;
      
      setDocuments(documents);
      setFilteredDocuments(documents);

      // Load stats from API
      const statsResponse = await DocumentsApiService.getDocumentStats();
      
      setStats({
        totalDocuments: statsResponse.total_documents,
        pendingReview: statsResponse.pending_review,
        expiringThisMonth: statsResponse.expiring_this_month,
        complianceIssues: statsResponse.compliance_issues,
        storageUsed: statsResponse.total_size_bytes,
        recentUploads: statsResponse.recent_uploads
      });

    } catch (error) {
      console.error('Error loading documents:', error);
      // Keep empty state on error
      setDocuments([]);
      setFilteredDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const categoriesResponse = await DocumentsApiService.getCategories();
      setCategories(categoriesResponse);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  // Filter and search logic
  useEffect(() => {
    let filtered = documents;

    // Apply tab filter
    if (activeTab !== 'all') {
      switch (activeTab) {
        case 'import':
          filtered = filtered.filter(doc => doc.category === 'IMPORT');
          break;
        case 'export':
          filtered = filtered.filter(doc => doc.category === 'EXPORT');
          break;
        case 'compliance':
          filtered = filtered.filter(doc => doc.category === 'COMPLIANCE' || doc.category === 'REGULATORY');
          break;
        case 'pending':
          filtered = filtered.filter(doc => doc.status === 'PENDING_REVIEW' || doc.status === 'DRAFT');
          break;
        case 'expiring':
          const nextMonth = new Date();
          nextMonth.setMonth(nextMonth.getMonth() + 1);
          filtered = filtered.filter(doc =>
            doc.expiry_date && new Date(doc.expiry_date) <= nextMonth
          );
          break;
      }
    }

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(doc =>
        doc.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.client_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.hs_code?.includes(searchQuery) ||
        doc.shipment_ref?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (doc.tags && doc.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase())))
      );
    }

    // Apply additional filters
    if (filterValues.type) {
      filtered = filtered.filter(doc => doc.document_type === filterValues.type);
    }
    if (filterValues.status) {
      filtered = filtered.filter(doc => doc.status === filterValues.status);
    }
    if (filterValues.client) {
      filtered = filtered.filter(doc => doc.client_name?.toLowerCase().includes(filterValues.client.toLowerCase()));
    }

    setFilteredDocuments(filtered);
  }, [documents, activeTab, searchQuery, filterValues]);

  // Action handlers
  const handleUpload = () => {
    console.log('Upload document');
  };

  const handleBulkAction = (actionId: string) => {
    console.log('Bulk action:', actionId, 'on documents:', selectedDocuments);
  };

  const handleDocumentAction = (action: string, documentId: number) => {
    console.log('Document action:', action, 'on document:', documentId);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'pending': return 'text-orange-600 bg-orange-100';
      case 'draft': return 'text-blue-600 bg-blue-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'expired': return 'text-gray-600 bg-gray-100';
      case 'archived': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getComplianceColor = (status: string): string => {
    switch (status) {
      case 'compliant': return 'text-green-600';
      case 'non_compliant': return 'text-red-600';
      case 'pending_review': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'invoice': return <FiFileText className="w-4 h-4" />;
      case 'certificate': return <FiShield className="w-4 h-4" />;
      case 'permit': return <FiCheckCircle className="w-4 h-4" />;
      case 'declaration': return <FiGlobe className="w-4 h-4" />;
      case 'ruling': return <FiArchive className="w-4 h-4" />;
      default: return <FiFileText className="w-4 h-4" />;
    }
  };

  // Table columns
  const columns = [
    {
      key: 'title',
      title: 'Document Name',
      sortable: true,
      render: (value: string, record: Document) => (
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-blue-100 text-blue-600">
            {getTypeIcon(record.document_type)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-medium text-gray-900 truncate">{value}</div>
            <div className="text-sm text-gray-500 truncate">{record.description}</div>
            {record.is_confidential && (
              <div className="flex items-center gap-1 mt-1">
                <FiShield className="w-3 h-3 text-red-500" />
                <span className="text-xs text-red-600">Confidential</span>
              </div>
            )}
          </div>
        </div>
      )
    },
    {
      key: 'document_type',
      title: 'Type',
      sortable: true,
      render: (value: string) => (
        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full capitalize">
          {value.replace('_', ' ')}
        </span>
      )
    },
    {
      key: 'status',
      title: 'Status',
      sortable: true,
      render: (value: string) => (
        <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(value)}`}>
          {value.replace('_', ' ')}
        </span>
      )
    },
    {
      key: 'client_name',
      title: 'Client',
      sortable: true,
      render: (value: string, record: DocumentSummary) => (
        <div>
          <div className="font-medium text-gray-900">{value || 'Internal'}</div>
        </div>
      )
    },
    {
      key: 'hs_code',
      title: 'HS Code',
      sortable: true,
      render: (value: string) => (
        <span className="font-mono text-sm text-gray-700">{value || '-'}</span>
      )
    },
    {
      key: 'compliance_status',
      title: 'Compliance',
      sortable: true,
      render: (value: string) => (
        <div className="flex items-center gap-1">
          {value === 'compliant' && <FiCheckCircle className="w-4 h-4 text-green-600" />}
          {value === 'non_compliant' && <FiXCircle className="w-4 h-4 text-red-600" />}
          {value === 'pending_review' && <FiClock className="w-4 h-4 text-orange-600" />}
          <span className={`text-sm ${getComplianceColor(value)}`}>
            {value.replace('_', ' ')}
          </span>
        </div>
      )
    },
    {
      key: 'created_at',
      title: 'Upload Date',
      sortable: true,
      render: (value: string, record: DocumentSummary) => (
        <div>
          <div className="text-sm text-gray-900">
            {new Date(value).toLocaleDateString()}
          </div>
          <div className="text-xs text-gray-500">
            by {record.uploaded_by || 'System'}
          </div>
        </div>
      )
    },
    {
      key: 'file_size',
      title: 'Size',
      sortable: true,
      render: (value: number) => (
        <span className="text-sm text-gray-600">{formatFileSize(value)}</span>
      )
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (value: any, record: DocumentSummary) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => handleDocumentAction('view', record.id)}
            className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
            title="View document"
          >
            <FiEye className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleDocumentAction('download', record.id)}
            className="p-1 text-gray-400 hover:text-green-600 transition-colors"
            title="Download document"
          >
            <FiDownload className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleDocumentAction('edit', record.id)}
            className="p-1 text-gray-400 hover:text-orange-600 transition-colors"
            title="Edit document"
          >
            <FiEdit3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleDocumentAction('more', record.id)}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="More actions"
          >
            <FiMoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      )
    }
  ];

  // Filter configurations
  const filterConfigs = [
    {
      key: 'type',
      label: 'Document Type',
      type: 'select' as const,
      options: [
        { label: 'Invoice', value: 'invoice' },
        { label: 'Packing List', value: 'packing_list' },
        { label: 'Certificate', value: 'certificate' },
        { label: 'Permit', value: 'permit' },
        { label: 'Declaration', value: 'declaration' },
        { label: 'Ruling', value: 'ruling' },
        { label: 'Correspondence', value: 'correspondence' },
        { label: 'Other', value: 'other' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select' as const,
      options: [
        { label: 'Draft', value: 'draft' },
        { label: 'Pending', value: 'pending' },
        { label: 'Approved', value: 'approved' },
        { label: 'Rejected', value: 'rejected' },
        { label: 'Expired', value: 'expired' },
        { label: 'Archived', value: 'archived' }
      ]
    },
    {
      key: 'client',
      label: 'Client',
      type: 'text' as const,
      placeholder: 'Search by client name...'
    },
    {
      key: 'dateRange',
      label: 'Upload Date',
      type: 'daterange' as const
    }
  ];

  // Action toolbar actions
  const toolbarActions = [
    {
      id: 'upload',
      label: 'Upload Document',
      icon: <FiUpload className="w-4 h-4" />,
      onClick: handleUpload,
      variant: 'primary' as const
    },
    {
      id: 'refresh',
      label: 'Refresh',
      icon: <FiRefreshCw className="w-4 h-4" />,
      onClick: loadDocuments,
      variant: 'default' as const
    }
  ];

  const bulkActions = [
    {
      id: 'download',
      label: 'Download Selected',
      icon: <FiDownload className="w-4 h-4" />,
      variant: 'default' as const
    },
    {
      id: 'archive',
      label: 'Archive Selected',
      icon: <FiArchive className="w-4 h-4" />,
      variant: 'default' as const
    },
    {
      id: 'delete',
      label: 'Delete Selected',
      icon: <FiTrash2 className="w-4 h-4" />,
      variant: 'danger' as const
    }
  ];

  // KPI data
  const kpiData = [
    {
      icon: FiFileText,
      value: stats.totalDocuments.toString(),
      label: 'Total Documents',
      color: 'blue',
      trend: '+12',
      subtitle: 'this month'
    },
    {
      icon: FiClock,
      value: stats.pendingReview.toString(),
      label: 'Pending Review',
      color: 'orange',
      trend: '-3',
      subtitle: 'from last week'
    },
    {
      icon: FiCalendar,
      value: stats.expiringThisMonth.toString(),
      label: 'Expiring This Month',
      color: 'red',
      trend: '+2',
      subtitle: 'requires attention'
    },
    {
      icon: FiShield,
      value: stats.complianceIssues.toString(),
      label: 'Compliance Issues',
      color: 'red',
      trend: '0',
      subtitle: 'no new issues'
    },
    {
      icon: FiArchive,
      value: formatFileSize(stats.storageUsed),
      label: 'Storage Used',
      color: 'purple',
      trend: '+15%',
      subtitle: 'of 10GB limit'
    },
    {
      icon: FiUpload,
      value: stats.recentUploads.toString(),
      label: 'Recent Uploads',
      color: 'green',
      trend: '+8',
      subtitle: 'last 7 days'
    }
  ];

  // Tab configuration
  const tabs = [
    { id: 'all', label: 'All Documents', count: documents.length },
    { id: 'import', label: 'Import Docs', count: documents.filter(d => d.category === 'IMPORT').length },
    { id: 'export', label: 'Export Docs', count: documents.filter(d => d.category === 'EXPORT').length },
    { id: 'compliance', label: 'Compliance', count: documents.filter(d => d.category === 'COMPLIANCE' || d.category === 'REGULATORY').length },
    { id: 'pending', label: 'Pending Review', count: documents.filter(d => d.status === 'PENDING_REVIEW' || d.status === 'DRAFT').length },
    { id: 'expiring', label: 'Expiring Soon', count: stats.expiringThisMonth }
  ];

  if (loading) {
    return (
      <div className="content">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-gray-600">Loading documents...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="content fade-in">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Document Management
            </h1>
            <p className="text-lg text-gray-600">
              Centralized document repository for customs and trade compliance
            </p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={loadDocuments}
              className="btn btn--secondary"
              disabled={loading}
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button 
              onClick={handleUpload}
              className="btn btn--primary"
            >
              <FiUpload className="w-4 h-4" />
              Upload Document
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <KPIGrid className="mb-8">
        {kpiData.map((kpi, index) => (
          <KPICard
            key={index}
            icon={kpi.icon}
            value={kpi.value}
            label={kpi.label}
            color={kpi.color as any}
            trend={kpi.trend}
            subtitle={kpi.subtitle}
          />
        ))}
      </KPIGrid>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Search and Filters */}
        <ProfessionalCard variant="default">
          <ProfessionalCardContent>
            <div className="space-y-4">
              <SearchBar
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search documents by name, client, HS code, or tags..."
                size="large"
              />
              
              <ProfessionalFilters
                filters={filterConfigs}
                values={filterValues}
                onChange={setFilterValues}
                onReset={() => setFilterValues({})}
                layout="grid"
              />
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>

        {/* Document Tabs and Table */}
        <ProfessionalCard variant="default">
          <ProfessionalCardHeader
            icon={<FiFolder className="w-5 h-5" />}
            subtitle="Organize and manage all your trade documents"
          >
            Documents Library
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="space-y-4">
              {/* Custom Tab Navigation */}
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      {tab.label}
                      <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-600">
                        {tab.count}
                      </span>
                    </button>
                  ))}
                </nav>
              </div>

              {/* Action Toolbar */}
              <ActionToolbar
                actions={selectedDocuments.length > 0 ? bulkActions.map(action => ({
                  ...action,
                  onClick: () => handleBulkAction(action.id)
                })) : toolbarActions}
                selectedCount={selectedDocuments.length}
                totalCount={filteredDocuments.length}
                showSelectionInfo={true}
              />

              {/* Documents Table */}
              <ProfessionalTable
                data={filteredDocuments as any[]}
                columns={columns}
                rowKey="id"
                loading={loading}
                selection={{
                  selectedRowKeys: selectedDocuments.map(String),
                  onChange: (keys) => setSelectedDocuments(keys.map(Number))
                }}
                pagination={{
                  current: 1,
                  pageSize: 20,
                  total: filteredDocuments.length,
                  onChange: (page, pageSize) => console.log('Pagination:', page, pageSize)
                }}
                onRow={(record) => ({
                  onClick: () => handleDocumentAction('view', record.id),
                  className: 'cursor-pointer'
                })}
              />
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Document Templates */}
          <ProfessionalCard variant="default">
            <ProfessionalCardHeader
              icon={<FiFileText className="w-5 h-5" />}
              subtitle="Pre-configured templates for common documents"
            >
              Document Templates
            </ProfessionalCardHeader>
            <ProfessionalCardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <button className="btn btn--secondary justify-start p-4 h-auto">
                  <FiFileText className="w-5 h-5 text-blue-600" />
                  <div className="text-left">
                    <div className="font-medium">Commercial Invoice</div>
                    <div className="text-xs opacity-75">Standard invoice template</div>
                  </div>
                </button>
                <button className="btn btn--secondary justify-start p-4 h-auto">
                  <FiShield className="w-5 h-5 text-green-600" />
                  <div className="text-left">
                    <div className="font-medium">Certificate of Origin</div>
                    <div className="text-xs opacity-75">FTA certificate template</div>
                  </div>
                </button>
                <button className="btn btn--secondary justify-start p-4 h-auto">
                  <FiGlobe className="w-5 h-5 text-purple-600" />
                  <div className="text-left">
                    <div className="font-medium">Import Declaration</div>
                    <div className="text-xs opacity-75">Customs declaration form</div>
                  </div>
                </button>
                <button className="btn btn--secondary justify-start p-4 h-auto">
                  <FiArchive className="w-5 h-5 text-orange-600" />
                  <div className="text-left">
                    <div className="font-medium">Packing List</div>
                    <div className="text-xs opacity-75">Detailed packing template</div>
                  </div>
                </button>
              </div>
            </ProfessionalCardContent>
            <ProfessionalCardFooter>
              <Link to="/templates" className="btn btn--ghost btn--sm w-full">
                View All Templates
                <FiPlus className="w-4 h-4" />
              </Link>
            </ProfessionalCardFooter>
          </ProfessionalCard>

          {/* Recent Activity */}
          <ProfessionalCard variant="default">
            <ProfessionalCardHeader
              icon={<FiClock className="w-5 h-5" />}
              subtitle="Latest document activities and updates"
            >
              Recent Activity
            </ProfessionalCardHeader>
            <ProfessionalCardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-green-100 text-green-600">
                    <FiUpload className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      Commercial Invoice uploaded
                    </p>
                    <p className="text-xs text-gray-500">
                      ABC Electronics Ltd • 2 hours ago
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-blue-100 text-blue-600">
                    <FiCheckCircle className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      Certificate approved
                    </p>
                    <p className="text-xs text-gray-500">
                      JAEPA Certificate • 4 hours ago
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-orange-100 text-orange-600">
                    <FiAlertCircle className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      Document expiring soon
                    </p>
                    <p className="text-xs text-gray-500">
                      Export Permit • Expires in 3 days
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-purple-100 text-purple-600">
                    <FiEdit3 className="w-4 h-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      Declaration updated
                    </p>
                    <p className="text-xs text-gray-500">
                      Import Declaration v3 • 1 day ago
                    </p>
                  </div>
                </div>
              </div>
            </ProfessionalCardContent>
            <ProfessionalCardFooter>
              <Link to="/activity" className="btn btn--ghost btn--sm w-full">
                View All Activity
                <FiClock className="w-4 h-4" />
              </Link>
            </ProfessionalCardFooter>
          </ProfessionalCard>
        </div>
      </div>
    </div>
  );
};

export default Documents;