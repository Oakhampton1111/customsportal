import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Plus, 
  X, 
  Search, 
  ArrowRight, 
  Download, 
  Share2, 
  Calculator,
  Scale,
  FileText,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Minus
} from 'lucide-react';

interface TariffCode {
  hs_code: string;
  description: string;
  general_rate: string;
  statistical_code?: string;
  unit_of_quantity: string;
  special_rates: {
    fta_name: string;
    rate: string;
    conditions?: string;
  }[];
  restrictions?: string[];
  notes?: string[];
}

interface ComparisonData {
  hs_code: string;
  tariff_data: TariffCode;
  duty_calculation?: {
    general_duty: number;
    gst: number;
    total_duty: number;
    best_fta_rate?: string;
    best_fta_duty?: number;
  };
  complexity_score: number;
  recommendation?: string;
}

interface TariffComparisonPanelProps {
  initialCodes?: string[];
  className?: string;
  onCalculate?: (codes: string[]) => void;
}

export const TariffComparisonPanel: React.FC<TariffComparisonPanelProps> = ({
  initialCodes = [],
  className = '',
  onCalculate
}) => {
  const [comparisonCodes, setComparisonCodes] = useState<string[]>(initialCodes);
  const [searchTerm, setSearchTerm] = useState('');
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<TariffCode[]>([]);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    if (comparisonCodes.length > 0) {
      fetchComparisonData();
    }
  }, [comparisonCodes]);

  const fetchComparisonData = async () => {
    if (comparisonCodes.length === 0) return;
    
    setLoading(true);
    try {
      const codesParam = comparisonCodes.join(',');
      const response = await fetch(`/api/tariff/compare?codes=${codesParam}`);
      
      if (response.ok) {
        const data = await response.json();
        setComparisonData(data);
      }
    } catch (error) {
      console.error('Failed to fetch comparison data:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchTariffCodes = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`/api/tariff/search?q=${encodeURIComponent(query)}&limit=10`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (error) {
      console.error('Failed to search tariff codes:', error);
    }
  };

  const addCode = (code: string) => {
    if (!comparisonCodes.includes(code) && comparisonCodes.length < 5) {
      setComparisonCodes(prev => [...prev, code]);
      setSearchTerm('');
      setSearchResults([]);
      setShowSearch(false);
    }
  };

  const removeCode = (code: string) => {
    setComparisonCodes(prev => prev.filter(c => c !== code));
  };

  const exportComparison = async (format: 'pdf' | 'csv' | 'excel') => {
    try {
      const response = await fetch('/api/tariff/comparison/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          codes: comparisonCodes,
          format,
          data: comparisonData
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tariff-comparison.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to export comparison:', error);
    }
  };

  const shareComparison = async () => {
    try {
      const response = await fetch('/api/tariff/comparison/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          codes: comparisonCodes,
          data: comparisonData
        })
      });

      if (response.ok) {
        const { share_url } = await response.json();
        await navigator.clipboard.writeText(share_url);
        // You could show a toast notification here
        console.log('Share URL copied to clipboard');
      }
    } catch (error) {
      console.error('Failed to share comparison:', error);
    }
  };

  const getComplexityColor = (score: number) => {
    if (score <= 3) return 'text-green-600';
    if (score <= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getComplexityLabel = (score: number) => {
    if (score <= 3) return 'Simple';
    if (score <= 6) return 'Moderate';
    return 'Complex';
  };

  const getBestRate = (data: ComparisonData) => {
    const generalRate = parseFloat(data.tariff_data.general_rate.replace('%', ''));
    let bestRate = generalRate;
    let bestFta = '';

    data.tariff_data.special_rates.forEach(rate => {
      const rateValue = parseFloat(rate.rate.replace('%', ''));
      if (rateValue < bestRate) {
        bestRate = rateValue;
        bestFta = rate.fta_name;
      }
    });

    return { rate: bestRate, fta: bestFta };
  };

  const renderComparisonHeader = () => (
    <div className="space-y-4">
      {/* Add Code Section */}
      <div className="flex gap-2">
        <div className="flex-1">
          {showSearch ? (
            <div className="relative">
              <Input
                placeholder="Search for HS codes to compare..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  searchTariffCodes(e.target.value);
                }}
                className="pr-8"
              />
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1 h-6 w-6 p-0"
                onClick={() => {
                  setShowSearch(false);
                  setSearchTerm('');
                  setSearchResults([]);
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              onClick={() => setShowSearch(true)}
              disabled={comparisonCodes.length >= 5}
              className="w-full justify-start"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add HS Code to Compare {comparisonCodes.length >= 5 && '(Max 5)'}
            </Button>
          )}
        </div>

        <Button
          variant="outline"
          onClick={() => onCalculate?.(comparisonCodes)}
          disabled={comparisonCodes.length === 0}
        >
          <Calculator className="h-4 w-4 mr-2" />
          Calculate All
        </Button>

        <Button
          variant="outline"
          onClick={() => exportComparison('pdf')}
          disabled={comparisonData.length === 0}
        >
          <Download className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          onClick={shareComparison}
          disabled={comparisonData.length === 0}
        >
          <Share2 className="h-4 w-4" />
        </Button>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <Card className="p-3">
          <div className="space-y-2">
            {searchResults.map((result) => (
              <div
                key={result.hs_code}
                className="flex items-center justify-between p-2 hover:bg-muted rounded cursor-pointer"
                onClick={() => addCode(result.hs_code)}
              >
                <div>
                  <span className="font-mono font-medium">{result.hs_code}</span>
                  <p className="text-sm text-muted-foreground truncate">
                    {result.description}
                  </p>
                </div>
                <Plus className="h-4 w-4 text-muted-foreground" />
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Current Codes */}
      {comparisonCodes.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {comparisonCodes.map((code) => (
            <Badge key={code} variant="outline" className="px-3 py-1">
              <span className="font-mono">{code}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-4 w-4 p-0 ml-2"
                onClick={() => removeCode(code)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );

  const renderSideBySideComparison = () => {
    if (comparisonData.length === 0) {
      return (
        <div className="text-center py-12">
          <Scale className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Add HS codes to start comparing</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Summary Comparison */}
        <Card className="p-4">
          <h4 className="font-semibold mb-3">Quick Comparison</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">HS Code</th>
                  <th className="text-left p-2">General Rate</th>
                  <th className="text-left p-2">Best FTA Rate</th>
                  <th className="text-left p-2">Complexity</th>
                  <th className="text-left p-2">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((data) => {
                  const bestRate = getBestRate(data);
                  return (
                    <tr key={data.hs_code} className="border-b">
                      <td className="p-2 font-mono font-medium">{data.hs_code}</td>
                      <td className="p-2">{data.tariff_data.general_rate}</td>
                      <td className="p-2">
                        {bestRate.fta ? (
                          <div>
                            <span className="font-medium">{bestRate.rate}%</span>
                            <p className="text-xs text-muted-foreground">{bestRate.fta}</p>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">No FTA</span>
                        )}
                      </td>
                      <td className="p-2">
                        <Badge variant="outline" className={getComplexityColor(data.complexity_score)}>
                          {getComplexityLabel(data.complexity_score)}
                        </Badge>
                      </td>
                      <td className="p-2">
                        {data.recommendation && (
                          <div className="flex items-center gap-1">
                            {data.complexity_score <= 3 ? (
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-yellow-500" />
                            )}
                            <span className="text-xs">{data.recommendation}</span>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Detailed Side-by-Side */}
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${Math.min(comparisonData.length, 3)}, 1fr)` }}>
          {comparisonData.slice(0, 3).map((data) => (
            <Card key={data.hs_code} className="p-4">
              <div className="space-y-4">
                {/* Header */}
                <div>
                  <h4 className="font-mono font-bold text-lg">{data.hs_code}</h4>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {data.tariff_data.description}
                  </p>
                </div>

                {/* Rates */}
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium">General Rate</span>
                    <p className="text-xl font-bold">{data.tariff_data.general_rate}</p>
                  </div>

                  {data.tariff_data.special_rates.length > 0 && (
                    <div>
                      <span className="text-sm font-medium">FTA Rates</span>
                      <div className="space-y-1 mt-1">
                        {data.tariff_data.special_rates.slice(0, 3).map((rate, index) => (
                          <div key={index} className="flex justify-between text-sm">
                            <span className="text-muted-foreground">{rate.fta_name}</span>
                            <span className="font-medium">{rate.rate}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Unit & Stats */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Unit</span>
                    <span>{data.tariff_data.unit_of_quantity}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Complexity</span>
                    <Badge variant="outline" className={getComplexityColor(data.complexity_score)}>
                      {getComplexityLabel(data.complexity_score)}
                    </Badge>
                  </div>
                </div>

                {/* Duty Calculation */}
                {data.duty_calculation && (
                  <div className="bg-muted/50 p-3 rounded">
                    <span className="text-sm font-medium">Estimated Duties (per $1000)</span>
                    <div className="space-y-1 mt-1 text-sm">
                      <div className="flex justify-between">
                        <span>General Duty</span>
                        <span>${data.duty_calculation.general_duty.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>GST</span>
                        <span>${data.duty_calculation.gst.toFixed(2)}</span>
                      </div>
                      <Separator className="my-1" />
                      <div className="flex justify-between font-medium">
                        <span>Total</span>
                        <span>${data.duty_calculation.total_duty.toFixed(2)}</span>
                      </div>
                      {data.duty_calculation.best_fta_duty && (
                        <div className="flex justify-between text-green-600">
                          <span>Best FTA</span>
                          <span>${data.duty_calculation.best_fta_duty.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Restrictions */}
                {data.tariff_data.restrictions && data.tariff_data.restrictions.length > 0 && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-xs">
                      {data.tariff_data.restrictions[0]}
                      {data.tariff_data.restrictions.length > 1 && (
                        <span className="text-muted-foreground"> (+{data.tariff_data.restrictions.length - 1} more)</span>
                      )}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </Card>
          ))}
        </div>

        {/* Additional Codes */}
        {comparisonData.length > 3 && (
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Additional Codes</h4>
            <div className="space-y-2">
              {comparisonData.slice(3).map((data) => {
                const bestRate = getBestRate(data);
                return (
                  <div key={data.hs_code} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <span className="font-mono font-medium">{data.hs_code}</span>
                      <p className="text-sm text-muted-foreground truncate max-w-[300px]">
                        {data.tariff_data.description}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{data.tariff_data.general_rate}</p>
                      {bestRate.fta && (
                        <p className="text-sm text-green-600">{bestRate.rate}% ({bestRate.fta})</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}
      </div>
    );
  };

  const renderMatrixView = () => {
    if (comparisonData.length === 0) return null;

    const attributes = [
      'General Rate',
      'Best FTA Rate',
      'Unit of Quantity',
      'Complexity',
      'Restrictions',
      'Special Conditions'
    ];

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr>
              <th className="text-left p-3 border-b font-medium">Attribute</th>
              {comparisonData.map((data) => (
                <th key={data.hs_code} className="text-left p-3 border-b font-mono">
                  {data.hs_code}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="p-3 font-medium">Description</td>
              {comparisonData.map((data) => (
                <td key={data.hs_code} className="p-3 max-w-[200px]">
                  <p className="line-clamp-2 text-muted-foreground">
                    {data.tariff_data.description}
                  </p>
                </td>
              ))}
            </tr>
            
            <tr className="border-b">
              <td className="p-3 font-medium">General Rate</td>
              {comparisonData.map((data) => (
                <td key={data.hs_code} className="p-3 font-bold">
                  {data.tariff_data.general_rate}
                </td>
              ))}
            </tr>

            <tr className="border-b">
              <td className="p-3 font-medium">Best FTA Rate</td>
              {comparisonData.map((data) => {
                const bestRate = getBestRate(data);
                return (
                  <td key={data.hs_code} className="p-3">
                    {bestRate.fta ? (
                      <div>
                        <span className="font-bold text-green-600">{bestRate.rate}%</span>
                        <p className="text-xs text-muted-foreground">{bestRate.fta}</p>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">No FTA</span>
                    )}
                  </td>
                );
              })}
            </tr>

            <tr className="border-b">
              <td className="p-3 font-medium">Unit of Quantity</td>
              {comparisonData.map((data) => (
                <td key={data.hs_code} className="p-3">
                  {data.tariff_data.unit_of_quantity}
                </td>
              ))}
            </tr>

            <tr className="border-b">
              <td className="p-3 font-medium">Complexity</td>
              {comparisonData.map((data) => (
                <td key={data.hs_code} className="p-3">
                  <Badge variant="outline" className={getComplexityColor(data.complexity_score)}>
                    {getComplexityLabel(data.complexity_score)}
                  </Badge>
                </td>
              ))}
            </tr>

            <tr className="border-b">
              <td className="p-3 font-medium">Restrictions</td>
              {comparisonData.map((data) => (
                <td key={data.hs_code} className="p-3">
                  {data.tariff_data.restrictions && data.tariff_data.restrictions.length > 0 ? (
                    <Badge variant="outline" className="text-red-600">
                      {data.tariff_data.restrictions.length} restriction(s)
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="text-green-600">
                      None
                    </Badge>
                  )}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    );
  };

  if (loading) {
    return (
      <Card className={`h-full ${className}`}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading comparison data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Scale className="h-5 w-5" />
          Tariff Code Comparison
        </CardTitle>
        {renderComparisonHeader()}
      </CardHeader>

      <CardContent className="pt-0">
        <Tabs defaultValue="sidebyside" className="h-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="sidebyside">Side by Side</TabsTrigger>
            <TabsTrigger value="matrix">Matrix View</TabsTrigger>
          </TabsList>

          <TabsContent value="sidebyside" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderSideBySideComparison()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="matrix" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderMatrixView()}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default TariffComparisonPanel;
