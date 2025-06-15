# Customs Broker Portal - Frontend Code Export

This file contains all the frontend design files for the Customs Broker Portal application.

## Project Structure

```
frontend/src/
├── App.tsx                 # Main application component
├── main.tsx               # Application entry point
├── index.css              # Global styles
├── App.css                # App-specific styles
├── pages/                 # Page components
├── components/            # Reusable components
├── styles/                # Design system styles
├── services/              # API services
├── types/                 # TypeScript type definitions
└── utils/                 # Utility functions
```

## Core Application Files

### main.tsx
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### App.tsx
```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/layout/Header';
import { Dashboard, TariffTree, AIAssistant, ExportTariffs } from './pages';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            {/* New 4-page structure */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/tariff-tree" element={<TariffTree />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
            <Route path="/export-tariffs" element={<ExportTariffs />} />
            
            {/* Legacy route redirects for backward compatibility */}
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
            <Route path="/home" element={<Navigate to="/" replace />} />
            <Route path="/search" element={<Navigate to="/ai-assistant" replace />} />
            <Route path="/duty-calculator" element={<Navigate to="/ai-assistant" replace />} />
            <Route path="/tariff-lookup" element={<Navigate to="/tariff-tree" replace />} />
            
            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
```

### App.css
```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 0;
  background-color: var(--color-gray-50);
}

/* Global layout utilities */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-container {
  min-height: calc(100vh - 80px);
  padding: 2rem 0;
}

/* Loading states */
.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

## Global Styles

### index.css
```css
/* Modern CSS Reset */
*, *::before, *::after {
  box-sizing: border-box;
}

* {
  margin: 0;
}

body {
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
}

p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}

#root {
  isolation: isolate;
}

/* Base styles */
body {
  font-family: var(--font-sans);
  background-color: var(--color-gray-50);
  color: var(--color-gray-900);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.25;
  margin-bottom: 0.5rem;
}

h1 { font-size: var(--text-3xl); }
h2 { font-size: var(--text-2xl); }
h3 { font-size: var(--text-xl); }
h4 { font-size: var(--text-lg); }
h5 { font-size: var(--text-base); }
h6 { font-size: var(--text-sm); }

/* Links */
a {
  color: var(--color-primary-600);
  text-decoration: none;
}

a:hover {
  color: var(--color-primary-700);
  text-decoration: underline;
}

/* Form elements */
input, textarea, select {
  border: 1px solid var(--color-gray-300);
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: var(--text-sm);
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Utility classes */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }
.font-medium { font-weight: 500; }

.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }

.mt-4 { margin-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
.mt-8 { margin-top: 2rem; }

.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }

.px-4 { padding-left: 1rem; padding-right: 1rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }

.rounded { border-radius: 0.25rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-xl { border-radius: 0.75rem; }

.shadow { box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }

.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.justify-center { justify-content: center; }

.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }
.gap-8 { gap: 2rem; }

.w-full { width: 100%; }
.h-full { height: 100%; }

