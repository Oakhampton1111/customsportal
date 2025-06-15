/**
 * User Onboarding E2E Tests
 * Tests the complete user onboarding workflow
 */

import { test, expect, Page } from '@playwright/test';
import { HomePage } from '../../utils/page-objects/HomePage';
import { DashboardPage } from '../../utils/page-objects/DashboardPage';
import { TestHelpers } from '../../utils/helpers';
import { TEST_USERS, TestDataManager } from '../../utils/test-data';

test.describe('User Onboarding Workflow', () => {
  let homePage: HomePage;
  let dashboardPage: DashboardPage;
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    homePage = new HomePage(page);
    dashboardPage = new DashboardPage(page);
    helpers = new TestHelpers(page);
    
    await helpers.setupPage();
  });

  test.afterEach(async () => {
    await helpers.cleanup();
  });

  test('should complete new user registration and onboarding', async ({ page }) => {
    // Generate a unique test user
    const testUser = TestDataManager.generateTestUser('broker');

    // Step 1: Navigate to home page
    await homePage.goto();
    await expect(homePage.heroTitle).toBeVisible();

    // Step 2: Click Get Started button
    await homePage.clickGetStarted();
    await expect(page).toHaveURL(/\/register/);

    // Step 3: Fill registration form
    await page.fill('[data-testid="name-input"]', testUser.name);
    await page.fill('[data-testid="email-input"]', testUser.email);
    await page.fill('[data-testid="password-input"]', testUser.password);
    await page.fill('[data-testid="confirm-password-input"]', testUser.password);
    await page.selectOption('[data-testid="role-select"]', testUser.role);

    // Step 4: Accept terms and conditions
    await page.check('[data-testid="terms-checkbox"]');

    // Step 5: Submit registration
    await page.click('[data-testid="register-button"]');

    // Step 6: Verify email verification page
    await expect(page).toHaveURL(/\/verify-email/);
    await expect(page.locator('[data-testid="verification-message"]')).toContainText(testUser.email);

    // Step 7: Simulate email verification (in real scenario, this would be done via email)
    // For testing, we'll navigate directly to the verification success page
    await page.goto('/verify-email/success');

    // Step 8: Verify redirect to onboarding
    await expect(page).toHaveURL(/\/onboarding/);

    // Step 9: Complete onboarding steps
    await completeOnboardingSteps(page);

    // Step 10: Verify redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(dashboardPage.welcomeMessage).toContainText(testUser.name);

    // Step 11: Verify dashboard elements are visible
    await expect(dashboardPage.quickActionsSection).toBeVisible();
    await expect(dashboardPage.statisticsSection).toBeVisible();
  });

  test('should handle existing user login flow', async ({ page }) => {
    const testUser = TEST_USERS.broker;

    // Step 1: Navigate to home page
    await homePage.goto();

    // Step 2: Click login button
    await homePage.clickLogin();
    await expect(page).toHaveURL(/\/login/);

    // Step 3: Fill login form
    await page.fill('[data-testid="email-input"]', testUser.email);
    await page.fill('[data-testid="password-input"]', testUser.password);

    // Step 4: Submit login
    await page.click('[data-testid="login-button"]');

    // Step 5: Verify redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(dashboardPage.welcomeMessage).toContainText(testUser.name);
  });

  test('should guide user through feature discovery', async ({ page }) => {
    const testUser = TEST_USERS.broker;

    // Login first
    await helpers.auth.login(testUser);
    await dashboardPage.goto();

    // Step 1: Take the feature tour
    const tourButton = page.locator('[data-testid="start-tour-button"]');
    if (await tourButton.isVisible()) {
      await tourButton.click();

      // Step through tour steps
      await page.click('[data-testid="tour-next-button"]'); // Duty Calculator
      await expect(page.locator('[data-testid="tour-tooltip"]')).toContainText('Calculate duties');

      await page.click('[data-testid="tour-next-button"]'); // Tariff Lookup
      await expect(page.locator('[data-testid="tour-tooltip"]')).toContainText('Search tariffs');

      await page.click('[data-testid="tour-next-button"]'); // Search
      await expect(page.locator('[data-testid="tour-tooltip"]')).toContainText('Find information');

      await page.click('[data-testid="tour-finish-button"]');
    }

    // Step 2: Try each main feature
    await dashboardPage.clickCalculateDuty();
    await expect(page).toHaveURL(/\/duty-calculator/);
    await page.goBack();

    await dashboardPage.clickSearchTariff();
    await expect(page).toHaveURL(/\/tariff-lookup/);
    await page.goBack();

    // Step 3: Verify user preferences are saved
    await dashboardPage.goToSettings();
    await expect(page).toHaveURL(/\/settings/);
    
    // Check that tour completion is saved
    const tourCompleted = page.locator('[data-testid="tour-completed-status"]');
    await expect(tourCompleted).toContainText('Completed');
  });

  test('should handle onboarding errors gracefully', async ({ page }) => {
    // Test registration with invalid email
    await homePage.goto();
    await homePage.clickGetStarted();

    await page.fill('[data-testid="name-input"]', 'Test User');
    await page.fill('[data-testid="email-input"]', 'invalid-email');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.fill('[data-testid="confirm-password-input"]', 'password123');

    await page.click('[data-testid="register-button"]');

    // Verify error message
    await expect(page.locator('[data-testid="email-error"]')).toContainText('valid email');

    // Test password mismatch
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="confirm-password-input"]', 'different-password');

    await page.click('[data-testid="register-button"]');

    // Verify error message
    await expect(page.locator('[data-testid="password-error"]')).toContainText('match');
  });

  test('should support accessibility during onboarding', async ({ page }) => {
    await homePage.goto();

    // Test keyboard navigation
    await page.keyboard.press('Tab'); // Should focus on first interactive element
    await page.keyboard.press('Tab'); // Navigate to next element
    
    // Verify focus is visible
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // Test screen reader support
    await helpers.accessibility.testAriaLabels();
    
    // Navigate to registration with keyboard
    await page.keyboard.press('Enter'); // Activate focused element
    
    // Test form accessibility
    const nameInput = page.locator('[data-testid="name-input"]');
    await expect(nameInput).toHaveAttribute('aria-label');
    
    const emailInput = page.locator('[data-testid="email-input"]');
    await expect(emailInput).toHaveAttribute('aria-label');
  });

  /**
   * Helper function to complete onboarding steps
   */
  async function completeOnboardingSteps(page: Page) {
    // Step 1: Company Information
    await page.fill('[data-testid="company-name-input"]', 'Test Customs Broker Ltd');
    await page.fill('[data-testid="company-abn-input"]', '12345678901');
    await page.selectOption('[data-testid="company-size-select"]', 'small');
    await page.click('[data-testid="onboarding-next-button"]');

    // Step 2: Business Focus
    await page.check('[data-testid="import-checkbox"]');
    await page.check('[data-testid="export-checkbox"]');
    await page.selectOption('[data-testid="primary-industry-select"]', 'electronics');
    await page.click('[data-testid="onboarding-next-button"]');

    // Step 3: Preferences
    await page.selectOption('[data-testid="currency-preference-select"]', 'AUD');
    await page.selectOption('[data-testid="timezone-select"]', 'Australia/Sydney');
    await page.check('[data-testid="email-notifications-checkbox"]');
    await page.click('[data-testid="onboarding-next-button"]');

    // Step 4: Complete onboarding
    await page.click('[data-testid="complete-onboarding-button"]');
  }
});

test.describe('Onboarding Performance', () => {
  test('should complete onboarding within acceptable time limits', async ({ page }) => {
    const helpers = new TestHelpers(page);
    await helpers.setupPage();

    const startTime = Date.now();

    // Measure registration page load time
    await page.goto('/register');
    const registrationLoadTime = await helpers.performance.measurePageLoadTime();
    expect(registrationLoadTime).toBeLessThan(3000); // 3 seconds

    // Measure onboarding flow completion time
    const testUser = TestDataManager.generateTestUser('broker');
    
    await page.fill('[data-testid="name-input"]', testUser.name);
    await page.fill('[data-testid="email-input"]', testUser.email);
    await page.fill('[data-testid="password-input"]', testUser.password);
    await page.fill('[data-testid="confirm-password-input"]', testUser.password);
    await page.selectOption('[data-testid="role-select"]', testUser.role);
    await page.check('[data-testid="terms-checkbox"]');
    
    await page.click('[data-testid="register-button"]');

    const totalTime = Date.now() - startTime;
    expect(totalTime).toBeLessThan(10000); // 10 seconds for complete flow
  });
});