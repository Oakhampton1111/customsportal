import React, { useState, useRef, useEffect } from 'react';
import {
  FiMessageSquare,
  FiFileText,
  FiTool,
  FiHelpCircle,
  FiUser,
  FiLoader,
  FiHash,
  FiImage,
  FiMic,
  FiCopy,
  FiRefreshCw,
  FiSettings,
  FiBookmark,
  FiClock,
  FiDownload,
  FiSend,
  FiSearch,
  FiUpload,
  FiZap,
  FiActivity
} from 'react-icons/fi';
import { dutyCalculatorApi } from '../services/dutyCalculatorApi';
import type { DutyCalculationRequest, DutyCalculationResult } from '../types';
import { ProfessionalCard, ProfessionalCardHeader, ProfessionalCardContent } from '../components/ui/ProfessionalCard';
import { ProfessionalTable } from '../components/ui/ProfessionalTable';
import { ProfessionalFilters, SearchBar, QuickFilters } from '../components/ui/ProfessionalFilters';
import { TabPanel, MasterDetail, Accordion } from '../components/ui/ProfessionalLayouts';
import { ActionToolbar } from '../components/ui/ActionToolbar';
import { KPICard, KPIGrid } from '../components/ui/KPICard';
import { cn } from '../lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'calculation' | 'classification' | 'document';
  data?: any;
}

interface ClassificationResult {
  hsCode: string;
  description: string;
  confidence: number;
  reasoning: string;
}

