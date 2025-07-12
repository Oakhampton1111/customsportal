import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { BreadcrumbItem } from '../../../types/portal';

interface PortalHeaderProps {
  breadcrumbs: BreadcrumbItem[];
  user?: {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    company: string;
  };
  onToggleMobileMenu: () => void;
  onLogout?: () => void;
}

const PortalHeader: React.FC<PortalHeaderProps> = ({
  breadcrumbs,
  user,
  onToggleMobileMenu,
  onLogout,
}) => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close user menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const getInitials = (firstName: string, lastName: string): string => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  return (
    <header className="portal-header">
      {/* Left section */}
      <div className="portal-header-left">
        {/* Mobile menu toggle */}
        <button
          onClick={onToggleMobileMenu}
          className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
          aria-label="Toggle mobile menu"
        >
          <span className="text-xl">☰</span>
        </button>

        {/* Breadcrumbs */}
        <nav className="portal-header-breadcrumb" aria-label="Breadcrumb">
          {breadcrumbs.map((item, index) => (
            <React.Fragment key={index}>
              {index > 0 && (
                <span className="portal-header-breadcrumb-separator">/</span>
              )}
              {item.path && !item.isActive ? (
                <Link
                  to={item.path}
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                  {item.label}
                </Link>
              ) : (
                <span className={item.isActive ? 'font-medium text-gray-900' : ''}>
                  {item.label}
                </span>
              )}
            </React.Fragment>
          ))}
        </nav>
      </div>

      {/* Right section */}
      <div className="portal-header-right">
        {/* Notifications */}
        <button
          className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md relative"
          aria-label="Notifications"
        >
          <span className="text-xl">🔔</span>
          {/* Notification badge */}
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            3
          </span>
        </button>

        {/* User menu */}
        {user && (
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-3 p-2 text-gray-700 hover:bg-gray-100 rounded-md"
              aria-label="User menu"
              aria-expanded={userMenuOpen}
            >
              {/* User avatar */}
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                {getInitials(user.firstName, user.lastName)}
              </div>
              
              {/* User info (hidden on mobile) */}
              <div className="hidden sm:block text-left">
                <div className="text-sm font-medium text-gray-900">
                  {user.firstName} {user.lastName}
                </div>
                <div className="text-xs text-gray-500">
                  {user.company}
                </div>
              </div>

              {/* Dropdown arrow */}
              <span className={`text-gray-400 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>

            {/* User dropdown menu */}
            {userMenuOpen && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                {/* User info header */}
                <div className="px-4 py-3 border-b border-gray-100">
                  <div className="text-sm font-medium text-gray-900">
                    {user.firstName} {user.lastName}
                  </div>
                  <div className="text-sm text-gray-500">{user.email}</div>
                  <div className="text-xs text-gray-400">{user.company}</div>
                </div>

                {/* Menu items */}
                <div className="py-1">
                  <Link
                    to="/portal/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <span className="mr-3">👤</span>
                    Profile Settings
                  </Link>
                  
                  <Link
                    to="/portal/preferences"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <span className="mr-3">⚙️</span>
                    Preferences
                  </Link>
                  
                  <Link
                    to="/portal/help"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <span className="mr-3">❓</span>
                    Help & Support
                  </Link>
                </div>

                {/* Logout */}
                <div className="border-t border-gray-100 py-1">
                  <button
                    onClick={() => {
                      setUserMenuOpen(false);
                      onLogout?.();
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                  >
                    <span className="mr-3">🚪</span>
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default PortalHeader;