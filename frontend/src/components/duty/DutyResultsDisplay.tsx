import React from 'react';
import { FiDownload, FiFileText, FiInfo, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { Button } from '../common/Button';
import type { DutyCalculationResult, DutyComponent } from '../../types';
import { formatCurrency, formatPercentage } from '../../utils';

interface DutyResultsDisplayProps {
  results: DutyCalculationResult;
  onExportPDF?: () => void;
  onExportCSV?: () => void;
  onPrint?: () => void;
}

export const DutyResultsDisplay: React.FC<DutyResultsDisplayProps> = ({
  results,
  onExportPDF,
  onExportCSV,
  onPrint,
}) => {
  const totalDutyAmount = results.components?.reduce((sum: number, component: DutyComponent) => sum + component.amount, 0) || 0;
  const totalDutyRate = results.customs_value > 0 ? (totalDutyAmount / results.customs_value) * 100 : 0;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 print:shadow-none">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 print:mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Duty Calculation Results</h2>
          <p className="text-sm text-gray-500 mt-1">
            Calculated on {new Date().toLocaleDateString('en-AU')}
          </p>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center space-x-2 print:hidden">
          {onExportPDF && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExportPDF}
              className="text-xs"
            >
              <FiDownload className="mr-1" />
              PDF
            </Button>
          )}
          {onExportCSV && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExportCSV}
              className="text-xs"
            >
              <FiDownload className="mr-1" />
              CSV
            </Button>
          )}
          {onPrint && (
            <Button
              variant="outline"
              size="sm"
              onClick={onPrint}
              className="text-xs"
            >
              <FiFileText className="mr-1" />
              Print
            </Button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Total Duty */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-primary-600">Total Duty</p>
              <p className="text-2xl font-bold text-primary-900">
                {formatCurrency(totalDutyAmount)}
              </p>
              <p className="text-sm text-primary-600">
                {formatPercentage(totalDutyRate)} of customs value
              </p>
            </div>
            <FiCheckCircle className="h-8 w-8 text-primary-500" />
          </div>
        </div>

        {/* Customs Value */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Customs Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(results.customs_value)}
              </p>
              <p className="text-sm text-gray-600">
                Quantity: 1
              </p>
            </div>
            <FiInfo className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        {/* Total Landed Cost */}
        <div className="bg-secondary-50 border border-secondary-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-secondary-600">Total Landed Cost</p>
              <p className="text-2xl font-bold text-secondary-900">
                {formatCurrency(results.customs_value + totalDutyAmount)}
              </p>
              <p className="text-sm text-secondary-600">
                Including all duties
              </p>
            </div>
            <FiAlertCircle className="h-8 w-8 text-secondary-500" />
          </div>
        </div>
      </div>

      {/* Product Information */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Product Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-600">HS Code</p>
            <p className="text-base text-gray-900 font-mono">{results.hs_code}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Country of Origin</p>
            <p className="text-base text-gray-900">{results.country_code}</p>
          </div>
          {/* Description field removed as it's not part of DutyCalculationResult type */}
        </div>
      </div>

      {/* Duty Breakdown */}
      {results.components && results.components.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Duty Breakdown</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duty Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Basis
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.components.map((component: DutyComponent, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {component.duty_type}
                        </div>
                        {component.description && (
                          <div className="text-sm text-gray-500">
                            {component.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatPercentage(component.rate)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(component.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {component.basis || 'Customs Value'}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                    Total
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                    {formatPercentage(totalDutyRate)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                    {formatCurrency(totalDutyAmount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}

      {/* Additional Information */}
      {/* Additional Information section removed as tco_eligible and fta_applied are not part of DutyCalculationResult type */}

      {/* Calculation Notes */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-yellow-900 mb-3">Important Notes</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• These calculations are estimates based on current tariff rates</li>
          <li>• Actual duties may vary depending on specific product characteristics</li>
          <li>• Additional charges such as GST, quarantine fees, and broker charges may apply</li>
          <li>• Consult with a licensed customs broker for official duty calculations</li>
          <li>• Rates are subject to change without notice</li>
        </ul>
      </div>

      {/* Print Styles */}
      <style>{`
        @media print {
          .print\\:shadow-none {
            box-shadow: none !important;
          }
          .print\\:hidden {
            display: none !important;
          }
          .print\\:mb-4 {
            margin-bottom: 1rem !important;
          }
        }
      `}</style>
    </div>
  );
};

export default DutyResultsDisplay;