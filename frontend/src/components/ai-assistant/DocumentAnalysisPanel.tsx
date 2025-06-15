import React, { useState, useRef, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  FileText, 
  Image, 
  Camera, 
  X, 
  Eye, 
  Download, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Scan,
  FileImage,
  FileSpreadsheet,
  File,
  Zap,
  Brain,
  Search
} from 'lucide-react';

interface UploadedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  analysis?: DocumentAnalysis;
}

interface DocumentAnalysis {
  document_type: 'commercial_invoice' | 'packing_list' | 'bill_of_lading' | 'certificate' | 'other';
  confidence: number;
  extracted_data: {
    hs_codes?: string[];
    product_descriptions?: string[];
    values?: {
      currency: string;
      amount: number;
    }[];
    parties?: {
      exporter?: string;
      importer?: string;
      consignee?: string;
    };
    shipping_details?: {
      origin_country?: string;
      destination_country?: string;
      port_of_loading?: string;
      port_of_discharge?: string;
    };
  };
  recommendations: {
    type: 'classification' | 'valuation' | 'compliance' | 'documentation';
    message: string;
    priority: 'high' | 'medium' | 'low';
  }[];
  ocr_text?: string;
}

interface ImageClassification {
  product_category: string;
  confidence: number;
  suggested_hs_codes: {
    code: string;
    description: string;
    confidence: number;
  }[];
  product_features: string[];
  classification_reasoning: string;
  additional_questions?: string[];
}

interface DocumentAnalysisPanelProps {
  className?: string;
  onCodeSuggestion?: (codes: string[]) => void;
  onAnalysisComplete?: (analysis: DocumentAnalysis | ImageClassification) => void;
}

