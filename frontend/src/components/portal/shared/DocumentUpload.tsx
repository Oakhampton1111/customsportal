import React, { useState, useRef, useCallback } from 'react';
import { documentsService } from '../../../services/portal/documentsService';
import type { DocumentType, Document } from '../../../types/portal';

interface DocumentUploadProps {
  jobId?: string;
  onUploadComplete?: (documents: Document[]) => void;
  onUploadError?: (error: string) => void;
  allowMultiple?: boolean;
  acceptedTypes?: DocumentType[];
  maxFileSize?: number; // in MB
  className?: string;
}

interface UploadFile {
  file: File;
  name: string;
  type: DocumentType;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
  document?: Document;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  jobId,
  onUploadComplete,
  onUploadError,
  allowMultiple = true,
  acceptedTypes,
  maxFileSize = 10, // 10MB default
  className = '',
}) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Document type options
  const documentTypes: { value: DocumentType; label: string }[] = [
    { value: 'invoice', label: 'Invoice' },
    { value: 'packing_list', label: 'Packing List' },
    { value: 'bill_of_lading', label: 'Bill of Lading' },
    { value: 'certificate_of_origin', label: 'Certificate of Origin' },
    { value: 'customs_declaration', label: 'Customs Declaration' },
    { value: 'permit', label: 'Permit' },
    { value: 'insurance', label: 'Insurance' },
    { value: 'other', label: 'Other' },
  ];

  const filteredDocumentTypes = acceptedTypes 
    ? documentTypes.filter(type => acceptedTypes.includes(type.value))
    : documentTypes;

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File size must be less than ${maxFileSize}MB`;
    }

    // Check file type
    const allowedExtensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xlsx', '.xls'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      return `File type not supported. Allowed types: ${allowedExtensions.join(', ')}`;
    }

    return null;
  };

  const addFiles = useCallback((newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles);
    const validFiles: UploadFile[] = [];

    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        onUploadError?.(error);
        return;
      }

      // Default document type based on file name/extension
      let defaultType: DocumentType = 'other';
      const fileName = file.name.toLowerCase();
      if (fileName.includes('invoice')) defaultType = 'invoice';
      else if (fileName.includes('packing')) defaultType = 'packing_list';
      else if (fileName.includes('bill') || fileName.includes('lading')) defaultType = 'bill_of_lading';
      else if (fileName.includes('certificate') || fileName.includes('origin')) defaultType = 'certificate_of_origin';
      else if (fileName.includes('customs') || fileName.includes('declaration')) defaultType = 'customs_declaration';
      else if (fileName.includes('permit')) defaultType = 'permit';
      else if (fileName.includes('insurance')) defaultType = 'insurance';

      validFiles.push({
        file,
        name: file.name,
        type: defaultType,
        progress: 0,
        status: 'pending',
      });
    });

    if (!allowMultiple && validFiles.length > 1) {
      onUploadError?.('Only one file can be uploaded at a time');
      return;
    }

    setFiles(prev => allowMultiple ? [...prev, ...validFiles] : validFiles);
  }, [allowMultiple, maxFileSize, onUploadError]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(e.target.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (e.dataTransfer.files) {
      addFiles(e.dataTransfer.files);
    }
  };

  const updateFile = (index: number, updates: Partial<UploadFile>) => {
    setFiles(prev => prev.map((file, i) => i === index ? { ...file, ...updates } : file));
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (!jobId) {
      onUploadError?.('Job ID is required for document upload');
      return;
    }

    setIsUploading(true);
    const uploadedDocuments: Document[] = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const uploadFile = files[i];
        
        if (uploadFile.status !== 'pending') continue;

        updateFile(i, { status: 'uploading', progress: 0 });

        try {
          const response = await documentsService.uploadDocument({
            jobId,
            name: uploadFile.name,
            type: uploadFile.type,
            file: uploadFile.file,
          });

          if (response.success && response.data) {
            updateFile(i, { 
              status: 'success', 
              progress: 100,
              document: response.data 
            });
            uploadedDocuments.push(response.data);
          } else {
            updateFile(i, { 
              status: 'error', 
              error: response.error || 'Upload failed' 
            });
          }
        } catch (error) {
          updateFile(i, { 
            status: 'error', 
            error: error instanceof Error ? error.message : 'Upload failed' 
          });
        }
      }

      if (uploadedDocuments.length > 0) {
        onUploadComplete?.(uploadedDocuments);
      }
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadFile['status']): string => {
    switch (status) {
      case 'pending': return '📄';
      case 'uploading': return '⏳';
      case 'success': return '✅';
      case 'error': return '❌';
      default: return '📄';
    }
  };

  const hasValidFiles = files.some(f => f.status === 'pending');
  const hasErrors = files.some(f => f.status === 'error');

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="text-4xl mb-4">📎</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Upload Documents
        </h3>
        <p className="text-gray-600 mb-4">
          Drag and drop files here, or click to select files
        </p>
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="portal-btn portal-btn-primary"
        >
          Select Files
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple={allowMultiple}
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.xlsx,.xls"
        />
        <p className="text-xs text-gray-500 mt-2">
          Supported formats: PDF, DOC, DOCX, JPG, PNG, GIF, XLS, XLSX (max {maxFileSize}MB)
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Selected Files</h4>
          {files.map((uploadFile, index) => (
            <div
              key={index}
              className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg"
            >
              <div className="text-2xl">
                {getStatusIcon(uploadFile.status)}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <input
                    type="text"
                    value={uploadFile.name}
                    onChange={(e) => updateFile(index, { name: e.target.value })}
                    className="font-medium text-gray-900 bg-transparent border-none p-0 focus:outline-none focus:ring-0"
                    disabled={uploadFile.status !== 'pending'}
                  />
                  <span className="text-sm text-gray-500">
                    ({formatFileSize(uploadFile.file.size)})
                  </span>
                </div>
                
                <div className="flex items-center gap-4">
                  <select
                    value={uploadFile.type}
                    onChange={(e) => updateFile(index, { type: e.target.value as DocumentType })}
                    className="text-sm border border-gray-300 rounded px-2 py-1"
                    disabled={uploadFile.status !== 'pending'}
                  >
                    {filteredDocumentTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  
                  {uploadFile.status === 'uploading' && (
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${uploadFile.progress}%` }}
                      />
                    </div>
                  )}
                  
                  {uploadFile.status === 'error' && uploadFile.error && (
                    <span className="text-sm text-red-600">{uploadFile.error}</span>
                  )}
                  
                  {uploadFile.status === 'success' && (
                    <span className="text-sm text-green-600">Uploaded successfully</span>
                  )}
                </div>
              </div>
              
              {uploadFile.status === 'pending' && (
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-600 hover:text-red-800 p-1"
                  title="Remove file"
                >
                  🗑️
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload Button */}
      {hasValidFiles && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {files.filter(f => f.status === 'pending').length} file(s) ready to upload
          </div>
          <button
            onClick={uploadFiles}
            disabled={isUploading || !jobId}
            className="portal-btn portal-btn-primary disabled:opacity-50"
          >
            {isUploading ? 'Uploading...' : 'Upload Files'}
          </button>
        </div>
      )}

      {/* Error Summary */}
      {hasErrors && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h5 className="font-medium text-red-800 mb-2">Upload Errors</h5>
          <ul className="text-sm text-red-700 space-y-1">
            {files
              .filter(f => f.status === 'error')
              .map((file, index) => (
                <li key={index}>
                  {file.name}: {file.error}
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;