.bg-white { background-color: #ffffff; }
.bg-gray-50 { background-color: var(--color-gray-50); }
.bg-gray-100 { background-color: var(--color-gray-100); }

.text-gray-600 { color: var(--color-gray-600); }
.text-gray-700 { color: var(--color-gray-700); }
.text-gray-900 { color: var(--color-gray-900); }

.text-xs { font-size: var(--text-xs); }
.text-sm { font-size: var(--text-sm); }
.text-base { font-size: var(--text-base); }
.text-lg { font-size: var(--text-lg); }
.text-xl { font-size: var(--text-xl); }
.text-2xl { font-size: var(--text-2xl); }
.text-3xl { font-size: var(--text-3xl); }
.text-4xl { font-size: var(--text-4xl); }

.border { border-width: 1px; }
.border-gray-200 { border-color: var(--color-gray-200); }
.border-gray-300 { border-color: var(--color-gray-300); }

.hover\:bg-gray-50:hover { background-color: var(--color-gray-50); }
.hover\:bg-gray-100:hover { background-color: var(--color-gray-100); }

.transition { transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter; }
.transition-colors { transition-property: color, background-color, border-color, text-decoration-color, fill, stroke; }
.duration-200 { transition-duration: 200ms; }

@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .md\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
```

---

*Note: This is part 1 of the frontend code export. The file will continue with page components, UI components, and design system files in subsequent sections.*

## Page Components

### pages/index.ts
```typescript
export { default as Dashboard } from './Dashboard';
export { default as TariffTree } from './TariffTree';
export { default as AIAssistant } from './AIAssistant';
export { default as ExportTariffs } from './ExportTariffs';
```

### pages/Dashboard.tsx
```typescript
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { newsApi } from '../services/newsApi';
import { rulingsApi } from '../services/rulingsApi';
import type { NewsItem, SystemAlert } from '../services/newsApi';
import type { TariffRuling } from '../services/rulingsApi';
import { Card, CardHeader, CardTitle, CardContent, Button, Alert, LoadingSpinner } from '../components/ui';
import { FiRefreshCw, FiExternalLink, FiCalendar, FiTrendingUp, FiFileText, FiAlertCircle, FiSearch, FiDollarSign, FiGlobe } from 'react-icons/fi';

const Dashboard: React.FC = () => {
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [rulings, setRulings] = useState<TariffRuling[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [newsData, alertsData, rulingsData] = await Promise.all([
        newsApi.getDashboardFeed(),
        newsApi.getAlerts(),
        rulingsApi.getRecentRulings()
      ]);

      setNewsItems(newsData.slice(0, 5));
      setAlerts(alertsData.filter(alert => !alert.read).slice(0, 3));
      setRulings(rulingsData.slice(0, 4));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const getPriorityBadgeClass = (priority: string) => {
    return `dashboard__priority-badge dashboard__priority-badge--${priority}`;
  };

  const getAlertClass = (type: string) => {
    return `dashboard__alert dashboard__alert--${type}`;
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard__loading">
          <div className="dashboard__loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard__error">
          <h2>Error Loading Dashboard</h2>
          <p>{error}</p>
          <Button onClick={loadDashboardData} className="btn btn--primary">
            <FiRefreshCw /> Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard__header">
        <h1 className="dashboard__title">Customs Intelligence Dashboard</h1>
        <p className="dashboard__subtitle">
          Your comprehensive overview of trade intelligence, regulatory updates, and compliance insights
        </p>
        <div className="dashboard__actions">
          <Button onClick={loadDashboardData} className="btn btn--secondary">
            <FiRefreshCw /> Refresh Data
          </Button>
          <Link to="/ai-assistant" className="btn btn--primary">
            <FiSearch /> Ask AI Assistant
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="dashboard__kpi-grid">
        <div className="dashboard__kpi-card">
          <div className="dashboard__kpi-value">{newsItems.length}</div>
          <div className="dashboard__kpi-label">Recent News Items</div>
        </div>
        <div className="dashboard__kpi-card">
          <div className="dashboard__kpi-value">{alerts.length}</div>
          <div className="dashboard__kpi-label">Active Alerts</div>
        </div>
        <div className="dashboard__kpi-card">
          <div className="dashboard__kpi-value">{rulings.length}</div>
          <div className="dashboard__kpi-label">Recent Rulings</div>
        </div>
        <div className="dashboard__kpi-card">
          <div className="dashboard__kpi-value">24/7</div>
          <div className="dashboard__kpi-label">System Status</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard__grid">
        {/* System Alerts */}
        {alerts.length > 0 && (
          <div className="dashboard__section">
            <div className="dashboard__section-header">
              <FiAlertCircle /> System Alerts
            </div>
            <div className="dashboard__section-content">
              {alerts.map((alert) => (
                <div key={alert.id} className={getAlertClass(alert.type)}>
                  <h4>{alert.title}</h4>
                  <p>{alert.message}</p>
                  <small>{new Date(alert.timestamp).toLocaleString()}</small>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Latest News */}
        <div className="dashboard__section">
          <div className="dashboard__section-header">
            <FiFileText /> Latest Trade Intelligence
          </div>
          <div className="dashboard__section-content">
            {newsItems.map((item) => (
              <div key={item.id} className="dashboard__news-item">
                <h4 className="dashboard__news-title">{item.title}</h4>
                <div className="dashboard__news-meta">
                  <span>{item.source}</span>
                  <span>•</span>
                  <span>{new Date(item.published_date).toLocaleDateString()}</span>
                  <span className={getPriorityBadgeClass(item.priority)}>
                    {item.priority}
                  </span>
                </div>
                <p className="dashboard__news-summary">{item.summary}</p>
                {item.url && (
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="btn btn--link">
                    <FiExternalLink /> Read More
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Recent Rulings */}
        <div className="dashboard__section">
          <div className="dashboard__section-header">
            <FiTrendingUp /> Recent Tariff Rulings
          </div>
          <div className="dashboard__section-content">
            {rulings.map((ruling) => (
              <div key={ruling.ruling_number} className="dashboard__news-item">
                <h4 className="dashboard__news-title">
                  {ruling.ruling_number}: {ruling.title}
                </h4>
                <div className="dashboard__news-meta">
                  <span>HS Code: {ruling.hs_code}</span>
                  <span>•</span>
                  <span>{new Date(ruling.ruling_date).toLocaleDateString()}</span>
                  <span className={`dashboard__priority-badge dashboard__priority-badge--${ruling.status === 'active' ? 'low' : 'medium'}`}>
                    {ruling.status}
                  </span>
                </div>
                <p className="dashboard__news-summary">{ruling.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="dashboard__section">
          <div className="dashboard__section-header">
            <FiSearch /> Quick Actions
          </div>
          <div className="dashboard__section-content">
            <div className="dashboard__quick-actions">
              <Link to="/tariff-tree" className="dashboard__quick-action">
                <FiFileText className="dashboard__quick-action-icon" />
                <span className="dashboard__quick-action-text">Browse Tariff Schedule</span>
              </Link>
              <Link to="/ai-assistant?context=calculation" className="dashboard__quick-action">
                <FiDollarSign className="dashboard__quick-action-icon" />
                <span className="dashboard__quick-action-text">Calculate Duties</span>
              </Link>
              <Link to="/export-tariffs" className="dashboard__quick-action">
                <FiGlobe className="dashboard__quick-action-icon" />
                <span className="dashboard__quick-action-text">Export Classification</span>
              </Link>
              <Link to="/ai-assistant?context=search" className="dashboard__quick-action">
                <FiSearch className="dashboard__quick-action-icon" />
                <span className="dashboard__quick-action-text">Search Regulations</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

## UI Components

### components/ui/index.ts
```typescript
export { Button } from './Button';
export { Card, CardHeader, CardTitle, CardContent } from './Card';
export { Alert } from './Alert';
export { LoadingSpinner } from './LoadingSpinner';
export { Input } from './Input';
export { Select } from './Select';
export { Badge } from './Badge';
export { Modal } from './Modal';
export { Tabs, TabsList, TabsTrigger, TabsContent } from './Tabs';
export { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from './Table';
```

### components/ui/Button.tsx
```typescript
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
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
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
      ) : leftIcon ? (
        <span className="mr-2">{leftIcon}</span>
      ) : null}
      
      {children}
      
      {rightIcon && !isLoading && (
        <span className="ml-2">{rightIcon}</span>
      )}
    </button>
  );
};
```

### components/ui/Card.tsx
```typescript
import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 border-b border-gray-200 ${className}`}>
      {children}
    </div>
  );
};

export const CardTitle: React.FC<CardTitleProps> = ({ children, className = '' }) => {
  return (
    <h3 className={`text-lg font-semibold text-gray-900 ${className}`}>
      {children}
    </h3>
  );
};

export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 ${className}`}>
      {children}
    </div>
  );
};
```

### components/ui/Alert.tsx
```typescript
import React from 'react';
import { FiAlertCircle, FiCheckCircle, FiInfo, FiAlertTriangle } from 'react-icons/fi';

interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({ 
  variant = 'info', 
  title, 
  children, 
  className = '' 
}) => {
  const variantClasses = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800'
  };

  const iconClasses = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400'
  };

  const icons = {
    info: FiInfo,
    success: FiCheckCircle,
    warning: FiAlertTriangle,
    error: FiAlertCircle
  };

  const Icon = icons[variant];

  return (
    <div className={`border rounded-lg p-4 ${variantClasses[variant]} ${className}`}>
      <div className="flex">
        <Icon className={`h-5 w-5 ${iconClasses[variant]} mt-0.5 mr-3 flex-shrink-0`} />
        <div className="flex-1">
          {title && (
            <h4 className="font-medium mb-1">{title}</h4>
          )}
          <div className="text-sm">{children}</div>
        </div>
      </div>
    </div>
  );
};
```

### components/ui/LoadingSpinner.tsx
```typescript
import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizeClasses[size]} ${className}`} />
  );
};
```

## Design System

### styles/enhanced.css
```css
/*
   ENHANCED CUSTOMS BROKER PORTAL DESIGN SYSTEM 2024
   Modern, accessible, professional UI with improved color contrast
   =============================================================================
*/

:root {
  /* Primary Brand Colors - Deep Professional Blue */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-200: #bae6fd;
  --color-primary-300: #7dd3fc;
  --color-primary-400: #38bdf8;
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;  /* Main brand color */
  --color-primary-700: #0369a1;
  --color-primary-800: #075985;
  --color-primary-900: #0c4a6e;
  --color-primary-950: #082f49;

  /* Secondary Colors - Professional Navy */
  --color-secondary-50: #f8fafc;
  --color-secondary-100: #f1f5f9;
  --color-secondary-200: #e2e8f0;
  --color-secondary-300: #cbd5e1;
  --color-secondary-400: #94a3b8;
  --color-secondary-500: #64748b;
  --color-secondary-600: #475569;
  --color-secondary-700: #334155;
  --color-secondary-800: #1e293b;
  --color-secondary-900: #0f172a;
  --color-secondary-950: #020617;

  /* Semantic Colors - Enhanced for Professional Use */
  --color-success-50: #f0fdf4;
  --color-success-100: #dcfce7;
  --color-success-500: #22c55e;
  --color-success-600: #16a34a;
  --color-success-700: #15803d;

  --color-warning-50: #fffbeb;
  --color-warning-100: #fef3c7;
  --color-warning-500: #f59e0b;
  --color-warning-600: #d97706;
  --color-warning-700: #b45309;

  --color-error-50: #fef2f2;
  --color-error-100: #fee2e2;
  --color-error-500: #ef4444;
  --color-error-600: #dc2626;
  --color-error-700: #b91c1c;

  --color-info-50: #eff6ff;
  --color-info-100: #dbeafe;
  --color-info-500: #3b82f6;
  --color-info-600: #2563eb;
  --color-info-700: #1d4ed8;

  /* Trade-Specific Colors */
  --color-duty: #7c3aed;
  --color-fta: #059669;
  --color-export: #0d9488;
  --color-compliance: #ea580c;

  /* Enhanced Gray Scale - Better Contrast */
  --color-gray-25: #fcfcfd;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  --color-gray-950: #030712;

  /* Typography System - Modern & Readable */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
  
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */

  /* Spacing & Layout */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  --space-24: 6rem;

  /* Border Radius */
  --radius-sm: 0.125rem;
  --radius: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
}

/* =============================================================================
   DASHBOARD STYLES - Professional Layout
   ============================================================================= */

.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-gray-100) 100%);
  padding: var(--space-6);
}

.dashboard__header {
  background: linear-gradient(135deg, var(--color-primary-600) 0%, var(--color-primary-700) 100%);
  color: white;
  padding: var(--space-8) var(--space-6);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-8);
  box-shadow: var(--shadow-lg);
}

.dashboard__title {
  font-size: var(--text-3xl);
  font-weight: 700;
  margin-bottom: var(--space-2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.dashboard__subtitle {
  font-size: var(--text-lg);
  opacity: 0.9;
  margin-bottom: var(--space-6);
  line-height: 1.6;
}

.dashboard__actions {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.dashboard__kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.dashboard__kpi-card {
  background: white;
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  border: 1px solid var(--color-gray-200);
  text-align: center;
  transition: all var(--transition-normal);
}

.dashboard__kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.dashboard__kpi-value {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--color-primary-600);
  margin-bottom: var(--space-2);
}

.dashboard__kpi-label {
  font-size: var(--text-sm);
  color: var(--color-gray-600);
  font-weight: 500;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-6);
}

.dashboard__section {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  border: 1px solid var(--color-gray-200);
  overflow: hidden;
}

.dashboard__section-header {
  background: var(--color-gray-50);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-gray-200);
  font-weight: 600;
  color: var(--color-gray-800);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.dashboard__section-content {
  padding: var(--space-6);
  max-height: 500px;
  overflow-y: auto;
}

.dashboard__news-item {
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--color-gray-100);
}

.dashboard__news-item:last-child {
  border-bottom: none;
}

.dashboard__news-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-gray-900);
  margin-bottom: var(--space-2);
  line-height: 1.4;
}

.dashboard__news-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-gray-500);
  margin-bottom: var(--space-2);
  flex-wrap: wrap;
}

.dashboard__news-summary {
  font-size: var(--text-sm);
  color: var(--color-gray-700);
  line-height: 1.5;
  margin-bottom: var(--space-3);
}

.dashboard__priority-badge {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius);
  font-size: var(--text-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.dashboard__priority-badge--low {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.dashboard__priority-badge--medium {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.dashboard__priority-badge--high {
  background: var(--color-error-100);
  color: var(--color-error-700);
}

.dashboard__priority-badge--urgent {
  background: var(--color-error-600);
  color: white;
}

.dashboard__alert {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  border-left: 4px solid;
}

.dashboard__alert--info {
  background: var(--color-info-50);
  border-left-color: var(--color-info-500);
  color: var(--color-info-800);
}

.dashboard__alert--warning {
  background: var(--color-warning-50);
  border-left-color: var(--color-warning-500);
  color: var(--color-warning-800);
}

.dashboard__alert--error {
  background: var(--color-error-50);
  border-left-color: var(--color-error-500);
  color: var(--color-error-800);
}

.dashboard__alert--success {
  background: var(--color-success-50);
  border-left-color: var(--color-success-500);
  color: var(--color-success-800);
}

.dashboard__quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}

.dashboard__quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-6);
  background: var(--color-gray-50);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-gray-700);
  transition: all var(--transition-normal);
}

.dashboard__quick-action:hover {
  background: var(--color-primary-50);
  border-color: var(--color-primary-200);
  color: var(--color-primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.dashboard__quick-action-icon {
  font-size: 2rem;
  margin-bottom: var(--space-3);
  color: var(--color-primary-600);
}

.dashboard__quick-action-text {
  font-size: var(--text-sm);
  font-weight: 500;
  text-align: center;
}

.dashboard__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  color: var(--color-gray-600);
}

.dashboard__loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-gray-200);
  border-top: 4px solid var(--color-primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-4);
}

