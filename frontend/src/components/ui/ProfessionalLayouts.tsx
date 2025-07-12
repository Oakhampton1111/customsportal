import React from 'react';
import { cn } from '../../lib/utils';
import { FiMaximize2, FiMinimize2, FiMoreVertical, FiX } from 'react-icons/fi';

interface SplitPanelProps {
  left: React.ReactNode;
  right: React.ReactNode;
  leftWidth?: string;
  rightWidth?: string;
  resizable?: boolean;
  minLeftWidth?: number;
  minRightWidth?: number;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

export function SplitPanel({
  left,
  right,
  leftWidth = '50%',
  rightWidth = '50%',
  resizable = true,
  minLeftWidth = 200,
  minRightWidth = 200,
  className = '',
  orientation = 'horizontal'
}: SplitPanelProps) {
  const [leftSize, setLeftSize] = React.useState(leftWidth);
  const [isResizing, setIsResizing] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!resizable) return;
    setIsResizing(true);
    e.preventDefault();
  };

  React.useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const container = containerRef.current;
      const rect = container.getBoundingClientRect();
      
      if (orientation === 'horizontal') {
        const newLeftWidth = e.clientX - rect.left;
        const containerWidth = rect.width;
        
        if (newLeftWidth >= minLeftWidth && containerWidth - newLeftWidth >= minRightWidth) {
          setLeftSize(`${(newLeftWidth / containerWidth) * 100}%`);
        }
      } else {
        const newLeftHeight = e.clientY - rect.top;
        const containerHeight = rect.height;
        
        if (newLeftHeight >= minLeftWidth && containerHeight - newLeftHeight >= minRightWidth) {
          setLeftSize(`${(newLeftHeight / containerHeight) * 100}%`);
        }
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, minLeftWidth, minRightWidth, orientation]);

  const flexDirection = orientation === 'horizontal' ? 'flex-row' : 'flex-col';
  const resizerClasses = orientation === 'horizontal' 
    ? 'w-1 cursor-col-resize hover:bg-blue-500' 
    : 'h-1 cursor-row-resize hover:bg-blue-500';

  return (
    <div 
      ref={containerRef}
      className={cn('flex h-full', flexDirection, className)}
    >
      <div 
        className="overflow-hidden"
        style={{ 
          [orientation === 'horizontal' ? 'width' : 'height']: leftSize 
        }}
      >
        {left}
      </div>
      
      {resizable && (
        <div
          className={cn('bg-gray-200 transition-colors', resizerClasses)}
          onMouseDown={handleMouseDown}
        />
      )}
      
      <div className="flex-1 overflow-hidden">
        {right}
      </div>
    </div>
  );
}

interface MasterDetailProps {
  masterList: React.ReactNode;
  detailView: React.ReactNode;
  masterWidth?: string;
  showDetail?: boolean;
  onCloseDetail?: () => void;
  className?: string;
  responsive?: boolean;
}

