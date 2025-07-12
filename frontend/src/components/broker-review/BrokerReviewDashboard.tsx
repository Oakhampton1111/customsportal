import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Alert } from '../ui/Alert';
import { Badge } from '../ui/badge';
import { DocumentProcessingQueue } from './DocumentProcessingQueue';
import { EntryCompiler } from './EntryCompiler';
import { OCRReviewPanel } from './OCRReviewPanel';
import { ComplianceChecker } from './ComplianceChecker';
import { DutyCalculationPanel } from './DutyCalculationPanel';
import { aiApi } from '../../services/aiApi';

interface ProcessingStats {
  total_documents: number;
  pending_review: number;
  completed_today: number;
  accuracy_rate: number;
  avg_processing_time: number;
}

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

export const BrokerReviewDashboard: React.FC = () => {
  const [stats, setStats] = useState<ProcessingStats | null>(null);
  const [pendingDocuments, setPendingDocuments] = useState<DocumentProcessing[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentProcessing | null>(null);
  const [activeTab, setActiveTab] = useState<'queue' | 'review' | 'compile' | 'compliance'>('queue');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load processing statistics
      const stats = await aiApi.getProcessingStats();
      setStats(stats);
      
      // Load pending documents requiring review
      const pendingDocuments = await aiApi.getPendingDocuments();
      setPendingDocuments(pendingDocuments);
      
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentSelect = (document: DocumentProcessing) => {
    setSelectedDocument(document);
    setActiveTab('review');
  };

  const handleDocumentProcessed = () => {
    loadDashboardData();
    if (selectedDocument) {
      setActiveTab('compile');
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Broker Review Dashboard</h1>
          <p className="text-gray-600 mt-1">AI-powered document processing and customs entry compilation</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          Refresh
        </Button>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card className="p-4">
            <div className="text-2xl font-bold text-blue-600">{stats.total_documents}</div>
            <div className="text-sm text-gray-600">Total Documents</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-orange-600">{stats.pending_review}</div>
            <div className="text-sm text-gray-600">Pending Review</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-green-600">{stats.completed_today}</div>
            <div className="text-sm text-gray-600">Completed Today</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-purple-600">{(stats.accuracy_rate * 100).toFixed(1)}%</div>
            <div className="text-sm text-gray-600">Accuracy Rate</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-indigo-600">{stats.avg_processing_time.toFixed(1)}s</div>
            <div className="text-sm text-gray-600">Avg Processing</div>
          </Card>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'queue', label: 'Processing Queue', count: pendingDocuments.length },
            { id: 'review', label: 'OCR Review', disabled: !selectedDocument },
            { id: 'compile', label: 'Entry Compiler', disabled: !selectedDocument },
            { id: 'compliance', label: 'Compliance Check', disabled: !selectedDocument }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => !tab.disabled && setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : tab.disabled
                  ? 'border-transparent text-gray-400 cursor-not-allowed'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              disabled={tab.disabled}
            >
              {tab.label}
              {tab.count !== undefined && (
                <Badge className="ml-2" variant="secondary">{tab.count}</Badge>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'queue' && (
          <DocumentProcessingQueue
            documents={pendingDocuments}
            onDocumentSelect={handleDocumentSelect}
            onRefresh={loadDashboardData}
          />
        )}

        {activeTab === 'review' && selectedDocument && (
          <OCRReviewPanel
            document={selectedDocument}
            onProcessingComplete={handleDocumentProcessed}
          />
        )}

        {activeTab === 'compile' && selectedDocument && (
          <EntryCompiler
            document={selectedDocument}
            onEntryGenerated={() => setActiveTab('compliance')}
          />
        )}

        {activeTab === 'compliance' && selectedDocument && (
          <ComplianceChecker
            document={selectedDocument}
          />
        )}
      </div>

      {/* Selected Document Info */}
      {selectedDocument && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-blue-900">Selected Document</h3>
              <p className="text-sm text-blue-700">{selectedDocument.document_name}</p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className={getConfidenceBadgeColor(selectedDocument.extraction_confidence)}>
                {selectedDocument.extraction_confidence} confidence
              </Badge>
              <Badge variant="outline">
                {selectedDocument.detected_document_type}
              </Badge>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};