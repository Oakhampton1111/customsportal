import React from 'react';

interface EnhancedCardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  elevated?: boolean;
  hoverable?: boolean;
  padding?: 'sm' | 'md' | 'lg';
  header?: React.ReactNode;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
}

export const EnhancedCard: React.FC<EnhancedCardProps> = ({
  children,
  title,
  subtitle,
  className = '',
  elevated = false,
  hoverable = true,
  padding = 'md',
  header,
  footer,
  actions
}) => {
  const getPaddingClass = () => {
    switch (padding) {
      case 'sm': return 'var(--space-4)';
      case 'lg': return 'var(--space-8)';
      default: return 'var(--space-6)';
    }
  };

  const cardClasses = [
    'card',
    elevated && 'card--elevated',
    hoverable && 'card--hoverable',
    className
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={cardClasses}
      style={{
        padding: getPaddingClass()
      }}
    >
      {(title || subtitle || header || actions) && (
        <div className="card__header">
          <div style={{ flex: 1 }}>
            {header || (
              <>
                {title && <h3 className="card__title">{title}</h3>}
                {subtitle && <p className="card__subtitle">{subtitle}</p>}
              </>
            )}
          </div>
          {actions && (
            <div style={{ marginLeft: 'var(--space-4)' }}>
              {actions}
            </div>
          )}
        </div>
      )}
      
      <div className="card__content">
        {children}
      </div>
      
      {footer && (
        <div className="card__footer" style={{
          marginTop: 'var(--space-4)',
          paddingTop: 'var(--space-4)',
          borderTop: '1px solid var(--color-gray-100)'
        }}>
          {footer}
        </div>
      )}
    </div>
  );
};

export default EnhancedCard;
