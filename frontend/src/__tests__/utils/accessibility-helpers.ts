// Accessibility testing utilities

// Accessibility testing utilities
export class AccessibilityHelpers {
  /**
   * Check if an element has proper accessible name
   */
  static hasAccessibleName(element: HTMLElement): boolean {
    const accessibleName = element.getAttribute('aria-label') ||
                          element.getAttribute('aria-labelledby') ||
                          element.textContent ||
                          element.getAttribute('title') ||
                          element.getAttribute('alt');
    
    return Boolean(accessibleName && accessibleName.trim().length > 0);
  }

  /**
   * Check if an element has proper accessible description
   */
  static hasAccessibleDescription(element: HTMLElement): boolean {
    const accessibleDescription = element.getAttribute('aria-describedby') ||
                                 element.getAttribute('title');
    
    return Boolean(accessibleDescription && accessibleDescription.trim().length > 0);
  }

  /**
   * Check if form controls have proper labels
   */
  static checkFormLabels(container: HTMLElement): string[] {
    const issues: string[] = [];
    const formControls = container.querySelectorAll('input, select, textarea');
    
    formControls.forEach((control, index) => {
      const element = control as HTMLElement;
      const id = element.getAttribute('id');
      const type = element.getAttribute('type');
      
      // Skip hidden inputs
      if (type === 'hidden') return;
      
      // Check for label association
      const hasLabel = id && container.querySelector(`label[for="${id}"]`);
      const hasAriaLabel = element.getAttribute('aria-label');
      const hasAriaLabelledBy = element.getAttribute('aria-labelledby');
      
      if (!hasLabel && !hasAriaLabel && !hasAriaLabelledBy) {
        issues.push(`Form control at index ${index} (${element.tagName.toLowerCase()}) lacks proper labeling`);
      }
    });
    
    return issues;
  }

  /**
   * Check if buttons have accessible names
   */
  static checkButtonAccessibility(container: HTMLElement): string[] {
    const issues: string[] = [];
    const buttons = container.querySelectorAll('button, [role="button"]');
    
    buttons.forEach((button, index) => {
      const element = button as HTMLElement;
      
      if (!this.hasAccessibleName(element)) {
        issues.push(`Button at index ${index} lacks accessible name`);
      }
    });
    
    return issues;
  }

  /**
   * Check if images have alt text
   */
  static checkImageAccessibility(container: HTMLElement): string[] {
    const issues: string[] = [];
    const images = container.querySelectorAll('img');
    
    images.forEach((img, index) => {
      const alt = img.getAttribute('alt');
      const role = img.getAttribute('role');
      
      // Decorative images should have empty alt or role="presentation"
      if (role === 'presentation' || role === 'none') return;
      
      if (alt === null) {
        issues.push(`Image at index ${index} missing alt attribute`);
      }
    });
    
    return issues;
  }

  /**
   * Check if links have accessible names
   */
  static checkLinkAccessibility(container: HTMLElement): string[] {
    const issues: string[] = [];
    const links = container.querySelectorAll('a, [role="link"]');
    
    links.forEach((link, index) => {
      const element = link as HTMLElement;
      
      if (!this.hasAccessibleName(element)) {
        issues.push(`Link at index ${index} lacks accessible name`);
      }
    });
    
    return issues;
  }

  /**
   * Check heading hierarchy
   */
  static checkHeadingHierarchy(container: HTMLElement): string[] {
    const issues: string[] = [];
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]');
    
    let previousLevel = 0;
    
    headings.forEach((heading, index) => {
      const element = heading as HTMLElement;
      let level: number;
      
      if (element.hasAttribute('aria-level')) {
        level = parseInt(element.getAttribute('aria-level') || '1');
      } else {
        const tagName = element.tagName.toLowerCase();
        level = parseInt(tagName.charAt(1)) || 1;
      }
      
      // First heading should be h1
      if (index === 0 && level !== 1) {
        issues.push('First heading should be h1');
      }
      
      // Check for skipped levels
      if (previousLevel > 0 && level > previousLevel + 1) {
        issues.push(`Heading level skipped: h${previousLevel} to h${level}`);
      }
      
      previousLevel = level;
    });
    
