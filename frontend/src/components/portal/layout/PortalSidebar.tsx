import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import type { SidebarItem } from '../../../types/portal';

interface PortalSidebarProps {
  items: SidebarItem[];
  collapsed: boolean;
  mobileOpen: boolean;
  onToggleCollapse: () => void;
  onCloseMobile: () => void;
}

const PortalSidebar: React.FC<PortalSidebarProps> = ({
  items,
  collapsed,
  mobileOpen,
  onToggleCollapse,
  onCloseMobile,
}) => {
  const location = useLocation();

  // Icon mapping for sidebar items
  const getIcon = (iconName: string) => {
    const icons: Record<string, string> = {
      dashboard: '📊',
      briefcase: '💼',
      document: '📄',
      'credit-card': '💳',
      clock: '🕐',
      support: '🎧',
      menu: '☰',
      close: '✕',
    };
    return icons[iconName] || '•';
  };

  const isItemActive = (item: SidebarItem): boolean => {
    return location.pathname === item.path || location.pathname.startsWith(item.path + '/');
  };

  return (
    <>
      <aside className={`portal-sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        {/* Logo section */}
        <div className="portal-sidebar-logo">
          {!collapsed && (
            <div className="flex items-center justify-center">
              <span className="text-xl font-bold text-white">Cargoclear</span>
            </div>
          )}
          {collapsed && (
            <div className="flex items-center justify-center">
              <span className="text-xl font-bold text-white">C</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="portal-sidebar-nav">
          {items.map((item) => {
            const isActive = isItemActive(item);
            
            return (
              <Link
                key={item.id}
                to={item.path}
                className={`portal-sidebar-nav-item ${isActive ? 'active' : ''}`}
                onClick={onCloseMobile}
                title={collapsed ? item.label : undefined}
              >
                <span className="portal-sidebar-nav-item-icon">
                  {getIcon(item.icon)}
                </span>
                <span className="portal-sidebar-nav-item-text">
                  {item.label}
                </span>
                {item.badge && !collapsed && (
                  <span className="ml-auto bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle (desktop only) */}
        <div className="hidden md:block absolute bottom-4 left-4 right-4">
          <button
            onClick={onToggleCollapse}
            className="w-full flex items-center justify-center p-2 text-white hover:bg-white hover:bg-opacity-10 rounded-md transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <span className="portal-sidebar-nav-item-icon">
              {collapsed ? '→' : '←'}
            </span>
            {!collapsed && (
              <span className="portal-sidebar-nav-item-text ml-2">
                Collapse
              </span>
            )}
          </button>
        </div>
      </aside>
    </>
  );
};

export default PortalSidebar;