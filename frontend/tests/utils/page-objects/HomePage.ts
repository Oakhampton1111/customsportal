/**
 * Home Page Object Model
 * Provides methods to interact with the home page elements
 */

import { Page, Locator } from '@playwright/test';

export class HomePage {
  readonly page: Page;
  readonly heroTitle: Locator;
  readonly heroSubtitle: Locator;
  readonly getStartedButton: Locator;
  readonly learnMoreButton: Locator;
  readonly featuresSection: Locator;
  readonly dutyCalculatorCard: Locator;
  readonly tariffLookupCard: Locator;
  readonly searchCard: Locator;
  readonly navigationMenu: Locator;
  readonly loginButton: Locator;
  readonly signupButton: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Hero section elements
    this.heroTitle = page.locator('[data-testid="hero-title"]');
    this.heroSubtitle = page.locator('[data-testid="hero-subtitle"]');
    this.getStartedButton = page.locator('[data-testid="get-started-button"]');
    this.learnMoreButton = page.locator('[data-testid="learn-more-button"]');
    
    // Features section
    this.featuresSection = page.locator('[data-testid="features-section"]');
    this.dutyCalculatorCard = page.locator('[data-testid="duty-calculator-card"]');
    this.tariffLookupCard = page.locator('[data-testid="tariff-lookup-card"]');
    this.searchCard = page.locator('[data-testid="search-card"]');
    
    // Navigation elements
    this.navigationMenu = page.locator('[data-testid="navigation-menu"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.signupButton = page.locator('[data-testid="signup-button"]');
  }

  /**
   * Navigate to the home page
   */
  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Click the Get Started button
   */
  async clickGetStarted(): Promise<void> {
    await this.getStartedButton.click();
  }

  /**
   * Click the Learn More button
   */
  async clickLearnMore(): Promise<void> {
    await this.learnMoreButton.click();
  }

  /**
   * Navigate to duty calculator from feature card
   */
  async goToDutyCalculator(): Promise<void> {
    await this.dutyCalculatorCard.click();
  }

  /**
   * Navigate to tariff lookup from feature card
   */
  async goToTariffLookup(): Promise<void> {
    await this.tariffLookupCard.click();
  }

  /**
   * Navigate to search from feature card
   */
  async goToSearch(): Promise<void> {
    await this.searchCard.click();
  }

  /**
   * Click login button
   */
  async clickLogin(): Promise<void> {
    await this.loginButton.click();
  }

  /**
   * Click signup button
   */
  async clickSignup(): Promise<void> {
    await this.signupButton.click();
  }

  /**
   * Check if the page is loaded correctly
   */
  async isLoaded(): Promise<boolean> {
    try {
      await this.heroTitle.waitFor({ state: 'visible', timeout: 5000 });
      await this.featuresSection.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the hero title text
   */
  async getHeroTitle(): Promise<string> {
    return await this.heroTitle.textContent() || '';
  }

  /**
   * Get the hero subtitle text
   */
  async getHeroSubtitle(): Promise<string> {
    return await this.heroSubtitle.textContent() || '';
  }

  /**
   * Check if user is logged in
   */
  async isUserLoggedIn(): Promise<boolean> {
    try {
      await this.page.waitForSelector('[data-testid="user-menu"]', { timeout: 2000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Wait for page animations to complete
   */
  async waitForAnimations(): Promise<void> {
    await this.page.waitForTimeout(500); // Wait for CSS animations
  }

  /**
   * Scroll to features section
   */
  async scrollToFeatures(): Promise<void> {
    await this.featuresSection.scrollIntoViewIfNeeded();
  }

  /**
   * Get all feature cards
   */
  async getFeatureCards(): Promise<Locator[]> {
    return [
      this.dutyCalculatorCard,
      this.tariffLookupCard,
      this.searchCard
    ];
  }

  /**
   * Check if all feature cards are visible
   */
  async areFeatureCardsVisible(): Promise<boolean> {
    const cards = await this.getFeatureCards();
    for (const card of cards) {
      if (!(await card.isVisible())) {
        return false;
      }
    }
    return true;
  }
}