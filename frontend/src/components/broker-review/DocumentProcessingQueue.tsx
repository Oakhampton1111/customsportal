import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { FiEye, FiRefreshCw, FiClock, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';

interface DocumentProcessing {
  id: number;
  document_id: number;
  document_name: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  detected_document_type: string;
  extraction_confidence: 'high' | 'medium' | 'low';
  requires_manual_review: boolean;
  created_at: string;
  processing_duration_seconds?: number;
}

interface DocumentProcessingQueueProps {
  documents: DocumentProcessing[];
  onDocumentSelect: (document: DocumentProcessing) => void;
  onRefresh: () => void;
}

export const DocumentProcessingQueue: React.FC<DocumentProcessingQueueProps> = ({
  documents,
  onDocumentSelect,
  onRefresh
}) => {
  const [loading, setLoading] = useState(false);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <FiClock className="h-4 w-4 text-yellow-500" />;
      case 'processing': return <LoadingSpinner size="sm" />;
      case 'completed': return <FiCheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed': return <FiAlertTriangle className="h-4 w-4 text-red-500" />;
      default: return <FiClock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceBadgeColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await onRefresh();
    } finally {
      setLoading(false);
    }
  };

  const priorityDocuments = documents.filter(doc => doc.requires_manual_review);
  const regularDocuments = documents.filter(doc => !doc.requires_manual_review);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Document Processing Queue</h2>
          <p className="text-sm text-gray-600 mt-1">
            {documents.length} documents • {priorityDocuments.length} require manual review
          </p>
        </div>
        <Button 
          onClick={handleRefresh} 
          variant="outline" 
          disabled={loading}
          className="flex items-center space-x-2"
        >
          <FiRefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Priority Documents */}
      {priorityDocuments.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-red-700 mb-3 flex items-center">
            <FiAlertTriangle className="h-5 w-5 mr-2" />
            Priority Review Required ({priorityDocuments.length})
          </h3>
          <div className="grid gap-4">
            {priorityDocuments.map((document) => (
              <Card key={document.id} className="p-4 border-red-200 bg-red-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(document.processing_status)}
                      <h4 className="font-medium text-gray-900">{document.document_name}</h4>
                      <Badge className={getStatusBadgeColor(document.processing_status)}>
                        {document.processing_status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>Type: {document.detected_document_type}</span>
                      <Badge className={getConfidenceBadgeColor(document.extraction_confidence)}>
                        {document.extraction_confidence} confidence
                      </Badge>
                      <span>Created: {formatDate(document.created_at)}</span>
                      {document.processing_duration_seconds && (
                        <span>Duration: {formatDuration(document.processing_duration_seconds)}</span>
                      )}
                    </div>
                  </div>
                  <Button
                    onClick={() => onDocumentSelect(document)}
                    className="flex items-center space-x-2"
                  >
                    <FiEye className="h-4 w-4" />
                    <span>Review</span>
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Regular Documents */}
      {regularDocuments.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-3">
            Standard Processing ({regularDocuments.length})
          </h3>
          <div className="grid gap-3">
            {regularDocuments.map((document) => (
              <Card key={document.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(document.processing_status)}
                      <h4 className="font-medium text-gray-900">{document.document_name}</h4>
                      <Badge className={getStatusBadgeColor(document.processing_status)}>
                        {document.processing_status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>Type: {document.detected_document_type}</span>
                      <Badge className={getConfidenceBadgeColor(document.extraction_confidence)}>
                        {document.extraction_confidence} confidence
                      </Badge>
                      <span>Created: {formatDate(document.created_at)}</span>
                      {document.processing_duration_seconds && (
                        <span>Duration: {formatDuration(document.processing_duration_seconds)}</span>
                      )}
                    </div>
                  </div>
                  <Button
                    onClick={() => onDocumentSelect(document)}
                    variant="outline"
                    size="sm"
                    className="flex items-center space-x-2"
                  >
                    <FiEye className="h-4 w-4" />
                    <span>View</span>
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {documents.length === 0 && (
        <Card className="p-8 text-center">
          <FiCheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">All Caught Up!</h3>
          <p className="text-gray-600">No documents are currently pending review.</p>
        </Card>
      )}
    </div>
  );
};