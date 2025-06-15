import React from 'react';
import { cn } from '../../lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'gradient' | 'premium';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
  fullWidth?: boolean;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  elevation?: 'none' | 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  fullWidth = false,
  rounded = 'md',
  elevation = 'sm',
  ...props
}) => {
  const baseClasses = `
    inline-flex items-center justify-center font-medium transition-all duration-200 
    focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 
    disabled:cursor-not-allowed disabled:transform-none relative overflow-hidden
    ${fullWidth ? 'w-full' : ''}
  `;
  
  const variantClasses = {
    primary: `
      bg-gradient-to-r from-blue-600 to-blue-700 text-white 
      hover:from-blue-700 hover:to-blue-800 hover:shadow-lg hover:-translate-y-0.5
      focus:ring-blue-500 active:from-blue-800 active:to-blue-900
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent 
      before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300
    `,
    secondary: `
      bg-gradient-to-r from-gray-600 to-gray-700 text-white 
      hover:from-gray-700 hover:to-gray-800 hover:shadow-lg hover:-translate-y-0.5
      focus:ring-gray-500 active:from-gray-800 active:to-gray-900
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent 
      before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300
    `,
    outline: `
      border-2 border-gray-300 bg-white text-gray-700 
      hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 hover:shadow-md hover:-translate-y-0.5
      focus:ring-blue-500 focus:border-blue-500 active:bg-blue-100
    `,
    ghost: `
      text-gray-700 hover:bg-gray-100 hover:text-gray-900 hover:shadow-sm
      focus:ring-gray-500 active:bg-gray-200 hover:-translate-y-0.5
    `,
    danger: `
      bg-gradient-to-r from-red-600 to-red-700 text-white 
      hover:from-red-700 hover:to-red-800 hover:shadow-lg hover:-translate-y-0.5
      focus:ring-red-500 active:from-red-800 active:to-red-900
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent 
      before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300
    `,
    success: `
      bg-gradient-to-r from-green-600 to-green-700 text-white 
      hover:from-green-700 hover:to-green-800 hover:shadow-lg hover:-translate-y-0.5
      focus:ring-green-500 active:from-green-800 active:to-green-900
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/20 before:to-transparent 
      before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300
    `,
    gradient: `
      bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 text-white 
      hover:from-purple-700 hover:via-blue-700 hover:to-indigo-700 hover:shadow-xl hover:-translate-y-1
      focus:ring-purple-500 active:from-purple-800 active:via-blue-800 active:to-indigo-800
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/30 before:to-transparent 
      before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300
    `,
    premium: `
      bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 text-white 
      hover:from-amber-600 hover:via-yellow-600 hover:to-orange-600 hover:shadow-xl hover:-translate-y-1
      focus:ring-amber-500 active:from-amber-700 active:via-yellow-700 active:to-orange-700
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-white/30 before:to-transparent 
      before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300
    `
  };
  
  const sizeClasses = {
    xs: 'px-2 py-1 text-xs min-h-[24px]',
    sm: 'px-3 py-1.5 text-sm min-h-[32px]',
    md: 'px-4 py-2 text-sm min-h-[40px]',
    lg: 'px-6 py-3 text-base min-h-[48px]',
    xl: 'px-8 py-4 text-lg min-h-[56px]'
  };

  const roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-lg',
    lg: 'rounded-xl',
    full: 'rounded-full'
  };

  const elevationClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg'
  };

  const iconSizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
    xl: 'h-6 w-6'
  };

  const loadingSpinnerClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
    xl: 'h-6 w-6'
  };

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        roundedClasses[rounded],
        elevationClasses[elevation],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <div className={`animate-spin rounded-full border-b-2 border-current mr-2 ${loadingSpinnerClasses[size]}`} />
      ) : leftIcon ? (
        <span className={`mr-2 ${iconSizeClasses[size]} flex items-center justify-center relative z-10`}>
          {leftIcon}
        </span>
      ) : null}
      
      <span className="relative z-10">{children}</span>
      
      {rightIcon && !isLoading && (
        <span className={`ml-2 ${iconSizeClasses[size]} flex items-center justify-center relative z-10`}>
          {rightIcon}
        </span>
      )}
    </button>
  );
};
