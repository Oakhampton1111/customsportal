import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import PortalSidebar from './PortalSidebar';
import PortalHeader from './PortalHeader';
import type { SidebarItem, BreadcrumbItem } from '../../../types/portal';
import '../../../styles/portal/portal.css';

import type { User } from '../../../types/portal';

interface PortalLayoutProps {
  user?: User;
  onLogout?: () => void;
}

const PortalLayout: React.FC<PortalLayoutProps> = ({ user, onLogout }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Sidebar navigation items
  const sidebarItems: SidebarItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'dashboard',
      path: '/portal/dashboard',
    },
    {
      id: 'jobs',
      label: 'My Jobs',
      icon: 'briefcase',
      path: '/portal/jobs',
      badge: '3', // This would come from API
    },
    {
      id: 'documents',
      label: 'Documents',
      icon: 'document',
      path: '/portal/documents',
    },
    {
      id: 'payments',
      label: 'Payments',
      icon: 'credit-card',
      path: '/portal/payments',
    },
    {
      id: 'activity',
      label: 'Activity',
      icon: 'clock',
      path: '/portal/activity',
    },
    {
      id: 'support',
      label: 'Support',
      icon: 'support',
      path: '/portal/support',
    },
  ];

  // Generate breadcrumbs based on current path
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [];

    // Always start with Portal
    breadcrumbs.push({
      label: 'Portal',
      path: '/portal',
    });

    // Map path segments to readable labels
    const segmentLabels: Record<string, string> = {
      dashboard: 'Dashboard',
      jobs: 'Jobs',
      documents: 'Documents',
      payments: 'Payments',
      activity: 'Activity',
      support: 'Support',
    };

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      if (segment === 'portal') return; // Skip portal segment

      currentPath += `/${segment}`;
      const isLast = index === pathSegments.length - 1;
      
      breadcrumbs.push({
        label: segmentLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1),
        path: isLast ? undefined : `/portal${currentPath}`,
        isActive: isLast,
      });
    });

    return breadcrumbs;
  };

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Handle escape key to close mobile menu
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const breadcrumbs = generateBreadcrumbs();

  return (
    <div className="portal-app">
      <div className="portal-layout">
        {/* Sidebar */}
        <PortalSidebar
          items={sidebarItems}
          collapsed={sidebarCollapsed}
          mobileOpen={mobileMenuOpen}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />

        {/* Mobile overlay */}
        {mobileMenuOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}

        {/* Main content area */}
        <main className={`portal-main ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          {/* Header */}
          <PortalHeader
            breadcrumbs={breadcrumbs}
            user={user}
            onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
            onLogout={onLogout}
          />

          {/* Page content */}
          <div className="portal-content">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default PortalLayout;