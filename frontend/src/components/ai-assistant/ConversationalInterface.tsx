import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import { 
  Send, 
  Paperclip, 
  Image, 
  Download, 
  Copy, 
  Bot, 
  User, 
  Loader2,
  FileText,
  Camera,
  MessageSquare
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: Attachment[];
  context?: ConversationContext;
}

interface Attachment {
  id: string;
  type: 'image' | 'document';
  name: string;
  url: string;
  size: number;
}

interface ConversationContext {
  hs_codes?: string[];
  calculations?: any[];
  referenced_documents?: string[];
}

interface ConversationalInterfaceProps {
  className?: string;
  onCodeReference?: (code: string) => void;
  initialContext?: ConversationContext;
}

export const ConversationalInterface: React.FC<ConversationalInterfaceProps> = ({
  className = '',
  onCodeReference,
  initialContext
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<File[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Initialize conversation
    initializeConversation();
    
    // Add welcome message
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'assistant',
      content: `Hello! I'm your AI customs assistant. I can help you with:

• **Tariff Classification** - Identify correct HS codes for your products
• **Duty Calculations** - Calculate import duties, taxes, and fees
• **Document Analysis** - Review commercial invoices and shipping documents
• **Image Recognition** - Classify products from photos
• **Compliance Questions** - Answer customs and trade regulations

What would you like assistance with today?`,
      timestamp: new Date(),
      context: initialContext
    };
    
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeConversation = async () => {
    try {
      const response = await fetch('/api/ai/conversation/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context: initialContext })
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversationId(data.conversation_id);
      }
    } catch (error) {
      console.error('Failed to initialize conversation:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() && attachments.length === 0) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: currentMessage,
      timestamp: new Date(),
      attachments: attachments.map(file => ({
        id: `att-${Date.now()}-${file.name}`,
        type: file.type.startsWith('image/') ? 'image' : 'document',
        name: file.name,
        url: URL.createObjectURL(file),
        size: file.size
      }))
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setAttachments([]);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', currentMessage);
      formData.append('conversation_id', conversationId || '');
      
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });

      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          type: 'assistant',
          content: data.response,
          timestamp: new Date(),
          context: data.context
        };

        setMessages(prev => [...prev, assistantMessage]);
        
        // Handle any code references
        if (data.context?.hs_codes) {
          data.context.hs_codes.forEach((code: string) => {
            onCodeReference?.(code);
          });
        }
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = (files: FileList | null) => {
    if (!files) return;
    
    const newFiles = Array.from(files).filter(file => {
      // Limit file size to 10MB
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      return true;
    });
    
    setAttachments(prev => [...prev, ...newFiles]);
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const exportConversation = async (format: 'pdf' | 'txt' | 'json') => {
    if (!conversationId) return;
    
    try {
      const response = await fetch(
        `/api/ai/conversation/${conversationId}/export?format=${format}`
      );
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation-${conversationId}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to export conversation:', error);
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <Bot className="h-4 w-4 text-primary" />
          </div>
        )}
        
        <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
          <div
            className={`p-3 rounded-lg ${
              isUser 
                ? 'bg-primary text-primary-foreground ml-auto' 
                : 'bg-muted'
            }`}
          >
            <div className="prose prose-sm max-w-none">
              {message.content.split('\n').map((line, index) => (
                <p key={index} className="mb-2 last:mb-0">
                  {line}
                </p>
              ))}
            </div>
            
            {/* Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <div className="mt-2 space-y-2">
                {message.attachments.map((attachment) => (
                  <div key={attachment.id} className="flex items-center gap-2 p-2 bg-background/50 rounded">
                    {attachment.type === 'image' ? (
                      <Image className="h-4 w-4" />
                    ) : (
                      <FileText className="h-4 w-4" />
                    )}
                    <span className="text-xs">{attachment.name}</span>
                    <span className="text-xs text-muted-foreground">
                      ({Math.round(attachment.size / 1024)}KB)
                    </span>
                  </div>
                ))}
              </div>
            )}
            
            {/* Context References */}
            {message.context?.hs_codes && message.context.hs_codes.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {message.context.hs_codes.map((code) => (
                  <Badge 
                    key={code} 
                    variant="secondary" 
                    className="text-xs cursor-pointer"
                    onClick={() => onCodeReference?.(code)}
                  >
                    {code}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted-foreground">
              {message.timestamp.toLocaleTimeString()}
            </span>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => copyMessage(message.content)}
            >
              <Copy className="h-3 w-3" />
            </Button>
          </div>
        </div>
        
        {isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
            <User className="h-4 w-4" />
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className={`flex flex-col h-full ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            AI Customs Assistant
          </CardTitle>
          
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportConversation('pdf')}
              disabled={messages.length <= 1}
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map(renderMessage)}
            
            {isLoading && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-muted p-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t p-4 space-y-3">
          {/* Attachments Preview */}
          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {attachments.map((file, index) => (
                <div key={index} className="flex items-center gap-2 bg-muted p-2 rounded text-sm">
                  {file.type.startsWith('image/') ? (
                    <Image className="h-4 w-4" />
                  ) : (
                    <FileText className="h-4 w-4" />
                  )}
                  <span>{file.name}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0"
                    onClick={() => removeAttachment(index)}
                  >
                    ×
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Input Row */}
          <div className="flex gap-2">
            <div className="flex gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
              >
                <Paperclip className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => imageInputRef.current?.click()}
                disabled={isLoading}
              >
                <Camera className="h-4 w-4" />
              </Button>
            </div>

            <Textarea
              placeholder="Ask about tariff classification, duty calculations, or upload documents for analysis..."
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              className="flex-1 min-h-[40px] max-h-[120px] resize-none"
            />

            <Button
              onClick={sendMessage}
              disabled={isLoading || (!currentMessage.trim() && attachments.length === 0)}
              size="sm"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>

          {/* Hidden File Inputs */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.csv,.xlsx"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
          
          <input
            ref={imageInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default ConversationalInterface;
