# Customs Broker Portal - UI/UX Design System PRD

## Executive Summary

This PRD defines the comprehensive UI/UX design system for the Customs Broker Portal, ensuring a modern, professional, and highly polished interface that meets the demanding standards of trade professionals while providing exceptional usability across all devices.

## Design Philosophy

### Core Principles
- **Professional Authority**: Interface conveys expertise and reliability expected in trade compliance
- **Information Density**: Efficiently display complex tariff and regulatory data without overwhelming users
- **Progressive Disclosure**: Layer information complexity based on user expertise and context
- **Contextual Intelligence**: Surface relevant information based on user actions and workflows
- **Cross-Platform Consistency**: Seamless experience across desktop, tablet, and mobile devices

### Target Audience Considerations
- **Primary**: Experienced customs brokers (information-dense, efficient workflows)
- **Secondary**: New team members (guided experiences, learning aids)
- **Tertiary**: Non-specialists using AI assistant (simplified, conversational interfaces)

---

## Visual Design System

### Color Palette

#### Primary Colors
```scss
$primary-brand: #1B365D;      // Deep Navy Blue - authority, trust
$primary-light: #2E5984;     // Medium Navy - interactive elements
$primary-dark: #0F1E2E;      // Dark Navy - headers, emphasis

$secondary-accent: #0369A1;   // Professional Blue - links, highlights
$secondary-light: #7DD3FC;    // Light Blue - backgrounds, success states
$secondary-dark: #0C4A6E;     // Dark Blue - active states
```

#### Semantic Colors
```scss
// Status & Feedback
$success: #059669;            // Green - approvals, completed actions
$success-light: #D1FAE5;     // Light Green - success backgrounds
$warning: #D97706;           // Amber - attention, pending items
$warning-light: #FEF3C7;     // Light Amber - warning backgrounds
$error: #DC2626;             // Red - errors, critical alerts
$error-light: #FEE2E2;       // Light Red - error backgrounds
$info: #2563EB;              // Blue - information, tips
$info-light: #DBEAFE;        // Light Blue - info backgrounds

// Trade-Specific Colors
$duty-rate: #7C3AED;         // Purple - duty rates and calculations
$fta-benefit: #059669;       // Green - FTA savings and benefits
$anti-dumping: #DC2626;      // Red - anti-dumping duties and restrictions
$tco-exemption: #0891B2;     // Cyan - TCO exemptions and concessions
```

#### Neutral Grays
```scss
$gray-50: #F9FAFB;           // Lightest - page backgrounds
$gray-100: #F3F4F6;          // Light - card backgrounds
$gray-200: #E5E7EB;          // Medium Light - borders, dividers
$gray-300: #D1D5DB;          // Medium - disabled states
$gray-400: #9CA3AF;          // Medium Dark - placeholder text
$gray-500: #6B7280;          // Dark - secondary text
$gray-600: #4B5563;          // Darker - primary text
$gray-700: #374151;          // Very Dark - headings
$gray-800: #1F2937;          // Darkest - high contrast text
$gray-900: #111827;          // Black - maximum contrast
```

### Typography System

#### Font Stack
```scss
// Primary: Professional Sans-Serif
$font-primary: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;

// Secondary: Monospace for codes and data
$font-mono: 'JetBrains Mono', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;

// Accent: Serif for formal documents
$font-serif: 'Charter', 'Georgia', 'Times New Roman', serif;
```

#### Type Scale (Responsive)
```scss
// Headings
$text-6xl: clamp(3.5rem, 5vw, 4rem);     // 56-64px - Hero headlines
$text-5xl: clamp(2.5rem, 4vw, 3rem);     // 40-48px - Page titles
$text-4xl: clamp(2rem, 3.5vw, 2.25rem);  // 32-36px - Section headers
$text-3xl: clamp(1.75rem, 3vw, 1.875rem); // 28-30px - Subsection headers
$text-2xl: clamp(1.5rem, 2.5vw, 1.5rem); // 24px - Card titles
$text-xl: clamp(1.25rem, 2vw, 1.25rem);  // 20px - Large text

// Body Text
$text-lg: 1.125rem;          // 18px - Large body text
$text-base: 1rem;            // 16px - Standard body text
$text-sm: 0.875rem;          // 14px - Small text, captions
$text-xs: 0.75rem;           // 12px - Fine print, metadata

// Code & Data
$text-code-lg: 1rem;         // 16px - Large code blocks
$text-code: 0.875rem;        // 14px - Inline code, HS codes
$text-code-sm: 0.75rem;      // 12px - Small data displays
```

