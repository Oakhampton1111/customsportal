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
  FiSearch
} from 'react-icons/fi';
import { dutyCalculatorApi } from '../services/dutyCalculatorApi';
import type { DutyCalculationRequest, DutyCalculationResult } from '../types';

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
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
                  <div>Total Duty: ${message.data.total_duty?.toFixed(2) || '0.00'}</div>
                  <div>GST: ${message.data.total_gst?.toFixed(2) || '0.00'}</div>
                  <div>Total Cost: ${message.data.total_amount?.toFixed(2) || '0.00'}</div>
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
    <div className="content fade-in">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              AI Customs Assistant
            </h1>
            <p className="text-lg text-gray-600">
              Expert guidance for duty calculations and customs compliance
            </p>
          </div>
          <div className="flex gap-3">
            <button className="btn btn--secondary">
              <FiSettings className="w-4 h-4" />
              Settings
            </button>
            <button className="btn btn--primary">
              <FiDownload className="w-4 h-4" />
              Export Chat
            </button>
          </div>
        </div>
      </div>

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
            <div className="card h-[600px] flex flex-col">
              <div className="card__header">
                <h3 className="card__title">AI Conversation</h3>
                <p className="card__subtitle">Ask questions about customs and trade</p>
              </div>
              
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
            </div>
          )}

          {activeTab === 'calculator' && (
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Comprehensive Duty Calculator</h3>
                <p className="card__subtitle">Calculate all import taxes and duties</p>
              </div>
              <div className="card__body">
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
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <div className="text-sm text-gray-600">Customs Duty</div>
                          <div className="text-lg font-semibold">${calculationResult.total_duty?.toFixed(2) || '0.00'}</div>
                        </div>
                        <div className="p-3 bg-gray-50 rounded-lg">
                          <div className="text-sm text-gray-600">GST</div>
                          <div className="text-lg font-semibold">${calculationResult.total_gst?.toFixed(2) || '0.00'}</div>
                        </div>
                        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="text-sm text-blue-600">Total Import Cost</div>
                          <div className="text-xl font-bold text-blue-900">${calculationResult.total_amount?.toFixed(2) || '0.00'}</div>
                        </div>
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
              </div>
            </div>
          )}

          {activeTab === 'tools' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card">
                  <div className="card__header">
                    <h3 className="card__title flex items-center gap-2">
                      <FiImage className="w-5 h-5 text-blue-500" />
                      Image Classification
                    </h3>
                    <p className="card__subtitle">Upload product images for HS code suggestions</p>
                  </div>
                  <div className="card__body">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <FiImage className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600 mb-2">Drop image here or click to upload</p>
                      <button className="btn btn--secondary btn--sm">
                        Choose File
                      </button>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <div className="card__header">
                    <h3 className="card__title flex items-center gap-2">
                      <FiFileText className="w-5 h-5 text-green-500" />
                      Document Analysis
                    </h3>
                    <p className="card__subtitle">Analyze invoices and shipping documents</p>
                  </div>
                  <div className="card__body">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <FiFileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600 mb-2">Upload PDF or image documents</p>
                      <button className="btn btn--secondary btn--sm">
                        Choose File
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card__header">
                  <h3 className="card__title">Quick Actions</h3>
                </div>
                <div className="card__body">
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
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="card">
            <div className="card__header">
              <h3 className="card__title">Session Stats</h3>
            </div>
            <div className="card__body">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Messages</span>
                  <span className="font-medium">{messages.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Calculations</span>
                  <span className="font-medium">
                    {messages.filter(m => m.type === 'calculation').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Files Analyzed</span>
                  <span className="font-medium">
                    {messages.filter(m => m.type === 'document').length}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Calculations */}
          <div className="card">
            <div className="card__header">
              <h3 className="card__title">Recent Calculations</h3>
            </div>
            <div className="card__body">
              <div className="text-center py-6">
                <FiClock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No recent calculations</p>
              </div>
            </div>
          </div>

          {/* Saved Queries */}
          <div className="card">
            <div className="card__header">
              <h3 className="card__title">Saved Queries</h3>
            </div>
            <div className="card__body">
              <div className="text-center py-6">
                <FiBookmark className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No saved queries</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
