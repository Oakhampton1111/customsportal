import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Alert } from '../ui/Alert';
import { aiApi } from '../../services/aiApi';
import { FiDollarSign, FiEdit3, FiSave, FiPlus, FiTrash2 } from 'react-icons/fi';

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

interface DutyCalculationPanelProps {
  document: DocumentProcessing;
}

interface DutyItem {
  hs_code: string;
  description: string;
  quantity: number;
  unit_value: number;
  country_of_origin: string;
}

interface DutyCalculation {
  total_customs_value: number;
  total_duty: number;
  total_gst: number;
  total_charges: number;
  item_breakdown: Array<{
    item_number: number;
    customs_value: number;
    duty_rate: number;
    duty_amount: number;
    gst_rate: number;
    gst_amount: number;
    total_item_charges: number;
    applicable_concessions: string[];
  }>;
}

export const DutyCalculationPanel: React.FC<DutyCalculationPanelProps> = ({
  document
}) => {
  const [items, setItems] = useState<DutyItem[]>([]);
  const [calculation, setCalculation] = useState<DutyCalculation | null>(null);
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  useEffect(() => {
    loadExtractedItems();
  }, [document.id]);

  const loadExtractedItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const processingDetails = await aiApi.getDocumentProcessing(document.id);
      
      // Extract items from the processed data
      const extractedFields = processingDetails.extracted_fields || {};
      const defaultItems: DutyItem[] = [];
      
      // Try to parse items from various field formats
      if (extractedFields.items && Array.isArray(extractedFields.items)) {
        defaultItems.push(...extractedFields.items);
      } else {
        // Create a single item from extracted fields
        defaultItems.push({
          hs_code: extractedFields.hs_code || '',
          description: extractedFields.description || extractedFields.product_description || '',
          quantity: Number(extractedFields.quantity) || 1,
          unit_value: Number(extractedFields.unit_value) || Number(extractedFields.value) || 0,
          country_of_origin: extractedFields.country_of_origin || extractedFields.origin_country || ''
        });
      }
      
      setItems(defaultItems.filter(item => item.hs_code || item.description));
    } catch (err) {
      setError('Failed to load extracted items');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateDuties = async () => {
    if (items.length === 0) {
      setError('Please add at least one item to calculate duties');
      return;
    }

    try {
      setCalculating(true);
      setError(null);
      const result = await aiApi.calculateDuties(items);
      setCalculation(result);
    } catch (err) {
      setError('Failed to calculate duties');
      console.error('Calculation error:', err);
    } finally {
      setCalculating(false);
    }
  };

  const addItem = () => {
    setItems([...items, {
      hs_code: '',
      description: '',
      quantity: 1,
      unit_value: 0,
      country_of_origin: ''
    }]);
    setEditingIndex(items.length);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
    if (editingIndex === index) {
      setEditingIndex(null);
    }
  };

  const updateItem = (index: number, field: keyof DutyItem, value: any) => {
    const updatedItems = [...items];
    updatedItems[index] = {
      ...updatedItems[index],
      [field]: field === 'quantity' || field === 'unit_value' ? Number(value) : value
    };
    setItems(updatedItems);
  };

  const saveItem = (index: number) => {
    setEditingIndex(null);
    // Recalculate if we have a previous calculation
    if (calculation) {
      calculateDuties();
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD'
    }).format(amount);
  };

  const renderItemRow = (item: DutyItem, index: number) => {
    const isEditing = editingIndex === index;
    
    return (
      <tr key={index} className={`border-b ${isEditing ? 'bg-blue-50' : 'hover:bg-gray-50'}`}>
        <td className="p-3">
          {isEditing ? (
            <Input
              value={item.hs_code}
              onChange={(e) => updateItem(index, 'hs_code', e.target.value)}
              placeholder="HS Code"
              className="w-full"
            />
          ) : (
            <span className="font-mono">{item.hs_code}</span>
          )}
        </td>
        
        <td className="p-3">
          {isEditing ? (
            <Input
              value={item.description}
              onChange={(e) => updateItem(index, 'description', e.target.value)}
              placeholder="Description"
              className="w-full"
            />
          ) : (
            <span className="max-w-xs truncate block" title={item.description}>
              {item.description}
            </span>
          )}
        </td>
        
        <td className="p-3">
          {isEditing ? (
            <Input
              type="number"
              value={item.quantity}
              onChange={(e) => updateItem(index, 'quantity', e.target.value)}
              placeholder="Qty"
              className="w-20"
              min="1"
            />
          ) : (
            <span>{item.quantity}</span>
          )}
        </td>
        
        <td className="p-3">
          {isEditing ? (
            <Input
              type="number"
              value={item.unit_value}
              onChange={(e) => updateItem(index, 'unit_value', e.target.value)}
              placeholder="0.00"
              className="w-24"
              min="0"
              step="0.01"
            />
          ) : (
            <span>{formatCurrency(item.unit_value)}</span>
          )}
        </td>
        
        <td className="p-3">
          {isEditing ? (
            <Input
              value={item.country_of_origin}
              onChange={(e) => updateItem(index, 'country_of_origin', e.target.value)}
              placeholder="Country"
              className="w-full"
            />
          ) : (
            <span>{item.country_of_origin}</span>
          )}
        </td>
        
        <td className="p-3">
          <span className="font-semibold">
            {formatCurrency(item.quantity * item.unit_value)}
          </span>
        </td>
        
        <td className="p-3">
          <div className="flex space-x-1">
            {isEditing ? (
              <Button
                onClick={() => saveItem(index)}
                size="sm"
                className="flex items-center space-x-1"
              >
                <FiSave className="h-3 w-3" />
                <span>Save</span>
              </Button>
            ) : (
              <Button
                onClick={() => setEditingIndex(index)}
                variant="outline"
                size="sm"
                className="flex items-center space-x-1"
              >
                <FiEdit3 className="h-3 w-3" />
                <span>Edit</span>
              </Button>
            )}
            
            <Button
              onClick={() => removeItem(index)}
              variant="outline"
              size="sm"
              className="text-red-600 hover:text-red-700"
            >
              <FiTrash2 className="h-3 w-3" />
            </Button>
          </div>
        </td>
      </tr>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Duty Calculation</h2>
          <p className="text-gray-600 mt-1">Calculate customs duties, taxes, and charges</p>
        </div>
        
        <div className="flex space-x-2">
          <Button onClick={addItem} variant="outline" className="flex items-center space-x-2">
            <FiPlus className="h-4 w-4" />
            <span>Add Item</span>
          </Button>
          
          <Button 
            onClick={calculateDuties} 
            disabled={calculating || items.length === 0}
            className="flex items-center space-x-2"
          >
            {calculating ? <LoadingSpinner size="sm" /> : <FiDollarSign className="h-4 w-4" />}
            <span>Calculate Duties</span>
          </Button>
        </div>
      </div>

      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}

      {/* Items Table */}
      <Card className="p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Items for Duty Calculation</h3>
        
        {items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left p-3 font-medium">HS Code</th>
                  <th className="text-left p-3 font-medium">Description</th>
                  <th className="text-left p-3 font-medium">Qty</th>
                  <th className="text-left p-3 font-medium">Unit Value</th>
                  <th className="text-left p-3 font-medium">Origin</th>
                  <th className="text-left p-3 font-medium">Total Value</th>
                  <th className="text-left p-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => renderItemRow(item, index))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <FiDollarSign className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No items added yet. Click "Add Item" to start calculating duties.</p>
          </div>
        )}
      </Card>

      {/* Calculation Results */}
      {calculation && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(calculation.total_customs_value)}
              </div>
              <div className="text-sm text-gray-600">Customs Value</div>
            </Card>
            
            <Card className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(calculation.total_duty)}
              </div>
              <div className="text-sm text-gray-600">Total Duty</div>
            </Card>
            
            <Card className="p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(calculation.total_gst)}
              </div>
              <div className="text-sm text-gray-600">GST</div>
            </Card>
            
            <Card className="p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {formatCurrency(calculation.total_charges)}
              </div>
              <div className="text-sm text-gray-600">Total Charges</div>
            </Card>
          </div>

          {/* Detailed Breakdown */}
          <Card className="p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Breakdown</h3>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-3">Item</th>
                    <th className="text-right p-3">Customs Value</th>
                    <th className="text-right p-3">Duty Rate</th>
                    <th className="text-right p-3">Duty Amount</th>
                    <th className="text-right p-3">GST Rate</th>
                    <th className="text-right p-3">GST Amount</th>
                    <th className="text-right p-3">Total Charges</th>
                    <th className="text-left p-3">Concessions</th>
                  </tr>
                </thead>
                <tbody>
                  {calculation.item_breakdown.map((breakdown, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-3">Item {breakdown.item_number}</td>
                      <td className="p-3 text-right">{formatCurrency(breakdown.customs_value)}</td>
                      <td className="p-3 text-right">{(breakdown.duty_rate * 100).toFixed(1)}%</td>
                      <td className="p-3 text-right">{formatCurrency(breakdown.duty_amount)}</td>
                      <td className="p-3 text-right">{(breakdown.gst_rate * 100).toFixed(1)}%</td>
                      <td className="p-3 text-right">{formatCurrency(breakdown.gst_amount)}</td>
                      <td className="p-3 text-right font-semibold">{formatCurrency(breakdown.total_item_charges)}</td>
                      <td className="p-3">
                        {breakdown.applicable_concessions.length > 0 ? (
                          <div className="space-y-1">
                            {breakdown.applicable_concessions.map((concession, concessionIndex) => (
                              <Badge key={concessionIndex} className="bg-green-100 text-green-800 text-xs">
                                {concession}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-400">None</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* No Calculation State */}
      {!calculation && !calculating && items.length > 0 && (
        <Card className="p-8 text-center">
          <FiDollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Calculate</h3>
          <p className="text-gray-600">
            Click "Calculate Duties" to compute customs duties, taxes, and charges for the items above.
          </p>
        </Card>
      )}
    </div>
  );
};