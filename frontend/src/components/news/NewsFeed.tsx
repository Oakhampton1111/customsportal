import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FiCalendar, FiTag, FiExternalLink, FiFilter, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { newsApi } from './NewsApi';
import type { NewsItem, NewsFilter } from './NewsApi';

interface NewsFeedProps {
  maxItems?: number;
  compact?: boolean;
  showFilters?: boolean;
  className?: string;
}

const NewsFeed: React.FC<NewsFeedProps> = ({ 
  maxItems = 20, 
  compact = false, 
  showFilters = true,
  className = '' 
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState<NewsFilter>({});
  const [showFilterPanel, setShowFilterPanel] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['news', currentPage, maxItems, filter],
    queryFn: () => newsApi.getNews(currentPage, maxItems, filter),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handleFilterChange = (newFilter: Partial<NewsFilter>) => {
    setFilter(prev => ({ ...prev, ...newFilter }));
    setCurrentPage(1); // Reset to first page when filtering
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'tariff': 'bg-blue-100 text-blue-800',
      'regulation': 'bg-yellow-100 text-yellow-800',
      'procedure': 'bg-green-100 text-green-800',
      'announcement': 'bg-purple-100 text-purple-800',
      'alert': 'bg-red-100 text-red-800',
    };
    return colors[category.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Customs News & Updates</h2>
        </div>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Customs News & Updates</h2>
        </div>
        <div className="p-6">
          <div className="text-center text-red-600">
            <p>Failed to load news updates</p>
            <p className="text-sm text-gray-500 mt-1">Please try again later</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Customs News & Updates</h2>
          {showFilters && (
            <button
              onClick={() => setShowFilterPanel(!showFilterPanel)}
              className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
            >
              <FiFilter />
              <span>Filter</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && showFilterPanel && (
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filter.category?.[0] || ''}
                onChange={(e) => handleFilterChange({ category: e.target.value ? [e.target.value] : undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="">All Categories</option>
                <option value="tariff">Tariff</option>
                <option value="regulation">Regulation</option>
                <option value="procedure">Procedure</option>
                <option value="announcement">Announcement</option>
                <option value="alert">Alert</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={filter.priority?.[0] || ''}
                onChange={(e) => handleFilterChange({ priority: e.target.value ? [e.target.value] : undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              >
                <option value="">All Priorities</option>
                <option value="urgent">Urgent</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                value={filter.search || ''}
                onChange={(e) => handleFilterChange({ search: e.target.value || undefined })}
                placeholder="Search news..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>
        </div>
      )}

      {/* News Items */}
      <div className="divide-y divide-gray-200">
        {data?.items.map((item: NewsItem) => (
          <div key={item.id} className={`p-6 hover:bg-gray-50 transition-colors ${compact ? 'py-4' : ''}`}>
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(item.category)}`}>
                    <FiTag className="mr-1" />
                    {item.category}
                  </span>
                  {item.priority === 'high' || item.priority === 'urgent' ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      {item.priority === 'urgent' ? 'Urgent' : 'High Priority'}
                    </span>
                  ) : null}
                  {item.is_featured && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                      Featured
                    </span>
                  )}
                </div>
                
                <h3 className={`font-semibold text-gray-900 ${compact ? 'text-sm' : 'text-base'} mb-2`}>
                  {item.title}
                </h3>
                
                {!compact && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {item.summary}
                  </p>
                )}
                
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <FiCalendar />
                    <span>{formatDate(item.published_date)}</span>
                  </div>
                  {item.source && (
                    <span>Source: {item.source}</span>
                  )}
                  {item.effective_date && (
                    <span>Effective: {formatDate(item.effective_date)}</span>
                  )}
                </div>

                {item.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {item.tags.slice(0, compact ? 3 : 5).map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                    {item.tags.length > (compact ? 3 : 5) && (
                      <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                        +{item.tags.length - (compact ? 3 : 5)} more
                      </span>
                    )}
                  </div>
                )}
              </div>
              
              <div className="ml-4 flex-shrink-0">
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  >
                    <FiExternalLink className="mr-1" />
                    Read More
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((currentPage - 1) * maxItems) + 1} to {Math.min(currentPage * maxItems, data.total)} of {data.total} results
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={!data.has_prev}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FiChevronLeft className="mr-1" />
                Previous
              </button>
              
              <span className="text-sm text-gray-700">
                Page {currentPage} of {data.total_pages}
              </span>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(data.total_pages, prev + 1))}
                disabled={!data.has_next}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <FiChevronRight className="ml-1" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;
