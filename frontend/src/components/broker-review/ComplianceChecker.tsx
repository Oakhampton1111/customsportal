import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Alert } from '../ui/Alert';
import { aiApi } from '../../services/aiApi';
import { 
  FiShield, 
  FiCheck, 
  FiAlertTriangle, 
  FiX, 
  FiFileText, 
  FiClock, 
  FiExternalLink,
  FiRefreshCw 
} from 'react-icons/fi';

interface DocumentProcessing {
  id: number;
  document_id: number;
  document_name: string;
  processing_status: string;
  detected_document_type: string;
  extraction_confidence: string;
  requires_manual_review: boolean;
  created_at: string;
}

interface ComplianceCheckerProps {
  document: DocumentProcessing;
}

interface ComplianceResult {
  overall_status: 'compliant' | 'non_compliant' | 'requires_review';
  checks: Array<{
    category: string;
    requirement: string;
    status: 'pass' | 'fail' | 'warning';
    message: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    required_action?: string;
    supporting_documents?: string[];
  }>;
  required_permits: Array<{
    permit_type: string;
    issuing_authority: string;
    estimated_processing_time: string;
    application_url?: string;
  }>;
  recommendations: string[];
}

export const ComplianceChecker: React.FC<ComplianceCheckerProps> = ({
  document
}) => {
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);
  const [entryData, setEntryData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEntryData();
  }, [document.id]);

  const loadEntryData = async () => {
    try {
      setLoading(true);
      setError(null);
      // Load the generated entry data from the previous step
      const processingDetails = await aiApi.getDocumentProcessing(document.id);
      setEntryData(processingDetails.extracted_fields || {});
    } catch (err) {
      setError('Failed to load entry data');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const runComplianceCheck = async () => {
    try {
      setChecking(true);
      setError(null);
      const result = await aiApi.checkCompliance(entryData);
      setComplianceResult(result);
    } catch (err) {
      setError('Failed to run compliance check');
      console.error('Compliance check error:', err);
    } finally {
      setChecking(false);
    }
  };

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'bg-green-100 text-green-800 border-green-200';
      case 'non_compliant': return 'bg-red-100 text-red-800 border-red-200';
      case 'requires_review': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <FiCheck className="h-4 w-4 text-green-500" />;
      case 'fail': return <FiX className="h-4 w-4 text-red-500" />;
      case 'warning': return <FiAlertTriangle className="h-4 w-4 text-yellow-500" />;
      default: return <FiAlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pass': return 'bg-green-100 text-green-800';
      case 'fail': return 'bg-red-100 text-red-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityBadgeColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-blue-100 text-blue-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getOverallStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant': return <FiCheck className="h-6 w-6 text-green-500" />;
      case 'non_compliant': return <FiX className="h-6 w-6 text-red-500" />;
      case 'requires_review': return <FiAlertTriangle className="h-6 w-6 text-yellow-500" />;
      default: return <FiShield className="h-6 w-6 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Compliance Analysis</h2>
          <p className="text-gray-600 mt-1">Automated compliance checking and permit requirements</p>
        </div>
        
        <div className="flex space-x-2">
          <Button onClick={runComplianceCheck} disabled={checking} className="flex items-center space-x-2">
            {checking ? <LoadingSpinner size="sm" /> : <FiRefreshCw className="h-4 w-4" />}
            <span>{complianceResult ? 'Re-check' : 'Run Compliance Check'}</span>
          </Button>
        </div>
      </div>

      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}

      {/* Overall Status */}
      {complianceResult && (
        <Card className={`p-6 border-2 ${getOverallStatusColor(complianceResult.overall_status)}`}>
          <div className="flex items-center space-x-4">
            {getOverallStatusIcon(complianceResult.overall_status)}
            <div>
              <h3 className="text-lg font-semibold">
                Overall Compliance Status: {complianceResult.overall_status.replace('_', ' ').toUpperCase()}
              </h3>
              <p className="text-sm mt-1">
                {complianceResult.overall_status === 'compliant' && 
                  'All compliance requirements have been met. Entry is ready for submission.'}
                {complianceResult.overall_status === 'non_compliant' && 
                  'Critical compliance issues detected. Entry cannot be submitted until resolved.'}
                {complianceResult.overall_status === 'requires_review' && 
                  'Some requirements need manual review before submission.'}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Compliance Checks */}
      {complianceResult && (
        <Card className="p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Compliance Checks</h3>
          
          <div className="space-y-4">
            {complianceResult.checks.map((check, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    {getStatusIcon(check.status)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium text-gray-900">{check.requirement}</h4>
                      <Badge className={getStatusBadgeColor(check.status)}>
                        {check.status}
                      </Badge>
                      <Badge className={getSeverityBadgeColor(check.severity)}>
                        {check.severity}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{check.message}</p>
                    
                    <div className="text-xs text-gray-500 mb-2">
                      Category: {check.category}
                    </div>
                    
                    {check.required_action && (
                      <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200">
                        <span className="text-xs font-medium text-blue-800">Required Action:</span>
                        <p className="text-xs text-blue-700 mt-1">{check.required_action}</p>
                      </div>
                    )}
                    
                    {check.supporting_documents && check.supporting_documents.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs font-medium text-gray-700">Supporting documents required:</span>
                        <ul className="text-xs text-gray-600 mt-1 space-y-1">
                          {check.supporting_documents.map((doc, docIndex) => (
                            <li key={docIndex} className="flex items-center space-x-1">
                              <FiFileText className="h-3 w-3" />
                              <span>{doc}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Required Permits */}
      {complianceResult && complianceResult.required_permits.length > 0 && (
        <Card className="p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Required Permits & Licenses</h3>
          
          <div className="space-y-4">
            {complianceResult.required_permits.map((permit, index) => (
              <div key={index} className="border rounded-lg p-4 bg-yellow-50 border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">{permit.permit_type}</h4>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">Issuing Authority:</span>
                        <span>{permit.issuing_authority}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <FiClock className="h-4 w-4" />
                        <span className="font-medium">Processing Time:</span>
                        <span>{permit.estimated_processing_time}</span>
                      </div>
                    </div>
                  </div>
                  
                  {permit.application_url && (
                    <Button
                      onClick={() => window.open(permit.application_url, '_blank')}
                      variant="outline"
                      size="sm"
                      className="flex items-center space-x-1"
                    >
                      <FiExternalLink className="h-3 w-3" />
                      <span>Apply</span>
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recommendations */}
      {complianceResult && complianceResult.recommendations.length > 0 && (
        <Card className="p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h3>
          
          <div className="space-y-2">
            {complianceResult.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded border border-blue-200">
                <FiShield className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-blue-800">{recommendation}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Summary Statistics */}
      {complianceResult && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {complianceResult.checks.filter(c => c.status === 'pass').length}
            </div>
            <div className="text-sm text-gray-600">Passed</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {complianceResult.checks.filter(c => c.status === 'warning').length}
            </div>
            <div className="text-sm text-gray-600">Warnings</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">
              {complianceResult.checks.filter(c => c.status === 'fail').length}
            </div>
            <div className="text-sm text-gray-600">Failed</div>
          </Card>
          
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {complianceResult.required_permits.length}
            </div>
            <div className="text-sm text-gray-600">Permits Required</div>
          </Card>
        </div>
      )}

      {/* No Results State */}
      {!complianceResult && !checking && (
        <Card className="p-8 text-center">
          <FiShield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready for Compliance Check</h3>
          <p className="text-gray-600 mb-4">
            Run automated compliance analysis to identify requirements and potential issues.
          </p>
          {Object.keys(entryData).length === 0 && (
            <Alert type="warning">
              No entry data available. Please complete entry compilation first.
            </Alert>
          )}
        </Card>
      )}
    </div>
  );
};