export const DocumentAnalysisPanel: React.FC<DocumentAnalysisPanelProps> = ({
  className = '',
  onCodeSuggestion,
  onAnalysisComplete
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFiles = async (files: FileList) => {
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        continue;
      }

      const uploadedFile: UploadedFile = {
        id: `file-${Date.now()}-${Math.random()}`,
        name: file.name,
        type: file.type,
        size: file.size,
        url: URL.createObjectURL(file),
        status: 'uploading',
        progress: 0
      };

      setUploadedFiles(prev => [...prev, uploadedFile]);
      
      // Start upload and analysis
      await uploadAndAnalyzeFile(file, uploadedFile.id);
    }
  };

  const uploadAndAnalyzeFile = async (file: File, fileId: string) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Update progress
      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, progress: 25 } : f
      ));

      // Determine analysis endpoint based on file type
      const isImage = file.type.startsWith('image/');
      const endpoint = isImage ? '/api/ai/classify-image' : '/api/ai/analyze-document';

      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'processing', progress: 50 } : f
      ));

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const analysis = await response.json();
        
        setUploadedFiles(prev => prev.map(f => 
          f.id === fileId ? { 
            ...f, 
            status: 'completed', 
            progress: 100, 
            analysis: analysis 
          } : f
        ));

        // Trigger callbacks
        onAnalysisComplete?.(analysis);
        
        if (isImage && analysis.suggested_hs_codes) {
          const codes = analysis.suggested_hs_codes.map((item: any) => item.code);
          onCodeSuggestion?.(codes);
        } else if (!isImage && analysis.extracted_data?.hs_codes) {
          onCodeSuggestion?.(analysis.extracted_data.hs_codes);
        }

      } else {
        throw new Error('Analysis failed');
      }

    } catch (error) {
      console.error('Upload/analysis error:', error);
      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, status: 'error', progress: 0 } : f
      ));
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => {
      const file = prev.find(f => f.id === fileId);
      if (file) {
        URL.revokeObjectURL(file.url);
      }
      return prev.filter(f => f.id !== fileId);
    });
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <FileImage className="h-8 w-8" />;
    if (type.includes('pdf')) return <FileText className="h-8 w-8" />;
    if (type.includes('spreadsheet') || type.includes('excel')) return <FileSpreadsheet className="h-8 w-8" />;
    return <File className="h-8 w-8" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const renderUploadArea = () => (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive 
            ? 'border-primary bg-primary/5' 
            : 'border-muted-foreground/25 hover:border-primary/50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="flex justify-center">
            <Upload className="h-12 w-12 text-muted-foreground" />
          </div>
          
          <div>
            <h3 className="text-lg font-semibold">Upload Documents or Images</h3>
            <p className="text-muted-foreground">
              Drag and drop files here, or click to select
            </p>
          </div>

          <div className="flex justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
            >
              <FileText className="h-4 w-4 mr-2" />
              Select Documents
            </Button>
            
            <Button
              variant="outline"
              onClick={() => cameraInputRef.current?.click()}
            >
              <Camera className="h-4 w-4 mr-2" />
              Take Photo
            </Button>
          </div>

          <div className="text-xs text-muted-foreground">
            Supported: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG, WEBP (Max 10MB)
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.webp"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
          className="hidden"
        />
        
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
          className="hidden"
        />
      </div>

      {/* Capabilities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <div className="flex items-start gap-3">
            <Scan className="h-6 w-6 text-blue-500 mt-1" />
            <div>
              <h4 className="font-semibold">Document Analysis</h4>
              <p className="text-sm text-muted-foreground">
                Extract HS codes, values, and shipping details from commercial invoices, 
                packing lists, and other trade documents.
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start gap-3">
            <Brain className="h-6 w-6 text-purple-500 mt-1" />
            <div>
              <h4 className="font-semibold">Image Classification</h4>
              <p className="text-sm text-muted-foreground">
                Identify products from photos and suggest appropriate HS codes 
                with AI-powered visual recognition.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );

  const renderFileList = () => (
    <div className="space-y-4">
      {uploadedFiles.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No files uploaded yet</p>
        </div>
      ) : (
        uploadedFiles.map((file) => (
          <Card key={file.id} className="p-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 text-muted-foreground">
                {getFileIcon(file.type)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium truncate">{file.name}</h4>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(file.status)}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                      className="h-6 w-6 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                  <span>{(file.size / 1024 / 1024).toFixed(1)} MB</span>
                  <Badge variant="outline">{file.status}</Badge>
                </div>

                {file.status === 'uploading' || file.status === 'processing' ? (
                  <div className="space-y-1">
                    <Progress value={file.progress} className="h-2" />
                    <p className="text-xs text-muted-foreground">
                      {file.status === 'uploading' ? 'Uploading...' : 'Analyzing...'}
                    </p>
                  </div>
                ) : file.status === 'completed' && file.analysis ? (
                  <div className="space-y-3 mt-3">
                    {/* Document Analysis Results */}
                    {'document_type' in file.analysis && (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">
                            {file.analysis.document_type.replace('_', ' ').toUpperCase()}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {file.analysis.confidence}% confidence
                          </span>
                        </div>

                        {file.analysis.extracted_data.hs_codes && (
                          <div>
                            <span className="text-sm font-medium">Extracted HS Codes:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {file.analysis.extracted_data.hs_codes.map((code, index) => (
                                <Badge key={index} variant="secondary" className="font-mono">
                                  {code}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {file.analysis.extracted_data.product_descriptions && (
                          <div>
                            <span className="text-sm font-medium">Products:</span>
                            <ul className="text-sm text-muted-foreground mt-1">
                              {file.analysis.extracted_data.product_descriptions.slice(0, 3).map((desc, index) => (
                                <li key={index}>• {desc}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Image Classification Results */}
                    {'product_category' in file.analysis && (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{file.analysis.product_category}</Badge>
                          <span className="text-sm text-muted-foreground">
                            {file.analysis.confidence}% confidence
                          </span>
                        </div>

                        {file.analysis.suggested_hs_codes && (
                          <div>
                            <span className="text-sm font-medium">Suggested HS Codes:</span>
                            <div className="space-y-1 mt-1">
                              {file.analysis.suggested_hs_codes.slice(0, 3).map((suggestion, index) => (
                                <div key={index} className="flex items-center justify-between text-sm">
                                  <span className="font-mono">{suggestion.code}</span>
                                  <span className="text-muted-foreground">{suggestion.confidence}%</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div>
                          <span className="text-sm font-medium">Detected Features:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {file.analysis.product_features.slice(0, 5).map((feature, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {feature}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {file.analysis.recommendations && file.analysis.recommendations.length > 0 && (
                      <div>
                        <span className="text-sm font-medium">Recommendations:</span>
                        <div className="space-y-1 mt-1">
                          {file.analysis.recommendations.slice(0, 2).map((rec, index) => (
                            <Alert key={index} className="py-2">
                              <AlertCircle className="h-4 w-4" />
                              <AlertDescription className="text-xs">
                                <Badge variant="outline" className={
                                  rec.priority === 'high' ? 'text-red-600' :
                                  rec.priority === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                                }>
                                  {rec.priority.toUpperCase()}
                                </Badge>
                                <span className="ml-2">{rec.message}</span>
                              </AlertDescription>
                            </Alert>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2 pt-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                      
                      {file.type.startsWith('image/') && (
                        <Button variant="outline" size="sm">
                          <Search className="h-4 w-4 mr-2" />
                          Find Similar
                        </Button>
                      )}
                    </div>
                  </div>
                ) : file.status === 'error' && (
                  <Alert className="mt-3">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      Failed to analyze this file. Please try again or contact support.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );

  const renderAnalysisHistory = () => {
    const completedFiles = uploadedFiles.filter(f => f.status === 'completed' && f.analysis);
    
    if (completedFiles.length === 0) {
      return (
        <div className="text-center py-8">
          <Zap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No analysis results yet</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {completedFiles.map((file) => (
          <Card key={file.id} className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium">{file.name}</h4>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>

            {file.analysis && (
              <div className="space-y-3">
                {'document_type' in file.analysis ? (
                  // Document analysis summary
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Document Type:</span>
                      <p className="text-muted-foreground">
                        {file.analysis.document_type.replace('_', ' ').toUpperCase()}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">HS Codes Found:</span>
                      <p className="text-muted-foreground">
                        {file.analysis.extracted_data.hs_codes?.length || 0} codes
                      </p>
                    </div>
                  </div>
                ) : (
                  // Image classification summary
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Product Category:</span>
                      <p className="text-muted-foreground">{file.analysis.product_category}</p>
                    </div>
                    <div>
                      <span className="font-medium">Suggested Codes:</span>
                      <p className="text-muted-foreground">
                        {file.analysis.suggested_hs_codes?.length || 0} suggestions
                      </p>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    {file.analysis.confidence}% Confidence
                  </Badge>
                  {file.analysis.recommendations && (
                    <Badge variant="outline">
                      {file.analysis.recommendations.length} Recommendations
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    );
  };

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Scan className="h-5 w-5" />
          Document & Image Analysis
        </CardTitle>
      </CardHeader>

      <CardContent className="pt-0">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upload">Upload</TabsTrigger>
            <TabsTrigger value="files">Files ({uploadedFiles.length})</TabsTrigger>
            <TabsTrigger value="history">Analysis History</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderUploadArea()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="files" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderFileList()}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="history" className="mt-4">
            <ScrollArea className="h-[600px]">
              {renderAnalysisHistory()}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default DocumentAnalysisPanel;
