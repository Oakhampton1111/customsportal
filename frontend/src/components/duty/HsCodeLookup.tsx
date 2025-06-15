import React, { useState, useEffect, useRef } from 'react';
import { FiSearch, FiX, FiClock, FiStar, FiBookOpen } from 'react-icons/fi';

interface HsCodeItem {
  code: string;
  description: string;
  level: number;
  parent?: string;
}

interface HsCodeLookupProps {
  value?: string;
  onChange: (code: string) => void;
  placeholder?: string;
  className?: string;
}

// Mock HS code data - in a real app, this would come from an API
const mockHsCodes: HsCodeItem[] = [
  { code: '8471', description: 'Automatic data processing machines and units thereof', level: 4 },
  { code: '8471.30', description: 'Portable automatic data processing machines', level: 6, parent: '8471' },
  { code: '8471.30.00', description: 'Portable automatic data processing machines, weighing not more than 10 kg', level: 8, parent: '8471.30' },
  { code: '8471.41', description: 'Comprising in the same housing at least a central processing unit and an input and output unit', level: 6, parent: '8471' },
  { code: '8471.41.00', description: 'Desktop computers and workstations', level: 8, parent: '8471.41' },
  { code: '8471.49', description: 'Other automatic data processing machines', level: 6, parent: '8471' },
  { code: '8471.49.00', description: 'Other automatic data processing machines and units thereof', level: 8, parent: '8471.49' },
  { code: '8471.50', description: 'Processing units other than those of subheadings 8471.41 and 8471.49', level: 6, parent: '8471' },
  { code: '8471.50.00', description: 'Processing units (CPUs) presented separately', level: 8, parent: '8471.50' },
  { code: '8471.60', description: 'Input or output units', level: 6, parent: '8471' },
  { code: '8471.60.10', description: 'Keyboards', level: 8, parent: '8471.60' },
  { code: '8471.60.20', description: 'Mice, trackballs and other pointing devices', level: 8, parent: '8471.60' },
  { code: '8471.60.30', description: 'Monitors and projectors', level: 8, parent: '8471.60' },
  { code: '8471.60.90', description: 'Other input or output units', level: 8, parent: '8471.60' },
  { code: '8471.70', description: 'Storage units', level: 6, parent: '8471' },
  { code: '8471.70.10', description: 'Hard disk drives', level: 8, parent: '8471.70' },
  { code: '8471.70.20', description: 'Solid-state drives (SSD)', level: 8, parent: '8471.70' },
  { code: '8471.70.90', description: 'Other storage units', level: 8, parent: '8471.70' },
  { code: '8471.80', description: 'Other units of automatic data processing machines', level: 6, parent: '8471' },
  { code: '8471.80.00', description: 'Other units of automatic data processing machines', level: 8, parent: '8471.80' },
  { code: '8471.90', description: 'Other', level: 6, parent: '8471' },
  { code: '8471.90.00', description: 'Other parts and accessories of automatic data processing machines', level: 8, parent: '8471.90' },
  { code: '8517', description: 'Telephone sets, including telephones for cellular networks', level: 4 },
  { code: '8517.12', description: 'Telephones for cellular networks or for other wireless networks', level: 6, parent: '8517' },
  { code: '8517.12.00', description: 'Mobile phones and smartphones', level: 8, parent: '8517.12' },
  { code: '8517.18', description: 'Other telephone sets and apparatus', level: 6, parent: '8517' },
  { code: '8517.18.00', description: 'Other telephone sets and apparatus for transmission', level: 8, parent: '8517.18' },
  { code: '9403', description: 'Other furniture and parts thereof', level: 4 },
  { code: '9403.10', description: 'Metal furniture of a kind used in offices', level: 6, parent: '9403' },
  { code: '9403.10.00', description: 'Metal office furniture', level: 8, parent: '9403.10' },
  { code: '9403.20', description: 'Other metal furniture', level: 6, parent: '9403' },
  { code: '9403.20.00', description: 'Other metal furniture', level: 8, parent: '9403.20' },
];