#### Font Weights
```scss
$font-thin: 100;
$font-light: 300;            // Rarely used
$font-normal: 400;           // Body text
$font-medium: 500;           // Emphasis, nav items
$font-semibold: 600;         // Subheadings, important info
$font-bold: 700;             // Headings, critical alerts
$font-black: 900;            // Hero text, major headings
```

### Spacing System

#### Base Unit: 4px
```scss
$space-px: 1px;
$space-0: 0;
$space-1: 0.25rem;    // 4px
$space-2: 0.5rem;     // 8px
$space-3: 0.75rem;    // 12px
$space-4: 1rem;       // 16px
$space-5: 1.25rem;    // 20px
$space-6: 1.5rem;     // 24px
$space-8: 2rem;       // 32px
$space-10: 2.5rem;    // 40px
$space-12: 3rem;      // 48px
$space-16: 4rem;      // 64px
$space-20: 5rem;      // 80px
$space-24: 6rem;      // 96px
$space-32: 8rem;      // 128px
```

#### Layout Spacing
```scss
// Page-level spacing
$container-padding: clamp(1rem, 5vw, 2rem);    // Responsive container padding
$section-spacing: clamp(3rem, 8vw, 6rem);      // Between major sections
$component-spacing: clamp(1.5rem, 4vw, 2.5rem); // Between components

// Component-level spacing
$card-padding: clamp(1rem, 3vw, 1.5rem);       // Card internal padding
$button-padding-y: 0.75rem;                     // Button vertical padding
$button-padding-x: 1.5rem;                      // Button horizontal padding
$input-padding: 0.75rem 1rem;                  // Form input padding
```

### Border Radius & Shadows

#### Border Radius
```scss
$radius-none: 0;
$radius-sm: 0.125rem;    // 2px - Small elements
$radius: 0.25rem;        // 4px - Standard buttons, inputs
$radius-md: 0.375rem;    // 6px - Cards, panels
$radius-lg: 0.5rem;      // 8px - Large cards, modals
$radius-xl: 0.75rem;     // 12px - Hero sections
$radius-2xl: 1rem;       // 16px - Feature cards
$radius-full: 9999px;    // Fully rounded - badges, avatars
```

#### Shadow System
```scss
// Elevation levels for depth hierarchy
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);                    // Subtle depth
$shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); // Standard cards
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); // Elevated cards
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); // Modals, dropdowns
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); // Major overlays
$shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);             // Maximum elevation

// Colored shadows for states
$shadow-primary: 0 4px 14px 0 rgba(27, 54, 93, 0.15);           // Primary button hover
$shadow-success: 0 4px 14px 0 rgba(5, 150, 105, 0.15);          // Success states
$shadow-error: 0 4px 14px 0 rgba(220, 38, 38, 0.15);            // Error states
```

---

## Component Design System

### Button Components

#### Primary Actions
```scss
.btn-primary {
  background: linear-gradient(135deg, $primary-brand 0%, $primary-light 100%);
  color: white;
  border: none;
  padding: $button-padding-y $button-padding-x;
  border-radius: $radius;
  font-weight: $font-semibold;
  font-size: $text-base;
  line-height: 1.5;
  transition: all 0.2s ease-in-out;
  box-shadow: $shadow-sm;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: $shadow-primary;
    background: linear-gradient(135deg, $primary-light 0%, $primary-brand 100%);
  }
  
  &:active {
    transform: translateY(0);
    box-shadow: $shadow-sm;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
}
```