    return issues;
  }

  /**
   * Check color contrast (basic check for common patterns)
   */
  static checkBasicColorContrast(container: HTMLElement): string[] {
    const issues: string[] = [];
    const elements = container.querySelectorAll('*');
    
    elements.forEach((element) => {
      const htmlElement = element as HTMLElement;
      const styles = window.getComputedStyle(htmlElement);
      const color = styles.color;
      const backgroundColor = styles.backgroundColor;
      
      // Basic check for very light text on light background
      if (color === 'rgb(255, 255, 255)' && backgroundColor === 'rgb(255, 255, 255)') {
        issues.push('Potential contrast issue: white text on white background');
      }
      
      // Check for very light gray text
      if (color.includes('rgb(') && color.includes('200,') && color.includes('200,')) {
        issues.push('Potential contrast issue: very light text detected');
      }
    });
    
    return issues;
  }

  /**
   * Check for keyboard navigation support
   */
  static checkKeyboardNavigation(container: HTMLElement): string[] {
    const issues: string[] = [];
    const interactiveElements = container.querySelectorAll(
      'button, a, input, select, textarea, [tabindex], [role="button"], [role="link"], [role="tab"]'
    );
    
    interactiveElements.forEach((element, index) => {
      const htmlElement = element as HTMLElement;
      const tabIndex = htmlElement.getAttribute('tabindex');
      
      // Check for positive tabindex (anti-pattern)
      if (tabIndex && parseInt(tabIndex) > 0) {
        issues.push(`Element at index ${index} has positive tabindex (${tabIndex}), which can disrupt tab order`);
      }
      
      // Check if custom interactive elements have proper role
      if (!['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(htmlElement.tagName)) {
        const role = htmlElement.getAttribute('role');
        if (!role || !['button', 'link', 'tab', 'menuitem'].includes(role)) {
          issues.push(`Custom interactive element at index ${index} may need proper role`);
        }
      }
    });
    
    return issues;
  }

  /**
   * Check ARIA attributes usage
   */
  static checkAriaAttributes(container: HTMLElement): string[] {
    const issues: string[] = [];
    const elementsWithAria = container.querySelectorAll('[aria-labelledby], [aria-describedby]');
    
    elementsWithAria.forEach((element, index) => {
      const htmlElement = element as HTMLElement;
      const labelledBy = htmlElement.getAttribute('aria-labelledby');
      const describedBy = htmlElement.getAttribute('aria-describedby');
      
      // Check if referenced elements exist
      if (labelledBy) {
        const referencedElement = container.querySelector(`#${labelledBy}`);
        if (!referencedElement) {
          issues.push(`Element at index ${index} references non-existent label: ${labelledBy}`);
        }
      }
      
      if (describedBy) {
        const referencedElement = container.querySelector(`#${describedBy}`);
        if (!referencedElement) {
          issues.push(`Element at index ${index} references non-existent description: ${describedBy}`);
        }
      }
    });
    
    return issues;
  }

  /**
   * Run comprehensive accessibility audit
   */
  static auditAccessibility(container: HTMLElement): {
    passed: boolean;
    issues: string[];
    warnings: string[];
  } {
    const issues: string[] = [];
    const warnings: string[] = [];
    
    // Run all checks
    issues.push(...this.checkFormLabels(container));
    issues.push(...this.checkButtonAccessibility(container));
    issues.push(...this.checkImageAccessibility(container));
    issues.push(...this.checkLinkAccessibility(container));
    issues.push(...this.checkHeadingHierarchy(container));
    issues.push(...this.checkKeyboardNavigation(container));
    issues.push(...this.checkAriaAttributes(container));
    
    // Warnings (less critical)
    warnings.push(...this.checkBasicColorContrast(container));
    
    return {
      passed: issues.length === 0,
      issues,
      warnings,
    };
  }
}

