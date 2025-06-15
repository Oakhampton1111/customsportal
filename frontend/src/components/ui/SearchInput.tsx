import React, { useState, useCallback, useEffect } from 'react';
import { FiSearch, FiX } from 'react-icons/fi';

interface SearchInputProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  onClear?: () => void;
  debounceMs?: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  autoFocus?: boolean;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  placeholder = 'Search...',
  value = '',
  onChange,
  onSearch,
  onClear,
  debounceMs = 300,
  className = '',
  size = 'md',
  disabled = false,
  autoFocus = false
}) => {
  const [internalValue, setInternalValue] = useState(value);
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);

    // Clear existing timer
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    // Set new timer for debounced search
    if (onSearch && debounceMs > 0) {
      const timer = setTimeout(() => {
        onSearch(newValue);
      }, debounceMs);
      setDebounceTimer(timer);
    } else if (onSearch) {
      onSearch(newValue);
    }
  }, [onChange, onSearch, debounceMs, debounceTimer]);

  const handleClear = useCallback(() => {
    setInternalValue('');
    onChange?.('');
    onSearch?.('');
    onClear?.();
    
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
  }, [onChange, onSearch, onClear, debounceTimer]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSearch) {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
      onSearch(internalValue);
    }
    if (e.key === 'Escape') {
      handleClear();
    }
  }, [onSearch, internalValue, debounceTimer, handleClear]);

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          height: '2rem',
          fontSize: 'var(--text-sm)',
          padding: '0 2.5rem 0 2rem'
        };
      case 'lg':
        return {
          height: '3rem',
          fontSize: 'var(--text-lg)',
          padding: '0 3rem 0 2.5rem'
        };
      default:
        return {
          height: '2.5rem',
          fontSize: 'var(--text-base)',
          padding: '0 2.75rem 0 2.25rem'
        };
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm': return 14;
      case 'lg': return 20;
      default: return 16;
    }
  };

  const getIconPosition = () => {
    switch (size) {
      case 'sm': return { left: '0.5rem' };
      case 'lg': return { left: '0.75rem' };
      default: return { left: '0.625rem' };
    }
  };

  const getClearPosition = () => {
    switch (size) {
      case 'sm': return { right: '0.5rem' };
      case 'lg': return { right: '0.75rem' };
      default: return { right: '0.625rem' };
    }
  };

  return (
    <div 
      className={`search-input ${className}`}
      style={{ position: 'relative', display: 'inline-block', width: '100%' }}
    >
      <FiSearch
        size={getIconSize()}
        style={{
          position: 'absolute',
          top: '50%',
          transform: 'translateY(-50%)',
          color: 'var(--color-gray-400)',
          pointerEvents: 'none',
          zIndex: 1,
          ...getIconPosition()
        }}
      />
      
      <input
        type="text"
        value={internalValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autoFocus}
        style={{
          width: '100%',
          border: '1px solid var(--color-gray-200)',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--color-white)',
          color: 'var(--color-gray-900)',
          transition: 'all var(--transition-fast)',
          outline: 'none',
          ...getSizeStyles()
        }}
        onFocus={(e) => {
          e.target.style.borderColor = 'var(--color-primary-300)';
          e.target.style.boxShadow = '0 0 0 3px var(--color-primary-50)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = 'var(--color-gray-200)';
          e.target.style.boxShadow = 'none';
        }}
      />
      
      {internalValue && (
        <button
          type="button"
          onClick={handleClear}
          disabled={disabled}
          style={{
            position: 'absolute',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--color-gray-400)',
            padding: '0.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'color var(--transition-fast)',
            ...getClearPosition()
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--color-gray-600)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--color-gray-400)';
          }}
        >
          <FiX size={getIconSize()} />
        </button>
      )}
    </div>
  );
};

export default SearchInput;
