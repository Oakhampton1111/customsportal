import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Alert } from '../ui/Alert';
import { aiApi } from '../../services/aiApi';
import { FiEdit3, FiCheck, FiX, FiRefreshCw, FiEye, FiZoomIn } from 'react-icons/fi';

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

interface OCRReviewPanelProps {
  document: DocumentProcessing;
  onProcessingComplete: () => void;
}

interface ProcessingDetails {
  id: number;
  document_id: number;
  document_name: string;
  processing_status: string;
  detected_document_type: string;
  extraction_confidence: string;
  extracted_fields: Record<string, any>;
  ocr_results: Array<{
    page_number: number;
    text_content: string;
    confidence_score: number;
    bounding_boxes: Array<{
      text: string;
      x: number;
      y: number;
      width: number;
      height: number;
    }>;
  }>;
  validation_errors: string[];
  requires_manual_review: boolean;
  created_at: string;
  updated_at: string;
}

export const OCRReviewPanel: React.FC<OCRReviewPanelProps> = ({
  document,
  onProcessingComplete
}) => {
  const [details, setDetails] = useState<ProcessingDetails | null>(null);
  const [editedFields, setEditedFields] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPage, setSelectedPage] = useState(1);
  const [editMode, setEditMode] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadProcessingDetails();
  }, [document.id]);

  const loadProcessingDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const processingDetails = await aiApi.getDocumentProcessing(document.id);
      setDetails(processingDetails);
      setEditedFields(processingDetails.extracted_fields || {});
    } catch (err) {
      setError('Failed to load document processing details');
      console.error('OCR details load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFieldEdit = (fieldName: string, value: any) => {
    setEditedFields(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const toggleEditMode = (fieldName: string) => {
    setEditMode(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const saveChanges = async () => {
    if (!details) return;
    
    try {
      setSaving(true);
      await aiApi.updateExtractedFields(details.id, editedFields);
      await loadProcessingDetails(); // Reload to get updated data
    } catch (err) {
      setError('Failed to save changes');
      console.error('Save error:', err);
    } finally {
      setSaving(false);
    }
  };

  const approveProcessing = async () => {
    if (!details) return;
    
    try {
      setSaving(true);
      await aiApi.approveProcessing(details.id);
      onProcessingComplete();
    } catch (err) {
      setError('Failed to approve processing');
      console.error('Approve error:', err);
    } finally {
      setSaving(false);
    }
  };

  const rejectProcessing = async () => {
    if (!details) return;
    
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;
    
    try {
      setSaving(true);
      await aiApi.rejectProcessing(details.id, reason);
      onProcessingComplete();
    } catch (err) {
      setError('Failed to reject processing');
      console.error('Reject error:', err);
    } finally {
      setSaving(false);
    }
  };

  const reprocessDocument = async () => {
    if (!details) return;
    
    try {
      setSaving(true);
      await aiApi.reprocessDocument(details.id);
      await loadProcessingDetails();
    } catch (err) {
      setError('Failed to reprocess document');
      console.error('Reprocess error:', err);
    } finally {
      setSaving(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const renderFieldEditor = (fieldName: string, value: any) => {
    const isEditing = editMode[fieldName];
    
    return (
      <div key={fieldName} className="border rounded-lg p-3">
        <div className="flex items-center justify-between mb-2">
          <label className="font-medium text-gray-700 capitalize">
            {fieldName.replace(/_/g, ' ')}
          </label>
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
            value={editedFields[fieldName] || ''}
            onChange={(e) => handleFieldEdit(fieldName, e.target.value)}
            className="w-full"
            placeholder={`Enter ${fieldName.replace(/_/g, ' ')}`}
          />
        ) : (
          <div className="p-2 bg-gray-50 rounded border min-h-[40px] flex items-center">
            {editedFields[fieldName] || value || <span className="text-gray-400">No value</span>}
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

  if (error) {
    return (
      <Alert type="error">
        {error}
      </Alert>
    );
  }

  if (!details) {
    return (
      <Alert type="warning">
        No processing details available for this document.
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">OCR Review & Field Extraction</h2>
          <p className="text-gray-600 mt-1">{details.document_name}</p>
          <div className="flex items-center space-x-3 mt-2">
            <Badge className="bg-blue-100 text-blue-800">
              {details.detected_document_type}
            </Badge>
            <Badge className={
              details.extraction_confidence === 'high' ? 'bg-green-100 text-green-800' :
              details.extraction_confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }>
              {details.extraction_confidence} confidence
            </Badge>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Button onClick={reprocessDocument} variant="outline" disabled={saving}>
            <FiRefreshCw className="h-4 w-4 mr-2" />
            Reprocess
          </Button>
          <Button onClick={saveChanges} disabled={saving}>
            {saving ? <LoadingSpinner size="sm" /> : <FiCheck className="h-4 w-4" />}
            <span className="ml-2">Save Changes</span>
          </Button>
        </div>
      </div>

      {/* Validation Errors */}
      {details.validation_errors.length > 0 && (
        <Alert type="warning" title="Validation Issues">
          <ul className="list-disc list-inside space-y-1">
            {details.validation_errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Extracted Fields */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Extracted Fields</h3>
          <div className="space-y-3">
            {Object.entries(details.extracted_fields || {}).map(([fieldName, value]) =>
              renderFieldEditor(fieldName, value)
            )}
            
            {Object.keys(details.extracted_fields || {}).length === 0 && (
              <Card className="p-4 text-center text-gray-500">
                No fields extracted from this document
              </Card>
            )}
          </div>
        </div>

        {/* OCR Results */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">OCR Text Results</h3>
            {details.ocr_results.length > 1 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Page:</span>
                <select
                  value={selectedPage}
                  onChange={(e) => setSelectedPage(Number(e.target.value))}
                  className="border rounded px-2 py-1 text-sm"
                >
                  {details.ocr_results.map((result) => (
                    <option key={result.page_number} value={result.page_number}>
                      {result.page_number}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {details.ocr_results.length > 0 ? (
            <div className="space-y-4">
              {details.ocr_results
                .filter(result => result.page_number === selectedPage)
                .map((result) => (
                  <Card key={result.page_number} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Page {result.page_number}</h4>
                      <Badge className={getConfidenceColor(result.confidence_score)}>
                        {(result.confidence_score * 100).toFixed(1)}% confidence
                      </Badge>
                    </div>
                    <div className="bg-gray-50 p-3 rounded border max-h-64 overflow-y-auto">
                      <pre className="text-sm whitespace-pre-wrap font-mono">
                        {result.text_content}
                      </pre>
                    </div>
                    
                    {result.bounding_boxes.length > 0 && (
                      <div className="mt-3">
                        <details>
                          <summary className="text-sm text-gray-600 cursor-pointer">
                            View {result.bounding_boxes.length} detected text regions
                          </summary>
                          <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                            {result.bounding_boxes.map((box, index) => (
                              <div key={index} className="text-xs bg-white p-2 rounded border">
                                <span className="font-mono">{box.text}</span>
                                <span className="text-gray-500 ml-2">
                                  ({box.x}, {box.y}, {box.width}×{box.height})
                                </span>
                              </div>
                            ))}
                          </div>
                        </details>
                      </div>
                    )}
                  </Card>
                ))}
            </div>
          ) : (
            <Card className="p-4 text-center text-gray-500">
              No OCR results available
            </Card>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <Button onClick={rejectProcessing} variant="outline" disabled={saving}>
          <FiX className="h-4 w-4 mr-2" />
          Reject
        </Button>
        <Button onClick={approveProcessing} disabled={saving}>
          <FiCheck className="h-4 w-4 mr-2" />
          Approve & Continue
        </Button>
      </div>
    </div>
  );
};