#### Secondary Actions
```scss
.btn-secondary {
  background: white;
  color: $primary-brand;
  border: 1.5px solid $gray-200;
  padding: calc($button-padding-y - 1.5px) calc($button-padding-x - 1.5px);
  
  &:hover {
    border-color: $primary-brand;
    background: $gray-50;
    transform: translateY(-1px);
    box-shadow: $shadow;
  }
}
```

#### Specialized Buttons
```scss
.btn-success {
  background: linear-gradient(135deg, $success 0%, #10B981 100%);
  color: white;
  
  &:hover { box-shadow: $shadow-success; }
}

.btn-danger {
  background: linear-gradient(135deg, $error 0%, #EF4444 100%);
  color: white;
  
  &:hover { box-shadow: $shadow-error; }
}

.btn-ghost {
  background: transparent;
  color: $gray-600;
  border: none;
  
  &:hover {
    background: $gray-100;
    color: $gray-700;
  }
}
```

### Card Components

#### Standard Information Card
```scss
.card {
  background: white;
  border-radius: $radius-md;
  border: 1px solid $gray-200;
  box-shadow: $shadow-sm;
  transition: all 0.2s ease-in-out;
  overflow: hidden;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
  
  .card-header {
    padding: $space-4 $space-6 $space-3;
    border-bottom: 1px solid $gray-100;
    background: $gray-50;
  }
  
  .card-body {
    padding: $space-6;
  }
  
  .card-footer {
    padding: $space-3 $space-6 $space-4;
    border-top: 1px solid $gray-100;
    background: $gray-50;
  }
}
```

#### Data Display Cards
```scss
.data-card {
  @extend .card;
  
  .data-value {
    font-size: $text-2xl;
    font-weight: $font-bold;
    color: $gray-800;
    margin: $space-2 0;
  }
  
  .data-label {
    font-size: $text-sm;
    color: $gray-500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: $font-medium;
  }
  
  .data-change {
    font-size: $text-sm;
    font-weight: $font-medium;
    
    &.positive { color: $success; }
    &.negative { color: $error; }
    &.neutral { color: $gray-500; }
  }
}
```

### Input Components

#### Text Inputs
```scss
.input {
  width: 100%;
  padding: $input-padding;
  border: 1.5px solid $gray-200;
  border-radius: $radius;
  font-size: $text-base;
  font-family: $font-primary;
  background: white;
  transition: all 0.2s ease-in-out;
  
  &:focus {
    outline: none;
    border-color: $primary-brand;
    box-shadow: 0 0 0 3px rgba(27, 54, 93, 0.1);
  }
  
  &:invalid {
    border-color: $error;
    
    &:focus {
      box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
    }
  }
  
  &:disabled {
    background: $gray-100;
    color: $gray-400;
    cursor: not-allowed;
  }
}
```

#### Specialized Inputs
```scss
.input-hs-code {
  font-family: $font-mono;
  font-size: $text-code;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.input-currency {
  text-align: right;
  font-family: $font-mono;
  
  &::before {
    content: '$';
    position: absolute;
    left: 12px;
    color: $gray-400;
  }
}

.input-search {
  position: relative;
  
  &::after {
    content: '🔍';
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.6;
  }
}
```

### Navigation Components

#### Main Navigation
```scss
.main-nav {
  background: white;
  border-bottom: 1px solid $gray-200;
  box-shadow: $shadow-sm;
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(8px);
  
  .nav-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 $container-padding;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
  }
  
  .nav-links {
    display: flex;
    gap: $space-1;
  }
  
  .nav-link {
    padding: $space-3 $space-4;
    border-radius: $radius;
    color: $gray-600;
    text-decoration: none;
    font-weight: $font-medium;
    transition: all 0.2s ease-in-out;
    
    &:hover {
      background: $gray-100;
      color: $gray-700;
    }
    
    &.active {
      background: $primary-brand;
      color: white;
    }
  }
}
```