export function MasterDetail({
  masterList,
  detailView,
  masterWidth = '400px',
  showDetail = true,
  onCloseDetail,
  className = '',
  responsive = true
}: MasterDetailProps) {
  const [isMobile, setIsMobile] = React.useState(false);

  React.useEffect(() => {
    if (!responsive) return;

    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [responsive]);

  if (responsive && isMobile) {
    return (
      <div className={cn('h-full', className)}>
        {showDetail ? (
          <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
              <h2 className="font-semibold text-gray-900">Details</h2>
              {onCloseDetail && (
                <button
                  onClick={onCloseDetail}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <FiX className="w-5 h-5" />
                </button>
              )}
            </div>
            <div className="flex-1 overflow-auto">
              {detailView}
            </div>
          </div>
        ) : (
          masterList
        )}
      </div>
    );
  }

  return (
    <div className={cn('flex h-full', className)}>
      <div 
        className="border-r border-gray-200 overflow-hidden"
        style={{ width: masterWidth }}
      >
        {masterList}
      </div>
      
      {showDetail && (
        <div className="flex-1 overflow-hidden">
          {detailView}
        </div>
      )}
    </div>
  );
}

interface TabPanelProps {
  tabs: Array<{
    id: string;
    label: string;
    content: React.ReactNode;
    badge?: string | number;
    disabled?: boolean;
  }>;
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
  size?: 'small' | 'medium' | 'large';
}

export function TabPanel({
  tabs,
  activeTab,
  onTabChange,
  className = '',
  variant = 'default',
  size = 'medium'
}: TabPanelProps) {
  const sizeClasses = {
    small: 'px-3 py-2 text-sm',
    medium: 'px-4 py-3 text-base',
    large: 'px-6 py-4 text-lg'
  };

  const variantClasses = {
    default: {
      container: 'border-b border-gray-200',
      tab: 'border-b-2 border-transparent hover:border-gray-300',
      active: 'border-blue-500 text-blue-600',
      inactive: 'text-gray-500 hover:text-gray-700'
    },
    pills: {
      container: 'bg-gray-100 p-1 rounded-lg',
      tab: 'rounded-md transition-colors',
      active: 'bg-white text-gray-900 shadow-sm',
      inactive: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
    },
    underline: {
      container: '',
      tab: 'border-b-2 border-transparent',
      active: 'border-blue-500 text-blue-600',
      inactive: 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
    }
  };

  const activeTabContent = tabs.find(tab => tab.id === activeTab)?.content;

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className={cn('flex', variantClasses[variant].container)}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => !tab.disabled && onTabChange(tab.id)}
            disabled={tab.disabled}
            className={cn(
              'flex items-center gap-2 font-medium transition-colors',
              sizeClasses[size],
              variantClasses[variant].tab,
              activeTab === tab.id 
                ? variantClasses[variant].active 
                : variantClasses[variant].inactive,
              tab.disabled && 'opacity-50 cursor-not-allowed'
            )}
          >
            <span>{tab.label}</span>
            {tab.badge && (
              <span className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded-full">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
      
      <div className="flex-1 overflow-auto">
        {activeTabContent}
      </div>
    </div>
  );
}

interface AccordionItem {
  id: string;
  title: string;
  content: React.ReactNode;
  disabled?: boolean;
  badge?: string | number;
}

interface AccordionProps {
  items: AccordionItem[];
  expandedItems: string[];
  onToggle: (itemId: string) => void;
  allowMultiple?: boolean;
  className?: string;
  variant?: 'default' | 'bordered' | 'filled';
}

export function Accordion({
  items,
  expandedItems,
  onToggle,
  allowMultiple = true,
  className = '',
  variant = 'default'
}: AccordionProps) {
  const handleToggle = (itemId: string) => {
    if (!allowMultiple) {
      onToggle(expandedItems.includes(itemId) ? '' : itemId);
    } else {
      onToggle(itemId);
    }
  };

  const variantClasses = {
    default: 'border-b border-gray-200',
    bordered: 'border border-gray-200 rounded-lg mb-2',
    filled: 'bg-gray-50 rounded-lg mb-2'
  };

  return (
    <div className={cn('space-y-0', className)}>
      {items.map((item) => {
        const isExpanded = expandedItems.includes(item.id);
        
        return (
          <div key={item.id} className={variantClasses[variant]}>
            <button
              onClick={() => !item.disabled && handleToggle(item.id)}
              disabled={item.disabled}
              className={cn(
                'w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors',
                item.disabled && 'opacity-50 cursor-not-allowed',
                variant === 'bordered' && 'rounded-lg',
                variant === 'filled' && 'rounded-lg'
              )}
            >
              <div className="flex items-center gap-3">
                <span className="font-medium text-gray-900">{item.title}</span>
                {item.badge && (
                  <span className="px-2 py-0.5 text-xs bg-gray-200 text-gray-700 rounded-full">
                    {item.badge}
                  </span>
                )}
              </div>
              <FiMoreVertical 
                className={cn(
                  'w-4 h-4 text-gray-400 transition-transform',
                  isExpanded && 'rotate-90'
                )}
              />
            </button>
            
            {isExpanded && (
              <div className="px-4 pb-4">
                {item.content}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

interface GridLayoutProps {
  children: React.ReactNode;
  columns?: number | { sm?: number; md?: number; lg?: number; xl?: number };
  gap?: number;
  className?: string;
  autoFit?: boolean;
  minItemWidth?: string;
}

export function GridLayout({
  children,
  columns = 3,
  gap = 4,
  className = '',
  autoFit = false,
  minItemWidth = '250px'
}: GridLayoutProps) {
  const getGridClasses = () => {
    if (autoFit) {
      return `grid-cols-[repeat(auto-fit,minmax(${minItemWidth},1fr))]`;
    }

    if (typeof columns === 'number') {
      return `grid-cols-${columns}`;
    }

    const responsiveClasses = [];
    if (columns.sm) responsiveClasses.push(`sm:grid-cols-${columns.sm}`);
    if (columns.md) responsiveClasses.push(`md:grid-cols-${columns.md}`);
    if (columns.lg) responsiveClasses.push(`lg:grid-cols-${columns.lg}`);
    if (columns.xl) responsiveClasses.push(`xl:grid-cols-${columns.xl}`);

    return `grid-cols-1 ${responsiveClasses.join(' ')}`;
  };

  return (
    <div className={cn(
      'grid',
      getGridClasses(),
      `gap-${gap}`,
      className
    )}>
      {children}
    </div>
  );
}

interface FlexLayoutProps {
  children: React.ReactNode;
  direction?: 'row' | 'column';
  wrap?: boolean;
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline';
  gap?: number;
  className?: string;
}

export function FlexLayout({
  children,
  direction = 'row',
  wrap = false,
  justify = 'start',
  align = 'start',
  gap = 0,
  className = ''
}: FlexLayoutProps) {
  const directionClass = direction === 'row' ? 'flex-row' : 'flex-col';
  const wrapClass = wrap ? 'flex-wrap' : 'flex-nowrap';
  
  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly'
  };

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
    baseline: 'items-baseline'
  };

  return (
    <div className={cn(
      'flex',
      directionClass,
      wrapClass,
      justifyClasses[justify],
      alignClasses[align],
      gap > 0 && `gap-${gap}`,
      className
    )}>
      {children}
    </div>
  );
}

interface StackProps {
  children: React.ReactNode;
  spacing?: number;
  divider?: React.ReactNode;
  className?: string;
}

export function Stack({
  children,
  spacing = 4,
  divider,
  className = ''
}: StackProps) {
  const childArray = React.Children.toArray(children);

  return (
    <div className={cn('flex flex-col', className)}>
      {childArray.map((child, index) => (
        <React.Fragment key={index}>
          <div className={index > 0 ? `mt-${spacing}` : ''}>
            {child}
          </div>
          {divider && index < childArray.length - 1 && (
            <div className={`mt-${spacing}`}>
              {divider}
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}