// Helper functions for testing specific accessibility features
export const accessibilityTestHelpers = {
  /**
   * Test if element is focusable
   */
  isFocusable: (element: HTMLElement): boolean => {
    const focusableElements = [
      'button', 'input', 'select', 'textarea', 'a[href]', '[tabindex]'
    ];
    
    return focusableElements.some(selector => element.matches(selector)) &&
           !element.hasAttribute('disabled') &&
           element.getAttribute('tabindex') !== '-1';
  },

  /**
   * Test keyboard navigation
   */
  testKeyboardNavigation: async (container: HTMLElement): Promise<string[]> => {
    const issues: string[] = [];
    const focusableElements = container.querySelectorAll(
      'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) {
      issues.push('No focusable elements found');
      return issues;
    }
    
    // Test if first element can receive focus
    const firstElement = focusableElements[0] as HTMLElement;
    firstElement.focus();
    
    if (document.activeElement !== firstElement) {
      issues.push('First focusable element cannot receive focus');
    }
    
    return issues;
  },

  /**
   * Test screen reader announcements
   */
  testScreenReaderAnnouncements: (container: HTMLElement): string[] => {
    const issues: string[] = [];
    const liveRegions = container.querySelectorAll('[aria-live], [role="status"], [role="alert"]');
    
    liveRegions.forEach((region, index) => {
      const element = region as HTMLElement;
      const ariaLive = element.getAttribute('aria-live');
      const role = element.getAttribute('role');
      
      if (!ariaLive && !['status', 'alert'].includes(role || '')) {
        issues.push(`Live region at index ${index} should have aria-live attribute`);
      }
    });
    
    return issues;
  },

  /**
   * Test form accessibility
   */
  testFormAccessibility: (form: HTMLElement): string[] => {
    const issues: string[] = [];
    
    // Check for fieldsets and legends
    const fieldsets = form.querySelectorAll('fieldset');
    fieldsets.forEach((fieldset, index) => {
      const legend = fieldset.querySelector('legend');
      if (!legend) {
        issues.push(`Fieldset at index ${index} missing legend`);
      }
    });
    
    // Check for required field indicators
    const requiredFields = form.querySelectorAll('[required], [aria-required="true"]');
    requiredFields.forEach((field, index) => {
      const element = field as HTMLElement;
      const hasRequiredIndicator = element.getAttribute('aria-label')?.includes('required') ||
                                  element.getAttribute('aria-describedby') ||
                                  form.querySelector(`[aria-describedby*="${element.id}"]`);
      
      if (!hasRequiredIndicator) {
        issues.push(`Required field at index ${index} should indicate it's required`);
      }
    });
    
    return issues;
  },
};

// Jest custom matchers for accessibility testing
export const accessibilityMatchers = {
  toBeAccessible: (container: HTMLElement) => {
    const audit = AccessibilityHelpers.auditAccessibility(container);
    
    return {
      pass: audit.passed,
      message: () => {
        if (audit.passed) {
          return 'Element passed accessibility audit';
        } else {
          return `Element failed accessibility audit:\n${audit.issues.join('\n')}${
            audit.warnings.length > 0 ? `\nWarnings:\n${audit.warnings.join('\n')}` : ''
          }`;
        }
      },
    };
  },

  toHaveAccessibleName: (element: HTMLElement) => {
    const hasName = AccessibilityHelpers.hasAccessibleName(element);
    
    return {
      pass: hasName,
      message: () => hasName 
        ? 'Element has accessible name'
        : 'Element does not have accessible name',
    };
  },

  toHaveAccessibleDescription: (element: HTMLElement) => {
    const hasDescription = AccessibilityHelpers.hasAccessibleDescription(element);
    
    return {
      pass: hasDescription,
      message: () => hasDescription
        ? 'Element has accessible description'
        : 'Element does not have accessible description',
    };
  },
};

// Export everything for easy importing
export default {
  AccessibilityHelpers,
  accessibilityTestHelpers,
  accessibilityMatchers,
};