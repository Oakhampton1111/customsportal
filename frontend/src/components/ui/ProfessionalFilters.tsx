import React from 'react';
import { cn } from '../../lib/utils';
import { FiSearch, FiFilter, FiX, FiChevronDown, FiCalendar } from 'react-icons/fi';

interface FilterOption {
  label: string;
  value: string | number;
  count?: number;
}

interface FilterConfig {
  key: string;
  label: string;
  type: 'select' | 'multiselect' | 'range' | 'date' | 'daterange' | 'text';
  options?: FilterOption[];
  placeholder?: string;
  min?: number;
  max?: number;
}

interface FilterValue {
  [key: string]: any;
}

interface ProfessionalFiltersProps {
  filters: FilterConfig[];
  values: FilterValue;
  onChange: (values: FilterValue) => void;
  onReset?: () => void;
  className?: string;
  layout?: 'horizontal' | 'vertical' | 'grid';
  showActiveCount?: boolean;
}

export function ProfessionalFilters({
  filters,
  values,
  onChange,
  onReset,
  className = '',
  layout = 'horizontal',
  showActiveCount = true
}: ProfessionalFiltersProps) {
  const activeFilterCount = Object.values(values).filter(value => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== undefined && value !== null && value !== '';
  }).length;

  const updateFilter = (key: string, value: any) => {
    onChange({ ...values, [key]: value });
  };

  const clearFilter = (key: string) => {
    const newValues = { ...values };
    delete newValues[key];
    onChange(newValues);
  };

  const layoutClasses = {
    horizontal: 'flex flex-wrap items-center gap-4',
    vertical: 'space-y-4',
    grid: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
  };

  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg p-4', className)}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FiFilter className="w-4 h-4 text-gray-500" />
          <span className="font-medium text-gray-700">Filters</span>
          {showActiveCount && activeFilterCount > 0 && (
            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
              {activeFilterCount} active
            </span>
          )}
        </div>
        {onReset && activeFilterCount > 0 && (
          <button
            onClick={onReset}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <FiX className="w-3 h-3" />
            Clear all
          </button>
        )}
      </div>

      <div className={layoutClasses[layout]}>
        {filters.map((filter) => (
          <FilterField
            key={filter.key}
            filter={filter}
            value={values[filter.key]}
            onChange={(value) => updateFilter(filter.key, value)}
            onClear={() => clearFilter(filter.key)}
          />
        ))}
      </div>
    </div>
  );
}

interface FilterFieldProps {
  filter: FilterConfig;
  value: any;
  onChange: (value: any) => void;
  onClear: () => void;
}

