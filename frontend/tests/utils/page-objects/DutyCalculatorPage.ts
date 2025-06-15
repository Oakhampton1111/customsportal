/**
 * Duty Calculator Page Object Model
 * Provides methods to interact with the duty calculator page elements
 */

import { Page, Locator } from '@playwright/test';
import { TestDutyCalculation } from '../test-data';

export class DutyCalculatorPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly calculatorForm: Locator;
  readonly hsCodeInput: Locator;
  readonly hsCodeSuggestions: Locator;
  readonly valueInput: Locator;
  readonly quantityInput: Locator;
  readonly countrySelect: Locator;
  readonly countryOptions: Locator;
  readonly currencySelect: Locator;
  readonly calculateButton: Locator;
  readonly clearButton: Locator;
  readonly resultsSection: Locator;
  readonly dutyAmount: Locator;
  readonly gstAmount: Locator;
  readonly totalAmount: Locator;
  readonly calculationBreakdown: Locator;
  readonly saveCalculationButton: Locator;
  readonly exportButton: Locator;
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;
  readonly historySection: Locator;
  readonly historyItems: Locator;
  readonly clearHistoryButton: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Page elements
    this.pageTitle = page.locator('[data-testid="duty-calculator-title"]');
    this.calculatorForm = page.locator('[data-testid="duty-calculator-form"]');
    
    // Form inputs
    this.hsCodeInput = page.locator('[data-testid="hs-code-input"]');
    this.hsCodeSuggestions = page.locator('[data-testid="hs-code-suggestions"]');
    this.valueInput = page.locator('[data-testid="value-input"]');
    this.quantityInput = page.locator('[data-testid="quantity-input"]');
    this.countrySelect = page.locator('[data-testid="country-select"]');
    this.countryOptions = page.locator('[data-testid="country-option"]');
    this.currencySelect = page.locator('[data-testid="currency-select"]');
    
    // Form buttons
    this.calculateButton = page.locator('[data-testid="calculate-button"]');
    this.clearButton = page.locator('[data-testid="clear-button"]');
    
    // Results section
    this.resultsSection = page.locator('[data-testid="calculation-results"]');
    this.dutyAmount = page.locator('[data-testid="duty-amount"]');
    this.gstAmount = page.locator('[data-testid="gst-amount"]');
    this.totalAmount = page.locator('[data-testid="total-amount"]');
    this.calculationBreakdown = page.locator('[data-testid="calculation-breakdown"]');
    this.saveCalculationButton = page.locator('[data-testid="save-calculation-button"]');
    this.exportButton = page.locator('[data-testid="export-button"]');
    
    // Status elements
    this.loadingSpinner = page.locator('[data-testid="loading-spinner"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
    this.successMessage = page.locator('[data-testid="success-message"]');
    
    // History section
    this.historySection = page.locator('[data-testid="calculation-history"]');
    this.historyItems = page.locator('[data-testid="history-item"]');
    this.clearHistoryButton = page.locator('[data-testid="clear-history-button"]');
  }

  /**
   * Navigate to the duty calculator page
   */
  async goto(): Promise<void> {
    await this.page.goto('/duty-calculator');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Check if the page is loaded correctly
   */
  async isLoaded(): Promise<boolean> {
    try {
      await this.pageTitle.waitFor({ state: 'visible', timeout: 5000 });
      await this.calculatorForm.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Fill the HS Code input
   */
  async fillHsCode(hsCode: string): Promise<void> {
    await this.hsCodeInput.fill(hsCode);
  }

  /**
   * Select HS Code from suggestions
   */
  async selectHsCodeSuggestion(hsCode: string): Promise<void> {
    await this.hsCodeInput.fill(hsCode.substring(0, 4)); // Type partial code
    await this.hsCodeSuggestions.waitFor({ state: 'visible' });
    await this.page.locator(`[data-testid="hs-suggestion-${hsCode}"]`).click();
  }

  /**
   * Fill the value input
   */
  async fillValue(value: number): Promise<void> {
    await this.valueInput.fill(value.toString());
  }

  /**
   * Fill the quantity input
   */
  async fillQuantity(quantity: number): Promise<void> {
    await this.quantityInput.fill(quantity.toString());
  }

  /**
   * Select country from dropdown
   */
  async selectCountry(country: string): Promise<void> {
    await this.countrySelect.click();
    await this.page.locator(`[data-testid="country-option-${country}"]`).click();
  }

  /**
   * Select currency from dropdown
   */
  async selectCurrency(currency: string): Promise<void> {
    await this.currencySelect.click();
    await this.page.locator(`[data-testid="currency-option-${currency}"]`).click();
  }

  /**
   * Fill the entire calculation form
   */
  async fillCalculationForm(calculation: TestDutyCalculation): Promise<void> {
    await this.fillHsCode(calculation.hsCode);
    await this.fillValue(calculation.value);
    await this.fillQuantity(calculation.quantity);
    await this.selectCountry(calculation.country);
  }

  /**
   * Submit the calculation form
   */
  async submitCalculation(): Promise<void> {
    await this.calculateButton.click();
    await this.waitForCalculationComplete();
  }

  /**
   * Clear the form
   */
  async clearForm(): Promise<void> {
    await this.clearButton.click();
  }

  /**
   * Wait for calculation to complete
   */
  async waitForCalculationComplete(): Promise<void> {
    // Wait for loading to start and finish
    try {
      await this.loadingSpinner.waitFor({ state: 'visible', timeout: 2000 });
      await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 });
    } catch {
      // Loading might be too fast to catch
    }
    
    // Wait for results to appear
    await this.resultsSection.waitFor({ state: 'visible', timeout: 10000 });
  }

  /**
   * Get the calculated duty amount
   */
  async getDutyAmount(): Promise<string> {
    return await this.dutyAmount.textContent() || '0';
  }

  /**
   * Get the calculated GST amount
   */
  async getGstAmount(): Promise<string> {
    return await this.gstAmount.textContent() || '0';
  }

  /**
   * Get the total amount
   */
  async getTotalAmount(): Promise<string> {
    return await this.totalAmount.textContent() || '0';
  }

  /**
   * Get the calculation breakdown details
   */
  async getCalculationBreakdown(): Promise<string> {
    return await this.calculationBreakdown.textContent() || '';
  }

  /**
   * Save the current calculation
   */
  async saveCalculation(): Promise<void> {
    await this.saveCalculationButton.click();
    await this.waitForSuccessMessage();
  }

  /**
   * Export the calculation results
   */
  async exportCalculation(): Promise<void> {
    await this.exportButton.click();
  }

  /**
   * Check if results are displayed
   */
  async areResultsVisible(): Promise<boolean> {
    return await this.resultsSection.isVisible();
  }

  /**
   * Check if there's an error message
   */
  async hasError(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  /**
   * Get the error message text
   */
  async getErrorMessage(): Promise<string> {
    return await this.errorMessage.textContent() || '';
  }

  /**
   * Wait for success message to appear
   */
  async waitForSuccessMessage(): Promise<void> {
    await this.successMessage.waitFor({ state: 'visible', timeout: 5000 });
  }

  /**
   * Get the success message text
   */
  async getSuccessMessage(): Promise<string> {
    return await this.successMessage.textContent() || '';
  }

  /**
   * Get the count of history items
   */
  async getHistoryCount(): Promise<number> {
    return await this.historyItems.count();
  }

  /**
   * Click on a specific history item
   */
  async clickHistoryItem(index: number): Promise<void> {
    await this.historyItems.nth(index).click();
  }

  /**
   * Clear calculation history
   */
  async clearHistory(): Promise<void> {
    await this.clearHistoryButton.click();
  }

  /**
   * Check if the form is valid (all required fields filled)
   */
  async isFormValid(): Promise<boolean> {
    const hsCode = await this.hsCodeInput.inputValue();
    const value = await this.valueInput.inputValue();
    const quantity = await this.quantityInput.inputValue();
    
    return hsCode.length > 0 && value.length > 0 && quantity.length > 0;
  }

  /**
   * Check if the calculate button is enabled
   */
  async isCalculateButtonEnabled(): Promise<boolean> {
    return await this.calculateButton.isEnabled();
  }

  /**
   * Get all available countries from the dropdown
   */
  async getAvailableCountries(): Promise<string[]> {
    await this.countrySelect.click();
    const options = this.countryOptions;
    const count = await options.count();
    const countries: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const country = await options.nth(i).textContent();
      if (country) {
        countries.push(country);
      }
    }
    
    // Close dropdown
    await this.countrySelect.click();
    
    return countries;
  }

  /**
   * Validate calculation results against expected values
   */
  async validateResults(expected: TestDutyCalculation): Promise<boolean> {
    const dutyText = await this.getDutyAmount();
    const gstText = await this.getGstAmount();
    const totalText = await this.getTotalAmount();
    
    // Extract numeric values (assuming format like "$50.00")
    const dutyValue = parseFloat(dutyText.replace(/[^0-9.]/g, ''));
    const gstValue = parseFloat(gstText.replace(/[^0-9.]/g, ''));
    const totalValue = parseFloat(totalText.replace(/[^0-9.]/g, ''));
    
    // Allow for small rounding differences
    const tolerance = 0.01;
    
    return (
      Math.abs(dutyValue - expected.expectedDuty) <= tolerance &&
      Math.abs(gstValue - expected.expectedGst) <= tolerance &&
      Math.abs(totalValue - expected.expectedTotal) <= tolerance
    );
  }

  /**
   * Perform a complete calculation workflow
   */
  async performCalculation(calculation: TestDutyCalculation): Promise<void> {
    await this.fillCalculationForm(calculation);
    await this.submitCalculation();
  }
}