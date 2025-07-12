import React from 'react';
import { cn } from '../../lib/utils';
import { 
  FiDownload, 
  FiUpload, 
  FiTrash2, 
  FiEdit3, 
  FiCopy, 
  FiShare2, 
  FiFilter, 
  FiRefreshCw,
  FiMoreHorizontal,
  FiCheck,
  FiX,
  FiPlus
} from 'react-icons/fi';

interface ActionItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'default' | 'primary' | 'danger' | 'success';
  tooltip?: string;
  shortcut?: string;
}

interface ActionToolbarProps {
  actions: ActionItem[];
  selectedCount?: number;
  totalCount?: number;
  onSelectAll?: () => void;
  onClearSelection?: () => void;
  className?: string;
  size?: 'small' | 'medium' | 'large';
  layout?: 'horizontal' | 'vertical';
  showSelectionInfo?: boolean;
}

export function ActionToolbar({
  actions,
  selectedCount = 0,
  totalCount = 0,
  onSelectAll,
  onClearSelection,
  className = '',
  size = 'medium',
  layout = 'horizontal',
  showSelectionInfo = true
}: ActionToolbarProps) {
  const [showOverflow, setShowOverflow] = React.useState(false);
  const [visibleActions, setVisibleActions] = React.useState<ActionItem[]>([]);
  const [overflowActions, setOverflowActions] = React.useState<ActionItem[]>([]);

  const sizeClasses = {
    small: 'px-2 py-1 text-xs',
    medium: 'px-3 py-2 text-sm',
    large: 'px-4 py-3 text-base'
  };

  const iconSizes = {
    small: 'w-3 h-3',
    medium: 'w-4 h-4',
    large: 'w-5 h-5'
  };

  // Split actions for overflow handling
  React.useEffect(() => {
    const primaryActions = actions.slice(0, 4);
    const overflow = actions.slice(4);
    setVisibleActions(primaryActions);
    setOverflowActions(overflow);
  }, [actions]);

  const getVariantClasses = (variant: ActionItem['variant'] = 'default') => {
    const baseClasses = 'inline-flex items-center gap-2 border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
    
    switch (variant) {
      case 'primary':
        return `${baseClasses} bg-blue-600 border-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500`;
      case 'danger':
        return `${baseClasses} bg-red-600 border-red-600 text-white hover:bg-red-700 focus:ring-red-500`;
      case 'success':
        return `${baseClasses} bg-green-600 border-green-600 text-white hover:bg-green-700 focus:ring-green-500`;
      default:
        return `${baseClasses} bg-white border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-blue-500`;
    }
  };

  const layoutClasses = layout === 'horizontal' 
    ? 'flex items-center gap-2' 
    : 'flex flex-col gap-2';

  return (
    <div className={cn(
      'bg-white border border-gray-200 rounded-lg p-4',
      className
    )}>
      <div className={cn('flex items-center justify-between', layoutClasses)}>
        {/* Selection Info */}
        {showSelectionInfo && (
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-600">
              {selectedCount > 0 ? (
                <span>
                  <span className="font-medium">{selectedCount}</span> of{' '}
                  <span className="font-medium">{totalCount}</span> selected
                </span>
              ) : (
                <span>{totalCount} items</span>
              )}
            </div>
            
            {selectedCount > 0 && (
              <div className="flex items-center gap-2">
                {onSelectAll && selectedCount < totalCount && (
                  <button
                    onClick={onSelectAll}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Select all
                  </button>
                )}
                {onClearSelection && (
                  <button
                    onClick={onClearSelection}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Clear selection
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className={cn('flex items-center gap-2', layout === 'vertical' && 'w-full')}>
          {visibleActions.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              size={size}
              className={getVariantClasses(action.variant)}
              iconSize={iconSizes[size]}
              textSize={sizeClasses[size]}
            />
          ))}

          {/* Overflow Menu */}
          {overflowActions.length > 0 && (
            <div className="relative">
              <button
                onClick={() => setShowOverflow(!showOverflow)}
                className={cn(
                  getVariantClasses('default'),
                  sizeClasses[size]
                )}
              >
                <FiMoreHorizontal className={iconSizes[size]} />
              </button>

              {showOverflow && (
                <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                  {overflowActions.map((action) => (
                    <button
                      key={action.id}
                      onClick={() => {
                        action.onClick();
                        setShowOverflow(false);
                      }}
                      disabled={action.disabled}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed first:rounded-t-lg last:rounded-b-lg"
                    >
                      {action.icon}
                      <span>{action.label}</span>
                      {action.shortcut && (
                        <span className="ml-auto text-xs text-gray-400">
                          {action.shortcut}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface ActionButtonProps {
  action: ActionItem;
  size: 'small' | 'medium' | 'large';
  className: string;
  iconSize: string;
  textSize: string;
}

function ActionButton({ action, size, className, iconSize, textSize }: ActionButtonProps) {
  return (
    <button
      onClick={action.onClick}
      disabled={action.disabled}
      title={action.tooltip}
      className={cn(
        className,
        textSize,
        action.disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {action.icon && (
        <span className={iconSize}>
          {action.icon}
        </span>
      )}
      <span>{action.label}</span>
      {action.shortcut && size !== 'small' && (
        <span className="ml-1 text-xs opacity-75">
          {action.shortcut}
        </span>
      )}
    </button>
  );
}

interface BulkActionsProps {
  selectedCount: number;
  actions: ActionItem[];
  onAction: (actionId: string) => void;
  className?: string;
}

export function BulkActions({
  selectedCount,
  actions,
  onAction,
  className = ''
}: BulkActionsProps) {
  if (selectedCount === 0) return null;

  return (
    <div className={cn(
      'fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50',
      className
    )}>
      <div className="flex items-center gap-4">
        <div className="text-sm font-medium text-gray-900">
          {selectedCount} item{selectedCount !== 1 ? 's' : ''} selected
        </div>
        
        <div className="flex items-center gap-2">
          {actions.map((action) => (
            <button
              key={action.id}
              onClick={() => onAction(action.id)}
              disabled={action.disabled}
              className={cn(
                'inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                action.variant === 'danger'
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : action.variant === 'primary'
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
                action.disabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              {action.icon}
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

interface QuickActionsProps {
  actions: Array<{
    id: string;
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
    variant?: 'default' | 'primary' | 'danger';
    disabled?: boolean;
  }>;
  className?: string;
  layout?: 'grid' | 'list';
}

export function QuickActions({
  actions,
  className = '',
  layout = 'grid'
}: QuickActionsProps) {
  const layoutClasses = layout === 'grid' 
    ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3'
    : 'space-y-2';

  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg p-4', className)}>
      <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
      
      <div className={layoutClasses}>
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={action.onClick}
            disabled={action.disabled}
            className={cn(
              'flex items-center gap-3 p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors',
              layout === 'grid' && 'flex-col text-center',
              action.disabled && 'opacity-50 cursor-not-allowed',
              action.variant === 'primary' && 'border-blue-200 bg-blue-50 hover:bg-blue-100',
              action.variant === 'danger' && 'border-red-200 bg-red-50 hover:bg-red-100'
            )}
          >
            <div className={cn(
              'flex-shrink-0',
              action.variant === 'primary' && 'text-blue-600',
              action.variant === 'danger' && 'text-red-600',
              !action.variant && 'text-gray-600'
            )}>
              {action.icon}
            </div>
            <span className="text-sm font-medium text-gray-900">
              {action.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface ContextMenuProps {
  items: Array<{
    id: string;
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    disabled?: boolean;
    variant?: 'default' | 'danger';
    divider?: boolean;
  }>;
  position: { x: number; y: number };
  onClose: () => void;
  className?: string;
}

export function ContextMenu({
  items,
  position,
  onClose,
  className = ''
}: ContextMenuProps) {
  const menuRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  return (
    <div
      ref={menuRef}
      className={cn(
        'fixed bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50 min-w-[160px]',
        className
      )}
      style={{
        left: position.x,
        top: position.y
      }}
    >
      {items.map((item, index) => (
        <React.Fragment key={item.id}>
          {item.divider && index > 0 && (
            <div className="border-t border-gray-100 my-1" />
          )}
          <button
            onClick={() => {
              item.onClick();
              onClose();
            }}
            disabled={item.disabled}
            className={cn(
              'w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-gray-50 transition-colors',
              item.variant === 'danger' && 'text-red-600 hover:bg-red-50',
              item.disabled && 'opacity-50 cursor-not-allowed'
            )}
          >
            {item.icon && (
              <span className="w-4 h-4 flex-shrink-0">
                {item.icon}
              </span>
            )}
            <span>{item.label}</span>
          </button>
        </React.Fragment>
      ))}
    </div>
  );
}

// Common action presets
export const commonActions = {
  export: {
    id: 'export',
    label: 'Export',
    icon: <FiDownload className="w-4 h-4" />,
    variant: 'default' as const
  },
  import: {
    id: 'import',
    label: 'Import',
    icon: <FiUpload className="w-4 h-4" />,
    variant: 'default' as const
  },
  delete: {
    id: 'delete',
    label: 'Delete',
    icon: <FiTrash2 className="w-4 h-4" />,
    variant: 'danger' as const
  },
  edit: {
    id: 'edit',
    label: 'Edit',
    icon: <FiEdit3 className="w-4 h-4" />,
    variant: 'default' as const
  },
  copy: {
    id: 'copy',
    label: 'Copy',
    icon: <FiCopy className="w-4 h-4" />,
    variant: 'default' as const
  },
  share: {
    id: 'share',
    label: 'Share',
    icon: <FiShare2 className="w-4 h-4" />,
    variant: 'default' as const
  },
  refresh: {
    id: 'refresh',
    label: 'Refresh',
    icon: <FiRefreshCw className="w-4 h-4" />,
    variant: 'default' as const
  },
  create: {
    id: 'create',
    label: 'Create',
    icon: <FiPlus className="w-4 h-4" />,
    variant: 'primary' as const
  }
};