function FilterField({ filter, value, onChange, onClear }: FilterFieldProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const hasValue = value !== undefined && value !== null && value !== '';

  const renderField = () => {
    switch (filter.type) {
      case 'text':
        return (
          <div className="relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder={filter.placeholder || `Search ${filter.label.toLowerCase()}...`}
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full min-w-[200px]"
            />
            {hasValue && (
              <button
                onClick={onClear}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <FiX className="w-4 h-4" />
              </button>
            )}
          </div>
        );

      case 'select':
        return (
          <div className="relative min-w-[160px]">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className={cn(
                'w-full px-3 py-2 text-left border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                hasValue ? 'text-gray-900' : 'text-gray-500'
              )}
            >
              <div className="flex items-center justify-between">
                <span className="truncate">
                  {hasValue 
                    ? filter.options?.find(opt => opt.value === value)?.label || value
                    : filter.placeholder || `Select ${filter.label.toLowerCase()}`
                  }
                </span>
                <FiChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
              </div>
            </button>
            {isOpen && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                {filter.options?.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => {
                      onChange(option.value);
                      setIsOpen(false);
                    }}
                    className={cn(
                      'w-full px-3 py-2 text-left text-sm hover:bg-gray-50',
                      value === option.value && 'bg-blue-50 text-blue-700'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span>{option.label}</span>
                      {option.count !== undefined && (
                        <span className="text-gray-400">({option.count})</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        );

      case 'multiselect':
        const selectedValues = Array.isArray(value) ? value : [];
        return (
          <div className="relative min-w-[180px]">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="w-full px-3 py-2 text-left border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <div className="flex items-center justify-between">
                <span className="truncate">
                  {selectedValues.length > 0
                    ? `${selectedValues.length} selected`
                    : filter.placeholder || `Select ${filter.label.toLowerCase()}`
                  }
                </span>
                <FiChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
              </div>
            </button>
            {isOpen && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                {filter.options?.map((option) => {
                  const isSelected = selectedValues.includes(option.value);
                  return (
                    <label
                      key={option.value}
                      className="flex items-center px-3 py-2 text-sm hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          const newValues = e.target.checked
                            ? [...selectedValues, option.value]
                            : selectedValues.filter(v => v !== option.value);
                          onChange(newValues);
                        }}
                        className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="flex-1">{option.label}</span>
                      {option.count !== undefined && (
                        <span className="text-gray-400">({option.count})</span>
                      )}
                    </label>
                  );
                })}
              </div>
            )}
          </div>
        );

      case 'range':
        const rangeValue = value || { min: '', max: '' };
        return (
          <div className="flex items-center gap-2 min-w-[200px]">
            <input
              type="number"
              placeholder="Min"
              value={rangeValue.min}
              min={filter.min}
              max={filter.max}
              onChange={(e) => onChange({ ...rangeValue, min: e.target.value })}
              className="w-20 px-2 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <span className="text-gray-400">to</span>
            <input
              type="number"
              placeholder="Max"
              value={rangeValue.max}
              min={filter.min}
              max={filter.max}
              onChange={(e) => onChange({ ...rangeValue, max: e.target.value })}
              className="w-20 px-2 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        );

      case 'date':
        return (
          <div className="relative min-w-[140px]">
            <FiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="date"
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              className="pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
            />
          </div>
        );

      case 'daterange':
        const dateRangeValue = value || { start: '', end: '' };
        return (
          <div className="flex items-center gap-2 min-w-[280px]">
            <div className="relative">
              <FiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="date"
                value={dateRangeValue.start}
                onChange={(e) => onChange({ ...dateRangeValue, start: e.target.value })}
                className="pl-10 pr-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-32"
              />
            </div>
            <span className="text-gray-400">to</span>
            <div className="relative">
              <FiCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="date"
                value={dateRangeValue.end}
                onChange={(e) => onChange({ ...dateRangeValue, end: e.target.value })}
                className="pl-10 pr-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-32"
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-1">
      <label className="block text-xs font-medium text-gray-700">
        {filter.label}
      </label>
      {renderField()}
    </div>
  );
}

interface QuickFiltersProps {
  filters: Array<{
    label: string;
    value: any;
    active?: boolean;
    count?: number;
  }>;
  onFilterClick: (value: any) => void;
  className?: string;
}

export function QuickFilters({ filters, onFilterClick, className = '' }: QuickFiltersProps) {
  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {filters.map((filter, index) => (
        <button
          key={index}
          onClick={() => onFilterClick(filter.value)}
          className={cn(
            'px-3 py-1.5 text-sm rounded-full border transition-colors',
            filter.active
              ? 'bg-blue-100 border-blue-300 text-blue-700'
              : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
          )}
        >
          {filter.label}
          {filter.count !== undefined && (
            <span className="ml-1 text-xs opacity-75">({filter.count})</span>
          )}
        </button>
      ))}
    </div>
  );
}

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  suggestions?: string[];
  onSuggestionClick?: (suggestion: string) => void;
  className?: string;
  size?: 'small' | 'medium' | 'large';
}

export function SearchBar({
  value,
  onChange,
  placeholder = 'Search...',
  suggestions = [],
  onSuggestionClick,
  className = '',
  size = 'medium'
}: SearchBarProps) {
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const [focusedIndex, setFocusedIndex] = React.useState(-1);

  const sizeClasses = {
    small: 'px-3 py-2 text-sm',
    medium: 'px-4 py-3 text-base',
    large: 'px-6 py-4 text-lg'
  };

  const iconSizes = {
    small: 'w-4 h-4',
    medium: 'w-5 h-5',
    large: 'w-6 h-6'
  };

  const filteredSuggestions = suggestions.filter(suggestion =>
    suggestion.toLowerCase().includes(value.toLowerCase())
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setFocusedIndex(prev => 
        prev < filteredSuggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setFocusedIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (focusedIndex >= 0 && filteredSuggestions[focusedIndex]) {
        onSuggestionClick?.(filteredSuggestions[focusedIndex]);
        setShowSuggestions(false);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setFocusedIndex(-1);
    }
  };

  return (
    <div className={cn('relative', className)}>
      <div className="relative">
        <FiSearch className={cn(
          'absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400',
          iconSizes[size]
        )} />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            'w-full pl-10 pr-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            sizeClasses[size]
          )}
        />
      </div>

      {showSuggestions && filteredSuggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {filteredSuggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => {
                onSuggestionClick?.(suggestion);
                setShowSuggestions(false);
              }}
              className={cn(
                'w-full px-4 py-2 text-left text-sm hover:bg-gray-50',
                index === focusedIndex && 'bg-blue-50 text-blue-700'
              )}
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}