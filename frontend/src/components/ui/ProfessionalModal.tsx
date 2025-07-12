import React from 'react';
import { cn } from '../../lib/utils';
import { FiX, FiAlertTriangle, FiCheckCircle, FiInfo, FiAlertCircle } from 'react-icons/fi';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large' | 'xlarge' | 'fullscreen';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  className?: string;
  overlayClassName?: string;
  contentClassName?: string;
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  className = '',
  overlayClassName = '',
  contentClassName = ''
}: ModalProps) {
  const modalRef = React.useRef<HTMLDivElement>(null);

  // Handle escape key
  React.useEffect(() => {
    if (!closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose, closeOnEscape]);

  // Handle body scroll lock
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Focus management
  React.useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const sizeClasses = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    xlarge: 'max-w-4xl',
    fullscreen: 'max-w-none w-full h-full m-0 rounded-none'
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center p-4',
        overlayClassName
      )}
      onClick={handleOverlayClick}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black bg-opacity-50 transition-opacity" />
      
      {/* Modal Content */}
      <div
        ref={modalRef}
        tabIndex={-1}
        className={cn(
          'relative bg-white rounded-lg shadow-xl w-full',
          sizeClasses[size],
          size === 'fullscreen' ? 'h-full' : 'max-h-[90vh]',
          className
        )}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            {title && (
              <h2 className="text-lg font-semibold text-gray-900">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <FiX className="w-5 h-5 text-gray-500" />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className={cn(
          'overflow-auto',
          size === 'fullscreen' ? 'flex-1' : 'max-h-[calc(90vh-8rem)]',
          contentClassName
        )}>
          {children}
        </div>
      </div>
    </div>
  );
}

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  type?: 'default' | 'warning' | 'danger' | 'success' | 'info';
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export function Dialog({
  isOpen,
  onClose,
  title,
  description,
  children,
  actions,
  type = 'default',
  size = 'medium',
  className = ''
}: DialogProps) {
  const typeIcons = {
    default: null,
    warning: <FiAlertTriangle className="w-6 h-6 text-yellow-600" />,
    danger: <FiAlertCircle className="w-6 h-6 text-red-600" />,
    success: <FiCheckCircle className="w-6 h-6 text-green-600" />,
    info: <FiInfo className="w-6 h-6 text-blue-600" />
  };

  const typeColors = {
    default: '',
    warning: 'border-yellow-200 bg-yellow-50',
    danger: 'border-red-200 bg-red-50',
    success: 'border-green-200 bg-green-50',
    info: 'border-blue-200 bg-blue-50'
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size={size}
      className={className}
    >
      <div className="p-6">
        <div className="flex items-start gap-4">
          {typeIcons[type] && (
            <div className="flex-shrink-0">
              {typeIcons[type]}
            </div>
          )}
          
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {title}
            </h3>
            
            {description && (
              <p className="text-sm text-gray-600 mb-4">
                {description}
              </p>
            )}
            
            {children && (
              <div className={cn(
                'p-4 rounded-lg border',
                typeColors[type] || 'border-gray-200 bg-gray-50'
              )}>
                {children}
              </div>
            )}
          </div>
        </div>
        
        {actions && (
          <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200">
            {actions}
          </div>
        )}
      </div>
    </Modal>
  );
}

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'danger';
  loading?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'warning',
  loading = false
}: ConfirmDialogProps) {
  const handleConfirm = () => {
    onConfirm();
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      description={message}
      type={type}
      size="small"
      actions={
        <>
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className={cn(
              'px-4 py-2 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50',
              type === 'danger'
                ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                : 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
            )}
          >
            {loading ? 'Processing...' : confirmText}
          </button>
        </>
      }
    />
  );
}

interface FormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  title: string;
  children: React.ReactNode;
  submitText?: string;
  cancelText?: string;
  loading?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export function FormDialog({
  isOpen,
  onClose,
  onSubmit,
  title,
  children,
  submitText = 'Save',
  cancelText = 'Cancel',
  loading = false,
  size = 'medium'
}: FormDialogProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const data = Object.fromEntries(formData.entries());
    onSubmit(data);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size={size}
    >
      <form onSubmit={handleSubmit}>
        <div className="p-6">
          {children}
        </div>
        
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Saving...' : submitText}
          </button>
        </div>
      </form>
    </Modal>
  );
}

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  position?: 'left' | 'right' | 'top' | 'bottom';
  size?: 'small' | 'medium' | 'large';
  overlay?: boolean;
  className?: string;
}

export function Drawer({
  isOpen,
  onClose,
  title,
  children,
  position = 'right',
  size = 'medium',
  overlay = true,
  className = ''
}: DrawerProps) {
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const sizeClasses = {
    small: position === 'left' || position === 'right' ? 'w-80' : 'h-80',
    medium: position === 'left' || position === 'right' ? 'w-96' : 'h-96',
    large: position === 'left' || position === 'right' ? 'w-[32rem]' : 'h-[32rem]'
  };

  const positionClasses = {
    left: 'left-0 top-0 h-full',
    right: 'right-0 top-0 h-full',
    top: 'top-0 left-0 w-full',
    bottom: 'bottom-0 left-0 w-full'
  };

  const transformClasses = {
    left: isOpen ? 'translate-x-0' : '-translate-x-full',
    right: isOpen ? 'translate-x-0' : 'translate-x-full',
    top: isOpen ? 'translate-y-0' : '-translate-y-full',
    bottom: isOpen ? 'translate-y-0' : 'translate-y-full'
  };

  if (!isOpen && !overlay) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Overlay */}
      {overlay && (
        <div
          className={cn(
            'absolute inset-0 bg-black transition-opacity duration-300',
            isOpen ? 'bg-opacity-50' : 'bg-opacity-0 pointer-events-none'
          )}
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div
        className={cn(
          'absolute bg-white shadow-xl transition-transform duration-300 ease-in-out',
          positionClasses[position],
          sizeClasses[size],
          transformClasses[position],
          className
        )}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-100 rounded-full transition-colors"
            >
              <FiX className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

interface PopoverProps {
  isOpen: boolean;
  onClose: () => void;
  trigger: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  align?: 'start' | 'center' | 'end';
  offset?: number;
  className?: string;
}

export function Popover({
  isOpen,
  onClose,
  trigger,
  children,
  position = 'bottom',
  align = 'center',
  offset = 8,
  className = ''
}: PopoverProps) {
  const triggerRef = React.useRef<HTMLDivElement>(null);
  const popoverRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        popoverRef.current &&
        triggerRef.current &&
        !popoverRef.current.contains(event.target as Node) &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  const getPositionClasses = () => {
    const positions = {
      top: 'bottom-full mb-2',
      bottom: 'top-full mt-2',
      left: 'right-full mr-2',
      right: 'left-full ml-2'
    };

    const alignments = {
      start: position === 'top' || position === 'bottom' ? 'left-0' : 'top-0',
      center: position === 'top' || position === 'bottom' ? 'left-1/2 -translate-x-1/2' : 'top-1/2 -translate-y-1/2',
      end: position === 'top' || position === 'bottom' ? 'right-0' : 'bottom-0'
    };

    return `${positions[position]} ${alignments[align]}`;
  };

  return (
    <div className="relative inline-block">
      <div ref={triggerRef}>
        {trigger}
      </div>
      
      {isOpen && (
        <div
          ref={popoverRef}
          className={cn(
            'absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg',
            getPositionClasses(),
            className
          )}
          style={{ marginTop: position === 'bottom' ? offset : undefined }}
        >
          {children}
        </div>
      )}
    </div>
  );
}