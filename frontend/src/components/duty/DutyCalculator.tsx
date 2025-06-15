import React from 'react';
import { Button, Input } from '../common';

interface DutyCalculatorProps {
  className?: string;
}

export const DutyCalculator: React.FC<DutyCalculatorProps> = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-primary mb-6">Duty Calculator</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Input
          label="HS Code"
          placeholder="e.g., 8471.30.00"
          required
        />
        
        <Input
          label="Country of Origin"
          placeholder="e.g., China"
          required
        />
        
        <Input
          label="Customs Value (AUD)"
          type="number"
          placeholder="0.00"
          required
        />
        
        <Input
          label="Quantity"
          type="number"
          placeholder="1"
          required
        />
      </div>
      
      <div className="flex justify-end">
        <Button variant="primary">
          Calculate Duty
        </Button>
      </div>
      
      {/* Results will be displayed here */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Calculation Results</h3>
        <p className="text-gray-600">Enter values above to calculate duties and taxes.</p>
      </div>
    </div>
  );
};