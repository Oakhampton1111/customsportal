import React from 'react';
import { cn } from '../../lib/utils';
import { FiAlertCircle, FiCheck, FiSearch, FiEye, FiEyeOff } from 'react-icons/fi';

interface ProfessionalInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'default' | 'search' | 'password';
  density?: 'compact' | 'normal' | 'spacious';
}

export const ProfessionalInput: React.FC<ProfessionalInputProps> = ({
  label,
  error,
  success,
  hint,
  leftIcon,
  rightIcon,
  variant = 'default',
  density = 'normal',
  className = '',
  type = 'text',
  ...props
}) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [isFocused, setIsFocused] = React.useState(false);

  const densityClasses = {
    compact: 'px-3 py-2 text-sm',
    normal: 'px-4 py-3 text-sm',
    spacious: 'px-5 py-4 text-base'
  };

  const inputType = variant === 'password' ? (showPassword ? 'text' : 'password') : type;

  const inputClasses = cn(
    'w-full border rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1',
    densityClasses[density],
    leftIcon && 'pl-10',
    (rightIcon || variant === 'password') && 'pr-10',
    error 
      ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
      : success
      ? 'border-green-300 focus:border-green-500 focus:ring-green-200'
      : isFocused
      ? 'border-blue-500 focus:border-blue-500 focus:ring-blue-200'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200',
    'bg-white hover:border-gray-400',
    className
  );

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {leftIcon}
          </div>
        )}
        
        {variant === 'search' && !leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <FiSearch className="w-4 h-4" />
          </div>
        )}
        
        <input
          type={inputType}
          className={cn(
            inputClasses,
            variant === 'search' && !leftIcon && 'pl-10'
          )}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
        
        {variant === 'password' && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
          </button>
        )}
        
        {rightIcon && variant !== 'password' && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            {rightIcon}
          </div>
        )}
        
        {error && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-red-500">
            <FiAlertCircle className="w-4 h-4" />
          </div>
        )}
        
        {success && !rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-green-500">
            <FiCheck className="w-4 h-4" />
          </div>
        )}
      </div>
      
      {(error || success || hint) && (
        <div className="space-y-1">
          {error && (
            <p className="text-sm text-red-600 flex items-center gap-1">
              <FiAlertCircle className="w-3 h-3" />
              {error}
            </p>
          )}
          {success && (
            <p className="text-sm text-green-600 flex items-center gap-1">
              <FiCheck className="w-3 h-3" />
              {success}
            </p>
          )}
          {hint && !error && !success && (
            <p className="text-sm text-gray-500">
              {hint}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

interface ProfessionalSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  success?: string;
  hint?: string;
  options: Array<{ value: string; label: string; disabled?: boolean }>;
  placeholder?: string;
  density?: 'compact' | 'normal' | 'spacious';
}

export const ProfessionalSelect: React.FC<ProfessionalSelectProps> = ({
  label,
  error,
  success,
  hint,
  options,
  placeholder,
  density = 'normal',
  className = '',
  ...props
}) => {
  const densityClasses = {
    compact: 'px-3 py-2 text-sm',
    normal: 'px-4 py-3 text-sm',
    spacious: 'px-5 py-4 text-base'
  };

  const selectClasses = cn(
    'w-full border rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 bg-white',
    densityClasses[density],
    error 
      ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
      : success
      ? 'border-green-300 focus:border-green-500 focus:ring-green-200'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200 hover:border-gray-400',
    className
  );

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <select className={selectClasses} {...props}>
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option 
              key={option.value} 
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        {error && (
          <div className="absolute right-8 top-1/2 transform -translate-y-1/2 text-red-500">
            <FiAlertCircle className="w-4 h-4" />
          </div>
        )}
        
        {success && (
          <div className="absolute right-8 top-1/2 transform -translate-y-1/2 text-green-500">
            <FiCheck className="w-4 h-4" />
          </div>
        )}
      </div>
      
      {(error || success || hint) && (
        <div className="space-y-1">
          {error && (
            <p className="text-sm text-red-600 flex items-center gap-1">
              <FiAlertCircle className="w-3 h-3" />
              {error}
            </p>
          )}
          {success && (
            <p className="text-sm text-green-600 flex items-center gap-1">
              <FiCheck className="w-3 h-3" />
              {success}
            </p>
          )}
          {hint && !error && !success && (
            <p className="text-sm text-gray-500">
              {hint}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

interface ProfessionalTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  success?: string;
  hint?: string;
  density?: 'compact' | 'normal' | 'spacious';
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export const ProfessionalTextarea: React.FC<ProfessionalTextareaProps> = ({
  label,
  error,
  success,
  hint,
  density = 'normal',
  resize = 'vertical',
  className = '',
  ...props
}) => {
  const densityClasses = {
    compact: 'px-3 py-2 text-sm',
    normal: 'px-4 py-3 text-sm',
    spacious: 'px-5 py-4 text-base'
  };

  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize'
  };

  const textareaClasses = cn(
    'w-full border rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 bg-white',
    densityClasses[density],
    resizeClasses[resize],
    error 
      ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
      : success
      ? 'border-green-300 focus:border-green-500 focus:ring-green-200'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200 hover:border-gray-400',
    className
  );

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <textarea className={textareaClasses} {...props} />
        
        {error && (
          <div className="absolute right-3 top-3 text-red-500">
            <FiAlertCircle className="w-4 h-4" />
          </div>
        )}
        
        {success && (
          <div className="absolute right-3 top-3 text-green-500">
            <FiCheck className="w-4 h-4" />
          </div>
        )}
      </div>
      
      {(error || success || hint) && (
        <div className="space-y-1">
          {error && (
            <p className="text-sm text-red-600 flex items-center gap-1">
              <FiAlertCircle className="w-3 h-3" />
              {error}
            </p>
          )}
          {success && (
            <p className="text-sm text-green-600 flex items-center gap-1">
              <FiCheck className="w-3 h-3" />
              {success}
            </p>
          )}
          {hint && !error && !success && (
            <p className="text-sm text-gray-500">
              {hint}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

interface FormGroupProps {
  children: React.ReactNode;
  className?: string;
  layout?: 'vertical' | 'horizontal' | 'inline';
  spacing?: 'tight' | 'normal' | 'loose';
}

export const FormGroup: React.FC<FormGroupProps> = ({
  children,
  className = '',
  layout = 'vertical',
  spacing = 'normal'
}) => {
  const layoutClasses = {
    vertical: 'flex flex-col',
    horizontal: 'flex flex-row items-end',
    inline: 'flex flex-row items-center'
  };

  const spacingClasses = {
    tight: 'gap-2',
    normal: 'gap-4',
    loose: 'gap-6'
  };

  return (
    <div className={cn(
      layoutClasses[layout],
      spacingClasses[spacing],
      className
    )}>
      {children}
    </div>
  );
};

interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  className = '',
  collapsible = false,
  defaultExpanded = true
}) => {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);

  return (
    <div className={cn('border border-gray-200 rounded-lg', className)}>
      <div 
        className={cn(
          'p-4 border-b border-gray-200 bg-gray-50',
          collapsible && 'cursor-pointer hover:bg-gray-100'
        )}
        onClick={collapsible ? () => setIsExpanded(!isExpanded) : undefined}
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {title}
            </h3>
            {description && (
              <p className="text-sm text-gray-600 mt-1">
                {description}
              </p>
            )}
          </div>
          {collapsible && (
            <div className={cn(
              'transform transition-transform duration-200',
              isExpanded ? 'rotate-180' : ''
            )}>
              ↓
            </div>
          )}
        </div>
      </div>
      {(!collapsible || isExpanded) && (
        <div className="p-6">
          {children}
        </div>
      )}
    </div>
  );
};