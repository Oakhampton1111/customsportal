import React, { useState, useCallback } from 'react';
import type { DocumentUploadRequest, DocumentType, DocumentCategory, ComplianceStatus } from '../../types/documents';

interface DocumentUploadProps {
  onUpload: (file: File, metadata: DocumentUploadRequest) => Promise<void>;
  loading?: boolean;
  error?: string;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  loading = false,
  error
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState<DocumentUploadRequest>({
    title: '',
    description: '',
    document_type: 'invoice' as DocumentType,
    category: 'import' as DocumentCategory,
    client_id: '',
    client_name: '',
    hs_code: '',
    shipment_ref: '',
    tags: [],
    is_confidential: false,
    compliance_status: 'pending_review' as ComplianceStatus,
    compliance_notes: '',
    expiry_date: ''
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      if (!metadata.title) {
        setMetadata(prev => ({
          ...prev,
          title: file.name.split('.')[0]
        }));
      }
    }
  }, [metadata.title]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (!metadata.title) {
        setMetadata(prev => ({
          ...prev,
          title: file.name.split('.')[0]
        }));
      }
    }
  };

  const handleMetadataChange = (field: keyof DocumentUploadRequest, value: any) => {
    setMetadata(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
    setMetadata(prev => ({
      ...prev,
      tags
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    
    await onUpload(selectedFile, metadata);
    
    // Reset form after successful upload
    setSelectedFile(null);
    setMetadata({
      title: '',
      description: '',
      document_type: 'invoice' as DocumentType,
      category: 'import' as DocumentCategory,
      client_id: '',
      client_name: '',
      hs_code: '',
      shipment_ref: '',
      tags: [],
      is_confidential: false,
      compliance_status: 'pending_review' as ComplianceStatus,
      compliance_notes: '',
      expiry_date: ''
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Document</h2>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-6 transition-colors ${
            dragActive
              ? 'border-indigo-500 bg-indigo-50'
              : selectedFile
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={handleFileSelect}
            accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif"
            disabled={loading}
          />
          
          <div className="text-center">
            {selectedFile ? (
              <div className="space-y-2">
                <div className="text-4xl">📄</div>
                <div className="text-lg font-medium text-gray-900">{selectedFile.name}</div>
                <div className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="text-4xl">📁</div>
                <div className="text-lg font-medium text-gray-900">
                  Drop files here or click to browse
                </div>
                <div className="text-sm text-gray-500">
                  Supports PDF, DOC, XLS, and image files up to 10MB
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Metadata Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Document Title *
            </label>
            <input
              type="text"
              id="title"
              required
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.title}
              onChange={(e) => handleMetadataChange('title', e.target.value)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="document_type" className="block text-sm font-medium text-gray-700">
              Document Type *
            </label>
            <select
              id="document_type"
              required
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.document_type}
              onChange={(e) => handleMetadataChange('document_type', e.target.value as DocumentType)}
              disabled={loading}
            >
              <option value="invoice">Invoice</option>
              <option value="packing_list">Packing List</option>
              <option value="certificate">Certificate</option>
              <option value="permit">Permit</option>
              <option value="declaration">Declaration</option>
              <option value="correspondence">Correspondence</option>
              <option value="report">Report</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700">
              Category *
            </label>
            <select
              id="category"
              required
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.category}
              onChange={(e) => handleMetadataChange('category', e.target.value as DocumentCategory)}
              disabled={loading}
            >
              <option value="import">Import</option>
              <option value="export">Export</option>
              <option value="compliance">Compliance</option>
              <option value="financial">Financial</option>
              <option value="legal">Legal</option>
              <option value="operational">Operational</option>
              <option value="archive">Archive</option>
            </select>
          </div>

          <div>
            <label htmlFor="client_name" className="block text-sm font-medium text-gray-700">
              Client Name
            </label>
            <input
              type="text"
              id="client_name"
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.client_name}
              onChange={(e) => handleMetadataChange('client_name', e.target.value)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="hs_code" className="block text-sm font-medium text-gray-700">
              HS Code
            </label>
            <input
              type="text"
              id="hs_code"
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.hs_code}
              onChange={(e) => handleMetadataChange('hs_code', e.target.value)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="shipment_ref" className="block text-sm font-medium text-gray-700">
              Shipment Reference
            </label>
            <input
              type="text"
              id="shipment_ref"
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.shipment_ref}
              onChange={(e) => handleMetadataChange('shipment_ref', e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="description"
            rows={3}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            value={metadata.description}
            onChange={(e) => handleMetadataChange('description', e.target.value)}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            id="tags"
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="urgent, customs, clearance"
            value={metadata.tags?.join(', ') || ''}
            onChange={handleTagsChange}
            disabled={loading}
          />
        </div>

        <div className="flex items-center space-x-6">
          <div className="flex items-center">
            <input
              id="is_confidential"
              type="checkbox"
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              checked={metadata.is_confidential}
              onChange={(e) => handleMetadataChange('is_confidential', e.target.checked)}
              disabled={loading}
            />
            <label htmlFor="is_confidential" className="ml-2 block text-sm text-gray-900">
              Mark as confidential
            </label>
          </div>

          <div>
            <label htmlFor="expiry_date" className="block text-sm font-medium text-gray-700">
              Expiry Date
            </label>
            <input
              type="date"
              id="expiry_date"
              className="mt-1 block border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={metadata.expiry_date}
              onChange={(e) => handleMetadataChange('expiry_date', e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            onClick={() => {
              setSelectedFile(null);
              setMetadata({
                title: '',
                description: '',
                document_type: 'invoice' as DocumentType,
                category: 'import' as DocumentCategory,
                client_id: '',
                client_name: '',
                hs_code: '',
                shipment_ref: '',
                tags: [],
                is_confidential: false,
                compliance_status: 'pending_review' as ComplianceStatus,
                compliance_notes: '',
                expiry_date: ''
              });
            }}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!selectedFile || loading}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </>
            ) : (
              'Upload Document'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};