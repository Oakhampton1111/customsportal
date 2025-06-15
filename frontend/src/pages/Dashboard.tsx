import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { newsApi } from '../services/newsApi';
import { rulingsApi } from '../services/rulingsApi';
import type { NewsItem, SystemAlert } from '../services/newsApi';
import type { TariffRuling } from '../services/rulingsApi';
import { 
  FiRefreshCw, 
  FiExternalLink, 
  FiCalendar, 
  FiTrendingUp, 
  FiFileText, 
  FiAlertCircle, 
  FiSearch, 
  FiDollarSign, 
  FiGlobe,
  FiActivity,
  FiShield,
  FiClock,
  FiArrowRight
} from 'react-icons/fi';

const Dashboard: React.FC = () => {
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [rulings, setRulings] = useState<TariffRuling[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [newsData, alertsData, rulingsData] = await Promise.all([
        newsApi.getDashboardFeed(),
        newsApi.getAlerts(),
        rulingsApi.getRecentRulings()
      ]);

      setNewsItems(newsData.slice(0, 5));
      setAlerts(alertsData.filter(alert => !alert.read).slice(0, 3));
      setRulings(rulingsData.slice(0, 4));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const kpiData = [
    {
      icon: FiFileText,
      value: newsItems.length,
      label: 'Recent News Items',
      color: 'blue'
    },
    {
      icon: FiAlertCircle,
      value: alerts.length,
      label: 'Active Alerts',
      color: 'orange'
    },
    {
      icon: FiShield,
      value: rulings.length,
      label: 'Recent Rulings',
      color: 'green'
    },
    {
      icon: FiActivity,
      value: 'Online',
      label: 'System Status',
      color: 'emerald'
    }
  ];

  if (loading) {
    return (
      <div className="content">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="content">
        <div className="card p-6 text-center">
          <FiAlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadDashboardData}
            className="btn btn--primary"
          >
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
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Customs Intelligence Dashboard
            </h1>
            <p className="text-lg text-gray-600">
              Real-time trade intelligence and regulatory updates
            </p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={loadDashboardData}
              className="btn btn--secondary"
              disabled={loading}
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <Link to="/ai-assistant" className="btn btn--primary">
              <FiSearch className="w-4 h-4" />
              AI Assistant
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpiData.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <div key={index} className="kpi-card">
              <div className="kpi-card__icon">
                <Icon className="w-6 h-6" />
              </div>
              <div className="kpi-card__value">{kpi.value}</div>
              <div className="kpi-card__label">{kpi.label}</div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Alerts */}
        <div className="card">
          <div className="card__header">
            <h3 className="card__title flex items-center gap-2">
              <FiAlertCircle className="w-5 h-5 text-orange-500" />
              System Alerts
            </h3>
            <p className="card__subtitle">Important notifications and updates</p>
          </div>
          <div className="card__body">
            {alerts.length === 0 ? (
              <div className="text-center py-6">
                <FiShield className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <p className="text-gray-500">No active alerts</p>
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.map((alert, index) => (
                  <div 
                    key={index} 
                    className={`p-3 rounded-lg border-l-4 ${
                      alert.type === 'error' ? 'bg-red-50 border-red-400' :
                      alert.type === 'warning' ? 'bg-orange-50 border-orange-400' :
                      'bg-blue-50 border-blue-400'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <FiAlertCircle className={`w-4 h-4 mt-0.5 ${
                        alert.type === 'error' ? 'text-red-500' :
                        alert.type === 'warning' ? 'text-orange-500' :
                        'text-blue-500'
                      }`} />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 text-sm">{alert.title}</p>
                        <p className="text-gray-600 text-xs mt-1">{alert.message}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Latest Trade Intelligence */}
        <div className="card">
          <div className="card__header">
            <h3 className="card__title flex items-center gap-2">
              <FiTrendingUp className="w-5 h-5 text-blue-500" />
              Trade Intelligence
            </h3>
            <p className="card__subtitle">Latest news and market updates</p>
          </div>
          <div className="card__body">
            {newsItems.length === 0 ? (
              <div className="text-center py-6">
                <FiFileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No recent news</p>
              </div>
            ) : (
              <div className="space-y-4">
                {newsItems.map((item, index) => (
                  <div key={index} className="group">
                    <div className="flex items-start gap-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        item.priority === 'high' ? 'bg-red-400' :
                        item.priority === 'medium' ? 'bg-orange-400' :
                        'bg-blue-400'
                      }`} />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                          {item.title}
                        </h4>
                        <p className="text-gray-600 text-xs mt-1 line-clamp-2">
                          {item.summary}
                        </p>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                          <FiCalendar className="w-3 h-3" />
                          {new Date(item.publishedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="card__footer">
            <Link to="/news" className="btn btn--ghost btn--sm w-full">
              View All News
              <FiArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Recent Tariff Rulings */}
        <div className="card">
          <div className="card__header">
            <h3 className="card__title flex items-center gap-2">
              <FiFileText className="w-5 h-5 text-green-500" />
              Recent Rulings
            </h3>
            <p className="card__subtitle">Latest tariff and customs decisions</p>
          </div>
          <div className="card__body">
            {rulings.length === 0 ? (
              <div className="text-center py-6">
                <FiFileText className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No recent rulings</p>
              </div>
            ) : (
              <div className="space-y-4">
                {rulings.map((ruling, index) => (
                  <div key={index} className="group">
                    <div className="flex items-start gap-3">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        ruling.status === 'active' ? 'bg-green-100 text-green-700' :
                        ruling.status === 'pending' ? 'bg-orange-100 text-orange-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {ruling.status}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                          {ruling.title}
                        </h4>
                        <p className="text-gray-600 text-xs mt-1">
                          HS Code: {ruling.hsCode}
                        </p>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                          <FiClock className="w-3 h-3" />
                          {new Date(ruling.dateIssued).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="card__footer">
            <Link to="/rulings" className="btn btn--ghost btn--sm w-full">
              View All Rulings
              <FiArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <div className="card">
          <div className="card__header">
            <h3 className="card__title">Quick Actions</h3>
            <p className="card__subtitle">Common tasks and tools</p>
          </div>
          <div className="card__body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Link to="/tariff-tree" className="btn btn--secondary justify-start">
                <FiSearch className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Tariff Lookup</div>
                  <div className="text-xs opacity-75">Browse Schedule 3</div>
                </div>
              </Link>
              <Link to="/ai-assistant" className="btn btn--secondary justify-start">
                <FiDollarSign className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Duty Calculator</div>
                  <div className="text-xs opacity-75">Calculate import costs</div>
                </div>
              </Link>
              <Link to="/export-tariffs" className="btn btn--secondary justify-start">
                <FiGlobe className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">Export Center</div>
                  <div className="text-xs opacity-75">AHECC codes & requirements</div>
                </div>
              </Link>
              <Link to="/ai-assistant" className="btn btn--secondary justify-start">
                <FiFileText className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">AI Assistant</div>
                  <div className="text-xs opacity-75">Get expert guidance</div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
