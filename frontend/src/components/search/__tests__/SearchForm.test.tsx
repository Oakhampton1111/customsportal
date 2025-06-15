import React from 'react';
import { render, screen } from '../../../__tests__/utils/test-utils';
import { AccessibilityHelpers } from '../../../__tests__/utils/accessibility-helpers';
import { SearchForm } from '../SearchForm';

describe('SearchForm Component', () => {
  it('renders search form with title and input', () => {
    render(<SearchForm />);
    
    expect(screen.getByRole('heading', { name: /tariff search/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/search by hs code, description, or keywords/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  it('handles search input and submission', async () => {
    const mockOnSearch = jest.fn();
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    const searchInput = screen.getByPlaceholderText(/search by hs code/i);
    const searchButton = screen.getByRole('button', { name: /search/i });
    
    await user.type(searchInput, 'electronics');
    await user.click(searchButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith('electronics', { searchType: 'all' });
  });

  it('shows and hides filters when filter button is clicked', async () => {
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<SearchForm />);
    
    const filterButton = screen.getAllByRole('button')[1]; // Filter button (second button)
    
    expect(screen.queryByText(/search filters/i)).not.toBeInTheDocument();
    
    await user.click(filterButton);
    expect(screen.getByText(/search filters/i)).toBeInTheDocument();
    
    await user.click(filterButton);
    expect(screen.queryByText(/search filters/i)).not.toBeInTheDocument();
  });

  it('disables search button when input is empty', () => {
    render(<SearchForm />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toBeDisabled();
  });

  it('shows loading state correctly', () => {
    render(<SearchForm loading={true} />);
    
    const searchInput = screen.getByPlaceholderText(/search by hs code/i);
    const searchButton = screen.getByRole('button', { name: /searching/i });
    
    expect(searchInput).toBeDisabled();
    expect(searchButton).toBeDisabled();
    expect(searchButton).toHaveTextContent('Searching...');
  });

  it('handles filter changes correctly', async () => {
    const mockOnSearch = jest.fn();
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<SearchForm onSearch={mockOnSearch} />);
    
    // Open filters
    const filterButton = screen.getByRole('button', { name: '' });
    await user.click(filterButton);
    
    // Change search type
    const searchTypeSelect = screen.getByDisplayValue(/all fields/i);
    await user.selectOptions(searchTypeSelect, 'hs_code');
    
    // Submit search
    const searchInput = screen.getByPlaceholderText(/search by hs code/i);
    await user.type(searchInput, 'test');
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    await user.click(searchButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith('test', { searchType: 'hs_code' });
  });

  it('meets accessibility requirements', () => {
    const { container } = render(<SearchForm />);
    
    const audit = AccessibilityHelpers.auditAccessibility(container);
    expect(audit.passed).toBe(true);
  });
});