interface DocumentAnalysis {
  documentType: string;
  extractedData: {
    invoiceNumber?: string;
    supplier?: string;
    consignee?: string;
    items?: Array<{
      description: string;
      quantity: number;
      value: number;
      suggestedHsCode?: string;
    }>;
    [key: string]: unknown;
  };
  hsCodeSuggestions: string[];
  confidence: number;
  summary: string;
}

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI customs assistant. I can help you with duty calculations, tariff classifications, document analysis, and customs regulations. How can I assist you today?',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [calculationData, setCalculationData] = useState<DutyCalculationRequest>({
    hs_code: '',
    country_code: 'CN',
    customs_value: 0,
    quantity: 1,
    currency: 'AUD'
  });
  const [calculationResult, setCalculationResult] = useState<DutyCalculationResult | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  
  // Professional component state
  const [filterValues, setFilterValues] = useState<Record<string, any>>({});
  const [showDetailView, setShowDetailView] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // Enhanced state for modern features
  const [savedQueries, setSavedQueries] = useState<Message[]>([]);
  const [recentCalculations, setRecentCalculations] = useState<DutyCalculationResult[]>([]);
  const [sessionStats, setSessionStats] = useState({
    messagesCount: 0,
    calculationsCount: 0,
    documentsAnalyzed: 0,
    sessionStartTime: new Date()
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollToBottom();
    // Update session stats
    setSessionStats(prev => ({
      ...prev,
      messagesCount: messages.length,
      calculationsCount: messages.filter(m => m.type === 'calculation').length,
      documentsAnalyzed: messages.filter(m => m.type === 'document').length
    }));
  }, [messages]);

  // Load saved data from localStorage
  useEffect(() => {
    const savedQueries = localStorage.getItem('ai-saved-queries');
    const recentCalcs = localStorage.getItem('ai-recent-calculations');
    
    if (savedQueries) {
      setSavedQueries(JSON.parse(savedQueries));
    }
    if (recentCalcs) {
      setRecentCalculations(JSON.parse(recentCalcs));
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const saveQuery = (message: Message) => {
    const newSavedQueries = [message, ...savedQueries.filter(q => q.id !== message.id)].slice(0, 10);
    setSavedQueries(newSavedQueries);
    localStorage.setItem('ai-saved-queries', JSON.stringify(newSavedQueries));
  };

  const saveCalculation = (result: DutyCalculationResult) => {
    const newRecentCalcs = [result, ...recentCalculations].slice(0, 5);
    setRecentCalculations(newRecentCalcs);
    localStorage.setItem('ai-recent-calculations', JSON.stringify(newRecentCalcs));
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Simulate AI response
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I understand you're asking about "${inputMessage}". Let me help you with that. Based on your query, I can provide guidance on customs regulations, duty calculations, or tariff classifications. Would you like me to elaborate on any specific aspect?`,
        timestamp: new Date(),
        type: 'text'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCalculation = async () => {
    if (!calculationData.hs_code || !calculationData.customs_value) return;

    setIsLoading(true);
    try {
      // Validate HS code format
      const cleanHsCode = calculationData.hs_code.replace(/\./g, '');
      if (!/^\d{8,10}$/.test(cleanHsCode)) {
        throw new Error('HS Code must be 8-10 digits');
      }

      const requestData: DutyCalculationRequest = {
        ...calculationData,
        hs_code: cleanHsCode.padEnd(10, '0').slice(0, 10)
      };

      const result = await dutyCalculatorApi.calculateDuty(requestData);
      setCalculationResult(result);
      saveCalculation(result);
      
      const calculationMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `I've calculated the duties for HS Code ${calculationData.hs_code}. Here's the breakdown:`,
        timestamp: new Date(),
        type: 'calculation',
        data: result
      };

      setMessages(prev => [...prev, calculationMessage]);
    } catch (error) {
      console.error('Calculation error:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error calculating duties: ${error instanceof Error ? error.message : 'Unknown error'}. Please check your inputs and try again.`,
        timestamp: new Date(),
        type: 'text'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setIsLoading(true);

    try {
      // Simulate file analysis
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const analysisMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `I've analyzed your uploaded file "${file.name}". Based on the document content, I can extract relevant information and suggest appropriate HS codes for classification.`,
        timestamp: new Date(),
        type: 'document',
        data: {
          fileName: file.name,
          fileSize: file.size,
          fileType: file.type
        }
      };

      setMessages(prev => [...prev, analysisMessage]);
    } catch (error) {
      console.error('File upload error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';
    
    return (
      <div key={message.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            <FiTool className="w-4 h-4 text-blue-600" />
          </div>
        )}
        
        <div className={`max-w-3xl ${isUser ? 'order-1' : ''}`}>
          <div className={`p-4 rounded-lg ${
            isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-white border border-gray-200'
          }`}>
            <p className="text-sm leading-relaxed">{message.content}</p>
            
            {message.type === 'calculation' && message.data && (
              <div className="mt-3 p-3 bg-gray-50 rounded border">
                <h4 className="font-medium text-gray-900 mb-2">Duty Calculation Result</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>Total Duty: ${parseFloat(message.data.total_duty || '0').toFixed(2)}</div>
                  <div>GST: ${parseFloat(message.data.total_gst || '0').toFixed(2)}</div>
                  <div>Total Cost: ${parseFloat(message.data.total_amount || '0').toFixed(2)}</div>
                </div>
              </div>
            )}
            
            {message.type === 'document' && message.data && (
              <div className="mt-3 p-3 bg-gray-50 rounded border">
                <h4 className="font-medium text-gray-900 mb-2">Document Analysis</h4>
                <div className="text-xs text-gray-600">
                  <div>File: {message.data.fileName}</div>
                  <div>Size: {(message.data.fileSize / 1024).toFixed(1)} KB</div>
                  <div>Type: {message.data.fileType}</div>
                </div>
              </div>
            )}
          </div>
          
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
        
        {isUser && (
          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
            <FiUser className="w-4 h-4 text-gray-600" />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Professional Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <FiZap className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">AI Customs Assistant</h1>
                  <p className="text-sm text-gray-600">Expert guidance for duty calculations and customs compliance</p>
                </div>
              </div>
            </div>
            
            <ActionToolbar
              actions={[
                {
                  id: 'settings',
                  label: 'Settings',
                  icon: <FiSettings className="w-4 h-4" />,
                  onClick: () => console.log('Settings'),
                  variant: 'default'
                },
                {
                  id: 'export',
                  label: 'Export Chat',
                  icon: <FiDownload className="w-4 h-4" />,
                  onClick: () => console.log('Export chat'),
                  variant: 'default'
                }
              ]}
              showSelectionInfo={false}
              className="border-0 bg-transparent p-0"
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <FiMessageSquare className="w-4 h-4 inline mr-2" />
              AI Chat
            </button>
            <button
              onClick={() => setActiveTab('calculator')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'calculator'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <FiHash className="w-4 h-4 inline mr-2" />
              Duty Calculator
            </button>
            <button
              onClick={() => setActiveTab('tools')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'tools'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <FiTool className="w-4 h-4 inline mr-2" />
              AI Tools
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === 'chat' && (
              <ProfessionalCard variant="default" className="h-[600px] flex flex-col">
                <ProfessionalCardHeader subtitle="Ask questions about customs and trade">
                  AI Conversation
                </ProfessionalCardHeader>
                <ProfessionalCardContent className="flex-1 flex flex-col">
                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map(renderMessage)}
                    {isLoading && (
                      <div className="flex gap-3 justify-start">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <FiTool className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="max-w-3xl">
                          <div className="p-4 rounded-lg bg-white border border-gray-200">
                            <div className="flex items-center gap-2">
                              <div className="loading-spinner w-4 h-4"></div>
                              <span className="text-sm text-gray-600">AI is thinking...</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                  
                  {/* Input */}
                  <div className="border-t p-4">
                    <div className="flex gap-3">
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                        className="hidden"
                        accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                      />
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="btn btn--ghost"
                        disabled={isLoading}
                      >
                        <FiImage className="w-4 h-4" />
                      </button>
                      <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Ask about customs regulations, duty calculations, or upload documents..."
                        className="input flex-1"
                        disabled={isLoading}
                      />
                      <button
                        onClick={handleSendMessage}
                        className="btn btn--primary"
                        disabled={isLoading || !inputMessage.trim()}
                      >
                        <FiSend className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </ProfessionalCardContent>
              </ProfessionalCard>
            )}

            {activeTab === 'calculator' && (
              <ProfessionalCard variant="default">
                <ProfessionalCardHeader subtitle="Calculate all import taxes and duties">
                  Comprehensive Duty Calculator
                </ProfessionalCardHeader>
                <ProfessionalCardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="label">HS Code</label>
                        <input
                          type="text"
                          value={calculationData.hs_code}
                          onChange={(e) => setCalculationData(prev => ({ ...prev, hs_code: e.target.value }))}
                          placeholder="e.g., 8471.30.00 or 8471300000"
                          className="input w-full"
                        />
                        <p className="text-xs text-gray-500 mt-1">Enter 8-10 digit HS code (dots optional)</p>
                      </div>
                      
                      <div>
                        <label className="label">Value (AUD)</label>
                        <input
                          type="number"
                          value={calculationData.customs_value}
                          onChange={(e) => setCalculationData(prev => ({ ...prev, customs_value: Number(e.target.value) }))}
                          placeholder="0.00"
                          className="input w-full"
                          min="0"
                          step="0.01"
                        />
                      </div>
                      
                      <div>
                        <label className="label">Country of Origin</label>
                        <select
                          value={calculationData.country_code}
                          onChange={(e) => setCalculationData(prev => ({ ...prev, country_code: e.target.value }))}
                          className="input w-full"
                        >
                          <option value="CN">China</option>
                          <option value="US">United States</option>
                          <option value="DE">Germany</option>
                          <option value="JP">Japan</option>
                          <option value="GB">United Kingdom</option>
                          <option value="KR">South Korea</option>
                          <option value="TH">Thailand</option>
                          <option value="VN">Vietnam</option>
                          <option value="MY">Malaysia</option>
                          <option value="SG">Singapore</option>
                        </select>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="label">Quantity</label>
                          <input
                            type="number"
                            value={calculationData.quantity}
                            onChange={(e) => setCalculationData(prev => ({ ...prev, quantity: Number(e.target.value) }))}
                            className="input w-full"
                            min="1"
                          />
                        </div>
                        <div>
                          <label className="label">Currency</label>
                          <select
                            value={calculationData.currency}
                            onChange={(e) => setCalculationData(prev => ({ ...prev, currency: e.target.value }))}
                            className="input w-full"
                          >
                            <option value="AUD">AUD</option>
                            <option value="USD">USD</option>
                            <option value="EUR">EUR</option>
                            <option value="GBP">GBP</option>
                          </select>
                        </div>
                      </div>
                      
                      <button
                        onClick={handleCalculation}
                        className="btn btn--primary w-full"
                        disabled={isLoading || !calculationData.hs_code || !calculationData.customs_value}
                      >
                        {isLoading ? (
                          <>
                            <FiLoader className="w-4 h-4 animate-spin" />
                            Calculating...
                          </>
                        ) : (
                          <>
                            <FiHash className="w-4 h-4" />
                            Calculate Duties
                          </>
                        )}
                      </button>
                    </div>
                    
                    {calculationResult && (
                      <div className="space-y-4">
                        <h4 className="font-semibold text-gray-900">Calculation Results</h4>
                        <div className="space-y-3">
                          <KPICard
                            icon={FiHash}
                            label="Customs Duty"
                            value={`$${parseFloat(String(calculationResult.total_duty || '0')).toFixed(2)}`}
                            color="blue"
                          />
                          <KPICard
                            icon={FiActivity}
                            label="GST"
                            value={`$${parseFloat(String(calculationResult.total_gst || '0')).toFixed(2)}`}
                            color="green"
                          />
                          <KPICard
                            icon={FiZap}
                            label="Total Import Cost"
                            value={`$${parseFloat(String(calculationResult.total_amount || '0')).toFixed(2)}`}
                            color="indigo"
                            className="border-blue-200 bg-blue-50"
                          />
                          {calculationResult.components && calculationResult.components.length > 0 && (
                            <div className="mt-4">
                              <h5 className="font-medium text-gray-900 mb-2">Duty Breakdown</h5>
                              <div className="space-y-2">
                                {calculationResult.components.map((component, index) => (
                                  <div key={index} className="flex justify-between text-sm">
                                    <span className="text-gray-600">{component.description}</span>
                                    <span className="font-medium">${component.amount.toFixed(2)}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          {calculationResult.warnings && calculationResult.warnings.length > 0 && (
                            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <h5 className="font-medium text-yellow-800 mb-1">Warnings</h5>
                              <ul className="text-sm text-yellow-700 space-y-1">
                                {calculationResult.warnings.map((warning, index) => (
                                  <li key={index}>• {warning}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </ProfessionalCardContent>
              </ProfessionalCard>
            )}

            {activeTab === 'tools' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <ProfessionalCard variant="default">
                    <ProfessionalCardHeader
                      icon={<FiImage className="w-5 h-5 text-blue-500" />}
                      subtitle="Upload product images for HS code suggestions"
                    >
                      Image Classification
                    </ProfessionalCardHeader>
                    <ProfessionalCardContent>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                        <FiImage className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-600 mb-2">Drop image here or click to upload</p>
                        <button className="btn btn--secondary btn--sm">
                          Choose File
                        </button>
                      </div>
                    </ProfessionalCardContent>
                  </ProfessionalCard>

                  <ProfessionalCard variant="default">
                    <ProfessionalCardHeader
                      icon={<FiFileText className="w-5 h-5 text-green-500" />}
                      subtitle="Analyze invoices and shipping documents"
                    >
                      Document Analysis
                    </ProfessionalCardHeader>
                    <ProfessionalCardContent>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                        <FiFileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-600 mb-2">Upload PDF or image documents</p>
                        <button className="btn btn--secondary btn--sm">
                          Choose File
                        </button>
                      </div>
                    </ProfessionalCardContent>
                  </ProfessionalCard>
                </div>

                <ProfessionalCard variant="default">
                  <ProfessionalCardHeader>
                    Quick Actions
                  </ProfessionalCardHeader>
                  <ProfessionalCardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <button className="btn btn--secondary justify-start">
                        <FiSearch className="w-5 h-5" />
                        <div className="text-left">
                          <div className="font-medium">Find HS Code</div>
                          <div className="text-xs opacity-75">Product classification</div>
                        </div>
                      </button>
                      <button className="btn btn--secondary justify-start">
                        <FiHash className="w-5 h-5" />
                        <div className="text-left">
                          <div className="font-medium">Calculate Duties</div>
                          <div className="text-xs opacity-75">Import cost estimation</div>
                        </div>
                      </button>
                      <button className="btn btn--secondary justify-start">
                        <FiHelpCircle className="w-5 h-5" />
                        <div className="text-left">
                          <div className="font-medium">Ask Question</div>
                          <div className="text-xs opacity-75">Customs guidance</div>
                        </div>
                      </button>
                    </div>
                  </ProfessionalCardContent>
                </ProfessionalCard>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Session Stats */}
            <ProfessionalCard variant="default">
              <ProfessionalCardHeader>
                Session Stats
              </ProfessionalCardHeader>
              <ProfessionalCardContent>
                <KPIGrid columns={1}>
                  <KPICard
                    icon={FiMessageSquare}
                    label="Messages"
                    value={sessionStats.messagesCount.toString()}
                    color="blue"
                  />
                  <KPICard
                    icon={FiHash}
                    label="Calculations"
                    value={sessionStats.calculationsCount.toString()}
                    color="green"
                  />
                  <KPICard
                    icon={FiFileText}
                    label="Documents"
                    value={sessionStats.documentsAnalyzed.toString()}
                    color="purple"
                  />
                </KPIGrid>
              </ProfessionalCardContent>
            </ProfessionalCard>

            {/* Recent Calculations */}
            {recentCalculations.length > 0 && (
              <ProfessionalCard variant="default">
                <ProfessionalCardHeader>
                  Recent Calculations
                </ProfessionalCardHeader>
                <ProfessionalCardContent>
                  <div className="space-y-3">
                    {recentCalculations.slice(0, 3).map((calc, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        <div className="text-sm font-medium text-gray-900">
                          ${calc.total_amount?.toFixed(2) || '0.00'}
                        </div>
                        <div className="text-xs text-gray-600">
                          Total import cost
                        </div>
                      </div>
                    ))}
                  </div>
                </ProfessionalCardContent>
              </ProfessionalCard>
            )}

            {/* Saved Queries */}
            {savedQueries.length > 0 && (
              <ProfessionalCard variant="default">
                <ProfessionalCardHeader>
                  Saved Queries
                </ProfessionalCardHeader>
                <ProfessionalCardContent>
                  <div className="space-y-2">
                    {savedQueries.slice(0, 5).map((query) => (
                      <button
                        key={query.id}
                        onClick={() => setInputMessage(query.content)}
                        className="w-full text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded"
                      >
                        {query.content.slice(0, 50)}...
                      </button>
                    ))}
                  </div>
                </ProfessionalCardContent>
              </ProfessionalCard>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
