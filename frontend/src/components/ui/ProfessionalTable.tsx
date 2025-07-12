import React from 'react';
import { cn } from '../../lib/utils';
import { FiChevronUp, FiChevronDown, FiMoreVertical, FiFilter, FiSearch } from 'react-icons/fi';

interface Column<T> {
  key: keyof T | string;
  title: string;
  width?: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
}

interface ProfessionalTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
  };
  selection?: {
    selectedRowKeys: string[];
    onChange: (selectedRowKeys: string[], selectedRows: T[]) => void;
    getCheckboxProps?: (record: T) => { disabled?: boolean };
  };
  rowKey: keyof T | ((record: T) => string);
  onRow?: (record: T, index: number) => {
    onClick?: () => void;
    onDoubleClick?: () => void;
    className?: string;
  };
  size?: 'small' | 'medium' | 'large';
  bordered?: boolean;
  striped?: boolean;
  hoverable?: boolean;
  className?: string;
  emptyText?: string;
  scroll?: { x?: number; y?: number };
}

export function ProfessionalTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  pagination,
  selection,
  rowKey,
  onRow,
  size = 'medium',
  bordered = true,
  striped = true,
  hoverable = true,
  className = '',
  emptyText = 'No data available',
  scroll
}: ProfessionalTableProps<T>) {
  const [sortConfig, setSortConfig] = React.useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);
  const [filters, setFilters] = React.useState<Record<string, string>>({});

  const getRowKey = (record: T, index: number): string => {
    if (typeof rowKey === 'function') {
      return rowKey(record);
    }
    return String(record[rowKey]) || String(index);
  };

  const handleSort = (columnKey: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === columnKey && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key: columnKey, direction });
  };

  const sortedData = React.useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [data, sortConfig]);

  const filteredData = React.useMemo(() => {
    if (Object.keys(filters).length === 0) return sortedData;

    return sortedData.filter(record => {
      return Object.entries(filters).every(([key, value]) => {
        if (!value) return true;
        const recordValue = String(record[key]).toLowerCase();
        return recordValue.includes(value.toLowerCase());
      });
    });
  }, [sortedData, filters]);

  const sizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base'
  };

  const cellPaddingClasses = {
    small: 'px-3 py-2',
    medium: 'px-4 py-3',
    large: 'px-6 py-4'
  };

  const tableClasses = cn(
    'w-full bg-white',
    bordered && 'border border-gray-200 rounded-lg overflow-hidden',
    sizeClasses[size],
    className
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-white border border-gray-200 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  if (filteredData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-white border border-gray-200 rounded-lg">
        <div className="text-center">
          <p className="text-gray-500 text-lg mb-2">No data found</p>
          <p className="text-gray-400 text-sm">{emptyText}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div 
        className={cn(
          'overflow-auto',
          scroll?.x && `max-w-[${scroll.x}px]`,
          scroll?.y && `max-h-[${scroll.y}px]`
        )}
      >
        <table className={tableClasses}>
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {selection && (
                <th className={cn('text-left font-medium text-gray-700', cellPaddingClasses[size])}>
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    checked={selection.selectedRowKeys.length === filteredData.length}
                    onChange={(e) => {
                      if (e.target.checked) {
                        const allKeys = filteredData.map((record, index) => getRowKey(record, index));
                        selection.onChange(allKeys, filteredData);
                      } else {
                        selection.onChange([], []);
                      }
                    }}
                  />
                </th>
              )}
              {columns.map((column, index) => (
                <th
                  key={String(column.key) || index}
                  className={cn(
                    'font-medium text-gray-700 border-b border-gray-200',
                    cellPaddingClasses[size],
                    column.align === 'center' && 'text-center',
                    column.align === 'right' && 'text-right',
                    column.sortable && 'cursor-pointer hover:bg-gray-100',
                    column.width && `w-[${column.width}]`
                  )}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(String(column.key))}
                >
                  <div className="flex items-center gap-2">
                    <span>{column.title}</span>
                    {column.sortable && (
                      <div className="flex flex-col">
                        <FiChevronUp 
                          className={cn(
                            'w-3 h-3',
                            sortConfig?.key === column.key && sortConfig.direction === 'asc'
                              ? 'text-blue-600'
                              : 'text-gray-400'
                          )}
                        />
                        <FiChevronDown 
                          className={cn(
                            'w-3 h-3 -mt-1',
                            sortConfig?.key === column.key && sortConfig.direction === 'desc'
                              ? 'text-blue-600'
                              : 'text-gray-400'
                          )}
                        />
                      </div>
                    )}
                    {column.filterable && (
                      <FiFilter className="w-3 h-3 text-gray-400" />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredData.map((record, index) => {
              const key = getRowKey(record, index);
              const rowProps = onRow?.(record, index) || {};
              const isSelected = selection?.selectedRowKeys.includes(key);

              return (
                <tr
                  key={key}
                  className={cn(
                    'border-b border-gray-100',
                    striped && index % 2 === 1 && 'bg-gray-50/50',
                    hoverable && 'hover:bg-blue-50/50',
                    isSelected && 'bg-blue-50',
                    rowProps.className
                  )}
                  onClick={rowProps.onClick}
                  onDoubleClick={rowProps.onDoubleClick}
                >
                  {selection && (
                    <td className={cellPaddingClasses[size]}>
                      <input
                        type="checkbox"
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        checked={isSelected}
                        onChange={(e) => {
                          const newSelectedKeys = e.target.checked
                            ? [...selection.selectedRowKeys, key]
                            : selection.selectedRowKeys.filter(k => k !== key);
                          const newSelectedRows = filteredData.filter((_, i) => 
                            newSelectedKeys.includes(getRowKey(filteredData[i], i))
                          );
                          selection.onChange(newSelectedKeys, newSelectedRows);
                        }}
                        {...selection.getCheckboxProps?.(record)}
                      />
                    </td>
                  )}
                  {columns.map((column, colIndex) => {
                    const value = record[column.key as keyof T];
                    const content = column.render 
                      ? column.render(value, record, index)
                      : String(value || '');

                    return (
                      <td
                        key={String(column.key) || colIndex}
                        className={cn(
                          cellPaddingClasses[size],
                          column.align === 'center' && 'text-center',
                          column.align === 'right' && 'text-right'
                        )}
                      >
                        {content}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200">
          <div className="text-sm text-gray-700">
            Showing {((pagination.current - 1) * pagination.pageSize) + 1} to{' '}
            {Math.min(pagination.current * pagination.pageSize, pagination.total)} of{' '}
            {pagination.total} results
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => pagination.onChange(pagination.current - 1, pagination.pageSize)}
              disabled={pagination.current === 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-3 py-1 text-sm">
              Page {pagination.current} of {Math.ceil(pagination.total / pagination.pageSize)}
            </span>
            <button
              onClick={() => pagination.onChange(pagination.current + 1, pagination.pageSize)}
              disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  title?: string;
  description?: string;
  searchable?: boolean;
  searchPlaceholder?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  title,
  description,
  searchable = true,
  searchPlaceholder = 'Search...',
  actions,
  className = ''
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = React.useState('');

  const filteredData = React.useMemo(() => {
    if (!searchTerm) return data;
    
    return data.filter(record => {
      return Object.values(record).some(value => 
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      );
    });
  }, [data, searchTerm]);

  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg', className)}>
      {(title || description || searchable || actions) && (
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {title}
                </h3>
              )}
              {description && (
                <p className="text-sm text-gray-600">
                  {description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-3 ml-4">
              {searchable && (
                <div className="relative">
                  <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder={searchPlaceholder}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              )}
              {actions}
            </div>
          </div>
        </div>
      )}
      
      <ProfessionalTable
        data={filteredData}
        columns={columns}
        rowKey="id"
        bordered={false}
      />
    </div>
  );
}