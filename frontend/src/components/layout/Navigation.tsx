import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  FaHome,
  FaFileAlt,
  FaFileContract,
  FaExchangeAlt,
  FaShieldAlt,
  FaCog,
  FaQuestionCircle,
  FaChevronDown,
  FaChevronRight,
  FaUserCheck
} from 'react-icons/fa';

interface NavigationProps {
  isMobileMenuOpen?: boolean;
  onMobileMenuClose?: () => void;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  children?: NavItem[];
}

const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: FaHome,
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: FaFileAlt,
    children: [
      { name: 'All Documents', href: '/documents', icon: FaFileAlt },
      { name: 'Upload Document', href: '/documents/upload', icon: FaFileAlt },
      { name: 'Categories', href: '/documents/categories', icon: FaFileAlt },
    ],
  },
  {
    name: 'Letter of Authority',
    href: '/loa',
    icon: FaFileContract,
    children: [
      { name: 'All LOAs', href: '/loa', icon: FaFileContract },
      { name: 'Create LOA', href: '/loa/create', icon: FaFileContract },
      { name: 'Templates', href: '/loa/templates', icon: FaFileContract },
    ],
  },
  {
    name: 'EDI Jobs',
    href: '/edi',
    icon: FaExchangeAlt,
    children: [
      { name: 'All Jobs', href: '/edi', icon: FaExchangeAlt },
      { name: 'Register Job', href: '/edi/register', icon: FaExchangeAlt },
      { name: 'Messages', href: '/edi/messages', icon: FaExchangeAlt },
    ],
  },
  {
    name: 'Broker Review',
    href: '/broker-review',
    icon: FaUserCheck,
  },
  {
    name: 'Compliance',
    href: '/compliance',
    icon: FaShieldAlt,
    children: [
      { name: 'Overview', href: '/compliance', icon: FaShieldAlt },
      { name: 'Requirements', href: '/compliance/requirements', icon: FaShieldAlt },
      { name: 'Audits', href: '/compliance/audits', icon: FaShieldAlt },
      { name: 'Reports', href: '/compliance/reports', icon: FaShieldAlt },
    ],
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: FaCog,
  },
  {
    name: 'Help & Support',
    href: '/help',
    icon: FaQuestionCircle,
  },
];

const Navigation: React.FC<NavigationProps> = ({ 
  isMobileMenuOpen = false, 
  onMobileMenuClose 
}) => {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  const handleNavClick = () => {
    if (onMobileMenuClose) {
      onMobileMenuClose();
    }
  };

  const renderNavItem = (item: NavItem, level = 0) => {
    const isExpanded = expandedItems.includes(item.name);
    const hasChildren = item.children && item.children.length > 0;
    const Icon = item.icon;

    return (
      <div key={item.name}>
        {hasChildren ? (
          <button
            onClick={() => toggleExpanded(item.name)}
            className={`
              w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md
              text-gray-600 hover:text-gray-900 hover:bg-gray-100
              ${level > 0 ? 'ml-6' : ''}
            `}
          >
            <div className="flex items-center">
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </div>
            {isExpanded ? (
              <FaChevronDown className="h-4 w-4" />
            ) : (
              <FaChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : (
          <NavLink
            to={item.href}
            onClick={handleNavClick}
            className={({ isActive }) => `
              flex items-center px-3 py-2 text-sm font-medium rounded-md
              ${level > 0 ? 'ml-6' : ''}
              ${isActive 
                ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }
            `}
          >
            <Icon className="mr-3 h-5 w-5" />
            {item.name}
          </NavLink>
        )}
        
        {hasChildren && isExpanded && (
          <div className="mt-1 space-y-1">
            {item.children!.map(child => renderNavItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Mobile menu overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onMobileMenuClose}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75"></div>
        </div>
      )}

      {/* Navigation sidebar */}
      <nav className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo area for mobile */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 lg:hidden">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">CB</span>
              </div>
              <span className="ml-2 text-lg font-semibold text-gray-900">
                Customs Broker Portal
              </span>
            </div>
          </div>

          {/* Navigation items */}
          <div className="flex-1 px-4 py-6 overflow-y-auto">
            <div className="space-y-1">
              {navigationItems.map(item => renderNavItem(item))}
            </div>
          </div>

          {/* Footer */}
          <div className="flex-shrink-0 border-t border-gray-200 p-4">
            <div className="text-xs text-gray-500 text-center">
              <p>Customs Broker Portal</p>
              <p>Version 1.0.0</p>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;