#### Breadcrumb Navigation
```scss
.breadcrumb {
  display: flex;
  align-items: center;
  gap: $space-2;
  margin: $space-4 0;
  font-size: $text-sm;
  
  .breadcrumb-item {
    color: $gray-500;
    
    &:not(:last-child)::after {
      content: '/';
      margin-left: $space-2;
      color: $gray-300;
    }
    
    &.active {
      color: $gray-700;
      font-weight: $font-medium;
    }
    
    a {
      color: $primary-brand;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
}
```

---

## Page-Specific Layouts

### Dashboard Layout

#### News Intelligence Center
```scss
.news-intelligence-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: $space-6;
  height: calc(100vh - 64px); // Subtract nav height
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
}

.news-feed {
  background: white;
  border-radius: $radius-lg;
  border: 1px solid $gray-200;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  .news-header {
    padding: $space-6;
    border-bottom: 1px solid $gray-200;
    background: $gray-50;
    
    .news-title {
      font-size: $text-2xl;
      font-weight: $font-bold;
      color: $gray-800;
      margin: 0 0 $space-4;
    }
    
    .news-filters {
      display: flex;
      gap: $space-2;
      flex-wrap: wrap;
    }
  }
  
  .news-content {
    flex: 1;
    overflow-y: auto;
    padding: $space-4;
  }
}

.news-item {
  padding: $space-4;
  border-bottom: 1px solid $gray-100;
  transition: background 0.2s ease;
  
  &:hover {
    background: $gray-50;
  }
  
  &:last-child {
    border-bottom: none;
  }
  
  .news-meta {
    display: flex;
    align-items: center;
    gap: $space-2;
    margin-bottom: $space-2;
  }
  
  .news-headline {
    font-size: $text-lg;
    font-weight: $font-semibold;
    color: $gray-800;
    margin-bottom: $space-2;
    line-height: 1.4;
    cursor: pointer;
    
    &:hover {
      color: $primary-brand;
    }
  }
  
  .news-summary {
    color: $gray-600;
    line-height: 1.6;
    margin-bottom: $space-3;
  }
  
  .related-codes {
    display: flex;
    flex-wrap: wrap;
    gap: $space-1;
  }
}
```

#### Trade Statistics Sidebar
```scss
.trade-sidebar {
  display: flex;
  flex-direction: column;
  gap: $space-4;
  
  .stat-card {
    @extend .data-card;
    
    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: $space-4;
      
      @media (max-width: 480px) {
        grid-template-columns: 1fr;
      }
    }
  }
  
  .quick-actions {
    @extend .card;
    
    .action-list {
      display: flex;
      flex-direction: column;
      gap: $space-2;
    }
    
    .action-item {
      @extend .btn-ghost;
      justify-content: flex-start;
      text-align: left;
      padding: $space-3;
      border-radius: $radius;
      
      .action-icon {
        margin-right: $space-3;
        font-size: $text-lg;
      }
    }
  }
}
```

### Tariff Tree Layout

```scss
.tariff-tree-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  height: calc(100vh - 64px);
  gap: 0;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
}

.tree-panel {
  background: white;
  border-right: 1px solid $gray-200;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  .tree-header {
    padding: $space-6;
    border-bottom: 1px solid $gray-200;
    background: $gray-50;
  }
  
  .tree-search {
    margin-bottom: $space-4;
  }
  
  .tree-content {
    flex: 1;
    overflow-y: auto;
    padding: $space-4;
  }
}

.tariff-tree {
  .ant-tree-node-content-wrapper {
    padding: $space-2 $space-3;
    border-radius: $radius;
    transition: all 0.2s ease;
    
    &:hover {
      background: $gray-100;
    }
    
    &.ant-tree-node-selected {
      background: $primary-brand !important;
      color: white;
    }
  }
  
  .tree-node {
    display: flex;
    align-items: center;
    gap: $space-2;
    
    .hs-code {
      font-family: $font-mono;
      font-size: $text-code;
      color: $primary-brand;
      font-weight: $font-semibold;
      min-width: 80px;
    }
    
    .description {
      flex: 1;
      font-size: $text-sm;
      line-height: 1.4;
    }
    
    .level-indicator {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: $gray-300;
      
      &.level-2 { background: $primary-brand; }
      &.level-4 { background: $secondary-accent; }
      &.level-6 { background: $success; }
      &.level-8 { background: $warning; }
      &.level-10 { background: $error; }
    }
  }
}

.detail-panel {
  background: $gray-50;
  overflow-y: auto;
  padding: $space-6;
  
  .detail-header {
    background: white;
    padding: $space-6;
    border-radius: $radius-lg;
    border: 1px solid $gray-200;
    margin-bottom: $space-6;
    
    .hs-code-display {
      font-family: $font-mono;
      font-size: $text-4xl;
      font-weight: $font-bold;
      color: $primary-brand;
      margin-bottom: $space-2;
    }
    
    .description-display {
      font-size: $text-lg;
      color: $gray-700;
      line-height: 1.5;
    }
  }
  
  .detail-sections {
    display: grid;
    gap: $space-4;
    
    @media (min-width: 1200px) {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}
```

