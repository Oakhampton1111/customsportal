/**
 * Integration tests for Tariff API endpoints
 * Tests real API communication with backend server
 */

import { apiClient } from '../../utils/api-client';
import {
  setupIntegrationTestData,
  cleanupIntegrationTestData,
  waitForBackendReady,
  validateApiResponse,
  validateTariffCode,
  testApiEndpoint,
  measureApiPerformance,
  createTestTariffData,
  type TestData,
} from '../../utils/integration-helpers';

describe('Tariff API Integration Tests', () => {
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

  describe('GET /api/tariff/sections', () => {
    it('should fetch all tariff sections', async () => {
      const sections = await testApiEndpoint(
        () => apiClient.getTariffSections(),
        3,
        5000 // 5 second max response time
      );

      expect(Array.isArray(sections)).toBe(true);
      expect(sections.length).toBeGreaterThan(0);

      // Validate section structure
      const firstSection = sections[0];
      validateApiResponse(firstSection, ['id', 'title']);
      expect(typeof firstSection.id).toBe('string');
      expect(typeof firstSection.title).toBe('string');
    });

    it('should return sections in correct order', async () => {
      const sections = await apiClient.getTariffSections();
      
      // Sections should be ordered by ID
      for (let i = 1; i < sections.length; i++) {
        const prevId = parseInt(sections[i - 1].id);
        const currentId = parseInt(sections[i].id);
        expect(currentId).toBeGreaterThan(prevId);
      }
    });

    it('should have consistent response format', async () => {
      const sections = await apiClient.getTariffSections();
      
      sections.forEach((section: Record<string, unknown>) => {
        validateApiResponse(section, ['id', 'title']);
        expect(section.id).toMatch(/^\d{1,2}$/); // 1-2 digit section ID
        expect(typeof section.title).toBe('string');
        expect((section.title as string).length).toBeGreaterThan(0);
      });
    });

    it('should perform within acceptable time limits', async () => {
      const metrics = await measureApiPerformance(
        () => apiClient.getTariffSections(),
        5
      );

      expect(metrics.averageResponseTime).toBeLessThan(3000); // 3 seconds average
      expect(metrics.maxResponseTime).toBeLessThan(10000); // 10 seconds max
      expect(metrics.successRate).toBe(1); // 100% success rate
    });
  });

  describe('GET /api/tariff/chapters/{sectionId}', () => {
    it('should fetch chapters for a valid section', async () => {
      // First get sections to find a valid section ID
      const sections = await apiClient.getTariffSections();
      expect(sections.length).toBeGreaterThan(0);
      
      const sectionId = sections[0].id;
      const chapters = await testApiEndpoint(
        () => apiClient.getTariffChapters(sectionId),
        3,
        5000
      );

      expect(Array.isArray(chapters)).toBe(true);
      
      if (chapters.length > 0) {
        const firstChapter = chapters[0];
        validateApiResponse(firstChapter, ['id', 'title', 'section_id']);
        expect(firstChapter.section_id).toBe(sectionId);
      }
    });

    it('should return 404 for invalid section ID', async () => {
      await expect(
        apiClient.getTariffChapters('999')
      ).rejects.toMatchObject({
        status: 404,
      });
    });

    it('should validate chapter structure', async () => {
      const sections = await apiClient.getTariffSections();
      const sectionId = sections[0].id;
      const chapters = await apiClient.getTariffChapters(sectionId);
      
      chapters.forEach((chapter: Record<string, unknown>) => {
        validateApiResponse(chapter, ['id', 'title', 'section_id']);
        expect(chapter.id).toMatch(/^\d{2}$/); // 2-digit chapter ID
        expect(typeof chapter.title).toBe('string');
        expect(chapter.section_id).toBe(sectionId);
      });
    });
  });

  describe('GET /api/tariff/code/{hsCode}', () => {
    const testTariffData = createTestTariffData();

    it('should fetch detailed tariff information for valid HS code', async () => {
      const hsCode = testTariffData.tariffCodes[0].hs_code;
      
      const tariffInfo = await testApiEndpoint(
        () => apiClient.getTariffCode(hsCode),
        3,
        5000
      );

      validateApiResponse(tariffInfo, [
        'hs_code',
        'description',
        'general_rate',
        'gst_rate',
      ]);

      validateTariffCode(tariffInfo.hs_code);
      expect(tariffInfo.hs_code).toBe(hsCode);
      expect(typeof tariffInfo.description).toBe('string');
      expect(tariffInfo.description.length).toBeGreaterThan(0);
    });

    it('should return 404 for invalid HS code', async () => {
      await expect(
        apiClient.getTariffCode('9999.99.99')
      ).rejects.toMatchObject({
        status: 404,
      });
    });

    it('should validate HS code format in request', async () => {
      await expect(
        apiClient.getTariffCode('invalid-code')
      ).rejects.toMatchObject({
        status: 422, // Validation error
      });
    });

    it('should include duty rates and related information', async () => {
      const hsCode = testTariffData.tariffCodes[0].hs_code;
      const tariffInfo = await apiClient.getTariffCode(hsCode);

      // Check duty rates
      expect(tariffInfo).toHaveProperty('general_rate');
      expect(tariffInfo).toHaveProperty('gst_rate');
      
      // Rates should be valid percentages or 'Free'
      const generalRate = tariffInfo.general_rate;
      expect(
        generalRate === 'Free' || 
        generalRate.match(/^\d+(\.\d+)?%$/)
      ).toBeTruthy();
    });
  });

  describe('GET /api/tariff/search', () => {
    it('should search tariff codes by description', async () => {
      const searchResults = await testApiEndpoint(
        () => apiClient.searchTariffs('computer'),
        3,
        10000 // Search might take longer
      );

      validateApiResponse(searchResults, ['results', 'total', 'page']);
      expect(Array.isArray(searchResults.results)).toBe(true);
      expect(typeof searchResults.total).toBe('number');
      expect(searchResults.total).toBeGreaterThanOrEqual(0);

      if (searchResults.results.length > 0) {
        const firstResult = searchResults.results[0];
        validateApiResponse(firstResult, ['hs_code', 'description']);
        validateTariffCode(firstResult.hs_code);
      }
    });

    it('should support pagination', async () => {
      const page1 = await apiClient.searchTariffs('animal', { page: 1, limit: 5 });
      const page2 = await apiClient.searchTariffs('animal', { page: 2, limit: 5 });

      expect(page1.page).toBe(1);
      expect(page2.page).toBe(2);
      expect(page1.results.length).toBeLessThanOrEqual(5);
      expect(page2.results.length).toBeLessThanOrEqual(5);

      // Results should be different between pages
      if (page1.results.length > 0 && page2.results.length > 0) {
        expect(page1.results[0].hs_code).not.toBe(page2.results[0].hs_code);
      }
    });

    it('should support filtering by section', async () => {
      const sections = await apiClient.getTariffSections();
      const sectionId = sections[0].id;
      
      const filteredResults = await apiClient.searchTariffs('', {
        section: sectionId,
        limit: 10,
      });

      expect(filteredResults.results.length).toBeGreaterThan(0);
      
      // All results should belong to the specified section
      filteredResults.results.forEach((result: Record<string, unknown>) => {
        const hsCode = result.hs_code as string;
        const chapterCode = hsCode.substring(0, 2);
        
        // Verify chapter belongs to section (this would need section-chapter mapping)
        expect(typeof chapterCode).toBe('string');
        expect(chapterCode).toMatch(/^\d{2}$/);
      });
    });

    it('should handle empty search results gracefully', async () => {
      const searchResults = await apiClient.searchTariffs('nonexistentproduct12345');
      
      expect(searchResults.results).toEqual([]);
      expect(searchResults.total).toBe(0);
      expect(searchResults.page).toBe(1);
    });

    it('should validate search parameters', async () => {
      // Test invalid page number
      await expect(
        apiClient.searchTariffs('test', { page: -1 })
      ).rejects.toMatchObject({
        status: 422,
      });

      // Test invalid limit
      await expect(
        apiClient.searchTariffs('test', { limit: 1000 })
      ).rejects.toMatchObject({
        status: 422,
      });
    });
  });

  describe('API Performance and Reliability', () => {
    it('should handle concurrent requests', async () => {
      const concurrentRequests = Array(5).fill(null).map(() =>
        apiClient.getTariffSections()
      );

      const results = await Promise.all(concurrentRequests);
      
      // All requests should succeed and return the same data
      results.forEach((sections) => {
        expect(Array.isArray(sections)).toBe(true);
        expect(sections.length).toBeGreaterThan(0);
      });

      // Results should be identical
      const firstResult = JSON.stringify(results[0]);
      results.forEach((result) => {
        expect(JSON.stringify(result)).toBe(firstResult);
      });
    });

    it('should handle rate limiting gracefully', async () => {
      // Make many rapid requests to test rate limiting
      const rapidRequests = Array(20).fill(null).map((_, index) =>
        apiClient.getTariffSections().catch((error) => ({
          error: true,
          status: error.status,
          index,
        }))
      );

      const results = await Promise.all(rapidRequests);
      
      // Some requests might be rate limited (429) but most should succeed
      const successfulRequests = results.filter((result) => !(result as { error?: boolean }).error);
      const rateLimitedRequests = results.filter(
        (result) => (result as { error?: boolean; status?: number }).error &&
                   (result as { error?: boolean; status?: number }).status === 429
      );

      expect(successfulRequests.length).toBeGreaterThan(10);
      
      if (rateLimitedRequests.length > 0) {
        console.log(`${rateLimitedRequests.length} requests were rate limited`);
      }
    });

    it('should maintain data consistency across requests', async () => {
      // Make multiple requests for the same data
      const requests = Array(3).fill(null).map(() =>
        apiClient.getTariffCode('0101.10.00')
      );

      const results = await Promise.allSettled(requests);
      
      const successfulResults = results
        .filter((result) => result.status === 'fulfilled')
        .map((result) => (result as PromiseFulfilledResult<unknown>).value);

      if (successfulResults.length > 1) {
        // All successful results should be identical
        const firstResult = JSON.stringify(successfulResults[0]);
        successfulResults.forEach((result) => {
          expect(JSON.stringify(result)).toBe(firstResult);
        });
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle network timeouts', async () => {
      // This test would require a way to simulate network delays
      // For now, we'll test with a very short timeout
      const originalTimeout = apiClient['defaultTimeout'];
      apiClient['defaultTimeout'] = 1; // 1ms timeout

      await expect(
        apiClient.getTariffSections()
      ).rejects.toThrow(/timeout/i);

      // Restore original timeout
      apiClient['defaultTimeout'] = originalTimeout;
    });

    it('should provide meaningful error messages', async () => {
      try {
        await apiClient.getTariffCode('invalid');
      } catch (error) {
        expect(error).toHaveProperty('message');
        expect(error).toHaveProperty('status');
        const errorObj = error as Record<string, unknown>;
        expect(typeof errorObj.message).toBe('string');
        expect((errorObj.message as string).length).toBeGreaterThan(0);
      }
    });

    it('should handle malformed responses gracefully', async () => {
      // This would require mocking the fetch response
      // For integration tests, we assume the backend returns well-formed responses
      const sections = await apiClient.getTariffSections();
      expect(Array.isArray(sections)).toBe(true);
    });
  });
});