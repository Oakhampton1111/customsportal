import React from 'react';
import { FiSearch, FiFilter } from 'react-icons/fi';
import { Button, Input } from '../common';

interface SearchFormProps {
  onSearch?: (query: string, filters: SearchFilters) => void;
  loading?: boolean;
  className?: string;
}

interface SearchFilters {
  searchType: 'hs_code' | 'description' | 'all';
  category?: string;
  minRate?: number;
  maxRate?: number;
}

export const SearchForm: React.FC<SearchFormProps> = ({
  onSearch,
  loading = false,
  className = ''
}) => {
  const [query, setQuery] = React.useState('');
  const [showFilters, setShowFilters] = React.useState(false);
  const [filters, setFilters] = React.useState<SearchFilters>({
    searchType: 'all'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && onSearch) {
      onSearch(query.trim(), filters);
    }
  };

  const handleFilterChange = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-primary mb-6">Tariff Search</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Input
              placeholder="Search by HS code, description, or keywords..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            disabled={loading || !query.trim()}
            className="px-6"
          >
            <FiSearch className="mr-2" />
            {loading ? 'Searching...' : 'Search'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="px-4"
          >
            <FiFilter />
          </Button>
        </div>

        {showFilters && (
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-gray-800">Search Filters</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search Type
                </label>
                <select
                  value={filters.searchType}
                  onChange={(e) => handleFilterChange('searchType', e.target.value as 'hs_code' | 'description' | 'all')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="all">All Fields</option>
                  <option value="hs_code">HS Code Only</option>
                  <option value="description">Description Only</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={filters.category || ''}
                  onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                >
                  <option value="">All Categories</option>
                  <option value="electronics">Electronics</option>
                  <option value="textiles">Textiles</option>
                  <option value="machinery">Machinery</option>
                  <option value="chemicals">Chemicals</option>
                  <option value="food">Food & Agriculture</option>
                  <option value="automotive">Automotive</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Duty Rate Range (%)
                </label>
                <div className="flex gap-2">
                  <Input
                    type="number"
                    placeholder="Min"
                    value={filters.minRate || ''}
                    onChange={(e) => handleFilterChange('minRate', e.target.value ? Number(e.target.value) : undefined)}
                    className="w-20"
                  />
                  <span className="self-center text-gray-500">to</span>
                  <Input
                    type="number"
                    placeholder="Max"
                    value={filters.maxRate || ''}
                    onChange={(e) => handleFilterChange('maxRate', e.target.value ? Number(e.target.value) : undefined)}
                    className="w-20"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};