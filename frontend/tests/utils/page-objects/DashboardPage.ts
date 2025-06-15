/**
 * Dashboard Page Object Model
 * Provides methods to interact with the dashboard page elements
 */

import { Page, Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly welcomeMessage: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;
  readonly quickActionsSection: Locator;
  readonly calculateDutyButton: Locator;
  readonly searchTariffButton: Locator;
  readonly viewHistoryButton: Locator;
  readonly recentCalculationsSection: Locator;
  readonly recentCalculationItems: Locator;
  readonly statisticsSection: Locator;
  readonly totalCalculationsCard: Locator;
  readonly averageDutyCard: Locator;
  readonly topCountriesCard: Locator;
  readonly navigationSidebar: Locator;
  readonly dutyCalculatorLink: Locator;
  readonly tariffLookupLink: Locator;
  readonly searchLink: Locator;
  readonly settingsLink: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Main dashboard elements
    this.pageTitle = page.locator('[data-testid="dashboard-title"]');
    this.welcomeMessage = page.locator('[data-testid="welcome-message"]');
    this.userMenu = page.locator('[data-testid="user-menu"]');
    this.logoutButton = page.locator('[data-testid="logout-button"]');
    
    // Quick actions section
    this.quickActionsSection = page.locator('[data-testid="quick-actions-section"]');
    this.calculateDutyButton = page.locator('[data-testid="calculate-duty-button"]');
    this.searchTariffButton = page.locator('[data-testid="search-tariff-button"]');
    this.viewHistoryButton = page.locator('[data-testid="view-history-button"]');
    
    // Recent calculations section
    this.recentCalculationsSection = page.locator('[data-testid="recent-calculations-section"]');
    this.recentCalculationItems = page.locator('[data-testid="recent-calculation-item"]');
    
    // Statistics section
    this.statisticsSection = page.locator('[data-testid="statistics-section"]');
    this.totalCalculationsCard = page.locator('[data-testid="total-calculations-card"]');
    this.averageDutyCard = page.locator('[data-testid="average-duty-card"]');
    this.topCountriesCard = page.locator('[data-testid="top-countries-card"]');
    
    // Navigation sidebar
    this.navigationSidebar = page.locator('[data-testid="navigation-sidebar"]');
    this.dutyCalculatorLink = page.locator('[data-testid="nav-duty-calculator"]');
    this.tariffLookupLink = page.locator('[data-testid="nav-tariff-lookup"]');
    this.searchLink = page.locator('[data-testid="nav-search"]');
    this.settingsLink = page.locator('[data-testid="nav-settings"]');
  }

  /**
   * Navigate to the dashboard page
   */
  async goto(): Promise<void> {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Check if the dashboard is loaded correctly
   */
  async isLoaded(): Promise<boolean> {
    try {
      await this.pageTitle.waitFor({ state: 'visible', timeout: 5000 });
      await this.quickActionsSection.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the welcome message text
   */
  async getWelcomeMessage(): Promise<string> {
    return await this.welcomeMessage.textContent() || '';
  }

  /**
   * Click the calculate duty quick action button
   */
  async clickCalculateDuty(): Promise<void> {
    await this.calculateDutyButton.click();
  }

  /**
   * Click the search tariff quick action button
   */
  async clickSearchTariff(): Promise<void> {
    await this.searchTariffButton.click();
  }

  /**
   * Click the view history quick action button
   */
  async clickViewHistory(): Promise<void> {
    await this.viewHistoryButton.click();
  }

  /**
   * Navigate to duty calculator via sidebar
   */
  async goToDutyCalculator(): Promise<void> {
    await this.dutyCalculatorLink.click();
  }

  /**
   * Navigate to tariff lookup via sidebar
   */
  async goToTariffLookup(): Promise<void> {
    await this.tariffLookupLink.click();
  }

  /**
   * Navigate to search via sidebar
   */
  async goToSearch(): Promise<void> {
    await this.searchLink.click();
  }

  /**
   * Navigate to settings via sidebar
   */
  async goToSettings(): Promise<void> {
    await this.settingsLink.click();
  }

  /**
   * Logout from the dashboard
   */
  async logout(): Promise<void> {
    await this.userMenu.click();
    await this.logoutButton.click();
  }

  /**
   * Get the count of recent calculations
   */
  async getRecentCalculationsCount(): Promise<number> {
    return await this.recentCalculationItems.count();
  }

  /**
   * Click on a specific recent calculation item
   */
  async clickRecentCalculation(index: number): Promise<void> {
    await this.recentCalculationItems.nth(index).click();
  }

  /**
   * Get the total calculations statistic
   */
  async getTotalCalculations(): Promise<string> {
    return await this.totalCalculationsCard.locator('[data-testid="stat-value"]').textContent() || '0';
  }

  /**
   * Get the average duty statistic
   */
  async getAverageDuty(): Promise<string> {
    return await this.averageDutyCard.locator('[data-testid="stat-value"]').textContent() || '0';
  }

  /**
   * Get the top countries data
   */
  async getTopCountries(): Promise<string[]> {
    const countryElements = this.topCountriesCard.locator('[data-testid="country-item"]');
    const count = await countryElements.count();
    const countries: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const country = await countryElements.nth(i).textContent();
      if (country) {
        countries.push(country);
      }
    }
    
    return countries;
  }

  /**
   * Check if the user menu is visible (user is logged in)
   */
  async isUserLoggedIn(): Promise<boolean> {
    try {
      await this.userMenu.waitFor({ state: 'visible', timeout: 2000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Wait for dashboard data to load
   */
  async waitForDataLoad(): Promise<void> {
    // Wait for statistics to load
    await this.totalCalculationsCard.waitFor({ state: 'visible' });
    await this.averageDutyCard.waitFor({ state: 'visible' });
    await this.topCountriesCard.waitFor({ state: 'visible' });
    
    // Wait for recent calculations to load
    await this.recentCalculationsSection.waitFor({ state: 'visible' });
  }

  /**
   * Refresh the dashboard data
   */
  async refreshData(): Promise<void> {
    await this.page.reload();
    await this.waitForDataLoad();
  }

  /**
   * Check if the navigation sidebar is visible
   */
  async isSidebarVisible(): Promise<boolean> {
    return await this.navigationSidebar.isVisible();
  }

  /**
   * Toggle the navigation sidebar (if it has a toggle button)
   */
  async toggleSidebar(): Promise<void> {
    const toggleButton = this.page.locator('[data-testid="sidebar-toggle"]');
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
    }
  }

  /**
   * Search for a specific calculation in recent calculations
   */
  async findRecentCalculation(hsCode: string): Promise<boolean> {
    const items = this.recentCalculationItems;
    const count = await items.count();
    
    for (let i = 0; i < count; i++) {
      const item = items.nth(i);
      const text = await item.textContent();
      if (text && text.includes(hsCode)) {
        return true;
      }
    }
    
    return false;
  }

  /**
   * Get all quick action buttons
   */
  async getQuickActionButtons(): Promise<Locator[]> {
    return [
      this.calculateDutyButton,
      this.searchTariffButton,
      this.viewHistoryButton
    ];
  }

  /**
   * Check if all quick action buttons are visible
   */
  async areQuickActionsVisible(): Promise<boolean> {
    const buttons = await this.getQuickActionButtons();
    for (const button of buttons) {
      if (!(await button.isVisible())) {
        return false;
      }
    }
    return true;
  }
}