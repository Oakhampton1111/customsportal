import React, { useState, useEffect } from 'react';
import {
  FiSearch,
  FiFolder,
  FiBarChart,
  FiPlus,
  FiMinus,
  FiChevronDown,
  FiChevronRight,
  FiBookmark,
  FiClock,
  FiInfo,
  FiRefreshCw,
} from 'react-icons/fi';
import { tariffApi } from '../services/tariffApi';
import type { TariffSection, TariffCodeDetails } from '../services/tariffApi';

const TariffTree: React.FC = () => {
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [comparisonCodes, setComparisonCodes] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('browse');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  
  // API state
  const [sections, setSections] = useState<TariffSection[]>([]);
  const [searchResults, setSearchResults] = useState<TariffCodeDetails[]>([]);
  const [comparisonData, setComparisonData] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSections();
  }, []);

  const loadSections = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await tariffApi.getSections();
      setSections(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tariff sections');
      console.error('Error loading sections:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSectionExpansion = (sectionId: number) => {
    const sectionIdStr = sectionId.toString();
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionIdStr)) {
        newSet.delete(sectionIdStr);
      } else {
        newSet.add(sectionIdStr);
      }
      return newSet;
    });
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const response = await tariffApi.searchTariffCodes(searchQuery);
      setSearchResults(response.results);
      setActiveTab('search');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeSelect = async (code: string) => {
    setSelectedCode(code);
    try {
      setIsLoading(true);
      const details = await tariffApi.getCodeDetails(code);
      console.log('Code details:', details);
      // TODO: Display code details in a modal or sidebar
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load code details');
      console.error('Error loading code details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const addToComparison = (code: string) => {
    if (!comparisonCodes.includes(code)) {
      setComparisonCodes(prev => [...prev, code]);
    }
  };

  const removeFromComparison = (code: string) => {
    setComparisonCodes(prev => prev.filter(c => c !== code));
  };

  const runComparison = async () => {
    if (comparisonCodes.length < 2) return;
    
    try {
      setIsLoading(true);
      const data = await tariffApi.compareCodes(comparisonCodes);
      setComparisonData(data);
      setActiveTab('comparison');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparison failed');
      console.error('Comparison error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (error) {
    return (
      <div className="content">
        <div className="card p-6 text-center">
          <FiInfo className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Tariff Tree</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={loadSections} className="btn btn--primary">
            <FiRefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="content fade-in">
      {/* Header Section */}
      <header className="page-header">
        <div className="page-header__content">
          <h1 className="page-header__title">
            Interactive Schedule 3 Explorer
          </h1>
          <p className="page-header__subtitle">
            Browse and search Australian tariff classifications
          </p>
        </div>
        <div className="page-header__actions">
          <button 
            onClick={loadSections}
            className="btn btn--secondary"
            disabled={isLoading}
          >
            <FiRefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {comparisonCodes.length >= 2 && (
            <button 
              onClick={runComparison}
              className="btn btn--primary"
              disabled={isLoading}
            >
              <FiBarChart className="w-4 h-4" />
              Compare ({comparisonCodes.length})
            </button>
          )}
        </div>
      </header>

      {/* Search Bar */}
      <div className="card p-4 mb-6">
        <div className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search tariff codes, descriptions, or HS codes..."
              className="input w-full"
            />
          </div>
          <button 
            onClick={handleSearch}
            className="btn btn--primary"
            disabled={isLoading || !searchQuery.trim()}
          >
            <FiSearch className="w-4 h-4" />
            Search
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="card mb-6">
        <nav className="nav nav--tabs">
          <button
            onClick={() => setActiveTab('browse')}
            className={`nav__item ${activeTab === 'browse' ? 'nav__item--active' : ''}`}
          >
            <FiFolder className="w-4 h-4" />
            Browse Sections
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`nav__item ${activeTab === 'search' ? 'nav__item--active' : ''}`}
          >
            <FiSearch className="w-4 h-4" />
            Search Results ({searchResults.length})
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`nav__item ${activeTab === 'comparison' ? 'nav__item--active' : ''}`}
          >
            <FiBarChart className="w-4 h-4" />
            Comparison ({comparisonCodes.length})
          </button>
        </nav>
      </div>

      {/* Comparison Bar */}
      {comparisonCodes.length > 0 && (
        <div className="alert alert--info mb-6">
          <div className="alert__content">
            <div className="alert__icon">
              <FiBarChart className="w-5 h-5" />
            </div>
            <div className="alert__body">
              <strong>Comparison Queue:</strong> {comparisonCodes.length} codes selected
              <div className="mt-2 flex flex-wrap gap-2">
                {comparisonCodes.map((code) => (
                  <span key={code} className="badge badge--primary">
                    {code}
                    <button
                      onClick={() => removeFromComparison(code)}
                      className="badge__close"
                    >
                      <FiMinus className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
            {comparisonCodes.length >= 2 && (
              <div className="alert__actions">
                <button onClick={runComparison} className="btn btn--sm btn--primary">
                  Compare
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="layout layout--sidebar">
        {/* Main Content */}
        <div className="layout__main">
          {activeTab === 'browse' && (
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Tariff Sections</h3>
                <p className="card__subtitle">Browse Schedule 3 by section</p>
              </div>
              <div className="card__body">
                {isLoading ? (
                  <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading sections...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sections.map((section) => (
                      <div key={section.id} className="tariff-section">
                        <button
                          onClick={() => toggleSectionExpansion(section.id)}
                          className="tariff-section__header w-full"
                        >
                          <div className="tariff-section__title">
                            <FiFolder className="tariff-section__icon" />
                            Section {section.section_number}: {section.title}
                          </div>
                          <div className={`tariff-section__expand ${expandedSections.has(section.id.toString()) ? 'tariff-section__expand--expanded' : ''}`}>
                            <FiChevronRight className="w-5 h-5" />
                          </div>
                        </button>
                        {expandedSections.has(section.id.toString()) && (
                          <div className="tariff-section__content">
                            <p className="tariff-section__description">
                              {section.description || 'No description available'}
                            </p>
                            <div className="tariff-section__stats">
                              <div className="tariff-section__stat">
                                <span className="tariff-section__stat-value">
                                  {section.chapter_range ? section.chapter_range.split('-').length : '0'}
                                </span>
                                <span className="tariff-section__stat-label">Chapters</span>
                              </div>
                              <div className="tariff-section__stat">
                                <span className="tariff-section__stat-value">
                                  {section.section_number}
                                </span>
                                <span className="tariff-section__stat-label">Section</span>
                              </div>
                            </div>
                            <div className="text-center py-4">
                              <p className="text-gray-500">
                                Chapter loading will be implemented with the InteractiveTariffTree component
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'search' && (
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Search Results</h3>
                <p className="card__subtitle">
                  {searchResults.length} results for "{searchQuery}"
                </p>
              </div>
              <div className="card__body">
                {searchResults.length === 0 ? (
                  <div className="text-center py-8">
                    <FiSearch className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">
                      {searchQuery ? 'No results found' : 'Enter a search term to begin'}
                    </p>
                  </div>
                ) : (
                  <div className="list list--interactive">
                    {searchResults.map((result) => (
                      <div key={result.id} className="list__item">
                        <div className="list__item-content">
                          <div className="list__item-body">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="badge badge--primary">
                                {result.hs_code}
                              </span>
                              <span className="badge badge--secondary">
                                Level {result.level}
                              </span>
                            </div>
                            <h4 className="list__item-title">
                              {result.description}
                            </h4>
                            <p className="list__item-subtitle">
                              {result.section_id && `Section ${result.section_id}`}
                              {result.chapter_id && ` • Chapter ${result.chapter_id}`}
                            </p>
                          </div>
                          <div className="list__item-actions">
                            <button
                              onClick={() => addToComparison(result.hs_code)}
                              className="btn btn--sm btn--ghost"
                              disabled={comparisonCodes.includes(result.hs_code) || comparisonCodes.length >= 5}
                            >
                              <FiPlus className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCodeSelect(result.hs_code)}
                              className="btn btn--sm btn--primary"
                            >
                              View Details
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'comparison' && (
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Code Comparison</h3>
                <p className="card__subtitle">
                  Comparing {comparisonCodes.length} tariff codes
                </p>
              </div>
              <div className="card__body">
                {comparisonData ? (
                  <div className="space-y-6">
                    <div className="overflow-x-auto">
                      <table className="table">
                        <thead>
                          <tr>
                            <th>Code</th>
                            <th>Description</th>
                            <th>Duty Rate</th>
                            <th>GST</th>
                            <th>FTA Rate</th>
                          </tr>
                        </thead>
                        <tbody>
                          {comparisonData.codes.map((code) => (
                            <tr key={code.code}>
                              <td className="font-mono">{code.code}</td>
                              <td>{code.description}</td>
                              <td>{code.dutyRate}%</td>
                              <td>{code.gstRate}%</td>
                              <td>{code.ftaRate || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FiBarChart className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">
                      Add at least 2 codes to comparison queue to compare
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="layout__sidebar">
          <div className="space-y-6">
            {/* Quick Jump */}
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Quick Jump</h3>
                <p className="card__subtitle">Jump to specific codes</p>
              </div>
              <div className="card__body">
                <div className="space-y-3">
                  <input
                    type="text"
                    placeholder="Enter HS code..."
                    className="input w-full"
                  />
                  <button className="btn btn--primary w-full">
                    <FiSearch className="w-4 h-4" />
                    Jump to Code
                  </button>
                </div>
              </div>
            </div>

            {/* Bookmarks */}
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Bookmarks</h3>
                <p className="card__subtitle">Saved codes</p>
              </div>
              <div className="card__body">
                <div className="text-center py-6">
                  <FiBookmark className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">No bookmarks yet</p>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <div className="card__header">
                <h3 className="card__title">Recent Activity</h3>
                <p className="card__subtitle">Recently viewed codes</p>
              </div>
              <div className="card__body">
                <div className="text-center py-6">
                  <FiClock className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">No recent activity</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TariffTree;