### AI Assistant Layout

```scss
.ai-assistant-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  height: calc(100vh - 64px);
  gap: 0;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
  
  &.calculator-collapsed {
    grid-template-columns: 1fr 0;
    
    @media (max-width: 1024px) {
      grid-template-columns: 1fr;
    }
  }
}

.conversation-panel {
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  .conversation-header {
    padding: $space-6;
    border-bottom: 1px solid $gray-200;
    background: $gray-50;
    
    .conversation-title {
      font-size: $text-xl;
      font-weight: $font-semibold;
      color: $gray-800;
    }
  }
  
  .conversation-content {
    flex: 1;
    overflow-y: auto;
    padding: $space-4;
    display: flex;
    flex-direction: column;
    gap: $space-4;
  }
  
  .conversation-input {
    padding: $space-6;
    border-top: 1px solid $gray-200;
    background: white;
  }
}

.message {
  max-width: 80%;
  padding: $space-4;
  border-radius: $radius-lg;
  line-height: 1.6;
  
  &.user {
    align-self: flex-end;
    background: $primary-brand;
    color: white;
    border-bottom-right-radius: $radius;
  }
  
  &.assistant {
    align-self: flex-start;
    background: $gray-100;
    color: $gray-800;
    border-bottom-left-radius: $radius;
    
    .message-content {
      margin-bottom: $space-3;
    }
    
    .suggested-actions {
      display: flex;
      gap: $space-2;
      flex-wrap: wrap;
      margin-top: $space-3;
    }
  }
  
  .message-timestamp {
    font-size: $text-xs;
    opacity: 0.7;
    margin-top: $space-2;
  }
}

.calculator-panel {
  background: white;
  border-left: 1px solid $gray-200;
  overflow-y: auto;
  transition: all 0.3s ease-in-out;
  
  &.collapsed {
    width: 0;
    opacity: 0;
    pointer-events: none;
  }
  
  .calculator-header {
    padding: $space-6;
    border-bottom: 1px solid $gray-200;
    background: $gray-50;
    
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .calculator-content {
    padding: $space-6;
  }
}
```

---

## Responsive Design System

### Breakpoint Strategy

```scss
$breakpoints: (
  'xs': 320px,    // Small phones
  'sm': 640px,    // Large phones
  'md': 768px,    // Tablets
  'lg': 1024px,   // Small laptops
  'xl': 1280px,   // Large laptops
  '2xl': 1536px   // Desktop monitors
);

// Mobile-first mixins
@mixin mobile-only {
  @media (max-width: 639px) { @content; }
}

@mixin tablet-up {
  @media (min-width: 640px) { @content; }
}

@mixin desktop-up {
  @media (min-width: 1024px) { @content; }
}

@mixin large-desktop-up {
  @media (min-width: 1280px) { @content; }
}
```

### Mobile-First Component Adaptations

