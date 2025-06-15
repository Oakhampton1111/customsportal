/**
 * Integration tests for Duty Calculator API endpoints
 * Tests real API communication with backend server
 */

import { apiClient } from '../../utils/api-client';
import {
  setupIntegrationTestData,
  cleanupIntegrationTestData,
  waitForBackendReady,
  validateApiResponse,
  validateDutyCalculation,
  testApiEndpoint,
  measureApiPerformance,
  createTestDutyData,
  type TestData,
} from '../../utils/integration-helpers';

describe('Duty Calculator API Integration Tests', () => {
  let testData: TestData;

  beforeAll(async () => {
    // Wait for backend to be ready
    await waitForBackendReady();
    
    // Setup test data
    testData = await setupIntegrationTestData();
    
    // Authenticate test user
    if (testData.users.length > 0) {
      apiClient.setAuthToken(testData.users[0].token!);
    }
  }, 60000);

  afterAll(async () => {
    // Cleanup test data
    await cleanupIntegrationTestData(testData);
  });

  describe('POST /api/duty/calculate', () => {
    const testDutyData = createTestDutyData();

    it('should calculate duty for valid inputs', async () => {
      const testCase = testDutyData.calculations[0];
      
      const calculation = await testApiEndpoint(
        () => apiClient.calculateDuty(
          testCase.hs_code,
          testCase.value,
          testCase.country_code
        ),
        3,
        10000 // 10 second max response time for calculations
      );

      validateDutyCalculation(calculation);
      expect(calculation.hs_code).toBe(testCase.hs_code);
      expect(calculation.total_duty).toBeGreaterThanOrEqual(0);
    });

    it('should handle different country codes', async () => {
      const hsCode = '0101.10.00';
      const value = 10000;
      const countries = ['US', 'CN', 'JP', 'GB', 'DE'];

      for (const countryCode of countries) {
        const calculation = await apiClient.calculateDuty(hsCode, value, countryCode);
        
        validateDutyCalculation(calculation);
        expect(calculation.hs_code).toBe(hsCode);
        expect(calculation.country_code).toBe(countryCode);
      }
    });

    it('should calculate GST correctly', async () => {
      const testCase = testDutyData.calculations[0];
      
      const calculation = await apiClient.calculateDuty(
        testCase.hs_code,
        testCase.value,
        testCase.country_code
      );

      // Check GST calculation
      const breakdown = calculation.breakdown as Array<Record<string, unknown>>;
      const gstComponent = breakdown.find(
        (component) => (component.type as string).toLowerCase().includes('gst')
      );

      if (gstComponent) {
        expect(typeof gstComponent.amount).toBe('number');
        expect(gstComponent.amount).toBeGreaterThanOrEqual(0);
        expect(typeof gstComponent.rate).toBe('string');
      }
    });

    it('should handle FTA preferences', async () => {
      const calculation = await apiClient.calculateDuty(
        '8471.30.00',
        5000,
        'US', // US has FTA with Australia
        { include_fta: true }
      );

      validateDutyCalculation(calculation);
      
      // Should include FTA analysis
      expect(calculation).toHaveProperty('fta_analysis');
      const ftaAnalysis = calculation.fta_analysis as Record<string, unknown>;
      expect(ftaAnalysis).toHaveProperty('applicable_agreements');
      expect(ftaAnalysis).toHaveProperty('best_rate');
    });

    it('should validate input parameters', async () => {
      // Test invalid HS code
      await expect(
        apiClient.calculateDuty('invalid', 1000, 'US')
      ).rejects.toMatchObject({
        status: 422,
      });

      // Test negative value
      await expect(
        apiClient.calculateDuty('0101.10.00', -1000, 'US')
      ).rejects.toMatchObject({
        status: 422,
      });

      // Test invalid country code
      await expect(
        apiClient.calculateDuty('0101.10.00', 1000, 'INVALID')
      ).rejects.toMatchObject({
        status: 422,
      });
    });

    it('should handle large values correctly', async () => {
      const largeValue = 1000000; // $1M
      
      const calculation = await apiClient.calculateDuty(
        '8471.30.00',
        largeValue,
        'US'
      );

      validateDutyCalculation(calculation);
      expect(calculation.total_duty).toBeGreaterThanOrEqual(0);
      expect(calculation.total_duty).toBeLessThan(largeValue); // Duty shouldn't exceed value
    });

    it('should provide detailed breakdown', async () => {
      const calculation = await apiClient.calculateDuty(
        '8471.30.00',
        10000,
        'CN'
      );

      const breakdown = calculation.breakdown as Array<Record<string, unknown>>;
      expect(Array.isArray(breakdown)).toBe(true);
      expect(breakdown.length).toBeGreaterThan(0);

      breakdown.forEach((component) => {
        validateApiResponse(component, ['type', 'rate', 'amount']);
        expect(typeof component.type).toBe('string');
        expect(typeof component.amount).toBe('number');
        expect(component.amount).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('GET /api/duty/rates/{hsCode}', () => {
    it('should fetch all duty rates for HS code', async () => {
      const hsCode = '0101.10.00';
      
      const rates = await testApiEndpoint(
        () => apiClient.getDutyRates(hsCode),
        3,
        5000
      );

      validateApiResponse(rates, ['hs_code', 'general_rate', 'gst_rate']);
      expect(rates.hs_code).toBe(hsCode);
      expect(typeof rates.general_rate).toBe('string');
      expect(typeof rates.gst_rate).toBe('string');
    });

    it('should include FTA rates when available', async () => {
      const hsCode = '8471.30.00';
      const rates = await apiClient.getDutyRates(hsCode);

      if (rates.fta_rates) {
        expect(Array.isArray(rates.fta_rates)).toBe(true);
        
        rates.fta_rates.forEach((ftaRate: Record<string, unknown>) => {
          validateApiResponse(ftaRate, ['country_code', 'rate', 'agreement']);
          expect(typeof ftaRate.country_code).toBe('string');
          expect(typeof ftaRate.rate).toBe('string');
          expect(typeof ftaRate.agreement).toBe('string');
        });
      }
    });

    it('should handle invalid HS codes', async () => {
      await expect(
        apiClient.getDutyRates('9999.99.99')
      ).rejects.toMatchObject({
        status: 404,
      });
    });
  });

  describe('GET /api/duty/fta-rates/{hsCode}/{countryCode}', () => {
    it('should fetch FTA rates for specific country', async () => {
      const hsCode = '8471.30.00';
      const countryCode = 'US';
      
      const ftaRates = await testApiEndpoint(
        () => apiClient.getFtaRates(hsCode, countryCode),
        3,
        5000
      );

      validateApiResponse(ftaRates, ['hs_code', 'country_code', 'rates']);
      expect(ftaRates.hs_code).toBe(hsCode);
      expect(ftaRates.country_code).toBe(countryCode);
      expect(Array.isArray(ftaRates.rates)).toBe(true);
    });

    it('should return empty rates for non-FTA countries', async () => {
      const hsCode = '0101.10.00';
      const countryCode = 'RU'; // Russia - no FTA with Australia
      
      const ftaRates = await apiClient.getFtaRates(hsCode, countryCode);
      
      expect(ftaRates.rates).toEqual([]);
      expect(ftaRates.has_fta).toBe(false);
    });

    it('should validate country codes', async () => {
      await expect(
        apiClient.getFtaRates('0101.10.00', 'INVALID')
      ).rejects.toMatchObject({
        status: 422,
      });
    });
  });

  describe('GET /api/duty/tco-check/{hsCode}', () => {
    it('should check TCO availability', async () => {
      const hsCode = '8471.30.00';
      
      const tcoCheck = await testApiEndpoint(
        () => apiClient.checkTco(hsCode),
        3,
        5000
      );

      validateApiResponse(tcoCheck, ['hs_code', 'has_tco']);
      expect(tcoCheck.hs_code).toBe(hsCode);
      expect(typeof tcoCheck.has_tco).toBe('boolean');
    });

    it('should provide TCO details when available', async () => {
      const hsCode = '8471.30.00';
      const tcoCheck = await apiClient.checkTco(hsCode);

      if (tcoCheck.has_tco) {
        expect(tcoCheck).toHaveProperty('tco_orders');
        expect(Array.isArray(tcoCheck.tco_orders)).toBe(true);
        
        if (tcoCheck.tco_orders.length > 0) {
          const tcoOrder = tcoCheck.tco_orders[0] as Record<string, unknown>;
          validateApiResponse(tcoOrder, ['order_number', 'description', 'rate']);
        }
      }
    });

    it('should handle HS codes without TCO', async () => {
      const hsCode = '0101.10.00'; // Live animals typically don't have TCO
      const tcoCheck = await apiClient.checkTco(hsCode);

      expect(tcoCheck.has_tco).toBe(false);
      expect(tcoCheck.tco_orders).toEqual([]);
    });
  });

  describe('Performance and Reliability', () => {
    it('should handle concurrent duty calculations', async () => {
      const testCase = createTestDutyData().calculations[0];
      
      const concurrentCalculations = Array(5).fill(null).map(() =>
        apiClient.calculateDuty(
          testCase.hs_code,
          testCase.value,
          testCase.country_code
        )
      );

      const results = await Promise.all(concurrentCalculations);
      
      // All calculations should succeed and return consistent results
      results.forEach((calculation) => {
        validateDutyCalculation(calculation);
        expect(calculation.hs_code).toBe(testCase.hs_code);
      });

      // Results should be identical for same inputs
      const firstResult = JSON.stringify(results[0]);
      results.forEach((result) => {
        expect(JSON.stringify(result)).toBe(firstResult);
      });
    });

    it('should maintain calculation accuracy', async () => {
      const testCases = createTestDutyData().calculations;
      
      for (const testCase of testCases) {
        const calculation = await apiClient.calculateDuty(
          testCase.hs_code,
          testCase.value,
          testCase.country_code
        );

        // Verify calculation accuracy within reasonable tolerance
        const expectedTotal = testCase.expected_duty + testCase.expected_gst;
        const actualTotal = calculation.total_duty;
        const tolerance = expectedTotal * 0.01; // 1% tolerance
        
        expect(Math.abs(actualTotal - expectedTotal)).toBeLessThanOrEqual(tolerance);
      }
    });

    it('should perform calculations within time limits', async () => {
      const metrics = await measureApiPerformance(
        () => apiClient.calculateDuty('8471.30.00', 10000, 'US'),
        3
      );

      expect(metrics.averageResponseTime).toBeLessThan(5000); // 5 seconds average
      expect(metrics.maxResponseTime).toBeLessThan(15000); // 15 seconds max
      expect(metrics.successRate).toBe(1); // 100% success rate
    });
  });

  describe('Complex Calculation Scenarios', () => {
    it('should handle anti-dumping duties', async () => {
      // Test with a product that might have anti-dumping duties
      const calculation = await apiClient.calculateDuty(
        '7208.10.00', // Steel products often have anti-dumping
        50000,
        'CN',
        { include_antidumping: true }
      );

      validateDutyCalculation(calculation);
      
      const breakdown = calculation.breakdown as Array<Record<string, unknown>>;
      const antidumpingComponent = breakdown.find(
        (component) => (component.type as string).toLowerCase().includes('dumping')
      );

      if (antidumpingComponent) {
        expect(typeof antidumpingComponent.amount).toBe('number');
        expect(antidumpingComponent.amount).toBeGreaterThanOrEqual(0);
      }
    });

    it('should calculate best rate scenarios', async () => {
      const calculation = await apiClient.calculateDuty(
        '8471.30.00',
        25000,
        'US',
        { 
          include_fta: true,
          include_tco: true,
          calculate_best_rate: true 
        }
      );

      validateDutyCalculation(calculation);
      expect(calculation).toHaveProperty('best_rate_analysis');
      
      const bestRateAnalysis = calculation.best_rate_analysis as Record<string, unknown>;
      expect(bestRateAnalysis).toHaveProperty('recommended_option');
      expect(bestRateAnalysis).toHaveProperty('potential_savings');
    });

    it('should handle multiple duty components', async () => {
      const calculation = await apiClient.calculateDuty(
        '2402.10.00', // Tobacco products have multiple duties
        15000,
        'US',
        { include_all_duties: true }
      );

      validateDutyCalculation(calculation);
      
      const breakdown = calculation.breakdown as Array<Record<string, unknown>>;
      expect(breakdown.length).toBeGreaterThan(1); // Should have multiple components
      
      // Should include customs duty, excise, and GST
      const dutyTypes = breakdown.map((component) => 
        (component.type as string).toLowerCase()
      );
      
      expect(dutyTypes.some(type => type.includes('customs'))).toBe(true);
      expect(dutyTypes.some(type => type.includes('gst'))).toBe(true);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle zero value calculations', async () => {
      const calculation = await apiClient.calculateDuty(
        '0101.10.00',
        0,
        'US'
      );

      validateDutyCalculation(calculation);
      expect(calculation.total_duty).toBe(0);
    });

    it('should handle very small values', async () => {
      const calculation = await apiClient.calculateDuty(
        '8471.30.00',
        0.01, // 1 cent
        'US'
      );

      validateDutyCalculation(calculation);
      expect(calculation.total_duty).toBeGreaterThanOrEqual(0);
    });

    it('should provide meaningful error messages for invalid inputs', async () => {
      try {
        await apiClient.calculateDuty('invalid', 1000, 'US');
      } catch (error) {
        const errorObj = error as Record<string, unknown>;
        expect(errorObj).toHaveProperty('message');
        expect(typeof errorObj.message).toBe('string');
        expect((errorObj.message as string).length).toBeGreaterThan(0);
      }
    });

    it('should handle currency conversion scenarios', async () => {
      const calculation = await apiClient.calculateDuty(
        '8471.30.00',
        10000,
        'US',
        { 
          currency: 'USD',
          exchange_rate: 1.5 // AUD to USD
        }
      );

      validateDutyCalculation(calculation);
      expect(calculation).toHaveProperty('currency_info');
      
      const currencyInfo = calculation.currency_info as Record<string, unknown>;
      expect(currencyInfo).toHaveProperty('original_currency');
      expect(currencyInfo).toHaveProperty('aud_value');
    });
  });
});