import React from 'react';
import { cn } from '../../lib/utils';
import { FiArrowRight, FiExternalLink, FiClock, FiAlertCircle } from 'react-icons/fi';

interface IntelligencePanelProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error';
  actions?: React.ReactNode;
  lastUpdated?: string;
}

export const IntelligencePanel: React.FC<IntelligencePanelProps> = ({
  title,
  subtitle,
  icon,
  children,
  className = '',
  variant = 'default',
  actions,
  lastUpdated
}) => {
  const variantClasses = {
    default: 'border-gray-200 bg-white',
    primary: 'border-blue-200 bg-gradient-to-br from-blue-50/50 to-white',
    success: 'border-green-200 bg-gradient-to-br from-green-50/50 to-white',
    warning: 'border-orange-200 bg-gradient-to-br from-orange-50/50 to-white',
    error: 'border-red-200 bg-gradient-to-br from-red-50/50 to-white'
  };

  return (
    <div className={cn(
      'rounded-lg border transition-all duration-200 hover:shadow-md',
      variantClasses[variant],
      className
    )}>
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3 flex-1">
            {icon && (
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-blue-100 text-blue-600">
                {icon}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900">
                {title}
              </h3>
              {subtitle && (
                <p className="text-sm text-gray-600 mt-1">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {actions && (
            <div className="flex-shrink-0 ml-4">
              {actions}
            </div>
          )}
        </div>
        {lastUpdated && (
          <div className="flex items-center gap-1 text-xs text-gray-500 mt-3">
            <FiClock className="w-3 h-3" />
            Last updated: {lastUpdated}
          </div>
        )}
      </div>
      <div className="p-6">
        {children}
      </div>
    </div>
  );
};

interface IntelligenceItemProps {
  title: string;
  description?: string;
  metadata?: Array<{ label: string; value: string; color?: string }>;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  status?: 'active' | 'pending' | 'resolved' | 'archived';
  date?: string;
  action?: {
    label: string;
    href?: string;
    onClick?: () => void;
    external?: boolean;
  };
  className?: string;
}

export const IntelligenceItem: React.FC<IntelligenceItemProps> = ({
  title,
  description,
  metadata,
  priority,
  status,
  date,
  action,
  className = ''
}) => {
  const priorityClasses = {
    low: 'bg-gray-100 text-gray-700',
    medium: 'bg-blue-100 text-blue-700',
    high: 'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700'
  };

  const statusClasses = {
    active: 'bg-green-100 text-green-700',
    pending: 'bg-yellow-100 text-yellow-700',
    resolved: 'bg-gray-100 text-gray-700',
    archived: 'bg-gray-100 text-gray-500'
  };

  return (
    <div className={cn(
      'bg-gray-50 border border-gray-200 rounded-lg p-4 transition-all duration-200 hover:bg-gray-100',
      className
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-3 mb-2">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900 text-sm">
                {title}
              </h4>
              {description && (
                <p className="text-gray-600 text-xs mt-1 line-clamp-2">
                  {description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              {priority && (
                <span className={cn(
                  'px-2 py-1 rounded text-xs font-medium',
                  priorityClasses[priority]
                )}>
                  {priority}
                </span>
              )}
              {status && (
                <span className={cn(
                  'px-2 py-1 rounded text-xs font-medium',
                  statusClasses[status]
                )}>
                  {status}
                </span>
              )}
            </div>
          </div>
          
          {metadata && metadata.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {metadata.map((item, index) => (
                <div key={index} className="flex items-center gap-1 text-xs">
                  <span className="text-gray-500">{item.label}:</span>
                  <span className={cn(
                    'font-medium',
                    item.color ? `text-${item.color}-600` : 'text-gray-700'
                  )}>
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          )}
          
          <div className="flex items-center justify-between">
            {date && (
              <div className="text-xs text-gray-500">
                {date}
              </div>
            )}
            {action && (
              <div className="ml-auto">
                {action.href ? (
                  <a
                    href={action.href}
                    className="text-blue-600 text-xs font-medium inline-flex items-center gap-1 hover:text-blue-700"
                    target={action.external ? '_blank' : undefined}
                    rel={action.external ? 'noopener noreferrer' : undefined}
                  >
                    {action.label}
                    {action.external ? (
                      <FiExternalLink className="w-3 h-3" />
                    ) : (
                      <FiArrowRight className="w-3 h-3" />
                    )}
                  </a>
                ) : (
                  <button
                    onClick={action.onClick}
                    className="text-blue-600 text-xs font-medium inline-flex items-center gap-1 hover:text-blue-700"
                  >
                    {action.label}
                    <FiArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

interface IntelligenceSummaryProps {
  items: Array<{
    label: string;
    value: string | number;
    icon?: React.ReactNode;
    color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
    trend?: string;
  }>;
  className?: string;
}

export const IntelligenceSummary: React.FC<IntelligenceSummaryProps> = ({
  items,
  className = ''
}) => {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    purple: 'text-purple-600'
  };

  return (
    <div className={cn(
      'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4',
      className
    )}>
      {items.map((item, index) => (
        <div key={index} className="bg-white rounded-lg p-4 border border-gray-100">
          <div className="flex items-center gap-2 mb-2">
            {item.icon && (
              <div className={cn(
                'w-4 h-4',
                item.color ? colorClasses[item.color] : 'text-gray-600'
              )}>
                {item.icon}
              </div>
            )}
            <span className="text-sm font-medium text-gray-700">
              {item.label}
            </span>
          </div>
          <div className="text-xl font-bold text-gray-900">
            {item.value}
          </div>
          {item.trend && (
            <div className="text-xs text-gray-500 mt-1">
              {item.trend}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

interface AlertBannerProps {
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({
  type,
  title,
  message,
  action,
  dismissible = false,
  onDismiss,
  className = ''
}) => {
  const typeClasses = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-orange-50 border-orange-200 text-orange-800',
    error: 'bg-red-50 border-red-200 text-red-800'
  };

  const iconClasses = {
    info: 'text-blue-600',
    success: 'text-green-600',
    warning: 'text-orange-600',
    error: 'text-red-600'
  };

  return (
    <div className={cn(
      'border rounded-lg p-4',
      typeClasses[type],
      className
    )}>
      <div className="flex items-start gap-3">
        <FiAlertCircle className={cn('w-5 h-5 mt-0.5', iconClasses[type])} />
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm">
            {title}
          </h4>
          {message && (
            <p className="text-sm mt-1 opacity-90">
              {message}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {action && (
            <button
              onClick={action.onClick}
              className="text-sm font-medium underline hover:no-underline"
            >
              {action.label}
            </button>
          )}
          {dismissible && onDismiss && (
            <button
              onClick={onDismiss}
              className="text-sm opacity-70 hover:opacity-100"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </div>
  );
};