import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  ChevronRight, 
  ChevronDown, 
  Search, 
  Globe, 
  Package, 
  FileText,
  ExternalLink
} from 'lucide-react';

interface AHECCNode {
  code: string;
  description: string;
  level: 'section' | 'chapter' | 'heading' | 'subheading';
  parent_code?: string;
  children?: AHECCNode[];
  has_children: boolean;
  export_requirements?: ExportRequirement[];
  market_access?: MarketAccess[];
}

interface ExportRequirement {
  country: string;
  requirement_type: 'permit' | 'certificate' | 'inspection' | 'documentation';
  description: string;
  authority: string;
  processing_time?: string;
  cost?: string;
}

interface MarketAccess {
  country: string;
  tariff_rate: string;
  quota?: string;
  restrictions?: string[];
  fta_benefits?: string;
}

interface AHECCTreeBrowserProps {
  className?: string;
  onCodeSelect?: (code: string) => void;
  selectedCode?: string;
}

export const AHECCTreeBrowser: React.FC<AHECCTreeBrowserProps> = ({
  className = '',
  onCodeSelect,
  selectedCode
}) => {
  const [treeData, setTreeData] = useState<AHECCNode[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<AHECCNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchMode, setSearchMode] = useState(false);

  useEffect(() => {
    loadInitialTree();
  }, []);

  useEffect(() => {
    if (searchTerm.length >= 2) {
      performSearch();
    } else {
      setSearchMode(false);
      setSearchResults([]);
    }
  }, [searchTerm]);

  const loadInitialTree = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/export/ahecc-tree?depth=2');
      if (response.ok) {
        const data = await response.json();
        setTreeData(data.tree || mockTreeData);
      } else {
        setTreeData(mockTreeData);
      }
    } catch (error) {
      console.error('Failed to load AHECC tree:', error);
      setTreeData(mockTreeData);
    } finally {
      setLoading(false);
    }
  };

  const loadChildren = async (parentCode: string) => {
    try {
      const response = await fetch(`/api/export/ahecc-tree?parent=${parentCode}&depth=1`);
      if (response.ok) {
        const data = await response.json();
        
        setTreeData(prevData => 
          updateTreeWithChildren(prevData, parentCode, data.tree)
        );
      }
    } catch (error) {
      console.error('Failed to load children:', error);
    }
  };

  const updateTreeWithChildren = (
    nodes: AHECCNode[], 
    parentCode: string, 
    children: AHECCNode[]
  ): AHECCNode[] => {
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

  const performSearch = async () => {
    try {
      const response = await fetch(
        `/api/export/ahecc-search?query=${encodeURIComponent(searchTerm)}&limit=20`
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

  const handleNodeToggle = (code: string, hasChildren: boolean) => {
    const newExpanded = new Set(expandedNodes);
    
    if (expandedNodes.has(code)) {
      newExpanded.delete(code);
    } else {
      newExpanded.add(code);
      
      if (hasChildren) {
        loadChildren(code);
      }
    }
    
    setExpandedNodes(newExpanded);
  };

  const handleCodeSelect = (code: string) => {
    onCodeSelect?.(code);
  };

  const renderTreeNode = (node: AHECCNode, depth: number = 0) => {
    const isExpanded = expandedNodes.has(node.code);
    const isSelected = selectedCode === node.code;
    const hasRequirements = node.export_requirements && node.export_requirements.length > 0;
    const hasMarketAccess = node.market_access && node.market_access.length > 0;

    return (
      <div key={node.code} className="select-none">
        <div
          className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-muted/50 transition-colors ${
            isSelected ? 'bg-primary/10 border-l-2 border-primary' : ''
          }`}
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
        >
          {/* Expand/Collapse Button */}
          {node.has_children ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => handleNodeToggle(node.code, node.has_children)}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          ) : (
            <div className="w-6" />
          )}

          {/* Node Content */}
          <div 
            className="flex-1 flex items-center gap-2"
            onClick={() => handleCodeSelect(node.code)}
          >
            <span className="font-mono text-sm font-medium">
              {node.code}
            </span>
            <span className="text-sm flex-1">
              {node.description}
            </span>
            
            {/* Level Badge */}
            <Badge variant="outline" className="text-xs">
              {node.level}
            </Badge>

            {/* Indicators */}
            <div className="flex gap-1">
              {hasRequirements && (
                <Badge variant="secondary" className="text-xs">
                  <FileText className="h-3 w-3 mr-1" />
                  Reqs
                </Badge>
              )}
              
              {hasMarketAccess && (
                <Badge variant="secondary" className="text-xs">
                  <Globe className="h-3 w-3 mr-1" />
                  Markets
                </Badge>
              )}
            </div>
          </div>

          {/* Actions */}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={(e) => {
              e.stopPropagation();
              window.open(`/export/${node.code}`, '_blank');
            }}
          >
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>

        {/* Children */}
        {isExpanded && node.children && (
          <div>
            {node.children.map(child => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderSearchResult = (result: AHECCNode) => {
    const hasRequirements = result.export_requirements && result.export_requirements.length > 0;
    const hasMarketAccess = result.market_access && result.market_access.length > 0;

    return (
      <div
        key={result.code}
        className="p-3 border rounded cursor-pointer hover:bg-muted/50"
        onClick={() => handleCodeSelect(result.code)}
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="font-mono font-medium">{result.code}</span>
          <Badge variant="outline" className="text-xs">
            {result.level}
          </Badge>
          
          {hasRequirements && (
            <Badge variant="secondary" className="text-xs">
              <FileText className="h-3 w-3 mr-1" />
              {result.export_requirements!.length} Requirements
            </Badge>
          )}
          
          {hasMarketAccess && (
            <Badge variant="secondary" className="text-xs">
              <Globe className="h-3 w-3 mr-1" />
              {result.market_access!.length} Markets
            </Badge>
          )}
        </div>
        
        <div className="text-sm text-muted-foreground">
          {result.description}
        </div>

        {/* Quick Preview of Requirements */}
        {hasRequirements && (
          <div className="mt-2 text-xs text-muted-foreground">
            <strong>Key Requirements:</strong> {
              result.export_requirements!
                .slice(0, 2)
                .map(req => `${req.country} (${req.requirement_type})`)
                .join(', ')
            }
            {result.export_requirements!.length > 2 && '...'}
          </div>
        )}
      </div>
    );
  };

  const mockTreeData: AHECCNode[] = [
    {
      code: '01',
      description: 'Live Animals and Animal Products',
      level: 'section',
      has_children: true,
      children: [
        {
          code: '0101',
          description: 'Live horses, asses, mules and hinnies',
          level: 'chapter',
          parent_code: '01',
          has_children: true,
          export_requirements: [
            {
              country: 'Japan',
              requirement_type: 'certificate',
              description: 'Health certificate required',
              authority: 'Department of Agriculture',
              processing_time: '5-10 days',
              cost: '$150'
            }
          ],
          market_access: [
            {
              country: 'Japan',
              tariff_rate: '0%',
              fta_benefits: 'JAEPA preferential rate'
            }
          ]
        }
      ]
    },
    {
      code: '02',
      description: 'Vegetable Products',
      level: 'section',
      has_children: true,
      export_requirements: [
        {
          country: 'China',
          requirement_type: 'permit',
          description: 'Export permit required for all vegetable products',
          authority: 'DAFF',
          processing_time: '2-3 weeks'
        }
      ]
    }
  ];

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse flex items-center gap-2">
                <div className="h-4 w-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded flex-1"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          AHECC Export Classification
        </CardTitle>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search export codes or descriptions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Quick Stats */}
        <div className="flex gap-4 text-sm text-muted-foreground">
          <span>📊 21 Sections</span>
          <span>📋 97 Chapters</span>
          <span>🌏 50+ Export Markets</span>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea className="h-[600px]">
          <div className="p-4">
            {searchMode ? (
              // Search Results
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground mb-3">
                  {searchResults.length} results for "{searchTerm}"
                </div>
                {searchResults.map(renderSearchResult)}
              </div>
            ) : (
              // Tree View
              <div className="space-y-1">
                {treeData.map(node => renderTreeNode(node))}
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default AHECCTreeBrowser;