.dashboard__error {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-error-600);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* =============================================================================
   BUTTON SYSTEM - Professional Styling
   ============================================================================= */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-normal);
  white-space: nowrap;
}

.btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: var(--color-primary-600);
  color: white;
  border-color: var(--color-primary-600);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-primary-700);
  border-color: var(--color-primary-700);
}

.btn--secondary {
  background: var(--color-gray-600);
  color: white;
  border-color: var(--color-gray-600);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--color-gray-700);
  border-color: var(--color-gray-700);
}

.btn--outline {
  background: white;
  color: var(--color-gray-700);
  border-color: var(--color-gray-300);
}

.btn--outline:hover:not(:disabled) {
  background: var(--color-gray-50);
  border-color: var(--color-gray-400);
}

.btn--ghost {
  background: transparent;
  color: var(--color-gray-700);
  border-color: transparent;
}

.btn--ghost:hover:not(:disabled) {
  background: var(--color-gray-100);
}

.btn--link {
  background: transparent;
  color: var(--color-primary-600);
  border-color: transparent;
  padding: 0;
  font-weight: 400;
}

.btn--link:hover:not(:disabled) {
  color: var(--color-primary-700);
  text-decoration: underline;
}

/* =============================================================================
   RESPONSIVE DESIGN
   ============================================================================= */

@media (max-width: 768px) {
  .dashboard {
    padding: var(--space-4);
  }
  
  .dashboard__header {
    padding: var(--space-6) var(--space-4);
  }
  
  .dashboard__title {
    font-size: var(--text-2xl);
  }
  
  .dashboard__subtitle {
    font-size: var(--text-base);
  }
  
  .dashboard__kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-4);
  }
  
  .dashboard__grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
  
  .dashboard__quick-actions {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
