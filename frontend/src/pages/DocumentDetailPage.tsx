import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaArrowLeft, FaDownload, FaEdit, FaTrash, FaEye } from 'react-icons/fa';
import type { Document } from '../types/documents';
import { documentsApi } from '../services/api';

const DocumentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadDocument(id);
    }
  }, [id]);

  const loadDocument = async (documentId: string) => {
    try {
      setLoading(true);
      const data = await documentsApi.getDocument(documentId);
      setDocument(data);
    } catch (err) {
      setError('Failed to load document');
      console.error('Error loading document:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!document) return;
    
    try {
      const blob = await documentsApi.downloadDocument(document.id.toString());
      const url = window.URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = document.original_name;
      window.document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading document:', err);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Document not found</h3>
        <p className="mt-2 text-sm text-gray-500">{error || 'The requested document could not be found.'}</p>
        <div className="mt-6">
          <Link
            to="/documents"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <FaArrowLeft className="mr-2 h-4 w-4" />
            Back to Documents
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/documents"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <FaArrowLeft className="mr-2 h-4 w-4" />
            Back to Documents
          </Link>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleDownload}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <FaDownload className="mr-2 h-4 w-4" />
            Download
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <FaEdit className="mr-2 h-4 w-4" />
            Edit
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50">
            <FaTrash className="mr-2 h-4 w-4" />
            Delete
          </button>
        </div>
      </div>

      {/* Document Info */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">{document.title}</h1>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(document.status)}`}>
              {document.status.toUpperCase()}
            </span>
          </div>
          <p className="mt-1 text-sm text-gray-500">{document.original_name}</p>
        </div>

        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Document Type</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {document.document_type.replace('_', ' ').toUpperCase()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Category</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {document.category.toUpperCase()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">File Size</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {formatFileSize(document.file_size)}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">MIME Type</dt>
              <dd className="mt-1 text-sm text-gray-900">{document.mime_type}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Upload Date</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(document.upload_date).toLocaleString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Uploaded By</dt>
              <dd className="mt-1 text-sm text-gray-900">{document.uploaded_by}</dd>
            </div>
            {document.client_name && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Client</dt>
                <dd className="mt-1 text-sm text-gray-900">{document.client_name}</dd>
              </div>
            )}
            {document.hs_code && (
              <div>
                <dt className="text-sm font-medium text-gray-500">HS Code</dt>
                <dd className="mt-1 text-sm text-gray-900">{document.hs_code}</dd>
              </div>
            )}
            {document.shipment_ref && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Shipment Reference</dt>
                <dd className="mt-1 text-sm text-gray-900">{document.shipment_ref}</dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500">Compliance Status</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {document.compliance_status.replace('_', ' ').toUpperCase()}
              </dd>
            </div>
            {document.expiry_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Expiry Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(document.expiry_date).toLocaleDateString()}
                </dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500">Confidential</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {document.is_confidential ? 'Yes' : 'No'}
              </dd>
            </div>
          </dl>

          {document.description && (
            <div className="mt-6">
              <dt className="text-sm font-medium text-gray-500">Description</dt>
              <dd className="mt-1 text-sm text-gray-900">{document.description}</dd>
            </div>
          )}

          {document.tags.length > 0 && (
            <div className="mt-6">
              <dt className="text-sm font-medium text-gray-500">Tags</dt>
              <dd className="mt-1">
                <div className="flex flex-wrap gap-2">
                  {document.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </dd>
            </div>
          )}

          {document.compliance_notes && (
            <div className="mt-6">
              <dt className="text-sm font-medium text-gray-500">Compliance Notes</dt>
              <dd className="mt-1 text-sm text-gray-900">{document.compliance_notes}</dd>
            </div>
          )}
        </div>
      </div>

      {/* Document Preview */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Document Preview</h3>
        </div>
        <div className="px-6 py-4">
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <FaEye className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Preview not available</h3>
            <p className="mt-1 text-sm text-gray-500">
              Document preview is not supported for this file type.
            </p>
            <div className="mt-6">
              <button
                onClick={handleDownload}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <FaDownload className="mr-2 h-4 w-4" />
                Download to View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetailPage;