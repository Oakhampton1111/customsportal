import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '../../Dashboard';
import TariffTree from '../../TariffTree';
import AIAssistant from '../../AIAssistant';
import ExportTariffs from '../../ExportTariffs';

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
          <Route path="*" element={<div>404 - Page Not Found</div>} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
};

describe('Routing Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Route Rendering', () => {
    it('renders Dashboard at root route', () => {
      render(<TestApp initialEntries={['/']} />);
      
      expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
    });

    it('renders TariffTree at /tariff-tree route', () => {
      render(<TestApp initialEntries={['/tariff-tree']} />);
      
      expect(screen.getByRole('heading', { name: /tariff tree/i })).toBeInTheDocument();
    });

    it('renders AIAssistant at /ai-assistant route', () => {
      render(<TestApp initialEntries={['/ai-assistant']} />);
      
      expect(screen.getByRole('heading', { name: /ai assistant/i })).toBeInTheDocument();
    });

    it('renders ExportTariffs at /export-tariffs route', () => {
      render(<TestApp initialEntries={['/export-tariffs']} />);
      
      expect(screen.getByRole('heading', { name: /export tariffs/i })).toBeInTheDocument();
    });

    it('renders 404 page for unknown routes', () => {
      render(<TestApp initialEntries={['/unknown-route']} />);
      
      expect(screen.getByText(/404 - page not found/i)).toBeInTheDocument();
    });
  });

  describe('Navigation Between Pages', () => {
    it('navigates between pages correctly', () => {
      const routes = [
        { path: '/', heading: /dashboard/i },
        { path: '/tariff-tree', heading: /tariff tree/i },
        { path: '/ai-assistant', heading: /ai assistant/i },
        { path: '/export-tariffs', heading: /export tariffs/i },
      ];

      routes.forEach(({ path, heading }) => {
        render(<TestApp initialEntries={[path]} />);
        expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument();
      });
    });
  });
});