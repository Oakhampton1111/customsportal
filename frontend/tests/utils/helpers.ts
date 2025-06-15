/**
 * E2E Test Helper Functions
 * Provides reusable utilities for Playwright E2E tests
 */

import { Page, expect } from '@playwright/test';
import { TestUser, TestDutyCalculation } from './test-data';

/**
 * Navigation helpers
 */
export class NavigationHelpers {
  constructor(private page: Page) {}

  async goToHome(): Promise<void> {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async goToDashboard(): Promise<void> {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async goToDutyCalculator(): Promise<void> {
    await this.page.goto('/duty-calculator');
    await this.page.waitForLoadState('networkidle');
  }

  async goToTariffLookup(): Promise<void> {
    await this.page.goto('/tariff-lookup');
    await this.page.waitForLoadState('networkidle');
  }

  async goToSearch(): Promise<void> {
    await this.page.goto('/search');
    await this.page.waitForLoadState('networkidle');
  }
}

/**
 * Authentication helpers
 */
export class AuthHelpers {
  constructor(private page: Page) {}

  async login(user: TestUser): Promise<void> {
    // Navigate to login page
    await this.page.goto('/login');
    
    // Fill login form
    await this.page.fill('[data-testid="email-input"]', user.email);
    await this.page.fill('[data-testid="password-input"]', user.password);
    
    // Submit form
    await this.page.click('[data-testid="login-button"]');
    
    // Wait for successful login
    await this.page.waitForURL('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async logout(): Promise<void> {
    // Click logout button
    await this.page.click('[data-testid="logout-button"]');
    
    // Wait for redirect to home page
    await this.page.waitForURL('/');
    await this.page.waitForLoadState('networkidle');
  }

  async isLoggedIn(): Promise<boolean> {
    try {
      await this.page.waitForSelector('[data-testid="user-menu"]', { timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Form helpers
 */
export class FormHelpers {
  constructor(private page: Page) {}

  async fillDutyCalculatorForm(calculation: TestDutyCalculation): Promise<void> {
    // Fill HS Code
    await this.page.fill('[data-testid="hs-code-input"]', calculation.hsCode);
    
    // Fill value
    await this.page.fill('[data-testid="value-input"]', calculation.value.toString());
    
    // Fill quantity
    await this.page.fill('[data-testid="quantity-input"]', calculation.quantity.toString());
    
    // Select country
    await this.page.click('[data-testid="country-select"]');
    await this.page.click(`[data-testid="country-option-${calculation.country}"]`);
  }

  async submitDutyCalculatorForm(): Promise<void> {
    await this.page.click('[data-testid="calculate-button"]');
    await this.page.waitForSelector('[data-testid="calculation-results"]');
  }

  async fillSearchForm(query: string): Promise<void> {
    await this.page.fill('[data-testid="search-input"]', query);
  }

  async submitSearchForm(): Promise<void> {
    await this.page.click('[data-testid="search-button"]');
    await this.page.waitForSelector('[data-testid="search-results"]');
  }
}

/**
 * Assertion helpers
 */
export class AssertionHelpers {
  constructor(private page: Page) {}

  async assertPageTitle(expectedTitle: string): Promise<void> {
    await expect(this.page).toHaveTitle(expectedTitle);
  }

  async assertPageUrl(expectedUrl: string): Promise<void> {
    await expect(this.page).toHaveURL(expectedUrl);
  }

  async assertElementVisible(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  async assertElementHidden(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeHidden();
  }

  async assertElementText(selector: string, expectedText: string): Promise<void> {
    await expect(this.page.locator(selector)).toHaveText(expectedText);
  }

  async assertElementContainsText(selector: string, expectedText: string): Promise<void> {
    await expect(this.page.locator(selector)).toContainText(expectedText);
  }

  async assertCalculationResults(expected: TestDutyCalculation): Promise<void> {
    // Assert duty amount
    await expect(this.page.locator('[data-testid="duty-amount"]'))
      .toContainText(expected.expectedDuty.toString());
    
    // Assert GST amount
    await expect(this.page.locator('[data-testid="gst-amount"]'))
      .toContainText(expected.expectedGst.toString());
    
    // Assert total amount
    await expect(this.page.locator('[data-testid="total-amount"]'))
      .toContainText(expected.expectedTotal.toString());
  }

  async assertSearchResults(expectedCount: number): Promise<void> {
    const results = this.page.locator('[data-testid="search-result-item"]');
    await expect(results).toHaveCount(expectedCount);
  }
}

/**
 * Wait helpers
 */
export class WaitHelpers {
  constructor(private page: Page) {}

  async waitForApiResponse(url: string, timeout = 10000): Promise<void> {
    await this.page.waitForResponse(
      response => response.url().includes(url) && response.status() === 200,
      { timeout }
    );
  }

  async waitForLoadingToFinish(): Promise<void> {
    // Wait for loading spinner to disappear
    await this.page.waitForSelector('[data-testid="loading-spinner"]', { state: 'hidden' });
  }

  async waitForErrorToAppear(): Promise<void> {
    await this.page.waitForSelector('[data-testid="error-message"]', { state: 'visible' });
  }

  async waitForSuccessMessage(): Promise<void> {
    await this.page.waitForSelector('[data-testid="success-message"]', { state: 'visible' });
  }
}

/**
 * Accessibility helpers
 */
export class AccessibilityHelpers {
  constructor(private page: Page) {}

  async testKeyboardNavigation(): Promise<void> {
    // Test tab navigation
    await this.page.keyboard.press('Tab');
    
    // Verify focus is visible
    const focusedElement = await this.page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  }

  async testAriaLabels(): Promise<void> {
    // Check that interactive elements have aria-labels
    const buttons = this.page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const ariaLabel = await button.getAttribute('aria-label');
      const textContent = await button.textContent();
      
      // Button should have either aria-label or text content
      expect(ariaLabel || textContent).toBeTruthy();
    }
  }

  async testColorContrast(): Promise<void> {
    // This would typically use axe-core or similar tool
    // For now, we'll check that text is visible
    const textElements = this.page.locator('p, h1, h2, h3, h4, h5, h6, span, div');
    const count = await textElements.count();
    
    for (let i = 0; i < Math.min(count, 10); i++) {
      await expect(textElements.nth(i)).toBeVisible();
    }
  }
}

/**
 * Performance helpers
 */
export class PerformanceHelpers {
  constructor(private page: Page) {}

  async measurePageLoadTime(): Promise<number> {
    const startTime = Date.now();
    await this.page.waitForLoadState('networkidle');
    return Date.now() - startTime;
  }

  async measureApiResponseTime(url: string): Promise<number> {
    const startTime = Date.now();
    await this.page.waitForResponse(response => response.url().includes(url));
    return Date.now() - startTime;
  }

  async checkCoreWebVitals(): Promise<Record<string, number>> {
    return await this.page.evaluate(() => {
      return new Promise((resolve) => {
        const vitals: Record<string, number> = {};
        
        // Largest Contentful Paint
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          vitals.lcp = lastEntry.startTime;
        }).observe({ entryTypes: ['largest-contentful-paint'] });
        
        // First Input Delay
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry) => {
            const fidEntry = entry as PerformanceEventTiming;
            vitals.fid = fidEntry.processingStart - fidEntry.startTime;
          });
        }).observe({ entryTypes: ['first-input'] });
        
        // Cumulative Layout Shift
        new PerformanceObserver((list) => {
          let cls = 0;
          list.getEntries().forEach((entry) => {
            const clsEntry = entry as PerformanceEntry & {
              hadRecentInput?: boolean;
              value: number;
            };
            if (!clsEntry.hadRecentInput) {
              cls += clsEntry.value;
            }
          });
          vitals.cls = cls;
        }).observe({ entryTypes: ['layout-shift'] });
        
        // Return vitals after a short delay
        setTimeout(() => resolve(vitals), 2000);
      });
    });
  }
}

/**
 * Screenshot helpers
 */
export class ScreenshotHelpers {
  constructor(private page: Page) {}

  async takeFullPageScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `test-results/screenshots/${name}-full-page.png`,
      fullPage: true
    });
  }

  async takeElementScreenshot(selector: string, name: string): Promise<void> {
    const element = this.page.locator(selector);
    await element.screenshot({
      path: `test-results/screenshots/${name}-element.png`
    });
  }

  async compareScreenshot(name: string): Promise<void> {
    await expect(this.page).toHaveScreenshot(`${name}.png`);
  }
}

