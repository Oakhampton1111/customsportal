import React, { useState, useEffect } from 'react';
import {
  FiSearch,
  FiFolder,
  FiBarChart,
  FiPlus,
  FiMinus,
  FiChevronDown,
  FiChevronRight,
  FiBookmark,
  FiClock,
  FiInfo,
  FiRefreshCw,
  FiFilter,
  FiTag,
  FiTrendingUp,
  FiX,
} from 'react-icons/fi';
import { tariffApi } from '../services/tariffApi';
import type { TariffSection, TariffCodeDetails } from '../services/tariffApi';
import { ProfessionalCard, ProfessionalCardHeader, ProfessionalCardContent } from '../components/ui/ProfessionalCard';
import { ProfessionalTable } from '../components/ui/ProfessionalTable';
import { ProfessionalFilters, SearchBar, QuickFilters } from '../components/ui/ProfessionalFilters';
import { TabPanel, MasterDetail } from '../components/ui/ProfessionalLayouts';
import { ActionToolbar } from '../components/ui/ActionToolbar';

const TariffTree: React.FC = () => {
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [comparisonCodes, setComparisonCodes] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('browse');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  
  // API state
  const [sections, setSections] = useState<TariffSection[]>([]);
  const [searchResults, setSearchResults] = useState<TariffCodeDetails[]>([]);
  const [comparisonData, setComparisonData] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Professional component state
  const [filterValues, setFilterValues] = useState<Record<string, any>>({});
  const [showDetailView, setShowDetailView] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // Mock data for demonstration
  const mockSections: TariffSection[] = [
    {
      id: 1,
      section_number: 1,
      title: "Live Animals; Animal Products",
      description: "Live animals and products of animal origin",
      chapter_range: "01-05"
    },
    {
      id: 2,
      section_number: 2,
      title: "Vegetable Products",
      description: "Products of the vegetable kingdom",
      chapter_range: "06-14"
    },
    {
      id: 3,
      section_number: 3,
      title: "Animal or Vegetable Fats and Oils",
      description: "Animal or vegetable fats and oils and their cleavage products",
      chapter_range: "15"
    },
    {
      id: 4,
      section_number: 4,
      title: "Prepared Foodstuffs",
      description: "Prepared foodstuffs; beverages, spirits and vinegar; tobacco",
      chapter_range: "16-24"
    }
  ];

  const mockSearchResults: TariffCodeDetails[] = [
    {
      id: 1,
      hs_code: '0101.21.00',
      description: 'Pure-bred breeding horses',
      level: 8,
      section_id: 1,
      chapter_id: 1,
      is_active: true
    },
    {
      id: 2,
      hs_code: '0102.31.00',
      description: 'Pure-bred breeding buffalo',
      level: 8,
      section_id: 1,
      chapter_id: 1,
      is_active: true
    },
    {
      id: 3,
      hs_code: '0201.10.00',
      description: 'Carcasses and half-carcasses of bovine animals, fresh or chilled',
      level: 8,
      section_id: 1,
      chapter_id: 2,
      is_active: true
    }
  ];

  // Mock comparison data
  const mockComparisonData = {
    codes: [
      {
        hs_code: '0101.21.00',
        description: 'Pure-bred breeding horses',
        duty_rate: '0%',
        unit: 'Number',
        fta_rates: []
      },
      {
        hs_code: '0102.31.00',
        description: 'Pure-bred breeding buffalo',
        duty_rate: '0%',
        unit: 'Number',
        fta_rates: []
      }
    ]
  };

  // Filter configurations for professional filters
  const filterConfigs = [
    {
      key: 'section',
      label: 'Section',
      type: 'select' as const,
      options: [
        { label: 'Section 1: Live Animals', value: 1 },
        { label: 'Section 2: Vegetable Products', value: 2 },
        { label: 'Section 3: Fats and Oils', value: 3 },
        { label: 'Section 4: Prepared Foodstuffs', value: 4 }
      ]
    },
    {
      key: 'level',
      label: 'HS Level',
      type: 'select' as const,
      options: [
        { label: 'Chapter (2-digit)', value: 2 },
        { label: 'Heading (4-digit)', value: 4 },
        { label: 'Subheading (6-digit)', value: 6 },
        { label: 'Statistical (8-digit)', value: 8 }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select' as const,
      options: [
        { label: 'Active', value: 'active' },
        { label: 'Inactive', value: 'inactive' },
        { label: 'All', value: 'all' }
      ]
    }
  ];

  // Quick filter options
  const quickFilters = [
    { label: 'Live Animals', value: { section: 1 }, active: filterValues.section === 1 },
    { label: 'Vegetable Products', value: { section: 2 }, active: filterValues.section === 2 },
    { label: '8-digit codes', value: { level: 8 }, active: filterValues.level === 8 },
    { label: 'Active only', value: { status: 'active' }, active: filterValues.status === 'active' }
  ];

  useEffect(() => {
    loadSections();
  }, []);

  const loadSections = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await tariffApi.getSections();
      setSections(data);
      console.log('✅ Loaded tariff sections from API:', data.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tariff sections');
      console.error('❌ Error loading sections:', err);
      setSections([]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSectionExpansion = (sectionId: number) => {
    const sectionIdStr = sectionId.toString();
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionIdStr)) {
        newSet.delete(sectionIdStr);
      } else {
        newSet.add(sectionIdStr);
      }
      return newSet;
    });
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const response = await tariffApi.searchTariffCodes(searchQuery);
      setSearchResults(response.results);
      setPagination(prev => ({ ...prev, total: response.total }));
      setActiveTab('search');
      console.log('✅ Search completed:', response.results.length, 'results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      console.error('❌ Search error:', err);
      setSearchResults([]);
      setPagination(prev => ({ ...prev, total: 0 }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeSelect = async (code: string) => {
    setSelectedCode(code);
    try {
      setIsLoading(true);
      const details = await tariffApi.getCodeDetails(code);
      console.log('Code details:', details);
      // TODO: Display code details in a modal or sidebar
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load code details');
      console.error('Error loading code details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const addToComparison = (code: string) => {
    if (!comparisonCodes.includes(code)) {
      setComparisonCodes(prev => [...prev, code]);
    }
  };

  const removeFromComparison = (code: string) => {
    setComparisonCodes(prev => prev.filter(c => c !== code));
  };

  const clearComparison = () => {
    setComparisonCodes([]);
    setComparisonData(null);
  };

  const runComparison = async () => {
    if (comparisonCodes.length < 2) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await tariffApi.compareCodes(comparisonCodes);
      setComparisonData(data);
      setActiveTab('comparison');
      console.log('✅ Comparison completed for codes:', comparisonCodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed');
      console.error('❌ Comparison error:', err);
      setComparisonData(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Render functions for tab content
  function renderBrowseTab() {
    return (
      <ProfessionalCard>
        <ProfessionalCardHeader
          subtitle="Browse Schedule 3 by section"
          icon={<FiFolder className="w-5 h-5" />}
        >
          Tariff Sections
        </ProfessionalCardHeader>
        <ProfessionalCardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-500">Loading sections...</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {sections.map((section) => (
                <div key={section.id} className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleSectionExpansion(section.id)}
                    className="w-full p-4 text-left hover:bg-gray-50 transition-colors rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FiFolder className="w-5 h-5 text-blue-600" />
                        <div>
                          <div className="font-medium text-gray-900">
                            Section {section.section_number}: {section.title}
                          </div>
                          <div className="text-sm text-gray-500">
                            {section.description || 'No description available'}
                          </div>
                        </div>
                      </div>
                      <FiChevronRight
                        className={`w-5 h-5 text-gray-400 transition-transform ${
                          expandedSections.has(section.id.toString()) ? 'rotate-90' : ''
                        }`}
                      />
                    </div>
                  </button>
                  {expandedSections.has(section.id.toString()) && (
                    <div className="px-4 pb-4 border-t border-gray-100">
                      <div className="mt-4 grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-blue-50 rounded-lg">
                          <div className="text-lg font-semibold text-blue-600">
                            {section.chapter_range ? section.chapter_range.split('-').length : '0'}
                          </div>
                          <div className="text-sm text-blue-600">Chapters</div>
                        </div>
                        <div className="text-center p-3 bg-green-50 rounded-lg">
                          <div className="text-lg font-semibold text-green-600">
                            {section.section_number}
                          </div>
                          <div className="text-sm text-green-600">Section</div>
                        </div>
                      </div>
                      <div className="mt-4 text-center py-4 text-gray-500">
                        Chapter loading will be implemented with the InteractiveTariffTree component
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ProfessionalCardContent>
      </ProfessionalCard>
    );
  }

  function renderSearchTab() {
    // Table columns for search results
    const searchResultColumns = [
      {
        key: 'hs_code',
        title: 'HS Code',
        width: '120px',
        sortable: true,
        render: (value: string) => (
          <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
            {value}
          </span>
        )
      },
      {
        key: 'description',
        title: 'Description',
        sortable: true,
        render: (value: string, record: TariffCodeDetails) => (
          <div>
            <div className="font-medium text-gray-900">{value}</div>
            <div className="text-sm text-gray-500">
              {record.section_id && `Section ${record.section_id}`}
              {record.chapter_id && ` • Chapter ${record.chapter_id}`}
            </div>
          </div>
        )
      },
      {
        key: 'level',
        title: 'Level',
        width: '80px',
        align: 'center' as const,
        render: (value: number) => (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {value}
          </span>
        )
      },
      {
        key: 'actions',
        title: 'Actions',
        width: '120px',
        align: 'center' as const,
        render: (_: any, record: TariffCodeDetails) => (
          <div className="flex items-center gap-2">
            <button
              onClick={() => addToComparison(record.hs_code)}
              disabled={comparisonCodes.includes(record.hs_code) || comparisonCodes.length >= 5}
              className="p-1 text-gray-400 hover:text-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Add to comparison"
            >
              <FiPlus className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleCodeSelect(record.hs_code)}
              className="p-1 text-gray-400 hover:text-blue-600"
              title="View details"
            >
              <FiInfo className="w-4 h-4" />
            </button>
          </div>
        )
      }
    ];

    return (
      <ProfessionalCard>
        <ProfessionalCardHeader
          subtitle={`${searchResults.length} results for "${searchQuery}"`}
          icon={<FiSearch className="w-5 h-5" />}
        >
          Search Results
        </ProfessionalCardHeader>
        <ProfessionalCardContent>
          {searchResults.length === 0 ? (
            <div className="text-center py-12">
              <FiSearch className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">
                {searchQuery ? 'No results found' : 'Enter a search term to begin'}
              </p>
            </div>
          ) : (
            <ProfessionalTable
              data={searchResults}
              columns={searchResultColumns}
              rowKey="id"
              pagination={{
                current: pagination.current,
                pageSize: pagination.pageSize,
                total: pagination.total,
                onChange: (page, pageSize) => setPagination({ current: page, pageSize, total: pagination.total })
              }}
              selection={{
                selectedRowKeys,
                onChange: (keys, rows) => setSelectedRowKeys(keys)
              }}
            />
          )}
        </ProfessionalCardContent>
      </ProfessionalCard>
    );
  }

  function renderComparisonTab() {
    // Table columns for comparison
    const comparisonColumns = [
      {
        key: 'hs_code',
        title: 'HS Code',
        width: '120px',
        render: (value: string) => (
          <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
            {value}
          </span>
        )
      },
      {
        key: 'description',
        title: 'Description',
        render: (value: string) => (
          <div className="font-medium text-gray-900">{value}</div>
        )
      },
      {
        key: 'duty_rate',
        title: 'Duty Rate',
        width: '100px',
        align: 'center' as const,
        render: (value: string) => (
          <span className="font-medium text-green-600">{value}</span>
        )
      },
      {
        key: 'unit',
        title: 'Unit',
        width: '80px',
        align: 'center' as const
      }
    ];

    return (
      <ProfessionalCard>
        <ProfessionalCardHeader
          subtitle={`Comparing ${comparisonCodes.length} tariff codes`}
          icon={<FiBarChart className="w-5 h-5" />}
        >
          Code Comparison
        </ProfessionalCardHeader>
        <ProfessionalCardContent>
          {comparisonData ? (
            <ProfessionalTable
              data={comparisonData.codes}
              columns={comparisonColumns}
              rowKey="hs_code"
              bordered={true}
              striped={true}
            />
          ) : (
            <div className="text-center py-12">
              <FiBarChart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">
                Add at least 2 codes to comparison queue to compare
              </p>
            </div>
          )}
        </ProfessionalCardContent>
      </ProfessionalCard>
    );
  }

  if (error) {
    return (
      <div className="content">
        <div className="card p-6 text-center">
          <FiInfo className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Tariff Tree</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={loadSections} className="btn btn--primary">
            <FiRefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="content fade-in">
      {/* Header Section */}
      <header className="page-header">
        <div className="page-header__content">
          <h1 className="page-header__title">
            Interactive Schedule 3 Explorer
          </h1>
          <p className="page-header__subtitle">
            Browse and search Australian tariff classifications
          </p>
        </div>
        <div className="page-header__actions">
          <button 
            onClick={loadSections}
            className="btn btn--secondary"
            disabled={isLoading}
          >
            <FiRefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {comparisonCodes.length >= 2 && (
            <button 
              onClick={runComparison}
              className="btn btn--primary"
              disabled={isLoading}
            >
              <FiBarChart className="w-4 h-4" />
              Compare ({comparisonCodes.length})
            </button>
          )}
        </div>
      </header>

      {/* Professional Search and Filters */}
      <div className="space-y-6 mb-6">
        <ProfessionalCard>
          <ProfessionalCardHeader
            subtitle="Find tariff codes and classifications"
            icon={<FiSearch className="w-5 h-5" />}
          >
            Search & Filter
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="space-y-4">
              <SearchBar
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search tariff codes, descriptions, or HS codes..."
                size="large"
                suggestions={[
                  'Live animals',
                  'Vegetable products',
                  'Animal fats',
                  'Prepared foodstuffs'
                ]}
                onSuggestionClick={(suggestion) => {
                  setSearchQuery(suggestion);
                  handleSearch();
                }}
              />
              
              <div className="flex items-center gap-4">
                <button
                  onClick={handleSearch}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  disabled={isLoading || !searchQuery.trim()}
                >
                  <FiSearch className="w-4 h-4" />
                  {isLoading ? 'Searching...' : 'Search'}
                </button>
                
                <QuickFilters
                  filters={quickFilters}
                  onFilterClick={(value) => {
                    setFilterValues(prev => ({ ...prev, ...value }));
                  }}
                />
              </div>
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>

        <ProfessionalFilters
          filters={filterConfigs}
          values={filterValues}
          onChange={setFilterValues}
          onReset={() => setFilterValues({})}
          layout="horizontal"
        />
      </div>

      {/* Professional Tab Navigation */}
      <div className="mb-6">
        <TabPanel
          tabs={[
            {
              id: 'browse',
              label: 'Browse Sections',
              content: renderBrowseTab(),
              badge: sections.length
            },
            {
              id: 'search',
              label: 'Search Results',
              content: renderSearchTab(),
              badge: searchResults.length
            },
            {
              id: 'comparison',
              label: 'Comparison',
              content: renderComparisonTab(),
              badge: comparisonCodes.length
            }
          ]}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          variant="default"
          size="medium"
        />
      </div>

      {/* Professional Comparison Bar */}
      {comparisonCodes.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-blue-600">
                  <FiBarChart className="w-5 h-5" />
                  <span className="font-medium">
                    {comparisonCodes.length} code{comparisonCodes.length !== 1 ? 's' : ''} in comparison
                  </span>
                </div>
                <div className="flex gap-1">
                  {comparisonCodes.map((code, index) => (
                    <span key={code} className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md">
                      {code}
                      <button
                        onClick={() => removeFromComparison(code)}
                        className="hover:bg-blue-200 rounded-full p-0.5"
                      >
                        <FiX className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab('comparison')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <FiBarChart className="w-4 h-4" />
                  Compare Codes
                </button>
                <button
                  onClick={clearComparison}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Professional Layout with Sidebar */}
      <MasterDetail
        masterList={
          <div className="space-y-6">
            {/* Quick Jump */}
            <ProfessionalCard variant="default" density="compact">
              <ProfessionalCardHeader
                subtitle="Jump to specific codes"
                icon={<FiSearch className="w-5 h-5" />}
              >
                Quick Jump
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Enter HS code..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2">
                    <FiSearch className="w-4 h-4" />
                    Jump to Code
                  </button>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>

            {/* Bookmarks */}
            <ProfessionalCard variant="default" density="compact">
              <ProfessionalCardHeader
                subtitle="Saved codes"
                icon={<FiBookmark className="w-5 h-5" />}
              >
                Bookmarks
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="text-center py-6">
                  <FiBookmark className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">No bookmarks yet</p>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>

            {/* Recent Activity */}
            <ProfessionalCard variant="default" density="compact">
              <ProfessionalCardHeader
                subtitle="Recently viewed codes"
                icon={<FiClock className="w-5 h-5" />}
              >
                Recent Activity
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <div className="text-center py-6">
                  <FiClock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">No recent activity</p>
                </div>
              </ProfessionalCardContent>
            </ProfessionalCard>
          </div>
        }
        detailView={<div />}
        masterWidth="320px"
        showDetail={false}
        responsive={true}
      />
    </div>
  );
};

export default TariffTree;
