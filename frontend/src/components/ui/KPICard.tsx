import React from 'react';
import { cn } from '../../lib/utils';
import { FiTrendingUp, FiTrendingDown, FiActivity } from 'react-icons/fi';

interface KPICardProps {
  icon: React.ComponentType<{ className?: string }>;
  value: string | number;
  label: string;
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple' | 'emerald' | 'indigo';
  trend?: string;
  subtitle?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  onClick?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
  icon: Icon,
  value,
  label,
  color = 'blue',
  trend,
  subtitle,
  className = '',
  size = 'md',
  interactive = false,
  onClick
}) => {
  const isPositiveTrend = trend?.startsWith('+') || (trend?.startsWith('-') && label.toLowerCase().includes('time'));
  
  const sizeClasses = {
    sm: 'p-4',
    md: 'p-5',
    lg: 'p-6'
  };

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const valueSizeClasses = {
    sm: 'text-xl',
    md: 'text-2xl',
    lg: 'text-3xl'
  };

  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    emerald: 'bg-emerald-100 text-emerald-600',
    indigo: 'bg-indigo-100 text-indigo-600'
  };

  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200 transition-all duration-200 group',
        sizeClasses[size],
        interactive && 'cursor-pointer hover:shadow-lg hover:-translate-y-0.5 hover:border-gray-300',
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={cn(
          'rounded-lg p-2 flex items-center justify-center',
          colorClasses[color]
        )}>
          <Icon className={iconSizeClasses[size]} />
        </div>
        {trend && (
          <div className={cn(
            'flex items-center gap-1 text-xs font-medium',
            isPositiveTrend ? 'text-green-600' : 'text-red-600'
          )}>
            {isPositiveTrend ? (
              <FiTrendingUp className="w-3 h-3" />
            ) : (
              <FiTrendingDown className="w-3 h-3" />
            )}
            {trend}
          </div>
        )}
      </div>
      
      <div className={cn(
        'font-bold text-gray-900 mb-1',
        valueSizeClasses[size]
      )}>
        {value}
      </div>
      
      <div className="text-sm font-medium text-gray-700 mb-1">
        {label}
      </div>
      
      {subtitle && (
        <div className="text-xs text-gray-500">
          {subtitle}
        </div>
      )}
    </div>
  );
};

interface KPIGridProps {
  children: React.ReactNode;
  className?: string;
  columns?: 1 | 2 | 3 | 4 | 5 | 6;
}

export const KPIGrid: React.FC<KPIGridProps> = ({
  children,
  className = '',
  columns = 4
}) => {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5',
    6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6'
  };

  return (
    <div className={cn(
      'grid gap-6',
      gridClasses[columns],
      className
    )}>
      {children}
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: string;
    type: 'increase' | 'decrease' | 'neutral';
    period?: string;
  };
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  icon,
  color = 'blue',
  className = ''
}) => {
  const colorClasses = {
    blue: 'border-blue-200 bg-blue-50/50',
    green: 'border-green-200 bg-green-50/50',
    orange: 'border-orange-200 bg-orange-50/50',
    red: 'border-red-200 bg-red-50/50',
    purple: 'border-purple-200 bg-purple-50/50'
  };

  const changeColorClasses = {
    increase: 'text-green-600',
    decrease: 'text-red-600',
    neutral: 'text-gray-600'
  };

  return (
    <div className={cn(
      'bg-white rounded-lg border p-4 transition-all duration-200 hover:shadow-md',
      colorClasses[color],
      className
    )}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium text-gray-700">
          {title}
        </div>
        {icon && (
          <div className="text-gray-400">
            {icon}
          </div>
        )}
      </div>
      
      <div className="text-2xl font-bold text-gray-900 mb-1">
        {value}
      </div>
      
      {change && (
        <div className={cn(
          'flex items-center gap-1 text-xs font-medium',
          changeColorClasses[change.type]
        )}>
          {change.type === 'increase' && <FiTrendingUp className="w-3 h-3" />}
          {change.type === 'decrease' && <FiTrendingDown className="w-3 h-3" />}
          {change.type === 'neutral' && <FiActivity className="w-3 h-3" />}
          {change.value}
          {change.period && <span className="text-gray-500 ml-1">{change.period}</span>}
        </div>
      )}
    </div>
  );
};