#### Navigation - Mobile
```scss
.main-nav {
  @include mobile-only {
    .nav-container {
      padding: 0 $space-4;
    }
    
    .nav-links {
      display: none;
      
      &.mobile-open {
        display: flex;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        flex-direction: column;
        border-top: 1px solid $gray-200;
        box-shadow: $shadow-lg;
      }
    }
    
    .mobile-menu-toggle {
      display: block;
      background: none;
      border: none;
      padding: $space-2;
      font-size: $text-xl;
    }
  }
  
  @include tablet-up {
    .mobile-menu-toggle {
      display: none;
    }
  }
}
```

#### Cards - Responsive Stacking
```scss
.card-grid {
  display: grid;
  gap: $space-4;
  
  // Mobile: Single column
  grid-template-columns: 1fr;
  
  // Tablet: Two columns
  @include tablet-up {
    grid-template-columns: repeat(2, 1fr);
  }
  
  // Desktop: Three or four columns based on content
  @include desktop-up {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}
```

#### Data Tables - Mobile Adaptation
```scss
.data-table {
  width: 100%;
  border-collapse: collapse;
  
  @include mobile-only {
    // Transform table to card layout on mobile
    display: block;
    
    thead {
      display: none;
    }
    
    tbody {
      display: block;
    }
    
    tr {
      display: block;
      background: white;
      border: 1px solid $gray-200;
      border-radius: $radius-md;
      margin-bottom: $space-4;
      padding: $space-4;
    }
    
    td {
      display: block;
      text-align: left;
      padding: $space-2 0;
      border-bottom: 1px solid $gray-100;
      
      &:before {
        content: attr(data-label) ": ";
        font-weight: $font-semibold;
        color: $gray-600;
      }
      
      &:last-child {
        border-bottom: none;
      }
    }
  }
  
  @include tablet-up {
    display: table;
    
    th,
    td {
      padding: $space-3 $space-4;
      text-align: left;
      border-bottom: 1px solid $gray-200;
    }
    
    th {
      background: $gray-50;
      font-weight: $font-semibold;
      color: $gray-700;
    }
  }
}
```

---

## Interactive States & Animations

### Hover Effects

```scss
// Subtle lift for interactive elements
.interactive-lift {
  transition: all 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
}

// Gentle highlight for clickable items
.hover-highlight {
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: $gray-50;
  }
}

// Scale effect for buttons and icons
.hover-scale {
  transition: transform 0.2s ease-in-out;
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.98);
  }
}
```

### Loading States

```scss
// Skeleton loading for content
.skeleton {
  background: linear-gradient(90deg, $gray-200 25%, $gray-100 50%, $gray-200 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: $radius;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

// Spinner for actions
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid $gray-200;
  border-top: 2px solid $primary-brand;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// Progress indicator
.progress {
  width: 100%;
  height: 4px;
  background: $gray-200;
  border-radius: $radius-full;
  overflow: hidden;
  
  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, $primary-brand, $secondary-accent);
    border-radius: $radius-full;
    transition: width 0.3s ease;
  }
}
```

### Micro-Interactions

```scss
// Notification entrance
.notification-enter {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

// Modal backdrop
.modal-backdrop {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// Button click feedback
.btn-feedback {
  position: relative;
  overflow: hidden;
  
  &:active::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    animation: ripple 0.6s ease-out;
  }
}

@keyframes ripple {
  to {
    width: 300px;
    height: 300px;
    opacity: 0;
  }
}
```

---

## Accessibility Standards

### Color Contrast Requirements

```scss
// WCAG AA compliance ratios
// Normal text: 4.5:1 minimum
// Large text: 3:1 minimum
// Graphical elements: 3:1 minimum

.text-high-contrast {
  color: $gray-900; // 16.23:1 against white
}

.text-medium-contrast {
  color: $gray-700; // 9.25:1 against white
}

.text-low-contrast {
  color: $gray-600; // 6.33:1 against white (meets AA large text)
}

// Interactive elements must meet 3:1 contrast
.interactive-element {
  border: 2px solid $primary-brand; // 5.89:1 against white
}
```

### Focus States

