import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  variant = 'default',
  padding = 'md'
}) => {
  const baseClasses = 'bg-white rounded-lg border';
  
  const variantClasses = {
    default: 'border-gray-200',
    elevated: 'border-gray-200 shadow-md',
    outlined: 'border-gray-300 border-2'
  };
  
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div className={`${baseClasses} ${variantClasses[variant]} ${paddingClasses[padding]} ${className}`}>
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>
    {children}
  </div>
);

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
  level?: 1 | 2 | 3 | 4;
}

export const CardTitle: React.FC<CardTitleProps> = ({ 
  children, 
  className = '', 
  level = 2 
}) => {
  const levelClasses = {
    1: 'text-2xl font-bold text-gray-900',
    2: 'text-xl font-semibold text-gray-900',
    3: 'text-lg font-semibold text-gray-900',
    4: 'text-base font-semibold text-gray-900'
  };

  const headingProps = {
    className: `${levelClasses[level]} ${className}`,
    children
  };

  switch (level) {
    case 1:
      return <h1 {...headingProps} />;
    case 2:
      return <h2 {...headingProps} />;
    case 3:
      return <h3 {...headingProps} />;
    case 4:
      return <h4 {...headingProps} />;
    default:
      return <h2 {...headingProps} />;
  }
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => (
  <div className={`text-gray-600 ${className}`}>
    {children}
  </div>
);
