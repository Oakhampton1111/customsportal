import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Globe, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Package, 
  AlertCircle,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  ExternalLink,
  BarChart3
} from 'lucide-react';

interface MarketAccessInfo {
  country_code: string;
  country_name: string;
  region: string;
  market_status: 'open' | 'restricted' | 'prohibited';
  tariff_rate: string;
  fta_eligible: boolean;
  fta_name?: string;
  fta_rate?: string;
  quota_applicable: boolean;
  quota_details?: string;
  market_size_usd: number;
  growth_rate: number;
  competition_level: 'low' | 'medium' | 'high';
  ease_of_access: number; // 1-10 scale
  regulatory_complexity: 'low' | 'medium' | 'high';
  key_requirements: string[];
  opportunities: string[];
  challenges: string[];
  trade_statistics: {
    exports_2023: number;
    exports_2022: number;
    market_share: number;
    rank: number;
  };
}

interface MarketOpportunity {
  id: string;
  country: string;
  product_category: string;
  opportunity_type: 'emerging' | 'growing' | 'stable' | 'declining';
  potential_value: number;
  confidence_score: number;
  timeframe: string;
  description: string;
  action_required: string[];
}

interface MarketAccessDashboardProps {
  ahecCode?: string;
  className?: string;
}

export const MarketAccessDashboard: React.FC<MarketAccessDashboardProps> = ({
  ahecCode,
  className = ''
}) => {
  const [marketData, setMarketData] = useState<MarketAccessInfo[]>([]);
  const [opportunities, setOpportunities] = useState<MarketOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [regionFilter, setRegionFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('market_size');

  useEffect(() => {
    fetchMarketData();
    fetchOpportunities();
  }, [ahecCode]);

  const fetchMarketData = async () => {
    setLoading(true);
    try {
      const endpoint = ahecCode 
        ? `/api/export/market-access?ahecc_code=${ahecCode}`
        : '/api/export/market-access';
      
      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setMarketData(data);
      }
    } catch (error) {
      console.error('Failed to fetch market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOpportunities = async () => {
    try {
      const endpoint = ahecCode 
        ? `/api/export/opportunities?ahecc_code=${ahecCode}`
        : '/api/export/opportunities';
      
      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setOpportunities(data);
      }
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'restricted': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'prohibited': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-green-600 bg-green-50';
      case 'restricted': return 'text-yellow-600 bg-yellow-50';
      case 'prohibited': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getCompetitionColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getOpportunityIcon = (type: string) => {
    switch (type) {
      case 'emerging': return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'growing': return <TrendingUp className="h-4 w-4 text-blue-500" />;
      case 'stable': return <BarChart3 className="h-4 w-4 text-gray-500" />;
      case 'declining': return <TrendingDown className="h-4 w-4 text-red-500" />;
      default: return <BarChart3 className="h-4 w-4 text-gray-500" />;
    }
  };

  const filteredMarketData = marketData
    .filter(market => {
      const matchesSearch = market.country_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           market.region.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRegion = regionFilter === 'all' || market.region === regionFilter;
      const matchesStatus = statusFilter === 'all' || market.market_status === statusFilter;
      return matchesSearch && matchesRegion && matchesStatus;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'market_size': return b.market_size_usd - a.market_size_usd;
        case 'growth_rate': return b.growth_rate - a.growth_rate;
        case 'ease_of_access': return b.ease_of_access - a.ease_of_access;
        case 'country_name': return a.country_name.localeCompare(b.country_name);
        default: return 0;
      }
    });

  const regions = [...new Set(marketData.map(m => m.region))];

  const renderMarketOverview = () => (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 p-4 bg-muted/50 rounded-lg">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search countries or regions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={regionFilter} onValueChange={setRegionFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Region" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Regions</SelectItem>
            {regions.map(region => (
              <SelectItem key={region} value={region}>{region}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="restricted">Restricted</SelectItem>
            <SelectItem value="prohibited">Prohibited</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="market_size">Market Size</SelectItem>
            <SelectItem value="growth_rate">Growth Rate</SelectItem>
            <SelectItem value="ease_of_access">Ease of Access</SelectItem>
            <SelectItem value="country_name">Country Name</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Market Cards */}
      <div className="grid gap-4">
        {filteredMarketData.map((market) => (
          <Card key={market.country_code} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <Globe className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h4 className="font-semibold">{market.country_name}</h4>
                  <p className="text-sm text-muted-foreground">{market.region}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(market.market_status)}
                <Badge className={getStatusColor(market.market_status)}>
                  {market.market_status.toUpperCase()}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <span className="text-xs text-muted-foreground">Market Size</span>
                <p className="font-semibold flex items-center gap-1">
                  <DollarSign className="h-3 w-3" />
                  ${(market.market_size_usd / 1000000).toFixed(1)}M
                </p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Growth Rate</span>
                <p className="font-semibold flex items-center gap-1">
                  {market.growth_rate >= 0 ? (
                    <TrendingUp className="h-3 w-3 text-green-500" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-red-500" />
                  )}
                  {market.growth_rate.toFixed(1)}%
                </p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Tariff Rate</span>
                <p className="font-semibold">{market.tariff_rate}</p>
                {market.fta_eligible && (
                  <p className="text-xs text-green-600">FTA: {market.fta_rate}</p>
                )}
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Competition</span>
                <p className={`font-semibold ${getCompetitionColor(market.competition_level)}`}>
                  {market.competition_level.toUpperCase()}
                </p>
              </div>
            </div>

            {market.fta_eligible && (
              <Alert className="mb-3">
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>FTA Eligible:</strong> {market.fta_name} - Preferential rate: {market.fta_rate}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium text-green-700">Opportunities:</span>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  {market.opportunities.slice(0, 2).map((opp, index) => (
                    <li key={index} className="text-muted-foreground">{opp}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="font-medium text-red-700">Challenges:</span>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  {market.challenges.slice(0, 2).map((challenge, index) => (
                    <li key={index} className="text-muted-foreground">{challenge}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="font-medium">Key Requirements:</span>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  {market.key_requirements.slice(0, 2).map((req, index) => (
                    <li key={index} className="text-muted-foreground">{req}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex justify-between items-center mt-4 pt-3 border-t">
              <div className="flex items-center gap-4 text-sm">
                <span>Ease of Access: <strong>{market.ease_of_access}/10</strong></span>
                <span>Regulatory Complexity: <strong className={getCompetitionColor(market.regulatory_complexity)}>{market.regulatory_complexity.toUpperCase()}</strong></span>
              </div>
              <Button variant="outline" size="sm">
                <ExternalLink className="h-4 w-4 mr-2" />
                View Details
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderOpportunities = () => (
    <div className="space-y-4">
      {opportunities.length > 0 ? (
        opportunities.map((opportunity) => (
          <Card key={opportunity.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                {getOpportunityIcon(opportunity.opportunity_type)}
                <div>
                  <h4 className="font-semibold">{opportunity.country}</h4>
                  <p className="text-sm text-muted-foreground">{opportunity.product_category}</p>
                </div>
              </div>
              <div className="text-right">
                <Badge variant="outline" className="mb-1">
                  {opportunity.opportunity_type.toUpperCase()}
                </Badge>
                <p className="text-sm font-semibold">
                  ${(opportunity.potential_value / 1000000).toFixed(1)}M potential
                </p>
              </div>
            </div>

            <p className="text-sm text-muted-foreground mb-3">{opportunity.description}</p>

            <div className="grid grid-cols-3 gap-4 mb-3 text-sm">
              <div>
                <span className="text-muted-foreground">Confidence Score</span>
                <p className="font-medium">{opportunity.confidence_score}/100</p>
              </div>
              <div>
                <span className="text-muted-foreground">Timeframe</span>
                <p className="font-medium">{opportunity.timeframe}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Priority</span>
                <Badge variant={opportunity.confidence_score > 75 ? 'default' : 'secondary'}>
                  {opportunity.confidence_score > 75 ? 'High' : 'Medium'}
                </Badge>
              </div>
            </div>

            <div>
              <span className="text-sm font-medium">Action Required:</span>
              <ul className="list-disc list-inside text-sm text-muted-foreground mt-1 space-y-1">
                {opportunity.action_required.map((action, index) => (
                  <li key={index}>{action}</li>
                ))}
              </ul>
            </div>
          </Card>
        ))
      ) : (
        <div className="text-center py-8">
          <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No market opportunities identified at this time</p>
        </div>
      )}
    </div>
  );

  const renderTradeStatistics = () => {
    const totalMarketSize = marketData.reduce((sum, market) => sum + market.market_size_usd, 0);
    const openMarkets = marketData.filter(m => m.market_status === 'open').length;
    const ftaEligible = marketData.filter(m => m.fta_eligible).length;
    const avgGrowthRate = marketData.reduce((sum, market) => sum + market.growth_rate, 0) / marketData.length;

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="p-4 text-center">
            <DollarSign className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">${(totalMarketSize / 1000000000).toFixed(1)}B</p>
            <p className="text-sm text-muted-foreground">Total Market Size</p>
          </Card>
          <Card className="p-4 text-center">
            <Globe className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{openMarkets}</p>
            <p className="text-sm text-muted-foreground">Open Markets</p>
          </Card>
          <Card className="p-4 text-center">
            <CheckCircle className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{ftaEligible}</p>
            <p className="text-sm text-muted-foreground">FTA Eligible</p>
          </Card>
          <Card className="p-4 text-center">
            <TrendingUp className="h-8 w-8 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold">{avgGrowthRate.toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground">Avg Growth Rate</p>
          </Card>
        </div>

        <Card className="p-4">
          <h4 className="font-semibold mb-3">Top Export Destinations</h4>
          <div className="space-y-3">
            {marketData
              .sort((a, b) => b.trade_statistics.exports_2023 - a.trade_statistics.exports_2023)
              .slice(0, 5)
              .map((market, index) => (
                <div key={market.country_code} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{index + 1}</Badge>
                    <span className="font-medium">{market.country_name}</span>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">${(market.trade_statistics.exports_2023 / 1000000).toFixed(1)}M</p>
                    <p className="text-sm text-muted-foreground">
                      {market.trade_statistics.market_share.toFixed(1)}% share
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <Card className={`h-full ${className}`}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading market access data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Market Access Intelligence
          {ahecCode && (
            <Badge variant="outline">{ahecCode}</Badge>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="pt-0">
        <Tabs defaultValue="overview" className="h-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Market Overview</TabsTrigger>
            <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
            <TabsTrigger value="statistics">Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4">
            <ScrollArea className="h-[700px]">
              {renderMarketOverview()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="opportunities" className="mt-4">
            <ScrollArea className="h-[700px]">
              {renderOpportunities()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="statistics" className="mt-4">
            <ScrollArea className="h-[700px]">
              {renderTradeStatistics()}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default MarketAccessDashboard;
