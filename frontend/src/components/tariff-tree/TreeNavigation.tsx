import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  ChevronRight, 
  ChevronDown, 
  Star, 
  Clock, 
  Bookmark,
  Filter,
  X,
  History,
  TreePine
} from 'lucide-react';

interface TreeNode {
  id: string;
  code: string;
  title: string;
  description: string;
  level: 'section' | 'chapter' | 'heading' | 'subheading' | 'item';
  parent_id?: string;
  children?: TreeNode[];
  has_children: boolean;
  hs_code?: string;
}

interface RecentlyViewed {
  hsCode: string;
  description: string;
  viewedAt: string;
}

interface Bookmark {
  hsCode: string;
  description: string;
  bookmarkedAt: string;
}

interface TreeNavigationProps {
  onNodeSelect?: (node: TreeNode) => void;
  selectedNodeId?: string;
  className?: string;
}

export const TreeNavigation: React.FC<TreeNavigationProps> = ({
  onNodeSelect,
  selectedNodeId,
  className = ''
}) => {
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewed[]>([]);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [activeTab, setActiveTab] = useState('tree');

  // Load initial tree data (sections)
  useEffect(() => {
    loadTreeData();
    loadRecentlyViewed();
    loadBookmarks();
  }, []);

  // Search functionality
  useEffect(() => {
    if (searchTerm.length >= 3) {
      performSearch();
    } else {
      setSearchResults([]);
    }
  }, [searchTerm]);

  const loadTreeData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/tariff/tree/sections');
      if (response.ok) {
        const sections = await response.json();
        setTreeData(sections);
      }
    } catch (error) {
      console.error('Failed to load tree data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecentlyViewed = () => {
    const stored = localStorage.getItem('recentlyViewed');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setRecentlyViewed(parsed.slice(0, 10)); // Keep only last 10
      } catch (error) {
        console.error('Failed to parse recently viewed:', error);
      }
    }
  };

  const loadBookmarks = () => {
    const bookmarkKeys = Object.keys(localStorage).filter(key => key.startsWith('bookmark_'));
    const bookmarkData = bookmarkKeys.map(key => {
      try {
        return JSON.parse(localStorage.getItem(key) || '');
      } catch {
        return null;
      }
    }).filter(Boolean);
    setBookmarks(bookmarkData);
  };

  const performSearch = useCallback(async () => {
    setSearchLoading(true);
    try {
      const response = await fetch(`/api/tariff/search?q=${encodeURIComponent(searchTerm)}&tree=true`);
      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearchLoading(false);
    }
  }, [searchTerm]);

  const toggleNode = async (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    
    if (expandedNodes.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
      
      // Load children if not already loaded
      const node = findNodeById(nodeId, treeData);
      if (node && node.has_children && (!node.children || node.children.length === 0)) {
        await loadNodeChildren(nodeId);
      }
    }
    
    setExpandedNodes(newExpanded);
  };

  const loadNodeChildren = async (nodeId: string) => {
    try {
      const response = await fetch(`/api/tariff/tree/${nodeId}/children`);
      if (response.ok) {
        const children = await response.json();
        
        // Update tree data with children
        const updateNodeChildren = (nodes: TreeNode[]): TreeNode[] => {
          return nodes.map(node => {
            if (node.id === nodeId) {
              return { ...node, children };
            }
            if (node.children) {
              return { ...node, children: updateNodeChildren(node.children) };
            }
            return node;
          });
        };
        
        setTreeData(updateNodeChildren(treeData));
      }
    } catch (error) {
      console.error('Failed to load node children:', error);
    }
  };

  const findNodeById = (id: string, nodes: TreeNode[]): TreeNode | null => {
    for (const node of nodes) {
      if (node.id === id) return node;
      if (node.children) {
        const found = findNodeById(id, node.children);
        if (found) return found;
      }
    }
    return null;
  };

  const handleNodeSelect = (node: TreeNode) => {
    onNodeSelect?.(node);
    
    // Add to recently viewed if it's a leaf node with HS code
    if (node.hs_code) {
      addToRecentlyViewed({
        hsCode: node.hs_code,
        description: node.description,
        viewedAt: new Date().toISOString()
      });
    }
  };

  const addToRecentlyViewed = (item: RecentlyViewed) => {
    const updated = [item, ...recentlyViewed.filter(r => r.hsCode !== item.hsCode)].slice(0, 10);
    setRecentlyViewed(updated);
    localStorage.setItem('recentlyViewed', JSON.stringify(updated));
  };

  const clearRecentlyViewed = () => {
    setRecentlyViewed([]);
    localStorage.removeItem('recentlyViewed');
  };

  const removeBookmark = (hsCode: string) => {
    localStorage.removeItem(`bookmark_${hsCode}`);
    loadBookmarks();
  };

  const clearSearch = () => {
    setSearchTerm('');
    setSearchResults([]);
  };

  const renderTreeNode = (node: TreeNode, level: number = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedNodeId === node.id;
    const hasChildren = node.has_children;

    return (
      <div key={node.id} className="select-none">
        <div
          className={`flex items-center gap-2 p-2 hover:bg-accent rounded cursor-pointer ${
            isSelected ? 'bg-accent' : ''
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => handleNodeSelect(node)}
        >
          {hasChildren ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-4 w-4 p-0"
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(node.id);
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
            </Button>
          ) : (
            <div className="w-4" />
          )}
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {node.code}
              </Badge>
              {node.hs_code && (
                <Badge variant="secondary" className="text-xs">
                  {node.hs_code}
                </Badge>
              )}
            </div>
            <p className="text-sm font-medium truncate">{node.title}</p>
            <p className="text-xs text-muted-foreground truncate">{node.description}</p>
          </div>
        </div>
        
        {isExpanded && node.children && (
          <div>
            {node.children.map(child => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderSearchResults = () => (
    <div className="space-y-2">
      {searchResults.map((result) => (
        <div
          key={result.id}
          className="p-3 border rounded hover:bg-accent cursor-pointer"
          onClick={() => handleNodeSelect(result)}
        >
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-xs">
              {result.code}
            </Badge>
            {result.hs_code && (
              <Badge variant="secondary" className="text-xs">
                {result.hs_code}
              </Badge>
            )}
            <Badge variant="outline" className="text-xs capitalize">
              {result.level}
            </Badge>
          </div>
          <p className="text-sm font-medium">{result.title}</p>
          <p className="text-xs text-muted-foreground">{result.description}</p>
        </div>
      ))}
    </div>
  );

  const renderRecentlyViewed = () => (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Recently Viewed</h4>
        {recentlyViewed.length > 0 && (
          <Button variant="ghost" size="sm" onClick={clearRecentlyViewed}>
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>
      {recentlyViewed.length > 0 ? (
        recentlyViewed.map((item, index) => (
          <div
            key={index}
            className="p-2 border rounded hover:bg-accent cursor-pointer"
            onClick={() => {
              // Navigate to this code
              setSearchTerm(item.hsCode);
              setActiveTab('search');
            }}
          >
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-3 w-3 text-muted-foreground" />
              <Badge variant="secondary" className="text-xs">
                {item.hsCode}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground truncate">{item.description}</p>
            <p className="text-xs text-muted-foreground">
              {new Date(item.viewedAt).toLocaleDateString()}
            </p>
          </div>
        ))
      ) : (
        <p className="text-sm text-muted-foreground text-center py-4">
          No recently viewed codes
        </p>
      )}
    </div>
  );

  const renderBookmarks = () => (
    <div className="space-y-2">
      <h4 className="text-sm font-medium">Bookmarked Codes</h4>
      {bookmarks.length > 0 ? (
        bookmarks.map((bookmark, index) => (
          <div
            key={index}
            className="p-2 border rounded hover:bg-accent cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <div
                className="flex-1"
                onClick={() => {
                  setSearchTerm(bookmark.hsCode);
                  setActiveTab('search');
                }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Star className="h-3 w-3 text-yellow-500 fill-current" />
                  <Badge variant="secondary" className="text-xs">
                    {bookmark.hsCode}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground truncate">{bookmark.description}</p>
                <p className="text-xs text-muted-foreground">
                  {new Date(bookmark.bookmarkedAt).toLocaleDateString()}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0"
                onClick={() => removeBookmark(bookmark.hsCode)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
        ))
      ) : (
        <p className="text-sm text-muted-foreground text-center py-4">
          No bookmarked codes
        </p>
      )}
    </div>
  );

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <TreePine className="h-5 w-5" />
          Schedule 3 Navigation
        </CardTitle>
        
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search tariff codes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchTerm && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
              onClick={clearSearch}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="tree">Tree</TabsTrigger>
            <TabsTrigger value="search">Search</TabsTrigger>
            <TabsTrigger value="recent">Recent</TabsTrigger>
            <TabsTrigger value="bookmarks">Saved</TabsTrigger>
          </TabsList>

          <TabsContent value="tree" className="mt-4">
            <ScrollArea className="h-[600px]">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
              ) : (
                <div className="space-y-1">
                  {treeData.map(node => renderTreeNode(node))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="search" className="mt-4">
            <ScrollArea className="h-[600px]">
              {searchLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
              ) : searchTerm.length >= 3 ? (
                searchResults.length > 0 ? (
                  renderSearchResults()
                ) : (
                  <div className="text-center py-8">
                    <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No results found for "{searchTerm}"</p>
                  </div>
                )
              ) : (
                <div className="text-center py-8">
                  <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Enter at least 3 characters to search</p>
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="recent" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderRecentlyViewed()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="bookmarks" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderBookmarks()}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default TreeNavigation;
