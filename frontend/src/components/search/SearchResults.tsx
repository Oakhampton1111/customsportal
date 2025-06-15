import React from 'react';
import { FiExternalLink, FiInfo, FiPercent, FiDollarSign } from 'react-icons/fi';

interface TariffItem {
  hsCode: string;
  description: string;
  generalRate: number;
  ftaRates?: { [country: string]: number };
  unit: string;
  category?: string;
}

interface SearchResultsProps {
  results?: TariffItem[];
  loading?: boolean;
  error?: string;
  query?: string;
  className?: string;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results = [],
  loading = false,
  error,
  query,
  className = ''
}) => {
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
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
          <p className="font-medium">Search Error</p>
          <p className="text-sm text-gray-600 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (results.length === 0 && query) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <FiInfo className="mx-auto mb-2 text-2xl" />
          <p className="font-medium">No Results Found</p>
          <p className="text-sm mt-1">
            No tariff items found for "{query}". Try adjusting your search terms or filters.
          </p>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 ${className}`}>
        <div className="text-center text-gray-500">
          <FiInfo className="mx-auto mb-2 text-2xl" />
          <p>Enter a search query to find tariff information</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-primary">
          Search Results
          {query && <span className="text-gray-600 font-normal"> for "{query}"</span>}
        </h3>
        <span className="text-sm text-gray-500">
          {results.length} item{results.length !== 1 ? 's' : ''} found
        </span>
      </div>

      <div className="space-y-4">
        {results.map((item, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-primary transition-colors">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-lg font-bold text-primary">
                    {item.hsCode}
                  </span>
                  {item.category && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                      {item.category}
                    </span>
                  )}
                </div>
                <p className="text-gray-800 mb-2">{item.description}</p>
                <p className="text-sm text-gray-600">Unit: {item.unit}</p>
              </div>
              <button className="text-primary hover:text-primary-dark transition-colors">
                <FiExternalLink className="text-lg" />
              </button>
            </div>

            <div className="border-t border-gray-100 pt-3">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* General Rate */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center text-gray-700 mb-1">
                    <FiPercent className="mr-1 text-sm" />
                    <span className="text-sm font-medium">General Rate</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">
                    {item.generalRate}%
                  </span>
                </div>

                {/* FTA Rates */}
                {item.ftaRates && Object.keys(item.ftaRates).length > 0 && (
                  <div className="bg-green-50 rounded-lg p-3">
                    <div className="flex items-center text-green-700 mb-1">
                      <FiDollarSign className="mr-1 text-sm" />
                      <span className="text-sm font-medium">Best FTA Rate</span>
                    </div>
                    <div className="space-y-1">
                      {Object.entries(item.ftaRates)
                        .sort(([,a], [,b]) => a - b)
                        .slice(0, 2)
                        .map(([country, rate]) => (
                          <div key={country} className="flex justify-between items-center">
                            <span className="text-xs text-green-600">{country}</span>
                            <span className="text-sm font-bold text-green-800">{rate}%</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Potential Savings */}
                {item.ftaRates && Object.keys(item.ftaRates).length > 0 && (
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="flex items-center text-blue-700 mb-1">
                      <FiDollarSign className="mr-1 text-sm" />
                      <span className="text-sm font-medium">Max Savings</span>
                    </div>
                    <span className="text-lg font-bold text-blue-900">
                      {Math.max(0, item.generalRate - Math.min(...Object.values(item.ftaRates)))}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {results.length > 10 && (
        <div className="mt-6 text-center">
          <button className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark transition-colors">
            Load More Results
          </button>
        </div>
      )}
    </div>
  );
};