import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  FileText, 
  ExternalLink,
  Download,
  Info
} from 'lucide-react';

interface ExportRequirement {
  id: string;
  requirement_type: 'permit' | 'certificate' | 'inspection' | 'documentation' | 'quarantine';
  title: string;
  description: string;
  authority: string;
  mandatory: boolean;
  processing_time: string;
  cost: string;
  validity_period: string;
  application_url?: string;
  documentation_required: string[];
  conditions: string[];
}

interface CountrySpecificInfo {
  country_code: string;
  country_name: string;
  market_access_status: 'open' | 'restricted' | 'prohibited';
  tariff_rate: string;
  quota_applicable: boolean;
  fta_eligible: boolean;
  fta_name?: string;
  special_conditions: string[];
  prohibited_uses: string[];
  import_restrictions: string[];
}

interface ExportRequirementsPanelProps {
  ahecCode: string;
  destinationCountry?: string;
  className?: string;
}

export const ExportRequirementsPanel: React.FC<ExportRequirementsPanelProps> = ({
  ahecCode,
  destinationCountry,
  className = ''
}) => {
  const [requirements, setRequirements] = useState<ExportRequirement[]>([]);
  const [countryInfo, setCountryInfo] = useState<CountrySpecificInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('requirements');

  useEffect(() => {
    if (ahecCode) {
      fetchExportRequirements();
    }
  }, [ahecCode, destinationCountry]);

  const fetchExportRequirements = async () => {
    setLoading(true);
    try {
      // Fetch general export requirements
      const reqResponse = await fetch(`/api/export/requirements/${ahecCode}`);
      if (reqResponse.ok) {
        const reqData = await reqResponse.json();
        setRequirements(reqData);
      }

      // Fetch country-specific information if destination is specified
      if (destinationCountry) {
        const countryResponse = await fetch(`/api/export/requirements/${ahecCode}/${destinationCountry}`);
        if (countryResponse.ok) {
          const countryData = await countryResponse.json();
          setCountryInfo(countryData);
        }
      }
    } catch (error) {
      console.error('Failed to fetch export requirements:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRequirementIcon = (type: string) => {
    switch (type) {
      case 'permit': return <CheckCircle className="h-4 w-4" />;
      case 'certificate': return <FileText className="h-4 w-4" />;
      case 'inspection': return <CheckCircle className="h-4 w-4" />;
      case 'quarantine': return <AlertCircle className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const getRequirementColor = (type: string, mandatory: boolean) => {
    if (mandatory) {
      return type === 'quarantine' ? 'destructive' : 'default';
    }
    return 'secondary';
  };

  const getMarketAccessColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-green-600';
      case 'restricted': return 'text-yellow-600';
      case 'prohibited': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const renderRequirements = () => (
    <div className="space-y-4">
      {requirements.length > 0 ? (
        requirements.map((req) => (
          <Card key={req.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                {getRequirementIcon(req.requirement_type)}
                <h4 className="font-semibold">{req.title}</h4>
                <Badge variant={getRequirementColor(req.requirement_type, req.mandatory)}>
                  {req.mandatory ? 'Mandatory' : 'Optional'}
                </Badge>
              </div>
              {req.application_url && (
                <Button variant="outline" size="sm" asChild>
                  <a href={req.application_url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Apply
                  </a>
                </Button>
              )}
            </div>

            <p className="text-sm text-muted-foreground mb-3">{req.description}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
              <div>
                <span className="text-xs text-muted-foreground">Authority</span>
                <p className="text-sm font-medium">{req.authority}</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Processing Time</span>
                <p className="text-sm font-medium flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {req.processing_time}
                </p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Cost</span>
                <p className="text-sm font-medium">{req.cost}</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Validity</span>
                <p className="text-sm font-medium">{req.validity_period}</p>
              </div>
            </div>

            {req.documentation_required.length > 0 && (
              <div className="mb-3">
                <span className="text-sm font-medium">Required Documentation:</span>
                <ul className="list-disc list-inside text-sm text-muted-foreground mt-1 space-y-1">
                  {req.documentation_required.map((doc, index) => (
                    <li key={index}>{doc}</li>
                  ))}
                </ul>
              </div>
            )}

            {req.conditions.length > 0 && (
              <div>
                <span className="text-sm font-medium">Conditions:</span>
                <ul className="list-disc list-inside text-sm text-muted-foreground mt-1 space-y-1">
                  {req.conditions.map((condition, index) => (
                    <li key={index}>{condition}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        ))
      ) : (
        <div className="text-center py-8">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No specific export requirements found for this AHECC code</p>
        </div>
      )}
    </div>
  );

  const renderCountryInfo = () => {
    if (!countryInfo) {
      return (
        <div className="text-center py-8">
          <Info className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            {destinationCountry 
              ? 'No country-specific information available' 
              : 'Select a destination country to view specific requirements'
            }
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* Market Access Status */}
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            <div className="flex items-center justify-between">
              <span>Market access status for {countryInfo.country_name}:</span>
              <Badge variant="outline" className={getMarketAccessColor(countryInfo.market_access_status)}>
                {countryInfo.market_access_status.toUpperCase()}
              </Badge>
            </div>
          </AlertDescription>
        </Alert>

        {/* Trade Information */}
        <Card className="p-4">
          <h4 className="font-semibold mb-3">Trade Information</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-muted-foreground">Import Tariff Rate</span>
              <p className="font-medium">{countryInfo.tariff_rate}</p>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Quota Applicable</span>
              <p className="font-medium">{countryInfo.quota_applicable ? 'Yes' : 'No'}</p>
            </div>
          </div>

          {countryInfo.fta_eligible && (
            <div className="mt-3 p-3 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">
                  FTA Eligible: {countryInfo.fta_name}
                </span>
              </div>
              <p className="text-sm text-green-700 mt-1">
                This product may qualify for preferential tariff treatment under the free trade agreement.
              </p>
            </div>
          )}
        </Card>

        {/* Special Conditions */}
        {countryInfo.special_conditions.length > 0 && (
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Special Conditions</h4>
            <ul className="space-y-2">
              {countryInfo.special_conditions.map((condition, index) => (
                <li key={index} className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{condition}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Import Restrictions */}
        {countryInfo.import_restrictions.length > 0 && (
          <Card className="p-4">
            <h4 className="font-semibold mb-3 text-red-700">Import Restrictions</h4>
            <ul className="space-y-2">
              {countryInfo.import_restrictions.map((restriction, index) => (
                <li key={index} className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{restriction}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Prohibited Uses */}
        {countryInfo.prohibited_uses.length > 0 && (
          <Card className="p-4">
            <h4 className="font-semibold mb-3 text-red-700">Prohibited Uses</h4>
            <ul className="space-y-2">
              {countryInfo.prohibited_uses.map((use, index) => (
                <li key={index} className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{use}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </div>
    );
  };

  const renderDocumentationChecklist = () => {
    const commonDocs = [
      { name: 'Commercial Invoice', required: true, description: 'Detailed invoice showing value, quantity, and description' },
      { name: 'Packing List', required: true, description: 'Detailed list of contents and packaging' },
      { name: 'Certificate of Origin', required: false, description: 'Required for FTA preferential treatment' },
      { name: 'Export Declaration', required: true, description: 'Australian Customs export declaration' },
      { name: 'Insurance Certificate', required: false, description: 'Proof of cargo insurance coverage' },
      { name: 'Bill of Lading/Airway Bill', required: true, description: 'Transport document and title to goods' }
    ];

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold">Export Documentation Checklist</h4>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Download Checklist
          </Button>
        </div>

        <div className="space-y-3">
          {commonDocs.map((doc, index) => (
            <Card key={index} className="p-3">
              <div className="flex items-start gap-3">
                <CheckCircle className={`h-5 w-5 mt-0.5 ${doc.required ? 'text-red-500' : 'text-green-500'}`} />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{doc.name}</span>
                    <Badge variant={doc.required ? 'destructive' : 'secondary'} className="text-xs">
                      {doc.required ? 'Required' : 'Optional'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{doc.description}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            This is a general checklist. Specific requirements may vary based on the product, destination country, 
            and applicable regulations. Always verify current requirements with relevant authorities.
          </AlertDescription>
        </Alert>
      </div>
    );
  };

  if (loading) {
    return (
      <Card className={`h-full ${className}`}>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading export requirements...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Export Requirements
          {ahecCode && (
            <Badge variant="outline">{ahecCode}</Badge>
          )}
        </CardTitle>
        {destinationCountry && (
          <p className="text-sm text-muted-foreground">
            Destination: {destinationCountry}
          </p>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="requirements">Requirements</TabsTrigger>
            <TabsTrigger value="country">Country Info</TabsTrigger>
            <TabsTrigger value="checklist">Checklist</TabsTrigger>
          </TabsList>

          <TabsContent value="requirements" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderRequirements()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="country" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderCountryInfo()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="checklist" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderDocumentationChecklist()}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default ExportRequirementsPanel;
