import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ExternalLink, FileText, Calendar, Tag } from 'lucide-react';

interface Ruling {
  id: string;
  ruling_number: string;
  title: string;
  summary: string;
  hs_codes: string[];
  ruling_type: 'binding' | 'classification' | 'valuation' | 'origin';
  status: 'active' | 'superseded' | 'revoked';
  published_date: string;
  effective_date: string;
  url?: string;
  impact_level: 'high' | 'medium' | 'low';
}

interface RecentRulingsPanelProps {
  className?: string;
  maxItems?: number;
}

export const RecentRulingsPanel: React.FC<RecentRulingsPanelProps> = ({ 
  className = '',
  maxItems = 10
}) => {
  const [rulings, setRulings] = useState<Ruling[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('all');

  useEffect(() => {
    fetchRecentRulings();
  }, [selectedType]);

  const fetchRecentRulings = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/rulings/recent?limit=${maxItems}&type=${selectedType}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setRulings(data.rulings || mockRulings);
      } else {
        setRulings(mockRulings);
      }
    } catch (error) {
      console.error('Failed to fetch rulings:', error);
      setRulings(mockRulings);
    } finally {
      setLoading(false);
    }
  };

  const mockRulings: Ruling[] = [
    {
      id: '1',
      ruling_number: 'BR-2024-001',
      title: 'Classification of Smart Home Devices',
      summary: 'Binding ruling on classification of IoT-enabled home automation devices under Chapter 85',
      hs_codes: ['8517.62.00', '8543.70.90'],
      ruling_type: 'binding',
      status: 'active',
      published_date: '2024-05-30',
      effective_date: '2024-06-01',
      impact_level: 'high',
      url: 'https://example.com/ruling/BR-2024-001'
    },
    {
      id: '2',
      ruling_number: 'CR-2024-045',
      title: 'Electric Vehicle Battery Classification',
      summary: 'Classification determination for lithium-ion battery packs used in electric vehicles',
      hs_codes: ['8507.60.00'],
      ruling_type: 'classification',
      status: 'active',
      published_date: '2024-05-28',
      effective_date: '2024-05-28',
      impact_level: 'medium',
      url: 'https://example.com/ruling/CR-2024-045'
    },
    {
      id: '3',
      ruling_number: 'VR-2024-012',
      title: 'Valuation of Software Licenses',
      summary: 'Valuation methodology for imported software licenses and digital products',
      hs_codes: ['8523.80.00'],
      ruling_type: 'valuation',
      status: 'active',
      published_date: '2024-05-25',
      effective_date: '2024-06-15',
      impact_level: 'high'
    },
    {
      id: '4',
      ruling_number: 'OR-2024-008',
      title: 'CPTPP Origin Rules for Automotive Parts',
      summary: 'Rules of origin determination for automotive components under CPTPP',
      hs_codes: ['8708.29.00', '8708.80.00'],
      ruling_type: 'origin',
      status: 'active',
      published_date: '2024-05-22',
      effective_date: '2024-05-22',
      impact_level: 'medium'
    }
  ];

  const rulingTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'binding', label: 'Binding Rulings' },
    { value: 'classification', label: 'Classification' },
    { value: 'valuation', label: 'Valuation' },
    { value: 'origin', label: 'Origin' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'superseded':
        return 'secondary';
      case 'revoked':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getRulingTypeIcon = (type: string) => {
    switch (type) {
      case 'binding':
        return '🔒';
      case 'classification':
        return '📋';
      case 'valuation':
        return '💰';
      case 'origin':
        return '🌏';
      default:
        return '📄';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Recent Rulings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
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
          <FileText className="h-5 w-5" />
          Recent Rulings
        </CardTitle>
        
        {/* Type Filter */}
        <div className="flex flex-wrap gap-1 mt-2">
          {rulingTypes.map((type) => (
            <Button
              key={type.value}
              variant={selectedType === type.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedType(type.value)}
              className="text-xs"
            >
              {type.label}
            </Button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          <div className="space-y-3 p-4">
            {rulings.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No recent rulings found</p>
              </div>
            ) : (
              rulings.map((ruling) => (
                <Card key={ruling.id} className="p-4 hover:shadow-md transition-shadow">
                  <div className="space-y-3">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">{getRulingTypeIcon(ruling.ruling_type)}</span>
                          <span className="font-mono text-sm font-medium">
                            {ruling.ruling_number}
                          </span>
                          <Badge variant={getStatusColor(ruling.status)} className="text-xs">
                            {ruling.status}
                          </Badge>
                        </div>
                        <h4 className="font-semibold text-sm leading-tight">
                          {ruling.title}
                        </h4>
                      </div>
                      {ruling.url && (
                        <Button variant="ghost" size="sm" asChild>
                          <a href={ruling.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </div>

                    {/* Summary */}
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {ruling.summary}
                    </p>

                    {/* HS Codes */}
                    {ruling.hs_codes.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        <Tag className="h-3 w-3 text-muted-foreground mt-0.5" />
                        {ruling.hs_codes.map((code) => (
                          <Badge key={code} variant="outline" className="text-xs">
                            {code}
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* Footer */}
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          Published: {formatDate(ruling.published_date)}
                        </span>
                        {ruling.effective_date !== ruling.published_date && (
                          <span className="flex items-center gap-1">
                            Effective: {formatDate(ruling.effective_date)}
                          </span>
                        )}
                      </div>
                      <Badge variant={getImpactColor(ruling.impact_level)} className="text-xs">
                        {ruling.impact_level} impact
                      </Badge>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default RecentRulingsPanel;
