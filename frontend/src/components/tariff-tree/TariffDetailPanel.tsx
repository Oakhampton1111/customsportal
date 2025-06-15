import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  BookOpen, 
  Calculator, 
  Globe, 
  FileText, 
  AlertTriangle, 
  TrendingUp,
  Star,
  Bookmark,
  Share2,
  Printer,
  ExternalLink
} from 'lucide-react';

interface TariffCode {
  hs_code: string;
  description: string;
  unit_of_quantity: string;
  general_duty_rate: string;
  statistical_code: string;
  working_tariff_number: string;
  chapter: number;
  heading: number;
  subheading: number;
  item: number;
  section: {
    id: number;
    title: string;
    description: string;
  };
  chapter_info: {
    title: string;
    description: string;
    notes: string[];
  };
  heading_info: {
    title: string;
    description: string;
    notes: string[];
  };
}

interface FTARate {
  country: string;
  agreement: string;
  preferential_rate: string;
  origin_criteria: string;
  effective_date: string;
  staging_category: string;
}

interface TCOExemption {
  tco_number: string;
  description: string;
  effective_date: string;
  expiry_date: string;
  conditions: string[];
  applicant: string;
}

interface TariffDetailPanelProps {
  hsCode: string;
  className?: string;
  onCalculate?: (hsCode: string) => void;
  onCompare?: (hsCode: string) => void;
}

