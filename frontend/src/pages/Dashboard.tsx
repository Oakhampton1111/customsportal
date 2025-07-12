import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { newsApi } from '../services/newsApi';
import { rulingsApi } from '../services/rulingsApi';
import { tariffApi } from '../services/tariffApi';
import type { NewsItem, SystemAlert } from '../services/newsApi';
import type { TariffRuling } from '../services/rulingsApi';
import {
  FiRefreshCw,
  FiFileText,
  FiAlertCircle,
  FiSearch,
  FiDollarSign,
  FiGlobe,
  FiShield,
  FiClock,
  FiArrowRight,
  FiTarget,
  FiZap,
  FiPercent,
  FiBookOpen,
  FiStar
} from 'react-icons/fi';

// Import Professional Components
import { IntelligencePanel } from '../components/ui';
import { KPICard, KPIGrid } from '../components/ui/KPICard';
import {
  ProfessionalCard,
  ProfessionalCardHeader,
  ProfessionalCardContent
} from '../components/ui/ProfessionalCard';

const Dashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [rulings, setRulings] = useState<TariffRuling[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Define types for intelligence data
  interface DutyRateChange {
    hsCode: string;
    description: string;
    oldRate: string;
    newRate: string;
    effectiveDate: string;
    impact: string;
  }

  interface FtaOpportunity {
    country: string;
    hsCode: string;
    standardRate: string;
    ftaRate: string;
    savings: string;
    agreement: string;
  }

  interface ClassificationUpdate {
    hsCode: string;
    description: string;
    date: string;
    priority: string;
  }

  interface ComplianceAlert {
    type: string;
    description: string;
    severity: string;
    date: string;
  }

  interface TradingPartner {
    country: string;
    volume: string;
    trend: string;
    value: string;
  }

  interface EmergingOpportunity {
    sector: string;
    growth: string;
    opportunity: string;
  }

  interface RiskAlert {
    type: string;
    description: string;
    impact: string;
  }

  interface SeasonalTrend {
    period: string;
    category: string;
    trend: string;
  }

  // New intelligence data state
  const [tradeIntelligence, setTradeIntelligence] = useState<{
    dutyRateChanges: DutyRateChange[];
    ftaOpportunities: FtaOpportunity[];
    classificationUpdates: ClassificationUpdate[];
    complianceAlerts: ComplianceAlert[];
  }>({
    dutyRateChanges: [],
    ftaOpportunities: [],
    classificationUpdates: [],
    complianceAlerts: []
  });

  const [brokerMetrics, setBrokerMetrics] = useState({
    monthlyDeclarations: 0,
    dutySavings: 0,
    avgProcessingTime: 0,
    complianceScore: 0,
    activeClients: 0,
    pendingClassifications: 0
  });

  const [marketInsights, setMarketInsights] = useState<{
    topTradingPartners: TradingPartner[];
    emergingOpportunities: EmergingOpportunity[];
    riskAlerts: RiskAlert[];
    seasonalTrends: SeasonalTrend[];
  }>({
    topTradingPartners: [],
    emergingOpportunities: [],
    riskAlerts: [],
    seasonalTrends: []
  });

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [, alertsData, rulingsData] = await Promise.all([
        newsApi.getDashboardFeed(),
        newsApi.getAlerts(),
        rulingsApi.getRecentRulings()
      ]);

      setAlerts(alertsData.filter(alert => !alert.read).slice(0, 3));
      setRulings(rulingsData.slice(0, 4));
      console.log('✅ Dashboard data loaded successfully from APIs');

      // Load new intelligence data
      await loadTradeIntelligence();
      await loadBrokerMetrics();
      await loadMarketInsights();

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadTradeIntelligence = async () => {
    try {
      // Synthesize data from existing APIs
      const [tariffResponse] = await Promise.all([
        tariffApi.searchTariffCodes('', 50, 0) // Get recent tariff data
      ]);

      // Mock intelligence data for now - will be replaced with real synthesis
      setTradeIntelligence({
        dutyRateChanges: [
          { hsCode: '8471.30.00', description: 'Portable computers', oldRate: '5%', newRate: '0%', effectiveDate: '2024-01-01', impact: 'high' },
          { hsCode: '8517.12.00', description: 'Mobile phones', oldRate: '5%', newRate: '0%', effectiveDate: '2024-02-01', impact: 'medium' }
        ],
        ftaOpportunities: [
          { country: 'Japan', hsCode: '8471.30.00', standardRate: '5%', ftaRate: '0%', savings: '$2,500', agreement: 'JAEPA' },
          { country: 'Korea', hsCode: '8517.12.00', standardRate: '5%', ftaRate: '0%', savings: '$1,800', agreement: 'KAFTA' }
        ],
        classificationUpdates: [
          { hsCode: '8471.30.00', description: 'New AI-enabled laptops classification guidance', date: '2024-01-15', priority: 'high' },
          { hsCode: '8517.62.00', description: 'Updated smartphone classification criteria', date: '2024-01-10', priority: 'medium' }
        ],
        complianceAlerts: [
          { type: 'Anti-dumping', description: 'New anti-dumping duties on steel imports from China', severity: 'high', date: '2024-01-20' },
          { type: 'Documentation', description: 'Updated COO requirements for textile imports', severity: 'medium', date: '2024-01-18' }
        ]
      });
    } catch (err) {
      console.error('Error loading trade intelligence:', err);
    }
  };

  const loadBrokerMetrics = async () => {
    try {
      // Mock broker metrics - will be replaced with real API calls
      setBrokerMetrics({
        monthlyDeclarations: 1247,
        dutySavings: 125000,
        avgProcessingTime: 2.3,
        complianceScore: 98.5,
        activeClients: 89,
        pendingClassifications: 23
      });
    } catch (err) {
      console.error('Error loading broker metrics:', err);
    }
  };

  const loadMarketInsights = async () => {
    try {
      // Mock market insights - will be replaced with real data synthesis
      setMarketInsights({
        topTradingPartners: [
          { country: 'China', volume: '45%', trend: 'up', value: '$2.1B' },
          { country: 'USA', volume: '23%', trend: 'stable', value: '$1.2B' },
          { country: 'Japan', volume: '12%', trend: 'up', value: '$580M' }
        ],
        emergingOpportunities: [
          { sector: 'Electric Vehicles', growth: '+35%', opportunity: 'Battery components classification' },
          { sector: 'Renewable Energy', growth: '+28%', opportunity: 'Solar panel duty optimization' }
        ],
        riskAlerts: [
          { type: 'Regulatory', description: 'Pending changes to automotive import standards', impact: 'medium' },
          { type: 'Trade', description: 'Potential tariff adjustments on electronics', impact: 'high' }
        ],
        seasonalTrends: [
          { period: 'Q1 2024', category: 'Consumer Electronics', trend: 'Peak import season approaching' },
          { period: 'Q2 2024', category: 'Textiles', trend: 'Seasonal duty rate changes expected' }
        ]
      });
    } catch (err) {
      console.error('Error loading market insights:', err);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const kpiData = [
    {
      icon: FiFileText,
      value: brokerMetrics.monthlyDeclarations.toLocaleString(),
      label: 'Monthly Declarations',
      color: 'blue',
      trend: '+12%',
      subtitle: 'vs last month'
    },
    {
      icon: FiDollarSign,
      value: `$${(brokerMetrics.dutySavings / 1000).toFixed(0)}K`,
      label: 'Duty Savings',
      color: 'green',
      trend: '+8%',
      subtitle: 'this month'
    },
    {
      icon: FiClock,
      value: `${brokerMetrics.avgProcessingTime}h`,
      label: 'Avg Processing Time',
      color: 'orange',
      trend: '-15%',
      subtitle: 'improvement'
    },
    {
      icon: FiShield,
      value: `${brokerMetrics.complianceScore}%`,
      label: 'Compliance Score',
      color: 'emerald',
      trend: '+2%',
      subtitle: 'excellent'
    },
    {
      icon: FiGlobe,
      value: brokerMetrics.activeClients,
      label: 'Active Clients',
      color: 'purple',
      trend: '+5',
      subtitle: 'new this month'
    },
    {
      icon: FiAlertCircle,
      value: brokerMetrics.pendingClassifications,
      label: 'Pending Classifications',
      color: 'red',
      trend: '-3',
      subtitle: 'priority items'
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

      {/* Professional KPI Cards */}
      <KPIGrid className="mb-8">
        {kpiData.map((kpi, index) => (
          <KPICard
            key={index}
            icon={kpi.icon}
            value={kpi.value}
            label={kpi.label}
            color={kpi.color as any}
            trend={kpi.trend}
            subtitle={kpi.subtitle}
          />
        ))}
      </KPIGrid>

      {/* Trade Intelligence Summary */}
      <IntelligencePanel
        title="Trade Intelligence Summary"
        subtitle="AI-powered insights and regulatory updates"
        icon={<FiZap className="w-5 h-5" />}
        variant="primary"
        className="mb-8"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <FiPercent className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-gray-700">Duty Rate Changes</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{tradeIntelligence.dutyRateChanges.length}</div>
            <div className="text-xs text-gray-500">Active this month</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <FiGlobe className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">FTA Opportunities</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{tradeIntelligence.ftaOpportunities.length}</div>
            <div className="text-xs text-gray-500">Potential savings</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <FiBookOpen className="w-4 h-4 text-orange-600" />
              <span className="text-sm font-medium text-gray-700">Classification Updates</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{tradeIntelligence.classificationUpdates.length}</div>
            <div className="text-xs text-gray-500">Requiring attention</div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <FiShield className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-gray-700">Compliance Alerts</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{tradeIntelligence.complianceAlerts.length}</div>
            <div className="text-xs text-gray-500">High priority</div>
          </div>
        </div>
      </IntelligencePanel>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
        {/* System Alerts */}
        <ProfessionalCard variant="alert">
          <ProfessionalCardHeader
            icon={<FiAlertCircle className="w-5 h-5" />}
            subtitle="Important notifications and updates"
          >
            System Alerts
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
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
          </ProfessionalCardContent>
        </ProfessionalCard>

        {/* Synthesized Intelligence Panel */}
        <ProfessionalCard variant="intelligence">
          <ProfessionalCardHeader
            icon={<FiZap className="w-5 h-5" />}
            subtitle="AI-powered trade insights and recommendations"
          >
            Synthesized Intelligence
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="space-y-6">
              {/* Duty Rate Changes */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <FiPercent className="w-4 h-4 text-green-600" />
                  <h4 className="font-medium text-gray-900 text-sm">Recent Duty Rate Changes</h4>
                </div>
                {tradeIntelligence.dutyRateChanges.length === 0 ? (
                  <p className="text-gray-500 text-xs">No recent changes</p>
                ) : (
                  <div className="space-y-2">
                    {tradeIntelligence.dutyRateChanges.slice(0, 2).map((change, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 text-xs">{change.hsCode}</p>
                            <p className="text-gray-600 text-xs mt-1">{change.description}</p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-red-600 line-through">{change.oldRate}</span>
                              <FiArrowRight className="w-3 h-3 text-gray-400" />
                              <span className="text-xs text-green-600 font-medium">{change.newRate}</span>
                            </div>
                          </div>
                          <div className={`px-2 py-1 rounded text-xs font-medium ${
                            change.impact === 'high' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                          }`}>
                            {change.impact}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* FTA Opportunities */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <FiGlobe className="w-4 h-4 text-blue-600" />
                  <h4 className="font-medium text-gray-900 text-sm">FTA Opportunities</h4>
                </div>
                {tradeIntelligence.ftaOpportunities.length === 0 ? (
                  <p className="text-gray-500 text-xs">No opportunities identified</p>
                ) : (
                  <div className="space-y-2">
                    {tradeIntelligence.ftaOpportunities.slice(0, 2).map((opportunity, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 text-xs">{opportunity.country} - {opportunity.hsCode}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-gray-600">Standard: {opportunity.standardRate}</span>
                              <FiArrowRight className="w-3 h-3 text-gray-400" />
                              <span className="text-xs text-blue-600 font-medium">FTA: {opportunity.ftaRate}</span>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">{opportunity.agreement}</p>
                          </div>
                          <div className="text-xs font-medium text-green-600">
                            {opportunity.savings}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Classification Updates */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <FiBookOpen className="w-4 h-4 text-orange-600" />
                  <h4 className="font-medium text-gray-900 text-sm">Classification Updates</h4>
                </div>
                {tradeIntelligence.classificationUpdates.length === 0 ? (
                  <p className="text-gray-500 text-xs">No recent updates</p>
                ) : (
                  <div className="space-y-2">
                    {tradeIntelligence.classificationUpdates.slice(0, 2).map((update, index) => (
                      <div key={index} className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 text-xs">{update.hsCode}</p>
                            <p className="text-gray-600 text-xs mt-1">{update.description}</p>
                            <p className="text-xs text-gray-500 mt-1">{new Date(update.date).toLocaleDateString()}</p>
                          </div>
                          <div className={`px-2 py-1 rounded text-xs font-medium ${
                            update.priority === 'high' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                          }`}>
                            {update.priority}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-gray-100">
              <Link to="/intelligence" className="btn btn--ghost btn--sm w-full">
                View Full Intelligence Report
                <FiArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>

        {/* Recent Tariff Rulings */}
        <ProfessionalCard variant="default">
          <ProfessionalCardHeader
            icon={<FiFileText className="w-5 h-5" />}
            subtitle="Latest tariff and customs decisions"
          >
            Recent Rulings
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
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
                        ruling.status === 'superseded' ? 'bg-orange-100 text-orange-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {ruling.status}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                          {ruling.title}
                        </h4>
                        <p className="text-gray-600 text-xs mt-1">
                          HS Code: {ruling.hs_code}
                        </p>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                          <FiClock className="w-3 h-3" />
                          {new Date(ruling.ruling_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-6 pt-4 border-t border-gray-100">
              <Link to="/rulings" className="btn btn--ghost btn--sm w-full">
                View All Rulings
                <FiArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>
      </div>

      {/* Enhanced Quick Actions & Smart Recommendations */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <ProfessionalCard variant="default">
          <ProfessionalCardHeader
            icon={<FiZap className="w-5 h-5" />}
            subtitle="Professional broker workflows"
          >
            Quick Actions
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Link to="/tariff-tree" className="btn btn--secondary justify-start p-4 h-auto">
                <FiSearch className="w-5 h-5 text-blue-600" />
                <div className="text-left">
                  <div className="font-medium">Classification Lookup</div>
                  <div className="text-xs opacity-75">Interactive tariff tree</div>
                </div>
              </Link>
              <Link to="/ai-assistant" className="btn btn--secondary justify-start p-4 h-auto">
                <FiDollarSign className="w-5 h-5 text-green-600" />
                <div className="text-left">
                  <div className="font-medium">Duty Calculator</div>
                  <div className="text-xs opacity-75">All-in-one cost analysis</div>
                </div>
              </Link>
              <Link to="/export-tariffs" className="btn btn--secondary justify-start p-4 h-auto">
                <FiGlobe className="w-5 h-5 text-purple-600" />
                <div className="text-left">
                  <div className="font-medium">FTA Optimizer</div>
                  <div className="text-xs opacity-75">Find best trade agreements</div>
                </div>
              </Link>
              <Link to="/ai-assistant" className="btn btn--secondary justify-start p-4 h-auto">
                <FiTarget className="w-5 h-5 text-orange-600" />
                <div className="text-left">
                  <div className="font-medium">AI Assistant</div>
                  <div className="text-xs opacity-75">Expert trade guidance</div>
                </div>
              </Link>
              <Link to="/rulings" className="btn btn--secondary justify-start p-4 h-auto">
                <FiFileText className="w-5 h-5 text-indigo-600" />
                <div className="text-left">
                  <div className="font-medium">Ruling Search</div>
                  <div className="text-xs opacity-75">Find precedents</div>
                </div>
              </Link>
              <Link to="/compliance" className="btn btn--secondary justify-start p-4 h-auto">
                <FiShield className="w-5 h-5 text-red-600" />
                <div className="text-left">
                  <div className="font-medium">Compliance Check</div>
                  <div className="text-xs opacity-75">Verify requirements</div>
                </div>
              </Link>
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>

        {/* Smart Recommendations */}
        <ProfessionalCard variant="recommendation">
          <ProfessionalCardHeader
            icon={<FiStar className="w-5 h-5" />}
            subtitle="AI-powered insights for your workflow"
          >
            Smart Recommendations
          </ProfessionalCardHeader>
          <ProfessionalCardContent>
            <div className="space-y-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <FiPercent className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">Review Duty Rate Changes</h4>
                    <p className="text-gray-600 text-xs mt-1">
                      {tradeIntelligence.dutyRateChanges.length} codes have updated rates affecting your clients
                    </p>
                    <Link to="/intelligence" className="text-blue-600 text-xs font-medium mt-2 inline-flex items-center gap-1">
                      Review Changes <FiArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <FiDollarSign className="w-5 h-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">Optimize FTA Usage</h4>
                    <p className="text-gray-600 text-xs mt-1">
                      Potential savings of $4,300 identified across {tradeIntelligence.ftaOpportunities.length} classifications
                    </p>
                    <Link to="/fta-optimizer" className="text-green-600 text-xs font-medium mt-2 inline-flex items-center gap-1">
                      View Opportunities <FiArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <FiBookOpen className="w-5 h-5 text-orange-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">Classification Updates</h4>
                    <p className="text-gray-600 text-xs mt-1">
                      {brokerMetrics.pendingClassifications} classifications need review based on recent guidance
                    </p>
                    <Link to="/classifications" className="text-orange-600 text-xs font-medium mt-2 inline-flex items-center gap-1">
                      Review Classifications <FiArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </ProfessionalCardContent>
        </ProfessionalCard>
      </div>
    </div>
  );
};

export default Dashboard;
