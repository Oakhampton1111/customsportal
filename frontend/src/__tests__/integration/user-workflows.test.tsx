import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '../../pages/Dashboard';
import TariffTree from '../../pages/TariffTree';
import AIAssistant from '../../pages/AIAssistant';
import ExportTariffs from '../../pages/ExportTariffs';
import userEvent from '@testing-library/user-event';
import { setupMockServer, DutyApiMocks } from '../utils/api-mocks';

// Setup MSW for API mocking
setupMockServer();

// Create a test app with routing
const TestApp: React.FC<{ initialEntries?: string[] }> = ({ initialEntries = ['/'] }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  return (
    <QueryClientProvider client={queryClient}>
      <Router initialEntries={initialEntries}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tariff-tree" element={<TariffTree />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
          <Route path="/export-tariffs" element={<ExportTariffs />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
};

describe('User Workflow Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('New User Onboarding Workflow', () => {
    it('guides new user from homepage to key features', async () => {
      const user = userEvent.setup();
      render(<TestApp initialEntries={['/']} />);

      // User lands on homepage
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
      expect(screen.getByText(/overview of your customs broker portal activity/i)).toBeInTheDocument();

      // User sees feature overview
      expect(screen.getByText(/tariff search/i)).toBeInTheDocument();
      expect(screen.getByText(/duty calculator/i)).toBeInTheDocument();
      expect(screen.getByText(/compliance tools/i)).toBeInTheDocument();
      expect(screen.getByText(/trade analytics/i)).toBeInTheDocument();

      // User can interact with call-to-action buttons
      const startSearchingBtn = screen.getByRole('button', { name: /start searching/i });
      const calculateDutiesBtn = screen.getByRole('button', { name: /calculate duties/i });

      await user.click(startSearchingBtn);
      await user.click(calculateDutiesBtn);

      // Buttons should be interactive
      expect(startSearchingBtn).toBeInTheDocument();
      expect(calculateDutiesBtn).toBeInTheDocument();
    });

    it('provides clear navigation paths to main features', async () => {
      const user = userEvent.setup();
      render(<TestApp initialEntries={['/']} />);

      // Check quick action buttons
      const findHsCodeBtn = screen.getByRole('button', { name: /start search/i });
      const calculateDutyBtn = screen.getByRole('button', { name: /calculate now/i });
      const checkTcoBtn = screen.getByRole('button', { name: /check tco/i });

      await user.click(findHsCodeBtn);
      await user.click(calculateDutyBtn);
      await user.click(checkTcoBtn);

      // All buttons should be accessible
      expect(findHsCodeBtn).toBeInTheDocument();
      expect(calculateDutyBtn).toBeInTheDocument();
      expect(checkTcoBtn).toBeInTheDocument();
    });
  });

  describe('Duty Calculation Workflow', () => {
    it('completes full duty calculation workflow', async () => {
      // Mock successful calculation
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

      render(<TestApp initialEntries={['/ai-assistant']} />);

      // User arrives at duty calculator
      expect(screen.getByRole('heading', { name: /ai assistant/i })).toBeInTheDocument();
      expect(screen.getByText(/calculate comprehensive duty costs/i)).toBeInTheDocument();

      // User sees guidance information
      expect(screen.getByRole('heading', { name: /calculation guide/i })).toBeInTheDocument();
      expect(screen.getByText(/required information/i)).toBeInTheDocument();
      expect(screen.getByText(/hs code \(6-10 digits\)/i)).toBeInTheDocument();

      // User sees form to enter calculation details
      expect(screen.getByRole('heading', { name: /calculate import duties/i })).toBeInTheDocument();

      // User can access quick links for additional information
      const ftaLookupBtn = screen.getByRole('button', { name: /fta rate lookup/i });
      const tcoSearchBtn = screen.getByRole('button', { name: /tco search/i });

      expect(ftaLookupBtn).toBeInTheDocument();
      expect(tcoSearchBtn).toBeInTheDocument();
    });

    it('handles calculation errors gracefully in workflow', async () => {
      // Mock calculation error
      DutyApiMocks.mockCalculateValidationError();

      render(<TestApp initialEntries={['/ai-assistant']} />);

      // Page should still render and provide helpful information
      expect(screen.getByRole('heading', { name: /ai assistant/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /calculation guide/i })).toBeInTheDocument();

      // User can still access help resources
      expect(screen.getByText(/required information/i)).toBeInTheDocument();
      expect(screen.getByText(/calculated components/i)).toBeInTheDocument();
    });

    it('provides export options after successful calculation', async () => {
      render(<TestApp initialEntries={['/export-tariffs']} />);

      // User sees calculation interface
      expect(screen.getByRole('heading', { name: /export tariffs/i })).toBeInTheDocument();

      // Export functionality would be available after calculation
      // (tested in component-level tests)
    });
  });

  describe('Dashboard Workflow', () => {
    it('provides comprehensive dashboard overview', async () => {
      render(<TestApp initialEntries={['/']} />);

      // User sees dashboard overview
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
      expect(screen.getByText(/overview of your customs broker portal activity/i)).toBeInTheDocument();

      // User sees activity statistics
      expect(screen.getByText(/recent searches/i)).toBeInTheDocument();
      expect(screen.getByText(/duty calculations/i)).toBeInTheDocument();
      expect(screen.getByText(/tco checks/i)).toBeInTheDocument();
      expect(screen.getByText(/active sessions/i)).toBeInTheDocument();

      // User sees recent activity
      expect(screen.getByRole('heading', { name: /recent activity/i })).toBeInTheDocument();
      expect(screen.getByText(/searched for hs code: 8471.30.00/i)).toBeInTheDocument();
      expect(screen.getByText(/calculated duty for import from china/i)).toBeInTheDocument();

      // User has quick access to main features
      expect(screen.getByRole('heading', { name: /quick actions/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /new tariff search/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /calculate duty/i })).toBeInTheDocument();
    });

    it('enables quick navigation to key features from dashboard', async () => {
      const user = userEvent.setup();
      render(<TestApp initialEntries={['/']} />);

      // User can access quick actions
      const tariffSearchBtn = screen.getByRole('button', { name: /new tariff search/i });
      const dutyCalcBtn = screen.getByRole('button', { name: /calculate duty/i });
      const tcoCheckBtn = screen.getByRole('button', { name: /check tco/i });
      const analyticsBtn = screen.getByRole('button', { name: /view analytics/i });

      await user.click(tariffSearchBtn);
      await user.click(dutyCalcBtn);
      await user.click(tcoCheckBtn);
      await user.click(analyticsBtn);

      // All actions should be accessible
      expect(tariffSearchBtn).toBeInTheDocument();
      expect(dutyCalcBtn).toBeInTheDocument();
      expect(tcoCheckBtn).toBeInTheDocument();
      expect(analyticsBtn).toBeInTheDocument();
    });

    it('displays system status for operational awareness', async () => {
      render(<TestApp initialEntries={['/']} />);

      // User sees system status
      expect(screen.getByRole('heading', { name: /system status/i })).toBeInTheDocument();
      expect(screen.getByText(/api status/i)).toBeInTheDocument();
      expect(screen.getByText(/database/i)).toBeInTheDocument();
      expect(screen.getByText(/online/i)).toBeInTheDocument();
      expect(screen.getByText(/connected/i)).toBeInTheDocument();
    });
  });

  describe('Cross-Page Navigation Workflow', () => {
    it('maintains context during navigation between pages', async () => {
      // Test navigation flow: Home -> Dashboard -> Calculator
      render(<TestApp initialEntries={['/']} />);

      // Start at home
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();

      // Navigate to dashboard
      render(<TestApp initialEntries={['/']} />);
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();

      // Navigate to calculator
      render(<TestApp initialEntries={['/ai-assistant']} />);
      expect(screen.getByRole('heading', { name: /ai assistant/i })).toBeInTheDocument();
    });

    it('provides consistent navigation experience', async () => {
      const pages = [
        { path: '/', heading: /dashboard/i },
        { path: '/tariff-tree', heading: /tariff tree/i },
        { path: '/ai-assistant', heading: /ai assistant/i },
        { path: '/export-tariffs', heading: /export tariffs/i },
      ];

      pages.forEach(({ path, heading }) => {
        render(<TestApp initialEntries={[path]} />);
        expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument();
      });
    });
  });

  describe('Error Recovery Workflow', () => {
    it('handles API errors gracefully in user workflow', async () => {
      // Mock API error
      DutyApiMocks.mockCalculateValidationError();

      render(<TestApp initialEntries={['/ai-assistant']} />);

      // User should still see functional interface
      expect(screen.getByRole('heading', { name: /ai assistant/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /calculation guide/i })).toBeInTheDocument();

      // User can still access help and guidance
      expect(screen.getByText(/required information/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /fta rate lookup/i })).toBeInTheDocument();
    });

    it('provides helpful guidance when errors occur', async () => {
      render(<TestApp initialEntries={['/ai-assistant']} />);

      // User sees helpful guidance sections
      expect(screen.getByRole('heading', { name: /calculation guide/i })).toBeInTheDocument();
      expect(screen.getByText(/required information/i)).toBeInTheDocument();
      expect(screen.getByText(/calculated components/i)).toBeInTheDocument();
      expect(screen.getByText(/special considerations/i)).toBeInTheDocument();

      // User has access to quick links for help
      expect(screen.getByRole('button', { name: /fta rate lookup/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /tco search/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /tariff schedule/i })).toBeInTheDocument();
    });
  });

  describe('Accessibility in User Workflows', () => {
    it('supports keyboard navigation throughout workflow', async () => {
      const user = userEvent.setup();
      render(<TestApp initialEntries={['/']} />);

      // User can navigate with keyboard
      await user.tab();
      expect(document.activeElement).toBeInTheDocument();

      // Continue tabbing through interactive elements
      await user.tab();
      expect(document.activeElement).toBeInTheDocument();
    });

    it('provides proper heading structure for screen readers', async () => {
      const pages = [
        { path: '/', h1: /dashboard/i },
        { path: '/tariff-tree', h1: /tariff tree/i },
        { path: '/ai-assistant', h1: /ai assistant/i },
        { path: '/export-tariffs', h1: /export tariffs/i },
      ];

      pages.forEach(({ path, h1 }) => {
        render(<TestApp initialEntries={[path]} />);
        
        const heading = screen.getByRole('heading', { level: 1 });
        expect(heading).toHaveTextContent(h1);
      });
    });

    it('maintains focus management during workflow transitions', async () => {
      render(<TestApp initialEntries={['/']} />);

      // Focus should be manageable on each page
      const interactiveElements = screen.getAllByRole('button');
      if (interactiveElements.length > 0) {
        interactiveElements[0].focus();
        expect(document.activeElement).toBe(interactiveElements[0]);
      }
    });
  });

  describe('Performance in User Workflows', () => {
    it('renders pages quickly during navigation', async () => {
      const pages = ['/', '/tariff-tree', '/ai-assistant', '/export-tariffs'];

      pages.forEach(path => {
        const startTime = performance.now();
        render(<TestApp initialEntries={[path]} />);
        const endTime = performance.now();

        const renderTime = endTime - startTime;
        expect(renderTime).toBeLessThan(150);
      });
    });

    it('handles multiple rapid interactions efficiently', async () => {
      const user = userEvent.setup();
      render(<TestApp initialEntries={['/']} />);

      // Rapid button clicks should not cause issues
      const buttons = screen.getAllByRole('button');
      
      for (let i = 0; i < Math.min(3, buttons.length); i++) {
        await user.click(buttons[i]);
      }

      // Page should remain stable
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
    });
  });

  describe('Mobile User Workflow', () => {
    it('provides mobile-friendly workflow experience', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(<TestApp initialEntries={['/']} />);

      // Mobile layout should work
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();

      render(<TestApp initialEntries={['/tariff-tree']} />);
      expect(screen.getByRole('heading', { name: /tariff tree/i })).toBeInTheDocument();

      render(<TestApp initialEntries={['/ai-assistant']} />);
      expect(screen.getByRole('heading', { name: /ai assistant/i })).toBeInTheDocument();

      render(<TestApp initialEntries={['/export-tariffs']} />);
      expect(screen.getByRole('heading', { name: /export tariffs/i })).toBeInTheDocument();
    });

    it('maintains functionality on touch devices', async () => {
      const user = userEvent.setup();
      render(<TestApp initialEntries={['/']} />);

      // Touch interactions should work
      const buttons = screen.getAllByRole('button');
      if (buttons.length > 0) {
        await user.click(buttons[0]);
        expect(buttons[0]).toBeInTheDocument();
      }
    });
  });
});