import React, { useState, useMemo } from 'react';
import { FiChevronDown, FiSearch, FiCheck } from 'react-icons/fi';

// Country data with major trading partners
const countries = [
  { code: 'AU', name: 'Australia', flag: '🇦🇺', ftaStatus: 'domestic' },
  { code: 'CN', name: 'China', flag: '🇨🇳', ftaStatus: 'fta' },
  { code: 'US', name: 'United States', flag: '🇺🇸', ftaStatus: 'fta' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵', ftaStatus: 'fta' },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷', ftaStatus: 'fta' },
  { code: 'NZ', name: 'New Zealand', flag: '🇳🇿', ftaStatus: 'fta' },
  { code: 'SG', name: 'Singapore', flag: '🇸🇬', ftaStatus: 'fta' },
  { code: 'TH', name: 'Thailand', flag: '🇹🇭', ftaStatus: 'fta' },
  { code: 'MY', name: 'Malaysia', flag: '🇲🇾', ftaStatus: 'fta' },
  { code: 'VN', name: 'Vietnam', flag: '🇻🇳', ftaStatus: 'fta' },
  { code: 'ID', name: 'Indonesia', flag: '🇮🇩', ftaStatus: 'fta' },
  { code: 'PH', name: 'Philippines', flag: '🇵🇭', ftaStatus: 'fta' },
  { code: 'IN', name: 'India', flag: '🇮🇳', ftaStatus: 'fta' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧', ftaStatus: 'fta' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪', ftaStatus: 'general' },
  { code: 'FR', name: 'France', flag: '🇫🇷', ftaStatus: 'general' },
  { code: 'IT', name: 'Italy', flag: '🇮🇹', ftaStatus: 'general' },
  { code: 'ES', name: 'Spain', flag: '🇪🇸', ftaStatus: 'general' },
  { code: 'NL', name: 'Netherlands', flag: '🇳🇱', ftaStatus: 'general' },
  { code: 'BE', name: 'Belgium', flag: '🇧🇪', ftaStatus: 'general' },
  { code: 'CH', name: 'Switzerland', flag: '🇨🇭', ftaStatus: 'general' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦', ftaStatus: 'general' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽', ftaStatus: 'general' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷', ftaStatus: 'general' },
  { code: 'AR', name: 'Argentina', flag: '🇦🇷', ftaStatus: 'general' },
  { code: 'CL', name: 'Chile', flag: '🇨🇱', ftaStatus: 'fta' },
  { code: 'PE', name: 'Peru', flag: '🇵🇪', ftaStatus: 'fta' },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦', ftaStatus: 'general' },
  { code: 'EG', name: 'Egypt', flag: '🇪🇬', ftaStatus: 'general' },
  { code: 'TR', name: 'Turkey', flag: '🇹🇷', ftaStatus: 'general' },
  { code: 'RU', name: 'Russia', flag: '🇷🇺', ftaStatus: 'general' },
  { code: 'UA', name: 'Ukraine', flag: '🇺🇦', ftaStatus: 'general' },
  { code: 'IL', name: 'Israel', flag: '🇮🇱', ftaStatus: 'general' },
  { code: 'AE', name: 'United Arab Emirates', flag: '🇦🇪', ftaStatus: 'general' },
  { code: 'SA', name: 'Saudi Arabia', flag: '🇸🇦', ftaStatus: 'general' },
  { code: 'PK', name: 'Pakistan', flag: '🇵🇰', ftaStatus: 'general' },
  { code: 'BD', name: 'Bangladesh', flag: '🇧🇩', ftaStatus: 'general' },
  { code: 'LK', name: 'Sri Lanka', flag: '🇱🇰', ftaStatus: 'general' },
  { code: 'MM', name: 'Myanmar', flag: '🇲🇲', ftaStatus: 'general' },
  { code: 'KH', name: 'Cambodia', flag: '🇰🇭', ftaStatus: 'general' },
  { code: 'LA', name: 'Laos', flag: '🇱🇦', ftaStatus: 'general' },
  { code: 'BN', name: 'Brunei', flag: '🇧🇳', ftaStatus: 'fta' },
  { code: 'FJ', name: 'Fiji', flag: '🇫🇯', ftaStatus: 'fta' },
  { code: 'PG', name: 'Papua New Guinea', flag: '🇵🇬', ftaStatus: 'fta' },
  { code: 'NC', name: 'New Caledonia', flag: '🇳🇨', ftaStatus: 'general' },
  { code: 'PF', name: 'French Polynesia', flag: '🇵🇫', ftaStatus: 'general' },
];

interface CountrySelectorProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export const CountrySelector: React.FC<CountrySelectorProps> = ({
  value,
  onChange,
  error,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [recentSelections, setRecentSelections] = useState<string[]>(() => {
    const stored = localStorage.getItem('recentCountrySelections');
    return stored ? JSON.parse(stored) : ['CN', 'US', 'JP', 'KR', 'NZ'];
  });

  // Filter countries based on search term
  const filteredCountries = useMemo(() => {
    if (!searchTerm) return countries;
    return countries.filter(country =>
      country.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      country.code.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm]);

  // Get recent countries
  const recentCountries = useMemo(() => {
    return recentSelections
      .map(code => countries.find(c => c.code === code))
      .filter(Boolean) as typeof countries;
  }, [recentSelections]);

  // Get FTA countries
  const ftaCountries = useMemo(() => {
    return countries.filter(country => country.ftaStatus === 'fta');
  }, []);

  const selectedCountry = countries.find(c => c.code === value);

  const handleSelect = (countryCode: string) => {
    onChange(countryCode);
    setIsOpen(false);
    setSearchTerm('');

    // Update recent selections
    const newRecent = [countryCode, ...recentSelections.filter(c => c !== countryCode)].slice(0, 5);
    setRecentSelections(newRecent);
    localStorage.setItem('recentCountrySelections', JSON.stringify(newRecent));
  };

  const getFtaStatusBadge = (status: string) => {
    switch (status) {
      case 'fta':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
            FTA
          </span>
        );
      case 'domestic':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
            Domestic
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
            General
          </span>
        );
    }
  };

  const CountryOption: React.FC<{ country: typeof countries[0]; isSelected: boolean }> = ({
    country,
    isSelected,
  }) => (
    <div
      onClick={() => handleSelect(country.code)}
      className={`flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-gray-50 ${
        isSelected ? 'bg-primary-50 text-primary-900' : ''
      }`}
    >
      <div className="flex items-center space-x-3">
        <span className="text-lg">{country.flag}</span>
        <div>
          <div className="font-medium text-sm">{country.name}</div>
          <div className="text-xs text-gray-500">{country.code}</div>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        {getFtaStatusBadge(country.ftaStatus)}
        {isSelected && <FiCheck className="text-primary-600" />}
      </div>
    </div>
  );

  return (
    <div className="relative">
      {/* Selected Value Display */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full flex items-center justify-between px-3 py-2 border rounded-md shadow-sm bg-white text-left focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
          error
            ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
            : 'border-gray-300'
        } ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <div className="flex items-center space-x-3">
          {selectedCountry ? (
            <>
              <span className="text-lg">{selectedCountry.flag}</span>
              <div>
                <div className="font-medium text-sm">{selectedCountry.name}</div>
                <div className="text-xs text-gray-500">{selectedCountry.code}</div>
              </div>
            </>
          ) : (
            <span className="text-gray-500">Select a country...</span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {selectedCountry && getFtaStatusBadge(selectedCountry.ftaStatus)}
          <FiChevronDown
            className={`h-4 w-4 text-gray-400 transition-transform ${
              isOpen ? 'transform rotate-180' : ''
            }`}
          />
        </div>
      </button>

      {/* Error Message */}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-96 overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search countries..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {/* Recent Selections */}
            {!searchTerm && recentCountries.length > 0 && (
              <div>
                <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-200">
                  Recent Selections
                </div>
                {recentCountries.map((country) => (
                  <CountryOption
                    key={`recent-${country.code}`}
                    country={country}
                    isSelected={country.code === value}
                  />
                ))}
              </div>
            )}

            {/* FTA Countries */}
            {!searchTerm && (
              <div>
                <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-200">
                  FTA Partners
                </div>
                {ftaCountries.map((country) => (
                  <CountryOption
                    key={`fta-${country.code}`}
                    country={country}
                    isSelected={country.code === value}
                  />
                ))}
              </div>
            )}

            {/* All Countries (when searching) */}
            {searchTerm && (
              <div>
                <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-200">
                  Search Results ({filteredCountries.length})
                </div>
                {filteredCountries.length > 0 ? (
                  filteredCountries.map((country) => (
                    <CountryOption
                      key={`search-${country.code}`}
                      country={country}
                      isSelected={country.code === value}
                    />
                  ))
                ) : (
                  <div className="px-3 py-4 text-sm text-gray-500 text-center">
                    No countries found matching "{searchTerm}"
                  </div>
                )}
              </div>
            )}

            {/* All Countries (when not searching) */}
            {!searchTerm && (
              <div>
                <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-200">
                  All Countries
                </div>
                {countries.map((country) => (
                  <CountryOption
                    key={`all-${country.code}`}
                    country={country}
                    isSelected={country.code === value}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default CountrySelector;