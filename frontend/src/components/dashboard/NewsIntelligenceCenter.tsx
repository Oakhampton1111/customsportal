import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Filter, RefreshCw, ExternalLink, Clock, TrendingUp } from 'lucide-react';

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  content: string;
  source: string;
  category: string;
  impact_score: number;
  related_hs_codes: string[];
  published_date: string;
  url?: string;
}

interface NewsIntelligenceCenterProps {
  className?: string;
}

export const NewsIntelligenceCenter: React.FC<NewsIntelligenceCenterProps> = ({ 
  className = '' 
}) => {
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const categories = [
    { value: 'all', label: 'All News', count: 0 },
    { value: 'critical', label: 'Critical Updates', count: 0 },
    { value: 'regulatory', label: 'Regulatory Changes', count: 0 },
    { value: 'tco', label: 'TCO Updates', count: 0 },
    { value: 'dumping', label: 'Anti-Dumping', count: 0 },
    { value: 'fta', label: 'FTA Changes', count: 0 }
  ];

  const fetchNews = useCallback(async (reset = false) => {
    setLoading(true);
    try {
      const currentPage = reset ? 1 : page;
      const response = await fetch(
        `/api/news/dashboard-feed?limit=20&category=${selectedCategory}&page=${currentPage}&search=${searchTerm}`
      );
      
      if (response.ok) {
        const newItems = await response.json();
        
        if (reset) {
          setNewsItems(newItems);
          setPage(2);
        } else {
          setNewsItems(prev => [...prev, ...newItems]);
          setPage(prev => prev + 1);
        }
        
        setHasMore(newItems.length === 20);
      }
    } catch (error) {
      console.error('Failed to fetch news:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, searchTerm, page]);

  // Initial load and refresh
  useEffect(() => {
    fetchNews(true);
  }, [selectedCategory, searchTerm]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchNews(true);
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [fetchNews]);

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      fetchNews(false);
    }
  };

  const getImpactBadgeColor = (score: number) => {
    if (score >= 4) return 'destructive';
    if (score >= 3) return 'default';
    return 'secondary';
  };

  const getImpactLabel = (score: number) => {
    if (score >= 4) return 'High Impact';
    if (score >= 3) return 'Medium Impact';
    return 'Low Impact';
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Trade Intelligence Center
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchNews(true)}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        
        {/* Search and Filters */}
        <div className="flex gap-2 mt-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search news, HS codes, or topics..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
          <TabsList className="grid w-full grid-cols-6 px-4">
            {categories.map((category) => (
              <TabsTrigger key={category.value} value={category.value} className="text-xs">
                {category.label}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value={selectedCategory} className="mt-0">
            <ScrollArea className="h-[600px]">
              <div className="space-y-3 p-4">
                {newsItems.map((item) => (
                  <Card key={item.id} className="p-4 hover:shadow-md transition-shadow">
                    <div className="space-y-3">
                      {/* Header */}
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-sm leading-tight">
                            {item.title}
                          </h4>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {item.source}
                            </Badge>
                            <Badge variant={getImpactBadgeColor(item.impact_score)} className="text-xs">
                              {getImpactLabel(item.impact_score)}
                            </Badge>
                            <span className="text-xs text-muted-foreground flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatTimeAgo(item.published_date)}
                            </span>
                          </div>
                        </div>
                        {item.url && (
                          <Button variant="ghost" size="sm" asChild>
                            <a href={item.url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        )}
                      </div>

                      {/* Summary */}
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {item.summary}
                      </p>

                      {/* Related HS Codes */}
                      {item.related_hs_codes.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          <span className="text-xs text-muted-foreground">Related codes:</span>
                          {item.related_hs_codes.slice(0, 3).map((code) => (
                            <Badge key={code} variant="secondary" className="text-xs">
                              {code}
                            </Badge>
                          ))}
                          {item.related_hs_codes.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{item.related_hs_codes.length - 3} more
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </Card>
                ))}

                {/* Load More Button */}
                {hasMore && (
                  <div className="text-center pt-4">
                    <Button
                      variant="outline"
                      onClick={handleLoadMore}
                      disabled={loading}
                    >
                      {loading ? 'Loading...' : 'Load More News'}
                    </Button>
                  </div>
                )}

                {!hasMore && newsItems.length > 0 && (
                  <div className="text-center text-sm text-muted-foreground pt-4">
                    You've reached the end of the news feed
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default NewsIntelligenceCenter;
