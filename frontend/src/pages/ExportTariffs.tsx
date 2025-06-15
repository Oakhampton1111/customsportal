import React, { useState, useEffect, useCallback } from 'react';
import { 
  FiSearch, 
  FiChevronDown, 
  FiChevronRight, 
  FiGlobe, 
  FiFileText, 
  FiShield, 
  FiTrendingUp,
  FiRefreshCw,
  FiDownload,
  FiBookmark,
  FiClock,
  FiAlertCircle,
  FiCheckCircle,
  FiBarChart,
  FiX,
  FiFilter,
  FiExternalLink,
  FiStar,
  FiEye
} from 'react-icons/fi';
import { FaFolderOpen, FaBookmark as FaBookmarkSolid } from 'react-icons/fa';
import { exportApi, type AHECCNode, type ExportCodeDetails, type ExportRequirement, type MarketAccessInfo, type ExportStatistics } from '../services/exportApi';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { cn } from '../lib/utils';

interface AHECCCode extends AHECCNode {
  id: string;
}

const ExportTariffs: React.FC = () => {
  const [selectedCode, setSelectedCode] = useState<AHECCCode | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [activeTab, setActiveTab] = useState<string>('requirements');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [searchMode, setSearchMode] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'tree' | 'list'>('tree');
  
  const [aheccCodes, setAheccCodes] = useState<AHECCCode[]>([]);
  const [searchResults, setSearchResults] = useState<AHECCCode[]>([]);
  const [codeDetails, setCodeDetails] = useState<ExportCodeDetails | null>(null);
  const [exportRequirements, setExportRequirements] = useState<ExportRequirement[]>([]);
  const [marketAccess, setMarketAccess] = useState<MarketAccessInfo | null>(null);
  const [exportStats, setExportStats] = useState<ExportStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [marketAccessLoading, setMarketAccessLoading] = useState(false);
  const [marketAccessError, setMarketAccessError] = useState<string | null>(null);

  // Enhanced state for modern features
  const [bookmarks, setBookmarks] = useState<Set<string>>(new Set());
  const [recentlyViewed, setRecentlyViewed] = useState<AHECCCode[]>([]);

  const countries = [
    'United States', 'United Kingdom', 'Japan', 'China', 'Singapore', 'New Zealand',
    'South Korea', 'India', 'Indonesia', 'Thailand', 'Vietnam', 'Malaysia'
  ];

  // Load bookmarks and recently viewed from localStorage
  useEffect(() => {
    const savedBookmarks = localStorage.getItem('export-bookmarks');
    const savedRecent = localStorage.getItem('export-recently-viewed');
    
    if (savedBookmarks) {
      setBookmarks(new Set(JSON.parse(savedBookmarks)));
    }
    if (savedRecent) {
      setRecentlyViewed(JSON.parse(savedRecent));
    }
  }, []);

  useEffect(() => {
    loadAHECCTree();
  }, []);

  const loadCountrySpecificData = useCallback(async () => {
    if (!selectedCode || !selectedCountry) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [requirements, stats] = await Promise.all([
        exportApi.getExportRequirements(selectedCode.code, selectedCountry),
        exportApi.getExportStatistics(selectedCode.code)
      ]);
      
      setExportRequirements(requirements);
      setExportStats(stats);
    } catch (error) {
      console.error('Error loading country data:', error);
      setError('Failed to load export data');
    } finally {
      setLoading(false);
    }
  }, [selectedCode, selectedCountry]);

  useEffect(() => {
    if (selectedCode && selectedCountry) {
      loadCountrySpecificData();
    }
  }, [selectedCode, selectedCountry, loadCountrySpecificData]);

  const loadAHECCTree = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const tree = await exportApi.getAHECCTree();
      
      const transformNode = (node: AHECCNode): AHECCCode => ({
        ...node,
        id: node.code,
        children: node.children?.map(transformNode) || []
      });
      
      const transformedTree = tree.map(transformNode);
      setAheccCodes(transformedTree);
    } catch (error) {
      console.error('Error loading AHECC tree:', error);
      setError('Failed to load AHECC codes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchMode(false);
      setSearchResults([]);
      return;
    }

    try {
      setSearchMode(true);
      setLoading(true);
      const results = await exportApi.searchAHECCCodes(query, 50);
      const transformedResults = results.map(node => ({ ...node, id: node.code }));
      setSearchResults(transformedResults);
    } catch (error) {
      console.error('Search error:', error);
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCodeSelect = useCallback(async (code: AHECCCode) => {
    setSelectedCode(code);
    setLoading(true);
    setError(null);
    
    // Add to recently viewed
    const newRecent = [code, ...recentlyViewed.filter(item => item.code !== code.code)].slice(0, 10);
    setRecentlyViewed(newRecent);
    localStorage.setItem('export-recently-viewed', JSON.stringify(newRecent));
    
    try {
      const details = await exportApi.getExportCodeDetails(code.code);
      setCodeDetails(details);
    } catch (error) {
      console.error('Error loading code details:', error);
      setError(error instanceof Error ? error.message : 'Failed to load code details');
    } finally {
      setLoading(false);
    }
  }, [recentlyViewed]);

  const toggleBookmark = (code: string) => {
    const newBookmarks = new Set(bookmarks);
    if (newBookmarks.has(code)) {
      newBookmarks.delete(code);
    } else {
      newBookmarks.add(code);
    }
    setBookmarks(newBookmarks);
    localStorage.setItem('export-bookmarks', JSON.stringify([...newBookmarks]));
  };

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const getCodeLevel = (code: string): string => {
    const length = code.replace(/\./g, '').length;
    if (length <= 2) return 'chapter';
    if (length <= 4) return 'heading';
    if (length <= 6) return 'subheading';
    if (length <= 8) return 'item';
    return 'statistical';
  };

  const getLevelColor = (level: string): string => {
    switch (level) {
      case 'chapter': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'heading': return 'bg-green-100 text-green-800 border-green-200';
      case 'subheading': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'item': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'statistical': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const renderTreeNode = (node: AHECCCode, level: number = 0): React.ReactNode => {
    const isExpanded = expandedNodes.has(node.id);
    const isHovered = hoveredNode === node.id;
    const isBookmarked = bookmarks.has(node.code);
    const hasChildren = node.children && node.children.length > 0;
    const nodeLevel = getCodeLevel(node.code);

    return (
      <div key={node.id} className="relative">
        <div
          className={cn(
            "group flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all duration-200",
            "hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50",
            "hover:shadow-md hover:scale-[1.02]",
            selectedCode?.id === node.id && "bg-gradient-to-r from-blue-100 to-indigo-100 shadow-lg ring-2 ring-blue-200",
            isHovered && "transform translate-x-1"
          )}
          style={{ paddingLeft: `${level * 20 + 12}px` }}
          onClick={() => handleCodeSelect(node)}
          onMouseEnter={() => setHoveredNode(node.id)}
          onMouseLeave={() => setHoveredNode(null)}
        >
          {hasChildren && (
            <Button
              variant="ghost"
              size="xs"
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(node.id);
              }}
              className="p-1 hover:bg-blue-100"
            >
              {isExpanded ? (
                <FiChevronDown className="w-4 h-4 text-blue-600" />
              ) : (
                <FiChevronRight className="w-4 h-4 text-gray-500" />
              )}
            </Button>
          )}
          
          {!hasChildren && (
            <div className="w-6 h-6 flex items-center justify-center">
              <FiFileText className="w-3 h-3 text-gray-400" />
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <code className="text-sm font-mono font-semibold text-blue-700 bg-blue-50 px-2 py-1 rounded">
                {node.code}
              </code>
              <Badge variant="outline" className={cn("text-xs", getLevelColor(nodeLevel))}>
                {nodeLevel}
              </Badge>
              {node.statistical_unit && (
                <Badge variant="secondary" className="text-xs">
                  {node.statistical_unit}
                </Badge>
              )}
            </div>
            <p className="text-sm text-gray-700 line-clamp-2 group-hover:text-gray-900 transition-colors">
              {node.description}
            </p>
            {node.corresponding_import_code && (
              <div className="flex items-center gap-1 mt-1">
                <FiExternalLink className="w-3 h-3 text-gray-400" />
                <span className="text-xs text-gray-500">
                  Import: {node.corresponding_import_code}
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="xs"
              onClick={(e) => {
                e.stopPropagation();
                toggleBookmark(node.code);
              }}
              className="p-1 hover:bg-yellow-100"
            >
              {isBookmarked ? (
                <FaBookmarkSolid className="w-3 h-3 text-yellow-600" />
              ) : (
                <FiBookmark className="w-3 h-3 text-gray-400" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="xs"
              className="p-1 hover:bg-blue-100"
            >
              <FiEye className="w-3 h-3 text-gray-400" />
            </Button>
          </div>
        </div>

        {isExpanded && hasChildren && (
          <div className="mt-1 space-y-1 animate-in slide-in-from-top-2 duration-200">
            {node.children.map(child => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderRequirementsTab = () => (
    <div className="space-y-6">
      {exportRequirements.length > 0 ? (
        exportRequirements.map((req, index) => (
          <Card key={index} className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <FiShield className="w-5 h-5 text-blue-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{req.requirement_type}</h3>
                    <p className="text-sm text-gray-600">
                      {req.mandatory ? 'Mandatory' : 'Optional'} • {req.issuing_authority}
                    </p>
                  </div>
                </div>
                <Badge variant="outline" className={cn("text-xs", req.mandatory ? 'bg-red-100 text-red-800 border-red-200' : 'bg-yellow-100 text-yellow-800 border-yellow-200')}>
                  {req.mandatory ? 'Required' : 'Optional'}
                </Badge>
              </div>
              
              <div className="space-y-4">
                <p className="text-gray-700">{req.description}</p>
                
                {req.documentation_required && req.documentation_required.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Required Documents:</h4>
                    <ul className="space-y-1">
                      {req.documentation_required.map((doc: string, docIndex: number) => (
                        <li key={docIndex} className="flex items-center gap-2 text-sm text-gray-600">
                          <FiFileText className="w-4 h-4 text-blue-500" />
                          {doc}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="flex items-center gap-4 text-sm">
                  {req.processing_time && (
                    <span className="flex items-center gap-1 text-gray-600">
                      <FiClock className="w-4 h-4" />
                      Processing: {req.processing_time}
                    </span>
                  )}
                  {req.cost && (
                    <span className="text-green-600 font-medium">Cost: {req.cost}</span>
                  )}
                </div>
              </div>
            </div>
          </Card>
        ))
      ) : (
        <div className="text-center py-8">
          <FiFileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No export requirements found for this code and country combination.</p>
        </div>
      )}
    </div>
  );

  const renderMarketAccessTab = () => (
    <div className="space-y-6">
      {marketAccessError && (
        <Card className="bg-red-50 border border-red-200">
          <div className="p-6">
            <div className="flex items-center gap-2 text-red-700">
              <FiAlertCircle className="w-5 h-5" />
              <span>{marketAccessError}</span>
            </div>
          </div>
        </Card>
      )}
      
      {marketAccess ? (
        <>
          {/* Access Status Card */}
          <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <FiGlobe className="w-5 h-5 text-blue-600" />
                Market Access Status
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Country</span>
                  <span className="text-sm font-semibold text-blue-700">{marketAccess.country}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Access Status</span>
                  <span className="text-sm font-semibold text-green-700">{marketAccess.access_status}</span>
                </div>
                {marketAccess.tariff_treatment && (
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm font-medium text-gray-700">Tariff Treatment</span>
                    <span className="text-sm font-semibold text-purple-700">{marketAccess.tariff_treatment}</span>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Requirements Card */}
          {marketAccess.requirements && marketAccess.requirements.length > 0 && (
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900">Market Access Requirements</h3>
                <ul className="space-y-2 mt-4">
                  {marketAccess.requirements.map((requirement: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <FiCheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{requirement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          )}

          {/* Restrictions Card */}
          {marketAccess.restrictions && marketAccess.restrictions.length > 0 && (
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900">Restrictions & Limitations</h3>
                <ul className="space-y-2 mt-4">
                  {marketAccess.restrictions.map((restriction: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <FiAlertCircle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{restriction}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <FiGlobe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No market access information available for the selected country.</p>
        </div>
      )}
    </div>
  );

  const renderStatisticsTab = () => (
    <div className="space-y-6">
      {exportStats ? (
        <>
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6 text-center">
                <div className="text-2xl font-bold text-blue-600">${exportStats.export_value?.toLocaleString() || 'N/A'}</div>
                <div className="text-sm text-gray-600 mt-1">Export Value</div>
              </div>
            </Card>
            
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6 text-center">
                <div className="text-2xl font-bold text-green-600">{exportStats.export_quantity?.toLocaleString() || 'N/A'}</div>
                <div className="text-sm text-gray-600 mt-1">Export Quantity</div>
              </div>
            </Card>
            
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6 text-center">
                <div className="text-2xl font-bold text-purple-600">{exportStats.year || 'N/A'}</div>
                <div className="text-sm text-gray-600 mt-1">Year</div>
              </div>
            </Card>
            
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6 text-center">
                <div className="text-2xl font-bold text-orange-600">{exportStats.unit || 'N/A'}</div>
                <div className="text-sm text-gray-600 mt-1">Unit</div>
              </div>
            </Card>
          </div>

          {/* Additional Statistics */}
          {(exportStats.market_share || exportStats.growth_rate || exportStats.trade_balance) && (
            <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900">Additional Trade Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  {exportStats.market_share && (
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Market Share</span>
                      <span className="text-sm font-semibold text-blue-700">{exportStats.market_share}%</span>
                    </div>
                  )}
                  {exportStats.growth_rate && (
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Growth Rate</span>
                      <span className="text-sm font-semibold text-green-700">{exportStats.growth_rate}%</span>
                    </div>
                  )}
                  {exportStats.trade_balance && (
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Trade Balance</span>
                      <span className="text-sm font-semibold text-purple-700">${exportStats.trade_balance.toLocaleString()}</span>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <FiBarChart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No export statistics available for this code and country combination.</p>
        </div>
      )}
    </div>
  );

  useEffect(() => {
    if (selectedCountry) {
      loadMarketAccess();
    }
  }, [selectedCountry]);

  const loadMarketAccess = useCallback(async () => {
    if (!selectedCountry) return;
    
    setMarketAccessLoading(true);
    setMarketAccessError(null);
    try {
      const data = await exportApi.getMarketAccessInfo(selectedCountry);
      setMarketAccess(data);
    } catch (error) {
      console.error('Failed to load market access info:', error);
      setMarketAccessError(error instanceof Error ? error.message : 'Failed to load market access information');
    } finally {
      setMarketAccessLoading(false);
    }
  }, [selectedCountry]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Enhanced Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <FiGlobe className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Export Classification</h1>
                  <p className="text-sm text-gray-600">AHECC Codes & Requirements</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm">
                <FiRefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button variant="outline" size="sm">
                <FiDownload className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Enhanced Tree Navigation */}
          <div className="lg:col-span-1">
            <Card className="h-[calc(100vh-200px)] bg-white/90 backdrop-blur-sm border-0 shadow-xl">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">AHECC Codes</h2>
                  <div className="flex items-center gap-2">
                    <Button
                      variant={viewMode === 'tree' ? 'primary' : 'outline'}
                      size="xs"
                      onClick={() => setViewMode('tree')}
                    >
                      Tree
                    </Button>
                    <Button
                      variant={viewMode === 'list' ? 'primary' : 'outline'}
                      size="xs"
                      onClick={() => setViewMode('list')}
                    >
                      List
                    </Button>
                  </div>
                </div>

                {/* Enhanced Search */}
                <div className="relative mb-4">
                  <div className="relative">
                    <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type="text"
                      placeholder="Search AHECC codes..."
                      value={searchQuery}
                      onChange={(e) => {
                        setSearchQuery(e.target.value);
                        handleSearch(e.target.value);
                      }}
                      className="pl-10 pr-10 bg-gray-50 border-gray-200 focus:bg-white transition-colors"
                    />
                    {searchQuery && (
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => {
                          setSearchQuery('');
                          setSearchMode(false);
                          setSearchResults([]);
                        }}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1"
                      >
                        <FiX className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>

                {/* Quick Access */}
                {(bookmarks.size > 0 || recentlyViewed.length > 0) && (
                  <div className="mb-4 space-y-3">
                    {bookmarks.size > 0 && (
                      <div>
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Bookmarked
                        </h4>
                        <div className="flex flex-wrap gap-1">
                          {[...bookmarks].slice(0, 3).map(code => (
                            <Badge key={code} variant="secondary" className="text-xs cursor-pointer hover:bg-yellow-100">
                              {code}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {recentlyViewed.length > 0 && (
                      <div>
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Recently Viewed
                        </h4>
                        <div className="flex flex-wrap gap-1">
                          {recentlyViewed.slice(0, 3).map(item => (
                            <Badge 
                              key={item.code} 
                              variant="outline" 
                              className="text-xs cursor-pointer hover:bg-blue-50"
                              onClick={() => handleCodeSelect(item)}
                            >
                              {item.code}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <ScrollArea className="flex-1">
                <div className="p-4">
                  {loading ? (
                    <div className="space-y-3">
                      {[...Array(5)].map((_, i) => (
                        <div key={i} className="animate-pulse">
                          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                          <div className="h-3 bg-gray-100 rounded w-1/2"></div>
                        </div>
                      ))}
                    </div>
                  ) : error ? (
                    <div className="text-center py-8">
                      <FiAlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                      <p className="text-red-600 font-medium">{error}</p>
                    </div>
                  ) : searchMode ? (
                    <div className="space-y-2">
                      {searchResults.length > 0 ? (
                        searchResults.map(node => renderTreeNode(node))
                      ) : (
                        <div className="text-center py-8">
                          <FiSearch className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-gray-600">No results found</p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {aheccCodes.map(node => renderTreeNode(node))}
                    </div>
                  )}
                </div>
              </ScrollArea>
            </Card>
          </div>

          {/* Enhanced Details Panel */}
          <div className="lg:col-span-2">
            {selectedCode ? (
              <div className="space-y-6">
                {/* Code Details Header */}
                <Card className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white border-0 shadow-xl">
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <code className="text-lg font-mono font-bold bg-white/20 px-3 py-1 rounded-lg">
                            {selectedCode.code}
                          </code>
                          <Badge className="bg-white/20 text-white border-white/30">
                            {getCodeLevel(selectedCode.code)}
                          </Badge>
                          {selectedCode.statistical_unit && (
                            <Badge className="bg-white/20 text-white border-white/30">
                              {selectedCode.statistical_unit}
                            </Badge>
                          )}
                        </div>
                        <h2 className="text-xl font-semibold mb-2">{selectedCode.description}</h2>
                        {selectedCode.corresponding_import_code && (
                          <div className="flex items-center gap-2 text-blue-100">
                            <FiExternalLink className="w-4 h-4" />
                            <span className="text-sm">Import Code: {selectedCode.corresponding_import_code}</span>
                          </div>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleBookmark(selectedCode.code)}
                        className="text-white hover:bg-white/20"
                      >
                        {bookmarks.has(selectedCode.code) ? (
                          <FaBookmarkSolid className="w-5 h-5" />
                        ) : (
                          <FiBookmark className="w-5 h-5" />
                        )}
                      </Button>
                    </div>
                  </div>
                </Card>

                {/* Country Selection */}
                <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
                  <div className="p-6">
                    <div className="flex items-center gap-4">
                      <FiGlobe className="w-5 h-5 text-blue-600" />
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Select Destination Country
                        </label>
                        <select
                          value={selectedCountry}
                          onChange={(e) => setSelectedCountry(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                        >
                          <option value="">Select a country...</option>
                          {countries.map(country => (
                            <option key={country} value={country}>{country}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Enhanced Tabs */}
                {selectedCountry && (
                  <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-lg">
                    <div className="border-b border-gray-100">
                      <nav className="flex space-x-1 p-4">
                        {[
                          { id: 'requirements', label: 'Requirements', icon: FiShield },
                          { id: 'market', label: 'Market Access', icon: FiGlobe },
                          { id: 'statistics', label: 'Statistics', icon: FiTrendingUp }
                        ].map(tab => (
                          <Button
                            key={tab.id}
                            variant={activeTab === tab.id ? 'primary' : 'ghost'}
                            size="sm"
                            onClick={() => setActiveTab(tab.id)}
                            className="flex items-center gap-2"
                          >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                          </Button>
                        ))}
                      </nav>
                    </div>
                    
                    <div className="p-6">
                      {loading || marketAccessLoading ? (
                        <div className="flex items-center justify-center py-12">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
                          <span className="text-gray-600">Loading data...</span>
                        </div>
                      ) : (
                        <>
                          {activeTab === 'requirements' && renderRequirementsTab()}
                          {activeTab === 'market' && renderMarketAccessTab()}
                          {activeTab === 'statistics' && renderStatisticsTab()}
                        </>
                      )}
                    </div>
                  </Card>
                )}
              </div>
            ) : (
              <Card className="h-[500px] flex items-center justify-center bg-white/90 backdrop-blur-sm border-0 shadow-lg">
                <div className="text-center">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <FiGlobe className="w-10 h-10 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    Select an AHECC Code
                  </h3>
                  <p className="text-gray-600 max-w-md">
                    Choose a code from the tree to view export requirements, market access information, and trade statistics
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Quick Actions */}
      <div className="fixed right-6 bottom-6 space-y-3">
        <Button 
          variant="primary" 
          size="sm"
          className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
        >
          <FiBookmark className="w-5 h-5" />
        </Button>
        <Button 
          variant="secondary" 
          size="sm"
          className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
        >
          <FiClock className="w-5 h-5" />
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          className="rounded-full shadow-lg hover:shadow-xl transition-shadow bg-white"
        >
          <FiFilter className="w-5 h-5" />
        </Button>
      </div>
    </div>
  );
};

export default ExportTariffs;
