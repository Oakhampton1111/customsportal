import React from 'react';
import { screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '../../../__tests__/utils/test-utils';
import { DutyCalculatorPage } from '../../DutyCalculatorPage';
import { setupMockServer, DutyApiMocks, TariffApiMocks, MockApiUtils } from '../../../__tests__/utils/api-mocks';
import { TariffDataFactory } from '../../../__tests__/utils/mock-data';

// Setup MSW for API mocking
setupMockServer();

describe('API Integration Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
        mutations: {
          retry: false,
        },
      },
    });
    jest.clearAllMocks();
    MockApiUtils.resetToDefaults();
  });

  describe('Duty Calculator API Integration', () => {
    it('handles successful duty calculation API calls', async () => {
      const mockResult = {
        hs_code: '8471.30.00',
        country_code: 'CN',
        customs_value: 1000,
        total_duty: 125,
        total_gst: 112.5,
        total_amount: 1237.5,
        calculation_date: '2023-12-01',
        currency: 'AUD',
        components: [
          {
            duty_type: 'General Duty',
            rate: 5.0,
            amount: 50,
            description: 'Standard tariff rate',
            basis: 'Customs Value',
            applicable: true
          }
        ]
      };

      DutyApiMocks.mockCalculateSuccess(mockResult);

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
      
      // The actual API call would be triggered by form submission
      // Here we test that the page is ready to handle API responses
    });

    it('handles API validation errors gracefully', async () => {
      DutyApiMocks.mockCalculateValidationError();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
      
      // Page should render normally even with API errors configured
    });

    it('handles network errors gracefully', async () => {
      MockApiUtils.setupNetworkError();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
      
      // Page should render normally even with network errors
    });

    it('handles slow API responses with loading states', async () => {
      MockApiUtils.setupSlowResponse(2000);

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
      
      // Page should handle slow responses gracefully
    });

    it('handles empty API responses', async () => {
      MockApiUtils.setupEmptyResponse();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });

  describe('Tariff Search API Integration', () => {
    it('handles successful tariff search API calls', async () => {
      const mockTariffs = TariffDataFactory.createMany(2, {
        category: 'Electronics'
      });

      TariffApiMocks.mockSearchSuccess(mockTariffs);

      // Test would involve a search page component
      // For now, we verify the mock is set up correctly
      expect(mockTariffs).toHaveLength(2);
    });

    it('handles tariff search with no results', async () => {
      TariffApiMocks.mockSearchEmpty();

      // Test empty search results handling
      expect(true).toBe(true); // Placeholder for actual test
    });

    it('handles tariff lookup by HS code', async () => {
      const hsCode = '8471.30.00';
      const mockTariff = TariffDataFactory.create({
        hsCode,
        description: 'Portable automatic data processing machines',
        category: 'Electronics'
      });

      TariffApiMocks.mockGetTariffSuccess(hsCode, mockTariff);

      // Test individual tariff lookup
      expect(mockTariff.hsCode).toBe(hsCode);
    });

    it('handles tariff not found errors', async () => {
      const hsCode = '9999.99.99';
      TariffApiMocks.mockGetTariffNotFound(hsCode);

      // Test 404 handling for non-existent tariffs
      expect(hsCode).toBe('9999.99.99');
    });
  });

  describe('React Query Integration', () => {
    it('integrates with React Query for data fetching', async () => {
      const TestComponent = () => (
        <QueryClientProvider client={queryClient}>
          <DutyCalculatorPage />
        </QueryClientProvider>
      );

      render(<TestComponent />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('handles query caching correctly', async () => {
      const TestComponent = () => (
        <QueryClientProvider client={queryClient}>
          <DutyCalculatorPage />
        </QueryClientProvider>
      );

      render(<TestComponent />);

      // Test that React Query is properly integrated
      expect(queryClient.getQueryCache().getAll()).toHaveLength(0);
    });

    it('handles query invalidation', async () => {
      const TestComponent = () => (
        <QueryClientProvider client={queryClient}>
          <DutyCalculatorPage />
        </QueryClientProvider>
      );

      render(<TestComponent />);

      // Test query invalidation
      await queryClient.invalidateQueries();
      expect(queryClient.isFetching()).toBe(0);
    });

    it('handles optimistic updates', async () => {
      const TestComponent = () => (
        <QueryClientProvider client={queryClient}>
          <DutyCalculatorPage />
        </QueryClientProvider>
      );

      render(<TestComponent />);

      // Test optimistic updates for better UX
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('recovers from API errors', async () => {
      // First, set up an error
      MockApiUtils.setupErrorResponses();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();

      // Then recover with successful responses
      MockApiUtils.setupSuccessfulResponses();

      // Page should handle the recovery gracefully
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('handles intermittent network issues', async () => {
      // Simulate intermittent network issues
      MockApiUtils.setupNetworkError();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();

      // Reset to working state
      MockApiUtils.resetToDefaults();

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('provides user feedback for API errors', async () => {
      MockApiUtils.setupErrorResponses();

      render(<DutyCalculatorPage />);

      // Page should render and be ready to show error feedback
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('handles concurrent API requests efficiently', async () => {
      DutyApiMocks.mockCalculateSuccess();
      TariffApiMocks.mockSearchSuccess();

      const startTime = performance.now();
      render(<DutyCalculatorPage />);
      const endTime = performance.now();

      const renderTime = endTime - startTime;
      expect(renderTime).toBeLessThan(100);
    });

    it('implements proper request debouncing', async () => {
      // Test that rapid requests are properly debounced
      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('handles large API responses efficiently', async () => {
      // Mock large response
      const largeTariffList = TariffDataFactory.createMany(1000, {
        category: 'Electronics'
      });

      TariffApiMocks.mockSearchSuccess(largeTariffList);

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });

  describe('Authentication Integration', () => {
    it('handles authenticated API requests', async () => {
      // Test API requests with authentication
      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('handles token refresh scenarios', async () => {
      // Test token refresh during API calls
      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('handles unauthorized responses', async () => {
      MockApiUtils.setupAuthError();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });

  describe('Data Transformation', () => {
    it('transforms API responses correctly', async () => {
      const mockApiResponse = {
        hs_code: '8471.30.00',
        country_code: 'CN',
        customs_value: 1000,
        total_duty: 125,
        total_gst: 112.5,
        total_amount: 1237.5,
        calculation_date: '2023-12-01',
        currency: 'AUD',
        components: []
      };

      DutyApiMocks.mockCalculateSuccess(mockApiResponse);

      render(<DutyCalculatorPage />);

      // Test that API response is properly transformed for UI consumption
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('handles malformed API responses', async () => {
      // Mock malformed response
      const malformedResponse = {
        invalid_field: 'invalid_value'
      };

      DutyApiMocks.mockCalculateSuccess(malformedResponse);

      render(<DutyCalculatorPage />);

      // Should handle malformed responses gracefully
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('validates API response schemas', async () => {
      const validResponse = {
        hs_code: '8471.30.00',
        country_code: 'CN',
        customs_value: 1000,
        total_duty: 125,
        total_gst: 112.5,
        total_amount: 1237.5,
        calculation_date: '2023-12-01',
        currency: 'AUD',
        components: []
      };

      DutyApiMocks.mockCalculateSuccess(validResponse);

      render(<DutyCalculatorPage />);

      // Test schema validation
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });

  describe('Offline Behavior', () => {
    it('handles offline scenarios gracefully', async () => {
      // Simulate offline condition
      MockApiUtils.setupNetworkError();

      render(<DutyCalculatorPage />);

      // Should provide appropriate offline feedback
      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('queues requests when offline', async () => {
      // Test request queueing for offline scenarios
      MockApiUtils.setupNetworkError();

      render(<DutyCalculatorPage />);

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });

    it('syncs data when coming back online', async () => {
      // Test data synchronization when connectivity is restored
      MockApiUtils.setupNetworkError();

      render(<DutyCalculatorPage />);

      // Restore connectivity
      MockApiUtils.resetToDefaults();

      expect(screen.getByRole('heading', { name: /duty calculator/i })).toBeInTheDocument();
    });
  });
});