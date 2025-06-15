import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { 
  FiChevronRight as ChevronRight, 
  FiChevronDown as ChevronDown, 
  FiSearch as Search, 
  FiBookmark as Bookmark, 
  FiFilter as Filter,
  FiExternalLink as ExternalLink,
  FiFolder as Folder,
  FiFileText as FileText,
  FiClock as Clock,
  FiArrowRight as ArrowRight,
  FiDownload as Download,
  FiStar as Star,
  FiZap as Zap
} from 'react-icons/fi';
import { FaTree as TreePine, FaBookmark as BookmarkCheck, FaFolderOpen as FolderOpen } from 'react-icons/fa';

interface TariffNode {
  code: string;
  description: string;
  level: 'section' | 'chapter' | 'heading' | 'subheading';
  parent_code?: string;
  children?: TariffNode[];
  duty_rate?: string;
  statistical_unit?: string;
  has_children: boolean;
  is_leaf: boolean;
  popularity?: number;
  recent_changes?: boolean;
}

interface InteractiveTariffTreeProps {
  className?: string;
  onCodeSelect?: (code: string) => void;
  selectedCode?: string;
  searchEnabled?: boolean;
  bookmarksEnabled?: boolean;
  recentlyViewedEnabled?: boolean;
}

export const InteractiveTariffTree: React.FC<InteractiveTariffTreeProps> = ({
  className = '',
  onCodeSelect,
  selectedCode,
  searchEnabled = true,
  bookmarksEnabled = true,
  recentlyViewedEnabled = true
}) => {
  const [treeData, setTreeData] = useState<TariffNode[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<TariffNode[]>([]);
  const [bookmarkedCodes, setBookmarkedCodes] = useState<Set<string>>(new Set());
  const [recentlyViewed, setRecentlyViewed] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchMode, setSearchMode] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'tree' | 'list' | 'grid'>('tree');

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/tariff/tree?depth=2');
        if (response.ok) {
          const data = await response.json();
          setTreeData(data.tree || mockTreeData);
        } else {
          setTreeData(mockTreeData);
        }
      } catch (error) {
        console.error('Failed to load tariff tree:', error);
        setTreeData(mockTreeData);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    loadBookmarks();
    loadRecentlyViewed();
  }, []);

  useEffect(() => {
    const performSearchAsync = async () => {
      try {
        const response = await fetch(
          `/api/tariff/search?query=${encodeURIComponent(searchTerm)}&limit=20`
        );
        if (response.ok) {
          const data = await response.json();
          setSearchResults(data.results || []);
          setSearchMode(true);
        }
      } catch (error) {
        console.error('Search failed:', error);
      }
    };

    if (searchTerm.length >= 2) {
      performSearchAsync();
    } else {
      setSearchMode(false);
      setSearchResults([]);
    }
  }, [searchTerm]);

  const loadChildren = async (parentCode: string) => {
    try {
      const response = await fetch(`/api/tariff/tree?parent=${parentCode}&depth=1`);
      if (response.ok) {
        const data = await response.json();
        
        // Update tree data with children
        setTreeData(prevData => 
          updateTreeWithChildren(prevData, parentCode, data.tree)
        );
      }
    } catch (error) {
      console.error('Failed to load children:', error);
    }
  };

  const updateTreeWithChildren = (
    nodes: TariffNode[], 
    parentCode: string, 
    children: TariffNode[]
  ): TariffNode[] => {
    return nodes.map(node => {
      if (node.code === parentCode) {
        return { ...node, children };
      }
      if (node.children) {
        return {
          ...node,
          children: updateTreeWithChildren(node.children, parentCode, children)
        };
      }
      return node;
    });
  };

  const handleNodeToggle = (code: string, hasChildren: boolean) => {
    const newExpanded = new Set(expandedNodes);
    
    if (expandedNodes.has(code)) {
      newExpanded.delete(code);
    } else {
      newExpanded.add(code);
      
      // Load children if not already loaded
      if (hasChildren) {
        loadChildren(code);
      }
    }
    
    setExpandedNodes(newExpanded);
  };

  const handleCodeSelect = (code: string) => {
    // Add to recently viewed
    const newRecentlyViewed = [code, ...recentlyViewed.filter(c => c !== code)].slice(0, 10);
    setRecentlyViewed(newRecentlyViewed);
    localStorage.setItem('tariff-recently-viewed', JSON.stringify(newRecentlyViewed));
    
    onCodeSelect?.(code);
  };

  const toggleBookmark = (code: string) => {
    const newBookmarks = new Set(bookmarkedCodes);
    if (bookmarkedCodes.has(code)) {
      newBookmarks.delete(code);
    } else {
      newBookmarks.add(code);
    }
    setBookmarkedCodes(newBookmarks);
    localStorage.setItem('tariff-bookmarks', JSON.stringify([...newBookmarks]));
  };

  const loadBookmarks = () => {
    const saved = localStorage.getItem('tariff-bookmarks');
    if (saved) {
      setBookmarkedCodes(new Set(JSON.parse(saved)));
    }
  };

  const loadRecentlyViewed = () => {
    const saved = localStorage.getItem('tariff-recently-viewed');
    if (saved) {
      setRecentlyViewed(JSON.parse(saved));
    }
  };

  const getLevelIcon = (level: string, isExpanded: boolean, hasChildren: boolean) => {
    if (level === 'section') {
      return hasChildren ? (isExpanded ? <FolderOpen className="h-4 w-4" /> : <Folder className="h-4 w-4" />) : <FileText className="h-4 w-4" />;
    }
    if (level === 'chapter') {
      return hasChildren ? (isExpanded ? <FolderOpen className="h-4 w-4" /> : <Folder className="h-4 w-4" />) : <FileText className="h-4 w-4" />;
    }
    return <FileText className="h-4 w-4" />;
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'section': return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'chapter': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'heading': return 'text-green-600 bg-green-50 border-green-200';
      case 'subheading': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const renderTreeNode = (node: TariffNode, depth: number = 0) => {
    const isExpanded = expandedNodes.has(node.code);
    const isSelected = selectedCode === node.code;
    const isBookmarked = bookmarkedCodes.has(node.code);
    const isHovered = hoveredNode === node.code;
    
    const indentClass = `ml-${Math.min(depth * 4, 16)}`;
    
    return (
      <div key={node.code} className="relative">
        <div
          className={cn(
            "group relative flex items-center gap-3 p-3 rounded-lg transition-all duration-200 cursor-pointer",
            "hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 hover:shadow-md hover:scale-[1.02]",
            isSelected && "bg-gradient-to-r from-blue-100 to-indigo-100 shadow-md ring-2 ring-blue-500/20",
            isHovered && "transform scale-[1.01]",
            indentClass
          )}
          onMouseEnter={() => setHoveredNode(node.code)}
          onMouseLeave={() => setHoveredNode(null)}
        >
          {/* Expand/Collapse Button */}
          {node.has_children && (
            <Button
              variant="ghost"
              size="xs"
              className="h-6 w-6 p-0 hover:bg-blue-100"
              onClick={(e) => {
                e.stopPropagation();
                handleNodeToggle(node.code, node.has_children);
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-3 w-3 text-blue-600" />
              ) : (
                <ChevronRight className="h-3 w-3 text-gray-500" />
              )}
            </Button>
          )}
          
          {/* Level Icon */}
          <div className={cn("flex-shrink-0 p-1.5 rounded-md border", getLevelColor(node.level))}>
            {getLevelIcon(node.level, isExpanded, node.has_children)}
          </div>
          
          {/* Content */}
          <div 
            className="flex-1 min-w-0"
            onClick={() => handleCodeSelect(node.code)}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono font-semibold text-gray-900 text-sm">
                {node.code}
              </span>
              
              <Badge 
                variant="outline" 
                className={cn("text-xs font-medium", getLevelColor(node.level))}
              >
                {node.level}
              </Badge>
              
              {node.recent_changes && (
                <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">
                  <Zap className="h-3 w-3 mr-1" />
                  Updated
                </Badge>
              )}
              
              {node.popularity && node.popularity > 80 && (
                <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                  <Star className="h-3 w-3 mr-1" />
                  Popular
                </Badge>
              )}
            </div>
            
            <div className="text-sm text-gray-700 line-clamp-2 group-hover:text-gray-900">
              {node.description}
            </div>
            
            {node.duty_rate && (
              <div className="mt-1 text-xs text-blue-600 font-medium">
                Duty: {node.duty_rate}
              </div>
            )}
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="xs"
              className="h-7 w-7 p-0"
              onClick={(e) => {
                e.stopPropagation();
                toggleBookmark(node.code);
              }}
            >
              {isBookmarked ? (
                <BookmarkCheck className="h-3 w-3 text-blue-600" />
              ) : (
                <Bookmark className="h-3 w-3 text-gray-400" />
              )}
            </Button>
            
            <Button
              variant="ghost"
              size="xs"
              className="h-7 w-7 p-0"
              onClick={(e) => {
                e.stopPropagation();
                // Open in new tab or detailed view
              }}
            >
              <ExternalLink className="h-3 w-3 text-gray-400" />
            </Button>
          </div>
        </div>

        {/* Children */}
        {isExpanded && node.children && (
          <div className="mt-1 space-y-1">
            {node.children.map(child => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const mockTreeData: TariffNode[] = [
    {
      code: '01',
      description: 'Live Animals and Animal Products',
      level: 'section',
      has_children: true,
      is_leaf: false,
      popularity: 85,
      recent_changes: true,
      children: [
        {
          code: '01',
          description: 'Live animals',
          level: 'chapter',
          parent_code: '01',
          has_children: true,
          is_leaf: false,
          popularity: 75
        }
      ]
    },
    {
      code: '02',
      description: 'Vegetable Products',
      level: 'section',
      has_children: true,
      is_leaf: false,
      popularity: 92
    }
  ];

  if (loading) {
    return (
      <Card className={cn("overflow-hidden", className)}>
        <CardContent className="p-6">
          <div className="space-y-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse flex items-center gap-3">
                <div className="h-8 w-8 bg-gradient-to-r from-gray-200 to-gray-300 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gradient-to-r from-gray-200 to-gray-300 rounded w-3/4"></div>
                  <div className="h-3 bg-gradient-to-r from-gray-100 to-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("overflow-hidden shadow-lg border-0 bg-white", className)}>
      <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <TreePine className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Australian Tariff Schedule</h3>
              <p className="text-sm text-gray-600">Interactive Schedule 3 Explorer</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'tree' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setViewMode('tree')}
            >
              Tree
            </Button>
            <Button
              variant={viewMode === 'list' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              List
            </Button>
          </div>
        </CardTitle>
        
        {/* Enhanced Search */}
        {searchEnabled && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search HS codes, descriptions, or keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
            />
            {searchTerm && (
              <Button
                variant="ghost"
                size="xs"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                onClick={() => setSearchTerm('')}
              >
                ×
              </Button>
            )}
          </div>
        )}

        {/* Quick Access Toolbar */}
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {bookmarksEnabled && bookmarkedCodes.size > 0 && (
              <Button variant="outline" size="sm" className="text-xs">
                <Bookmark className="h-3 w-3 mr-1" />
                Bookmarks ({bookmarkedCodes.size})
              </Button>
            )}
            
            {recentlyViewedEnabled && recentlyViewed.length > 0 && (
              <Button variant="outline" size="sm" className="text-xs">
                <Clock className="h-3 w-3 mr-1" />
                Recent ({recentlyViewed.length})
              </Button>
            )}
          </div>
          
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" className="text-xs">
              <Download className="h-3 w-3 mr-1" />
              Export
            </Button>
            <Button variant="ghost" size="sm" className="text-xs">
              <Filter className="h-3 w-3 mr-1" />
              Filter
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea className="h-[700px]">
          <div className="p-4">
            {searchMode ? (
              // Enhanced Search Results
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">{searchResults.length}</span> results for 
                    <span className="font-medium text-blue-600"> "{searchTerm}"</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSearchMode(false);
                      setSearchTerm('');
                    }}
                  >
                    Clear Search
                  </Button>
                </div>
                
                {searchResults.map(result => (
                  <div
                    key={result.code}
                    className="group p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 hover:shadow-md transition-all duration-200 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50"
                    onClick={() => handleCodeSelect(result.code)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-mono font-semibold text-gray-900">
                            {result.code}
                          </span>
                          <Badge 
                            variant="outline" 
                            className={cn("text-xs", getLevelColor(result.level))}
                          >
                            {result.level}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-700 mb-2">
                          {result.description}
                        </div>
                        {result.duty_rate && (
                          <div className="text-xs text-blue-600 font-medium">
                            Duty Rate: {result.duty_rate}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="xs"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleBookmark(result.code);
                          }}
                        >
                          {bookmarkedCodes.has(result.code) ? (
                            <BookmarkCheck className="h-4 w-4 text-blue-600" />
                          ) : (
                            <Bookmark className="h-4 w-4 text-gray-400" />
                          )}
                        </Button>
                        <ArrowRight className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              // Enhanced Tree View
              <div className="space-y-2">
                {treeData.map(node => renderTreeNode(node))}
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default InteractiveTariffTree;
