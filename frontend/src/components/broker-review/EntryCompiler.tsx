import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Alert } from '../ui/Alert';
import { aiApi } from '../../services/aiApi';
import { FiFileText, FiDollarSign, FiCheck, FiAlertTriangle, FiEdit3, FiSave } from 'react-icons/fi';

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

interface EntryCompilerProps {
  document: DocumentProcessing;
  onEntryGenerated: () => void;
}

interface CustomsEntry {
  entry_id: string;
  declaration_data: Record<string, any>;
  calculated_duties: Array<{
    item_number: string;
    hs_code: string;
    description: string;
    quantity: number;
    unit_value: number;
    total_value: number;
    duty_rate: number;
    duty_amount: number;
    gst_amount: number;
    total_charges: number;
  }>;
  compliance_checks: Array<{
    check_type: string;
    status: 'pass' | 'fail' | 'warning';
    message: string;
    required_documents?: string[];
  }>;
  estimated_clearance_time: string;
}

export const EntryCompiler: React.FC<EntryCompilerProps> = ({
  document,
  onEntryGenerated
}) => {
  const [entry, setEntry] = useState<CustomsEntry | null>(null);
  const [extractedData, setExtractedData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState<Record<string, boolean>>({});
  const [editedEntry, setEditedEntry] = useState<Record<string, any>>({});

  useEffect(() => {
    loadExtractedData();
  }, [document.id]);

  const loadExtractedData = async () => {
    try {
      setLoading(true);
      setError(null);
      const processingDetails = await aiApi.getDocumentProcessing(document.id);
      setExtractedData(processingDetails.extracted_fields || {});
    } catch (err) {
      setError('Failed to load extracted data');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateEntry = async () => {
    try {
      setGenerating(true);
      setError(null);
      const generatedEntry = await aiApi.generateCustomsEntry(document.document_id, extractedData);
      setEntry(generatedEntry);
      setEditedEntry(generatedEntry.declaration_data);
    } catch (err) {
      setError('Failed to generate customs entry');
      console.error('Generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const validateHSCode = async (code: string, description: string) => {
    try {
      const validation = await aiApi.validateHSCode(code, description);
      return validation;
    } catch (err) {
      console.error('HS Code validation error:', err);
      return null;
    }
  };

  const toggleEditMode = (fieldName: string) => {
    setEditMode(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const handleFieldEdit = (fieldName: string, value: any) => {
    setEditedEntry(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const saveEntryChanges = () => {
    if (entry) {
      setEntry({
        ...entry,
        declaration_data: editedEntry
      });
    }
    setEditMode({});
  };

  const getComplianceStatusColor = (status: string) => {
    switch (status) {
      case 'pass': return 'bg-green-100 text-green-800';
      case 'fail': return 'bg-red-100 text-red-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD'
    }).format(amount);
  };

  const renderEditableField = (fieldName: string, value: any, label: string) => {
    const isEditing = editMode[fieldName];
    
    return (
      <div className="border rounded-lg p-3">
        <div className="flex items-center justify-between mb-2">
          <label className="font-medium text-gray-700">{label}</label>
          <Button
            onClick={() => toggleEditMode(fieldName)}
            variant="outline"
            size="sm"
            className="flex items-center space-x-1"
          >
            <FiEdit3 className="h-3 w-3" />
            <span>{isEditing ? 'Cancel' : 'Edit'}</span>
          </Button>
        </div>
        
        {isEditing ? (
          <Input
            value={editedEntry[fieldName] || ''}
            onChange={(e) => handleFieldEdit(fieldName, e.target.value)}
            className="w-full"
            placeholder={`Enter ${label.toLowerCase()}`}
          />
        ) : (
          <div className="p-2 bg-gray-50 rounded border min-h-[40px] flex items-center">
            {editedEntry[fieldName] || value || <span className="text-gray-400">No value</span>}
          </div>
        )}
      </div>
    );
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
          <h2 className="text-xl font-semibold text-gray-900">Customs Entry Compiler</h2>
          <p className="text-gray-600 mt-1">Generate and review customs declaration from extracted data</p>
        </div>
        
        <div className="flex space-x-2">
          {entry && Object.keys(editMode).some(key => editMode[key]) && (
            <Button onClick={saveEntryChanges} className="flex items-center space-x-2">
              <FiSave className="h-4 w-4" />
              <span>Save Changes</span>
            </Button>
          )}
          <Button 
            onClick={generateEntry} 
            disabled={generating || Object.keys(extractedData).length === 0}
            className="flex items-center space-x-2"
          >
            {generating ? <LoadingSpinner size="sm" /> : <FiFileText className="h-4 w-4" />}
            <span>{entry ? 'Regenerate Entry' : 'Generate Entry'}</span>
          </Button>
        </div>
      </div>

      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}

      {/* Extracted Data Summary */}
      <Card className="p-4">
        <h3 className="font-medium text-gray-900 mb-3">Source Data</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(extractedData).map(([key, value]) => (
            <div key={key} className="text-sm">
              <span className="font-medium text-gray-600 capitalize">
                {key.replace(/_/g, ' ')}:
              </span>
              <span className="ml-2 text-gray-900">{String(value)}</span>
            </div>
          ))}
        </div>
        {Object.keys(extractedData).length === 0 && (
          <p className="text-gray-500 text-center py-4">No extracted data available</p>
        )}
      </Card>

      {/* Generated Entry */}
      {entry && (
        <div className="space-y-6">
          {/* Entry Summary */}
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Entry Summary</h3>
              <Badge className="bg-blue-100 text-blue-800">
                Entry ID: {entry.entry_id}
              </Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-3">Declaration Data</h4>
                <div className="space-y-3">
                  {Object.entries(entry.declaration_data).map(([key, value]) =>
                    renderEditableField(key, value, key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()))
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-3">Processing Info</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">Estimated Clearance:</span>
                    <span className="ml-2">{entry.estimated_clearance_time}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Total Items:</span>
                    <span className="ml-2">{entry.calculated_duties.length}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">Total Value:</span>
                    <span className="ml-2 font-semibold">
                      {formatCurrency(entry.calculated_duties.reduce((sum, item) => sum + item.total_value, 0))}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Duty Calculations */}
          <Card className="p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <FiDollarSign className="h-5 w-5 mr-2" />
              Duty Calculations
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Item</th>
                    <th className="text-left p-2">HS Code</th>
                    <th className="text-left p-2">Description</th>
                    <th className="text-right p-2">Qty</th>
                    <th className="text-right p-2">Unit Value</th>
                    <th className="text-right p-2">Total Value</th>
                    <th className="text-right p-2">Duty</th>
                    <th className="text-right p-2">GST</th>
                    <th className="text-right p-2">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {entry.calculated_duties.map((item, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-2">{item.item_number}</td>
                      <td className="p-2 font-mono">{item.hs_code}</td>
                      <td className="p-2 max-w-xs truncate" title={item.description}>
                        {item.description}
                      </td>
                      <td className="p-2 text-right">{item.quantity}</td>
                      <td className="p-2 text-right">{formatCurrency(item.unit_value)}</td>
                      <td className="p-2 text-right">{formatCurrency(item.total_value)}</td>
                      <td className="p-2 text-right">
                        {formatCurrency(item.duty_amount)}
                        <div className="text-xs text-gray-500">({(item.duty_rate * 100).toFixed(1)}%)</div>
                      </td>
                      <td className="p-2 text-right">{formatCurrency(item.gst_amount)}</td>
                      <td className="p-2 text-right font-semibold">{formatCurrency(item.total_charges)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 font-semibold">
                    <td colSpan={5} className="p-2 text-right">Totals:</td>
                    <td className="p-2 text-right">
                      {formatCurrency(entry.calculated_duties.reduce((sum, item) => sum + item.total_value, 0))}
                    </td>
                    <td className="p-2 text-right">
                      {formatCurrency(entry.calculated_duties.reduce((sum, item) => sum + item.duty_amount, 0))}
                    </td>
                    <td className="p-2 text-right">
                      {formatCurrency(entry.calculated_duties.reduce((sum, item) => sum + item.gst_amount, 0))}
                    </td>
                    <td className="p-2 text-right">
                      {formatCurrency(entry.calculated_duties.reduce((sum, item) => sum + item.total_charges, 0))}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </Card>

          {/* Compliance Checks */}
          <Card className="p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Compliance Checks</h3>
            
            <div className="space-y-3">
              {entry.compliance_checks.map((check, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                  <div className="flex-shrink-0 mt-1">
                    {check.status === 'pass' && <FiCheck className="h-4 w-4 text-green-500" />}
                    {check.status === 'fail' && <FiAlertTriangle className="h-4 w-4 text-red-500" />}
                    {check.status === 'warning' && <FiAlertTriangle className="h-4 w-4 text-yellow-500" />}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-900">{check.check_type}</span>
                      <Badge className={getComplianceStatusColor(check.status)}>
                        {check.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{check.message}</p>
                    
                    {check.required_documents && check.required_documents.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs font-medium text-gray-700">Required documents:</span>
                        <ul className="text-xs text-gray-600 mt-1">
                          {check.required_documents.map((doc, docIndex) => (
                            <li key={docIndex} className="ml-2">• {doc}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button onClick={onEntryGenerated} className="flex items-center space-x-2">
              <FiCheck className="h-4 w-4" />
              <span>Proceed to Compliance Review</span>
            </Button>
          </div>
        </div>
      )}

      {/* No Entry State */}
      {!entry && !generating && (
        <Card className="p-8 text-center">
          <FiFileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Generate Entry</h3>
          <p className="text-gray-600 mb-4">
            Click "Generate Entry" to create a customs declaration from the extracted document data.
          </p>
          {Object.keys(extractedData).length === 0 && (
            <Alert type="warning">
              No extracted data available. Please complete OCR review first.
            </Alert>
          )}
        </Card>
      )}
    </div>
  );
};