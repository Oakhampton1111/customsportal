import React from 'react';
import { FiInfo, FiPercent, FiGlobe, FiTruck } from 'react-icons/fi';

interface TariffData {
  hsCode: string;
  description: string;
  generalRate: number;
  unit: string;
  ftaRates?: { [country: string]: number };
  specialConditions?: string[];
  lastUpdated?: string;
}

interface TariffDisplayProps {
  tariff?: TariffData;
  loading?: boolean;
  error?: string;
  className?: string;
}

export const TariffDisplay: React.FC<TariffDisplayProps> = ({
  tariff,
  loading = false,
  error,
  className = ''
}) => {
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-4"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center text-red-600">
          <FiInfo className="mx-auto mb-2 text-2xl" />
          <p className="font-medium">Error Loading Tariff</p>
          <p className="text-sm text-gray-600 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!tariff) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <FiInfo className="mx-auto mb-2 text-2xl" />
          <p>Select an HS code to view tariff details</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold text-primary">{tariff.hsCode}</h2>
          {tariff.lastUpdated && (
            <span className="text-sm text-gray-500">
              Updated: {new Date(tariff.lastUpdated).toLocaleDateString()}
            </span>
          )}
        </div>
        <p className="text-gray-800 text-lg mb-2">{tariff.description}</p>
        <div className="flex items-center text-gray-600">
          <FiTruck className="mr-1" />
          <span className="text-sm">Unit: {tariff.unit}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* General Rate */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <FiPercent className="mr-2 text-primary" />
            <h3 className="font-semibold text-gray-800">General Rate</h3>
          </div>
          <div className="text-3xl font-bold text-primary">
            {tariff.generalRate}%
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Standard duty rate for all countries
          </p>
        </div>

        {/* Best FTA Rate */}
        {tariff.ftaRates && Object.keys(tariff.ftaRates).length > 0 && (
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <FiGlobe className="mr-2 text-green-600" />
              <h3 className="font-semibold text-gray-800">Best FTA Rate</h3>
            </div>
            <div className="text-3xl font-bold text-green-600">
              {Math.min(...Object.values(tariff.ftaRates))}%
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Lowest available preferential rate
            </p>
          </div>
        )}
      </div>

      {/* FTA Rates Table */}
      {tariff.ftaRates && Object.keys(tariff.ftaRates).length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            Free Trade Agreement Rates
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-200">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border border-gray-200 px-4 py-2 text-left font-medium text-gray-700">
                    Country/Agreement
                  </th>
                  <th className="border border-gray-200 px-4 py-2 text-left font-medium text-gray-700">
                    Rate
                  </th>
                  <th className="border border-gray-200 px-4 py-2 text-left font-medium text-gray-700">
                    Savings
                  </th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(tariff.ftaRates)
                  .sort(([,a], [,b]) => a - b)
                  .map(([country, rate]) => (
                    <tr key={country} className="hover:bg-gray-50">
                      <td className="border border-gray-200 px-4 py-2">{country}</td>
                      <td className="border border-gray-200 px-4 py-2 font-medium">
                        {rate}%
                      </td>
                      <td className="border border-gray-200 px-4 py-2 text-green-600 font-medium">
                        {Math.max(0, tariff.generalRate - rate)}%
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Special Conditions */}
      {tariff.specialConditions && tariff.specialConditions.length > 0 && (
        <div className="bg-yellow-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-2">Special Conditions</h3>
          <ul className="list-disc list-inside space-y-1">
            {tariff.specialConditions.map((condition, index) => (
              <li key={index} className="text-sm text-gray-700">
                {condition}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};