```scss
// Consistent focus indicator
.focus-visible {
  outline: none;
  
  &:focus-visible {
    outline: 2px solid $primary-brand;
    outline-offset: 2px;
    border-radius: $radius;
  }
}

// High contrast focus for form elements
.input {
  &:focus-visible {
    outline: 3px solid $primary-brand;
    outline-offset: 0;
    box-shadow: 0 0 0 1px white, 0 0 0 4px $primary-brand;
  }
}
```

### Screen Reader Support

```scss
// Visually hidden but available to screen readers
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

// Skip navigation link
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: $primary-brand;
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  border-radius: $radius;
  z-index: 1000;
  
  &:focus {
    top: 6px;
  }
}
```

---

## Dark Mode Support

### Color Variables (Dark Theme)

```scss
[data-theme="dark"] {
  // Dark mode color overrides
  --bg-primary: #{$gray-900};
  --bg-secondary: #{$gray-800};
  --bg-tertiary: #{$gray-700};
  
  --text-primary: #{$gray-100};
  --text-secondary: #{$gray-300};
  --text-tertiary: #{$gray-400};
  
  --border-primary: #{$gray-600};
  --border-secondary: #{$gray-700};
  
  // Adjust brand colors for dark mode
  --primary-brand: #3B82F6;
  --primary-light: #60A5FA;
  
  // Semantic colors - adjusted for dark backgrounds
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
}
```

### Component Dark Mode Adaptations

```scss
.card {
  background: var(--bg-primary, white);
  border-color: var(--border-primary, $gray-200);
  color: var(--text-primary, $gray-800);
  
  [data-theme="dark"] & {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  }
}

.input {
  background: var(--bg-primary, white);
  border-color: var(--border-primary, $gray-200);
  color: var(--text-primary, $gray-800);
  
  &::placeholder {
    color: var(--text-tertiary, $gray-400);
  }
}
```

---

## Performance Considerations

### CSS Optimization

```scss
// Use CSS custom properties for dynamic theming
:root {
  --animation-duration: 0.2s;
  --animation-easing: ease-in-out;
}

// Optimize animations for performance
.optimized-animation {
  will-change: transform, opacity;
  transform: translateZ(0); // Force hardware acceleration
}

// Reduce layout thrashing
.layout-stable {
  contain: layout style paint;
}
```

### Image Optimization

```scss
.responsive-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  loading: lazy; // Native lazy loading
}

// Progressive image loading
.image-placeholder {
  background: $gray-200;
  aspect-ratio: 16/9;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.loaded {
    background: none;
  }
}
```

---

## Implementation Guidelines

### CSS Architecture

```scss
// Use BEM methodology for component classes
.component-name {
  // Block styles
  
  &__element {
    // Element styles
  }
  
  &--modifier {
    // Modifier styles
  }
  
  &__element--modifier {
    // Element with modifier
  }
}
```

### Component Organization

```
styles/
├── base/
│   ├── _reset.scss
│   ├── _typography.scss
│   └── _variables.scss
├── components/
│   ├── _buttons.scss
│   ├── _cards.scss
│   ├── _forms.scss
│   └── _navigation.scss
├── layout/
│   ├── _grid.scss
│   ├── _containers.scss
│   └── _header.scss
├── pages/
│   ├── _dashboard.scss
│   ├── _tariff-tree.scss
│   └── _ai-assistant.scss
├── utilities/
│   ├── _spacing.scss
│   ├── _colors.scss
│   └── _responsive.scss
└── main.scss
```

### CSS Custom Properties Usage

```scss
// Define in :root for global access
:root {
  --spacing-unit: 1rem;
  --border-radius: 0.25rem;
  --transition-duration: 0.2s;
}

// Use in components
.component {
  padding: var(--spacing-unit);
  border-radius: var(--border-radius);
  transition: all var(--transition-duration) ease;
}
```

This comprehensive UI/UX design system ensures the Customs Broker Portal delivers a professional, modern, and highly polished interface that meets the demanding standards of trade professionals while providing exceptional usability across all devices and use cases.
