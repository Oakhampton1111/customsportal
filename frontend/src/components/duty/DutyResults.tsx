import React from 'react';
import { FiInfo, FiDollarSign, FiPercent } from 'react-icons/fi';

interface DutyComponent {
  type: string;
  rate: number;
  amount: number;
  description: string;
}

interface DutyResultsProps {
  hsCode?: string;
  countryCode?: string;
  customsValue?: number;
  components?: DutyComponent[];
  totalDuty?: number;
  totalGst?: number;
  grandTotal?: number;
  className?: string;
}

export const DutyResults: React.FC<DutyResultsProps> = ({
  hsCode,
  countryCode,
  customsValue,
  components = [],
  totalDuty = 0,
  totalGst = 0,
  grandTotal = 0,
  className = ''
}) => {
  if (!hsCode) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <FiInfo className="mx-auto mb-2 text-2xl" />
          <p>Enter calculation details to see duty breakdown</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-xl font-bold text-primary mb-4">Duty Calculation Results</h3>
      
      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">HS Code:</span>
            <span className="ml-2 font-medium">{hsCode}</span>
          </div>
          <div>
            <span className="text-gray-600">Country:</span>
            <span className="ml-2 font-medium">{countryCode}</span>
          </div>
          <div>
            <span className="text-gray-600">Customs Value:</span>
            <span className="ml-2 font-medium">AUD ${customsValue?.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Duty Components */}
      {components.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-3">Duty Breakdown</h4>
          <div className="space-y-2">
            {components.map((component, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200">
                <div>
                  <span className="font-medium text-gray-800">{component.type}</span>
                  <p className="text-sm text-gray-600">{component.description}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center text-gray-700">
                    <FiPercent className="mr-1 text-sm" />
                    <span className="text-sm">{component.rate}%</span>
                  </div>
                  <div className="flex items-center font-medium">
                    <FiDollarSign className="mr-1 text-sm" />
                    <span>AUD {component.amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Totals */}
      <div className="border-t border-gray-200 pt-4">
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-gray-700">Total Duty:</span>
            <span className="font-medium">AUD {totalDuty.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-700">GST (10%):</span>
            <span className="font-medium">AUD {totalGst.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center text-lg font-bold text-primary border-t border-gray-200 pt-2">
            <span>Grand Total:</span>
            <span>AUD {grandTotal.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};