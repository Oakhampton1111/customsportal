import React from 'react';
import { cn } from '../../lib/utils';

interface ProfessionalCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'intelligence' | 'kpi' | 'metric' | 'alert' | 'recommendation';
  density?: 'compact' | 'normal' | 'spacious';
  interactive?: boolean;
  status?: 'default' | 'success' | 'warning' | 'error' | 'info';
  elevation?: 'none' | 'sm' | 'md' | 'lg';
  border?: 'none' | 'subtle' | 'accent' | 'strong';
}

export const ProfessionalCard: React.FC<ProfessionalCardProps> = ({
  children,
  className = '',
  variant = 'default',
  density = 'normal',
  interactive = false,
  status = 'default',
  elevation = 'sm',
  border = 'subtle',
  ...props
}) => {
  const baseClasses = `
    bg-white rounded-lg transition-all duration-200 overflow-hidden
    ${interactive ? 'cursor-pointer hover:shadow-md hover:-translate-y-0.5' : ''}
  `;

  const variantClasses = {
    default: 'border-gray-200',
    intelligence: 'border-blue-200 bg-gradient-to-br from-blue-50/50 to-white',
    kpi: 'border-gray-200 hover:border-blue-300',
    metric: 'border-gray-200 bg-gradient-to-br from-gray-50/30 to-white',
    alert: 'border-orange-200 bg-gradient-to-br from-orange-50/50 to-white',
    recommendation: 'border-green-200 bg-gradient-to-br from-green-50/50 to-white'
  };

  const densityClasses = {
    compact: 'p-3',
    normal: 'p-4',
    spacious: 'p-6'
  };

  const statusClasses = {
    default: '',
    success: 'border-l-4 border-l-green-500',
    warning: 'border-l-4 border-l-orange-500',
    error: 'border-l-4 border-l-red-500',
    info: 'border-l-4 border-l-blue-500'
  };

  const elevationClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg'
  };

  const borderClasses = {
    none: 'border-0',
    subtle: 'border border-gray-200',
    accent: 'border-2 border-blue-200',
    strong: 'border-2 border-gray-300'
  };

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        densityClasses[density],
        statusClasses[status],
        elevationClasses[elevation],
        borderClasses[border],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

interface ProfessionalCardHeaderProps {
  children: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  subtitle?: string;
}

export const ProfessionalCardHeader: React.FC<ProfessionalCardHeaderProps> = ({
  children,
  className = '',
  icon,
  actions,
  subtitle
}) => (
  <div className={cn('flex items-start justify-between mb-4', className)}>
    <div className="flex items-center gap-3 flex-1 min-w-0">
      {icon && (
        <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-blue-100 text-blue-600">
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <h3 className="text-lg font-semibold text-gray-900 truncate">
          {children}
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
);

interface ProfessionalCardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const ProfessionalCardContent: React.FC<ProfessionalCardContentProps> = ({
  children,
  className = ''
}) => (
  <div className={cn('text-gray-700', className)}>
    {children}
  </div>
);

interface ProfessionalCardFooterProps {
  children: React.ReactNode;
  className?: string;
  bordered?: boolean;
}

export const ProfessionalCardFooter: React.FC<ProfessionalCardFooterProps> = ({
  children,
  className = '',
  bordered = true
}) => (
  <div className={cn(
    'mt-4 pt-4',
    bordered && 'border-t border-gray-100',
    className
  )}>
    {children}
  </div>
);