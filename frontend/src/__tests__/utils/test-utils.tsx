import React, { type ReactElement } from 'react';
import { render, type RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Custom render function that includes providers
interface AllTheProvidersProps {
  children: React.ReactNode;
}

const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  // Create a new QueryClient for each test to ensure isolation
  const queryClient = new QueryClient({
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

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Custom render with specific providers
export const renderWithRouter = (ui: ReactElement, options?: RenderOptions) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>{children}</BrowserRouter>
  );
  
  return render(ui, { wrapper: Wrapper, ...options });
};

export const renderWithQueryClient = (ui: ReactElement, options?: RenderOptions) => {
  const queryClient = new QueryClient({
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

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
  
  return render(ui, { wrapper: Wrapper, ...options });
};

// Form testing utilities
export const fillForm = async (
  getByLabelText: (text: string) => HTMLElement,
  formData: Record<string, string>
) => {
  const { userEvent } = await import('@testing-library/user-event');
  const user = userEvent.setup();
  
  for (const [label, value] of Object.entries(formData)) {
    const field = getByLabelText(label);
    await user.clear(field);
    await user.type(field, value);
  }
};

// Wait for loading states
export const waitForLoadingToFinish = async (container: HTMLElement) => {
  const { waitForElementToBeRemoved } = await import('@testing-library/react');
  
  const loadingElement = container.querySelector('[data-testid="loading"]') ||
                        container.querySelector('.loading') ||
                        Array.from(container.querySelectorAll('*')).find(el =>
                          el.textContent?.toLowerCase().includes('loading')
                        );
  
  if (loadingElement) {
    await waitForElementToBeRemoved(loadingElement);
  }
};

// Custom matchers for common assertions
export const expectElementToBeVisible = (element: HTMLElement | null) => {
  expect(element).toBeInTheDocument();
  expect(element).toBeVisible();
};

export const expectElementToHaveText = (element: HTMLElement | null, text: string) => {
  expect(element).toBeInTheDocument();
  expect(element).toHaveTextContent(text);
};

// Mock data generators
export const createMockUser = (overrides = {}) => ({
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
  role: 'user',
  ...overrides,
});

export const createMockTariffData = (overrides = {}) => ({
  hsCode: '1234567890',
  description: 'Test Product',
  dutyRate: 5.0,
  gstRate: 10.0,
  country: 'AU',
  ...overrides,
});

export const createMockDutyCalculation = (overrides = {}) => ({
  hsCode: '1234567890',
  value: 1000,
  country: 'CN',
  dutyAmount: 50,
  gstAmount: 105,
  totalAmount: 1155,
  ...overrides,
});

// Test data factories
export class TestDataFactory {
  static createTariffSearchResult(count = 1, overrides = {}) {
    return Array.from({ length: count }, (_, index) => ({
      id: `tariff-${index + 1}`,
      hsCode: `123456789${index}`,
      description: `Test Product ${index + 1}`,
      dutyRate: 5.0 + index,
      ...overrides,
    }));
  }

  static createDutyCalculationHistory(count = 3, overrides = {}) {
    return Array.from({ length: count }, (_, index) => ({
      id: `calc-${index + 1}`,
      hsCode: `123456789${index}`,
      value: 1000 * (index + 1),
      country: ['CN', 'US', 'JP'][index] || 'CN',
      calculatedAt: new Date(Date.now() - index * 24 * 60 * 60 * 1000).toISOString(),
      ...overrides,
    }));
  }
}

// Performance testing utilities
export const measureRenderTime = async (renderFn: () => void) => {
  const start = performance.now();
  renderFn();
  const end = performance.now();
  return end - start;
};

// Accessibility testing helpers
export const checkAccessibility = async (container: HTMLElement) => {
  // Basic accessibility checks
  const buttons = container.querySelectorAll('button');
  const inputs = container.querySelectorAll('input');
  const links = container.querySelectorAll('a');

  // Check for proper ARIA labels
  buttons.forEach(button => {
    if (!button.textContent && !button.getAttribute('aria-label')) {
      console.warn('Button without accessible name found:', button);
    }
  });

  inputs.forEach(input => {
    if (!input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
      const label = container.querySelector(`label[for="${input.id}"]`);
      if (!label) {
        console.warn('Input without accessible name found:', input);
      }
    }
  });

  links.forEach(link => {
    if (!link.textContent && !link.getAttribute('aria-label')) {
      console.warn('Link without accessible name found:', link);
    }
  });
};

// Error boundary testing
export class TestErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Test Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div data-testid="error-boundary">Something went wrong.</div>;
    }

    return this.props.children;
  }
}

export const renderWithErrorBoundary = (ui: ReactElement, options?: RenderOptions) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AllTheProviders>
      <TestErrorBoundary>{children}</TestErrorBoundary>
    </AllTheProviders>
  );
  
  return render(ui, { wrapper: Wrapper, ...options });
};