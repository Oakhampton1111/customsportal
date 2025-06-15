import React, { useState, useEffect } from 'react';
import { FiTrendingUp, FiTrendingDown, FiDollarSign, FiPackage, FiGlobe, FiAlertTriangle } from 'react-icons/fi';

interface TradeStatistic {
  label: string;
  value: string;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  period: string;
}

interface AlertItem {
  id: string;
  type: 'duty_change' | 'tco_expiry' | 'fta_update' | 'compliance';
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  date: string;
}

interface TradeStatsSidebarProps {
  className?: string;
}

export const TradeStatsSidebar: React.FC<TradeStatsSidebarProps> = ({ 
  className = '' 
}) => {
  const [stats, setStats] = useState<TradeStatistic[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTradeStats = async () => {
    try {
      setLoading(true);
      // Mock API call - replace with actual API
      const mockStats: TradeStatistic[] = [
        { label: 'Total Imports', value: '$2.4M', change: 12, changeType: 'increase', period: 'vs last week' },
        { label: 'Active TCOs', value: '23', change: 2, changeType: 'increase', period: 'vs last month' },
        { label: 'Avg Duty Rate', value: '8.5%', change: -0.3, changeType: 'decrease', period: 'vs last quarter' },
        { label: 'FTA Utilization', value: '76%', change: 4, changeType: 'increase', period: 'vs last year' }
      ];
      setStats(mockStats);
    } catch (error) {
      console.error('Failed to fetch trade stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      // Mock API call - replace with actual API
      const mockAlerts: AlertItem[] = [
        {
          id: '1',
          type: 'duty_change',
          title: 'Duty Rate Update',
          description: 'New duty rates effective for electronics imports from China',
          severity: 'medium',
          date: new Date().toISOString().split('T')[0]
        },
        {
          id: '2',
          type: 'tco_expiry',
          title: 'TCO Expiring Soon',
          description: '3 Tariff Concession Orders expiring within 30 days',
          severity: 'high',
          date: new Date().toISOString().split('T')[0]
        }
      ];
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  useEffect(() => {
    fetchTradeStats();
    fetchAlerts();
  }, []);

  const getTrendIcon = (changeType: string) => {
    switch (changeType) {
      case 'increase':
        return <FiTrendingUp className="h-4 w-4 text-green-500" />;
      case 'decrease':
        return <FiTrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <FiDollarSign className="h-4 w-4 text-gray-500" />;
    }
  };

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
      case 'increase':
        return 'text-green-600';
      case 'decrease':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      default:
        return 'secondary';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'duty_change':
        return <FiDollarSign className="h-4 w-4" />;
      case 'tco_expiry':
        return <FiPackage className="h-4 w-4" />;
      case 'fta_update':
        return <FiGlobe className="h-4 w-4" />;
      default:
        return <FiAlertTriangle className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className={className}>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-6 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Trade Statistics */}
      <div>
        <div className="pb-3">
          <div className="text-lg flex items-center gap-2">
            <FiTrendingUp className="h-5 w-5" />
            Trade Statistics
          </div>
        </div>
        <div className="space-y-4">
          {stats.map((stat, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{stat.label}</span>
                {getTrendIcon(stat.changeType)}
              </div>
              <div className="flex items-end justify-between">
                <span className="text-2xl font-bold">{stat.value}</span>
                <div className="text-right">
                  <div className={`text-sm font-medium ${getChangeColor(stat.changeType)}`}>
                    {stat.change > 0 ? '+' : ''}{stat.change}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {stat.period}
                  </div>
                </div>
              </div>
              {index < stats.length - 1 && <div className="mt-4" />}
            </div>
          ))}
        </div>
      </div>

      {/* System Alerts */}
      <div>
        <div className="pb-3">
          <div className="text-lg flex items-center gap-2">
            <FiAlertTriangle className="h-5 w-5" />
            System Alerts
            {alerts.length > 0 && (
              <div className="ml-auto">
                {alerts.length}
              </div>
            )}
          </div>
        </div>
        <div className="space-y-3">
          {alerts.length === 0 ? (
            <div className="text-center text-muted-foreground py-4">
              <FiAlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No active alerts</p>
            </div>
          ) : (
            alerts.map((alert) => (
              <div key={alert.id} className="p-3 border rounded-lg space-y-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {getAlertIcon(alert.type)}
                    <span className="font-medium text-sm">{alert.title}</span>
                  </div>
                  <div className={`text-xs ${getSeverityColor(alert.severity)}`}>
                    {alert.severity}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {alert.description}
                </p>
                <div className="text-xs text-muted-foreground">
                  {new Date(alert.date).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <div className="pb-3">
          <div className="text-lg">Quick Actions</div>
        </div>
        <div className="space-y-2">
          <button className="w-full text-left p-2 rounded hover:bg-muted transition-colors">
            <div className="font-medium text-sm">View TCO Expiries</div>
            <div className="text-xs text-muted-foreground">Check upcoming expirations</div>
          </button>
          <button className="w-full text-left p-2 rounded hover:bg-muted transition-colors">
            <div className="font-medium text-sm">Duty Rate Changes</div>
            <div className="text-xs text-muted-foreground">Recent rate updates</div>
          </button>
          <button className="w-full text-left p-2 rounded hover:bg-muted transition-colors">
            <div className="font-medium text-sm">FTA Utilization Report</div>
            <div className="text-xs text-muted-foreground">Monthly performance</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TradeStatsSidebar;