export const TariffDetailPanel: React.FC<TariffDetailPanelProps> = ({
  hsCode,
  className = '',
  onCalculate,
  onCompare
}) => {
  const [tariffData, setTariffData] = useState<TariffCode | null>(null);
  const [ftaRates, setFtaRates] = useState<FTARate[]>([]);
  const [tcoExemptions, setTcoExemptions] = useState<TCOExemption[]>([]);
  const [loading, setLoading] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    if (hsCode) {
      fetchTariffDetails();
    }
  }, [hsCode]);

  const fetchTariffDetails = async () => {
    setLoading(true);
    try {
      // Fetch main tariff data
      const tariffResponse = await fetch(`/api/tariff/code/${hsCode}/details`);
      if (tariffResponse.ok) {
        const tariffData = await tariffResponse.json();
        setTariffData(tariffData);
      }

      // Fetch FTA rates
      const ftaResponse = await fetch(`/api/tariff/fta-rates/${hsCode}`);
      if (ftaResponse.ok) {
        const ftaData = await ftaResponse.json();
        setFtaRates(ftaData);
      }

      // Fetch TCO exemptions
      const tcoResponse = await fetch(`/api/tariff/tco-exemptions/${hsCode}`);
      if (tcoResponse.ok) {
        const tcoData = await tcoResponse.json();
        setTcoExemptions(tcoData);
      }

      // Check if bookmarked
      const bookmarked = localStorage.getItem(`bookmark_${hsCode}`);
      setIsBookmarked(!!bookmarked);

    } catch (error) {
      console.error('Failed to fetch tariff details:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleBookmark = () => {
    if (isBookmarked) {
      localStorage.removeItem(`bookmark_${hsCode}`);
      setIsBookmarked(false);
    } else {
      localStorage.setItem(`bookmark_${hsCode}`, JSON.stringify({
        hsCode,
        description: tariffData?.description,
        bookmarkedAt: new Date().toISOString()
      }));
      setIsBookmarked(true);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `HS Code ${hsCode}`,
          text: tariffData?.description,
          url: window.location.href
        });
      } catch (error) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback to clipboard
      const shareUrl = `${window.location.origin}/tariff-tree?code=${hsCode}`;
      await navigator.clipboard.writeText(shareUrl);
      // Could show a toast notification here
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <Card className={`h-full ${className}`}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading tariff details...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!tariffData) {
    return (
      <Card className={`h-full ${className}`}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Select a tariff code to view details</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">HS Code {tariffData.hs_code}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {tariffData.description}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleBookmark}
              className={isBookmarked ? 'text-yellow-500' : ''}
            >
              {isBookmarked ? <Star className="h-4 w-4 fill-current" /> : <Bookmark className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleShare}>
              <Share2 className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handlePrint}>
              <Printer className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex gap-2 mt-3">
          <Button
            onClick={() => onCalculate?.(hsCode)}
            className="flex-1"
          >
            <Calculator className="h-4 w-4 mr-2" />
            Calculate Duties
          </Button>
          <Button
            variant="outline"
            onClick={() => onCompare?.(hsCode)}
            className="flex-1"
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            Compare Codes
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <Tabs defaultValue="overview" className="h-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="fta">FTA Rates</TabsTrigger>
            <TabsTrigger value="tco">TCO</TabsTrigger>
            <TabsTrigger value="notes">Notes</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4">
            <ScrollArea className="h-[500px]">
              <div className="space-y-4">
                {/* Basic Information */}
                <div>
                  <h4 className="font-semibold mb-2">Basic Information</h4>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">General Duty Rate:</span>
                      <Badge variant="outline" className="ml-2">
                        {tariffData.general_duty_rate}
                      </Badge>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Unit of Quantity:</span>
                      <span className="ml-2 font-medium">{tariffData.unit_of_quantity}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Statistical Code:</span>
                      <span className="ml-2 font-medium">{tariffData.statistical_code}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Working Tariff Number:</span>
                      <span className="ml-2 font-medium">{tariffData.working_tariff_number}</span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Hierarchy */}
                <div>
                  <h4 className="font-semibold mb-2">Classification Hierarchy</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">Section {tariffData.section.id}</Badge>
                      <span>{tariffData.section.title}</span>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Badge variant="secondary">Chapter {tariffData.chapter}</Badge>
                      <span>{tariffData.chapter_info.title}</span>
                    </div>
                    <div className="flex items-center gap-2 ml-8">
                      <Badge variant="secondary">Heading {tariffData.heading}</Badge>
                      <span>{tariffData.heading_info.title}</span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Section Description */}
                <div>
                  <h4 className="font-semibold mb-2">Section Description</h4>
                  <p className="text-sm text-muted-foreground">
                    {tariffData.section.description}
                  </p>
                </div>

                {/* Chapter Description */}
                <div>
                  <h4 className="font-semibold mb-2">Chapter Description</h4>
                  <p className="text-sm text-muted-foreground">
                    {tariffData.chapter_info.description}
                  </p>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="fta" className="mt-4">
            <ScrollArea className="h-[500px]">
              <div className="space-y-3">
                {ftaRates.length > 0 ? (
                  ftaRates.map((fta, index) => (
                    <Card key={index} className="p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Globe className="h-4 w-4" />
                          <span className="font-medium">{fta.country}</span>
                        </div>
                        <Badge variant="outline">{fta.agreement}</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Preferential Rate:</span>
                          <Badge variant="secondary" className="ml-2">
                            {fta.preferential_rate}
                          </Badge>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Staging:</span>
                          <span className="ml-2">{fta.staging_category}</span>
                        </div>
                      </div>
                      <div className="mt-2 text-sm">
                        <span className="text-muted-foreground">Origin Criteria:</span>
                        <p className="mt-1">{fta.origin_criteria}</p>
                      </div>
                    </Card>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No FTA rates available for this code</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="tco" className="mt-4">
            <ScrollArea className="h-[500px]">
              <div className="space-y-3">
                {tcoExemptions.length > 0 ? (
                  tcoExemptions.map((tco, index) => (
                    <Card key={index} className="p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          <span className="font-medium">TCO {tco.tco_number}</span>
                        </div>
                        <Badge variant="outline">
                          Valid until {new Date(tco.expiry_date).toLocaleDateString()}
                        </Badge>
                      </div>
                      <p className="text-sm mb-2">{tco.description}</p>
                      <div className="text-sm">
                        <span className="text-muted-foreground">Applicant:</span>
                        <span className="ml-2">{tco.applicant}</span>
                      </div>
                      {tco.conditions.length > 0 && (
                        <div className="mt-2">
                          <span className="text-sm text-muted-foreground">Conditions:</span>
                          <ul className="list-disc list-inside text-sm mt-1 space-y-1">
                            {tco.conditions.map((condition, idx) => (
                              <li key={idx}>{condition}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </Card>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No TCO exemptions available for this code</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="notes" className="mt-4">
            <ScrollArea className="h-[500px]">
              <div className="space-y-4">
                {/* Chapter Notes */}
                {tariffData.chapter_info.notes.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Chapter {tariffData.chapter} Notes
                    </h4>
                    <div className="space-y-2">
                      {tariffData.chapter_info.notes.map((note, index) => (
                        <Card key={index} className="p-3">
                          <p className="text-sm">{note}</p>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Heading Notes */}
                {tariffData.heading_info.notes.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Heading {tariffData.heading} Notes
                    </h4>
                    <div className="space-y-2">
                      {tariffData.heading_info.notes.map((note, index) => (
                        <Card key={index} className="p-3">
                          <p className="text-sm">{note}</p>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {tariffData.chapter_info.notes.length === 0 && tariffData.heading_info.notes.length === 0 && (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No additional notes available for this classification</p>
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

export default TariffDetailPanel;
