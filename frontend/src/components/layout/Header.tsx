import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FiHome,
  FiSearch,
  FiMessageSquare,
  FiGlobe,
  FiBell,
  FiSettings,
  FiUser,
  FiMenu,
  FiX,
  FiChevronDown
} from 'react-icons/fi';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

interface UserMenuProps {
  isOpen: boolean;
  onToggle: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ isOpen, onToggle }) => (
  <div className="header__user-menu">
    <button
      onClick={onToggle}
      className="header__user-button"
      aria-expanded={isOpen}
      aria-haspopup="true"
    >
      <div className="header__user-avatar">
        <FiUser className="header__user-icon" />
      </div>
      <FiChevronDown className={`header__user-chevron ${isOpen ? 'header__user-chevron--open' : ''}`} />
    </button>
    
    {isOpen && (
      <div className="header__user-dropdown">
        <div className="header__user-info">
          <div className="header__user-name">John Doe</div>
          <div className="header__user-role">Customs Broker</div>
        </div>
        <div className="header__user-divider"></div>
        <a href="#" className="header__user-link">Profile Settings</a>
        <a href="#" className="header__user-link">Preferences</a>
        <a href="#" className="header__user-link">Help & Support</a>
        <div className="header__user-divider"></div>
        <a href="#" className="header__user-link header__user-link--danger">Sign Out</a>
      </div>
    )}
  </div>
);

export const Header: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const navigation: NavigationItem[] = [
    { 
      name: 'Dashboard', 
      href: '/', 
      icon: FiHome, 
      description: 'Overview and trade intelligence' 
    },
    { 
      name: 'Tariff Search', 
      href: '/tariff-tree', 
      icon: FiSearch, 
      description: 'Interactive Schedule 3 explorer' 
    },
    { 
      name: 'AI Assistant', 
      href: '/ai-assistant', 
      icon: FiMessageSquare, 
      description: 'AI consultation and calculations' 
    },
    { 
      name: 'Export Center', 
      href: '/export-tariffs', 
      icon: FiGlobe, 
      description: 'AHECC codes and requirements' 
    },
  ];

  const isActive = (path: string): boolean => {
    return location.pathname === path || (path === '/' && location.pathname === '/dashboard');
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Navigate to search results or trigger search
      console.log('Search:', searchQuery);
    }
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
    setIsUserMenuOpen(false);
  };

  const toggleUserMenu = () => {
    setIsUserMenuOpen(!isUserMenuOpen);
  };

  return (
    <header className="header">
      <div className="header__container">
        {/* Left Section - Branding */}
        <div className="header__brand">
          <Link to="/" className="header__logo" onClick={() => setIsMobileMenuOpen(false)}>
            <div className="header__logo-icon">
              <span className="header__logo-text">CB</span>
            </div>
            <div className="header__logo-content">
              <span className="header__logo-title">Customs Broker Portal</span>
              <span className="header__logo-subtitle">Trade Intelligence Platform</span>
            </div>
          </Link>
          <div className="header__divider"></div>
        </div>

        {/* Center Section - Main Navigation */}
        <nav className="header__nav">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`header__nav-link ${active ? 'header__nav-link--active' : ''}`}
                title={item.description}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Icon className="header__nav-icon" />
                <span className="header__nav-text">{item.name}</span>
                {active && <div className="header__nav-indicator"></div>}
              </Link>
            );
          })}
        </nav>

        {/* Right Section - User Actions */}
        <div className="header__actions">
          {/* Global Search */}
          <form onSubmit={handleSearchSubmit} className="header__search">
            <div className="header__search-input-wrapper">
              <FiSearch className="header__search-icon" />
              <input
                type="text"
                placeholder="Search tariffs, codes, regulations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="header__search-input"
                aria-label="Global search"
              />
            </div>
          </form>

          {/* Notifications */}
          <button className="header__action-button" aria-label="Notifications">
            <FiBell className="header__action-icon" />
            <span className="header__notification-badge">3</span>
          </button>

          {/* Settings */}
          <button className="header__action-button" aria-label="Settings">
            <FiSettings className="header__action-icon" />
          </button>

          {/* User Menu */}
          <UserMenu isOpen={isUserMenuOpen} onToggle={toggleUserMenu} />

          {/* Mobile Menu Toggle */}
          <button
            onClick={toggleMobileMenu}
            className="header__mobile-toggle"
            aria-label="Toggle mobile menu"
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? (
              <FiX className="header__mobile-icon" />
            ) : (
              <FiMenu className="header__mobile-icon" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Overlay */}
      {isMobileMenuOpen && (
        <div className="header__mobile-overlay">
          <div className="header__mobile-menu">
            {/* Mobile Search */}
            <form onSubmit={handleSearchSubmit} className="header__mobile-search">
              <div className="header__search-input-wrapper">
                <FiSearch className="header__search-icon" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="header__search-input"
                />
              </div>
            </form>

            {/* Mobile Navigation */}
            <nav className="header__mobile-nav">
              {navigation.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`header__mobile-link ${active ? 'header__mobile-link--active' : ''}`}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <Icon className="header__mobile-icon" />
                    <div className="header__mobile-content">
                      <span className="header__mobile-title">{item.name}</span>
                      <span className="header__mobile-description">{item.description}</span>
                    </div>
                  </Link>
                );
              })}
            </nav>

            {/* Mobile User Actions */}
            <div className="header__mobile-actions">
              <button className="header__mobile-action">
                <FiBell className="header__mobile-action-icon" />
                <span>Notifications</span>
                <span className="header__notification-badge">3</span>
              </button>
              <button className="header__mobile-action">
                <FiSettings className="header__mobile-action-icon" />
                <span>Settings</span>
              </button>
              <button className="header__mobile-action">
                <FiUser className="header__mobile-action-icon" />
                <span>Profile</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};