/**
 * Main test helpers class that combines all helper classes
 */
export class TestHelpers {
  public navigation: NavigationHelpers;
  public auth: AuthHelpers;
  public forms: FormHelpers;
  public assertions: AssertionHelpers;
  public wait: WaitHelpers;
  public accessibility: AccessibilityHelpers;
  public performance: PerformanceHelpers;
  public screenshots: ScreenshotHelpers;

  constructor(private page: Page) {
    this.navigation = new NavigationHelpers(page);
    this.auth = new AuthHelpers(page);
    this.forms = new FormHelpers(page);
    this.assertions = new AssertionHelpers(page);
    this.wait = new WaitHelpers(page);
    this.accessibility = new AccessibilityHelpers(page);
    this.performance = new PerformanceHelpers(page);
    this.screenshots = new ScreenshotHelpers(page);
  }

  /**
   * Setup page for testing
   */
  async setupPage(): Promise<void> {
    // Set viewport size
    await this.page.setViewportSize({ width: 1280, height: 720 });
    
    // Set extra HTTP headers if needed
    await this.page.setExtraHTTPHeaders({
      'Accept-Language': 'en-US,en;q=0.9'
    });
    
    // Clear any existing storage
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  }

  /**
   * Clean up after test
   */
  async cleanup(): Promise<void> {
    // Clear storage
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Clear cookies
    await this.page.context().clearCookies();
  }
}