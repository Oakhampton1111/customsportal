// Portal Theme Configuration
// Based on Cargoclear International branding from customer portal design

export const portalTheme = {
  colors: {
    // Primary Cargoclear colors
    primary: '#1e3a5f',      // Navy blue
    secondary: '#ff6b35',    // Orange
    
    // UI colors
    background: '#f8fafc',   // Light gray background
    surface: '#ffffff',      // White surfaces
    border: '#e2e8f0',       // Light border
    
    // Text colors
    text: {
      primary: '#1e293b',    // Dark text
      secondary: '#64748b',  // Medium gray text
      muted: '#94a3b8',      // Light gray text
      inverse: '#ffffff',    // White text
    },
    
    // Status colors
    status: {
      success: '#10b981',    // Green
      warning: '#f59e0b',    // Amber
      error: '#ef4444',      // Red
      info: '#3b82f6',       // Blue
    },
    
    // Sidebar colors
    sidebar: {
      background: '#1e3a5f', // Navy blue
      text: '#ffffff',       // White text
      textMuted: '#94a3b8',  // Light gray text
      hover: '#2d4a6b',      // Lighter navy on hover
      active: '#ff6b35',     // Orange for active items
    },
    
    // Header colors
    header: {
      background: '#ffffff', // White background
      text: '#1e293b',       // Dark text
      border: '#e2e8f0',     // Light border
    },
  },
  
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
  },
  
  borderRadius: {
    sm: '0.25rem',   // 4px
    md: '0.375rem',  // 6px
    lg: '0.5rem',    // 8px
    xl: '0.75rem',   // 12px
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['Monaco', 'Consolas', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',   // 12px
      sm: '0.875rem',  // 14px
      base: '1rem',    // 16px
      lg: '1.125rem',  // 18px
      xl: '1.25rem',   // 20px
      '2xl': '1.5rem', // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
    lineHeight: {
      tight: '1.25',
      normal: '1.5',
      relaxed: '1.75',
    },
  },
  
  layout: {
    sidebar: {
      width: '280px',
      collapsedWidth: '80px',
    },
    header: {
      height: '64px',
    },
    container: {
      maxWidth: '1200px',
    },
  },
  
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060,
  },
} as const;

export type PortalTheme = typeof portalTheme;

// CSS Custom Properties for portal theme
export const portalCSSVariables = `
  :root {
    /* Colors */
    --portal-primary: ${portalTheme.colors.primary};
    --portal-secondary: ${portalTheme.colors.secondary};
    --portal-background: ${portalTheme.colors.background};
    --portal-surface: ${portalTheme.colors.surface};
    --portal-border: ${portalTheme.colors.border};
    
    /* Text colors */
    --portal-text-primary: ${portalTheme.colors.text.primary};
    --portal-text-secondary: ${portalTheme.colors.text.secondary};
    --portal-text-muted: ${portalTheme.colors.text.muted};
    --portal-text-inverse: ${portalTheme.colors.text.inverse};
    
    /* Status colors */
    --portal-success: ${portalTheme.colors.status.success};
    --portal-warning: ${portalTheme.colors.status.warning};
    --portal-error: ${portalTheme.colors.status.error};
    --portal-info: ${portalTheme.colors.status.info};
    
    /* Sidebar colors */
    --portal-sidebar-bg: ${portalTheme.colors.sidebar.background};
    --portal-sidebar-text: ${portalTheme.colors.sidebar.text};
    --portal-sidebar-text-muted: ${portalTheme.colors.sidebar.textMuted};
    --portal-sidebar-hover: ${portalTheme.colors.sidebar.hover};
    --portal-sidebar-active: ${portalTheme.colors.sidebar.active};
    
    /* Header colors */
    --portal-header-bg: ${portalTheme.colors.header.background};
    --portal-header-text: ${portalTheme.colors.header.text};
    --portal-header-border: ${portalTheme.colors.header.border};
    
    /* Layout */
    --portal-sidebar-width: ${portalTheme.layout.sidebar.width};
    --portal-sidebar-collapsed-width: ${portalTheme.layout.sidebar.collapsedWidth};
    --portal-header-height: ${portalTheme.layout.header.height};
    
    /* Spacing */
    --portal-spacing-xs: ${portalTheme.spacing.xs};
    --portal-spacing-sm: ${portalTheme.spacing.sm};
    --portal-spacing-md: ${portalTheme.spacing.md};
    --portal-spacing-lg: ${portalTheme.spacing.lg};
    --portal-spacing-xl: ${portalTheme.spacing.xl};
    --portal-spacing-2xl: ${portalTheme.spacing['2xl']};
    --portal-spacing-3xl: ${portalTheme.spacing['3xl']};
    
    /* Border radius */
    --portal-radius-sm: ${portalTheme.borderRadius.sm};
    --portal-radius-md: ${portalTheme.borderRadius.md};
    --portal-radius-lg: ${portalTheme.borderRadius.lg};
    --portal-radius-xl: ${portalTheme.borderRadius.xl};
    
    /* Shadows */
    --portal-shadow-sm: ${portalTheme.shadows.sm};
    --portal-shadow-md: ${portalTheme.shadows.md};
    --portal-shadow-lg: ${portalTheme.shadows.lg};
    --portal-shadow-xl: ${portalTheme.shadows.xl};
  }
`;