const HsCodeLookup: React.FC<HsCodeLookupProps> = ({
  value = '',
  onChange,
  placeholder = 'Search HS codes...',
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCodes, setFilteredCodes] = useState<HsCodeItem[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load saved data from localStorage
  useEffect(() => {
    const savedRecent = localStorage.getItem('hsCodeRecentSearches');
    const savedFavorites = localStorage.getItem('hsCodeFavorites');
    
    if (savedRecent) {
      setRecentSearches(JSON.parse(savedRecent));
    }
    
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Filter HS codes based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredCodes([]);
      return;
    }

    const filtered = mockHsCodes.filter(item => 
      item.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 10); // Limit to 10 results

    setFilteredCodes(filtered);
    setSelectedIndex(-1);
  }, [searchTerm]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setSearchTerm(newValue);
    onChange(newValue);
    setIsOpen(true);
  };

  // Handle HS code selection
  const handleSelectCode = (code: string) => {
    onChange(code);
    setSearchTerm(code);
    setIsOpen(false);
    
    // Add to recent searches
    const updatedRecent = [code, ...recentSearches.filter(item => item !== code)].slice(0, 5);
    setRecentSearches(updatedRecent);
    localStorage.setItem('hsCodeRecentSearches', JSON.stringify(updatedRecent));
  };

  // Toggle favorite
  const toggleFavorite = (code: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    const updatedFavorites = favorites.includes(code)
      ? favorites.filter(item => item !== code)
      : [...favorites, code];
    
    setFavorites(updatedFavorites);
    localStorage.setItem('hsCodeFavorites', JSON.stringify(updatedFavorites));
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < filteredCodes.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && filteredCodes[selectedIndex]) {
          handleSelectCode(filteredCodes[selectedIndex].code);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Format HS code with dots
  const formatHsCode = (code: string) => {
    if (code.length <= 4) return code;
    if (code.length <= 6) return `${code.slice(0, 4)}.${code.slice(4)}`;
    return `${code.slice(0, 4)}.${code.slice(4, 6)}.${code.slice(6)}`;
  };

  // Get level indicator
  const getLevelIndicator = (level: number) => {
    const dots = '•'.repeat(Math.max(0, (level - 4) / 2));
    return dots;
  };

  return (
    <div className={`relative ${className}`}>
      {/* Input Field */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <FiSearch className="h-5 w-5 text-gray-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          value={searchTerm || value}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
        {(searchTerm || value) && (
          <button
            onClick={() => {
              setSearchTerm('');
              onChange('');
              setIsOpen(false);
            }}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <FiX className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto"
        >
          {/* Search Results */}
          {filteredCodes.length > 0 && (
            <div>
              <div className="px-4 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b">
                Search Results
              </div>
              {filteredCodes.map((item, index) => (
                <div
                  key={item.code}
                  onClick={() => handleSelectCode(item.code)}
                  className={`px-4 py-3 cursor-pointer border-b border-gray-100 hover:bg-gray-50 ${
                    index === selectedIndex ? 'bg-primary-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span className="text-xs text-gray-400 mr-2">
                          {getLevelIndicator(item.level)}
                        </span>
                        <span className="font-mono text-sm font-medium text-primary-600">
                          {formatHsCode(item.code)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700 mt-1">
                        {item.description}
                      </div>
                    </div>
                    <button
                      onClick={(e) => toggleFavorite(item.code, e)}
                      className="ml-2 p-1 hover:bg-gray-200 rounded"
                    >
                      <FiStar
                        className={`h-4 w-4 ${
                          favorites.includes(item.code)
                            ? 'text-yellow-500 fill-current'
                            : 'text-gray-400'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recent Searches */}
          {!searchTerm && recentSearches.length > 0 && (
            <div>
              <div className="px-4 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b flex items-center">
                <FiClock className="h-3 w-3 mr-1" />
                Recent Searches
              </div>
              {recentSearches.map((code) => {
                const item = mockHsCodes.find(item => item.code === code);
                return (
                  <div
                    key={code}
                    onClick={() => handleSelectCode(code)}
                    className="px-4 py-3 cursor-pointer border-b border-gray-100 hover:bg-gray-50"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-mono text-sm font-medium text-primary-600">
                          {formatHsCode(code)}
                        </div>
                        {item && (
                          <div className="text-sm text-gray-700 mt-1">
                            {item.description}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={(e) => toggleFavorite(code, e)}
                        className="ml-2 p-1 hover:bg-gray-200 rounded"
                      >
                        <FiStar
                          className={`h-4 w-4 ${
                            favorites.includes(code)
                              ? 'text-yellow-500 fill-current'
                              : 'text-gray-400'
                          }`}
                        />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Favorites */}
          {!searchTerm && favorites.length > 0 && (
            <div>
              <div className="px-4 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b flex items-center">
                <FiStar className="h-3 w-3 mr-1" />
                Favorites
              </div>
              {favorites.map((code) => {
                const item = mockHsCodes.find(item => item.code === code);
                return (
                  <div
                    key={code}
                    onClick={() => handleSelectCode(code)}
                    className="px-4 py-3 cursor-pointer border-b border-gray-100 hover:bg-gray-50"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-mono text-sm font-medium text-primary-600">
                          {formatHsCode(code)}
                        </div>
                        {item && (
                          <div className="text-sm text-gray-700 mt-1">
                            {item.description}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={(e) => toggleFavorite(code, e)}
                        className="ml-2 p-1 hover:bg-gray-200 rounded"
                      >
                        <FiStar className="h-4 w-4 text-yellow-500 fill-current" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* No Results */}
          {searchTerm && filteredCodes.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">
              <FiBookOpen className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <div className="text-sm">No HS codes found</div>
              <div className="text-xs mt-1">
                Try searching with a different term or browse the tariff classification tool
              </div>
            </div>
          )}

          {/* Empty State */}
          {!searchTerm && recentSearches.length === 0 && favorites.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">
              <FiSearch className="h-8 w-8 mx-auto mb-2 text-gray-400" />
              <div className="text-sm">Start typing to search HS codes</div>
              <div className="text-xs mt-1">
                Search by code number or product description
              </div>
            </div>
          )}

          {/* Help Footer */}
          <div className="px-4 py-2 bg-gray-50 border-t text-xs text-gray-500">
            <div className="flex items-center justify-between">
              <span>Use ↑↓ to navigate, Enter to select, Esc to close</span>
              <a
                href="https://www.abf.gov.au/importing-exporting-and-manufacturing/tariff-classification"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700"
              >
                Tariff Tool →
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HsCodeLookup;