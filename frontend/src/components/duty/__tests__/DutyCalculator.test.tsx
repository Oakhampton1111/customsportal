import React from 'react';
import { render, screen } from '../../../__tests__/utils/test-utils';
import { AccessibilityHelpers } from '../../../__tests__/utils/accessibility-helpers';
import { DutyCalculator } from '../DutyCalculator';

describe('DutyCalculator Component', () => {
  it('renders duty calculator with title', () => {
    render(<DutyCalculator />);
    
    const title = screen.getByRole('heading', { name: /duty calculator/i });
    expect(title).toBeInTheDocument();
    expect(title).toHaveClass('text-2xl');
    expect(title).toHaveClass('font-bold');
  });

  it('renders all required input fields', () => {
    render(<DutyCalculator />);
    
    expect(screen.getByLabelText(/hs code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/country of origin/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customs value/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/quantity/i)).toBeInTheDocument();
  });

  it('has correct input field types and placeholders', () => {
    render(<DutyCalculator />);
    
    const hsCodeInput = screen.getByLabelText(/hs code/i);
    const countryInput = screen.getByLabelText(/country of origin/i);
    const valueInput = screen.getByLabelText(/customs value/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    
    expect(hsCodeInput).toHaveAttribute('placeholder', 'e.g., 8471.30.00');
    expect(countryInput).toHaveAttribute('placeholder', 'e.g., China');
    expect(valueInput).toHaveAttribute('type', 'number');
    expect(valueInput).toHaveAttribute('placeholder', '0.00');
    expect(quantityInput).toHaveAttribute('type', 'number');
    expect(quantityInput).toHaveAttribute('placeholder', '1');
  });

  it('marks all input fields as required', () => {
    render(<DutyCalculator />);
    
    expect(screen.getByLabelText(/hs code/i)).toBeRequired();
    expect(screen.getByLabelText(/country of origin/i)).toBeRequired();
    expect(screen.getByLabelText(/customs value/i)).toBeRequired();
    expect(screen.getByLabelText(/quantity/i)).toBeRequired();
  });

  it('renders calculate button', () => {
    render(<DutyCalculator />);
    
    const calculateButton = screen.getByRole('button', { name: /calculate duty/i });
    expect(calculateButton).toBeInTheDocument();
    expect(calculateButton).toHaveClass('variant-primary');
  });

  it('renders results section with placeholder text', () => {
    render(<DutyCalculator />);
    
    const resultsTitle = screen.getByRole('heading', { name: /calculation results/i });
    const placeholderText = screen.getByText(/enter values above to calculate duties and taxes/i);
    
    expect(resultsTitle).toBeInTheDocument();
    expect(placeholderText).toBeInTheDocument();
  });

  it('handles user input in form fields', async () => {
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<DutyCalculator />);
    
    const hsCodeInput = screen.getByLabelText(/hs code/i);
    const countryInput = screen.getByLabelText(/country of origin/i);
    const valueInput = screen.getByLabelText(/customs value/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    
    await user.type(hsCodeInput, '8471.30.00');
    await user.type(countryInput, 'China');
    await user.type(valueInput, '1000');
    await user.type(quantityInput, '2');
    
    expect(hsCodeInput).toHaveValue('8471.30.00');
    expect(countryInput).toHaveValue('China');
    expect(valueInput).toHaveValue(1000);
    expect(quantityInput).toHaveValue(2);
  });

  it('handles button click events', async () => {
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<DutyCalculator />);
    
    const calculateButton = screen.getByRole('button', { name: /calculate duty/i });
    
    // Button should be clickable
    await user.click(calculateButton);
    expect(calculateButton).toBeInTheDocument();
  });

  it('applies custom className when provided', () => {
    const { container } = render(<DutyCalculator className="custom-class" />);
    
    const dutyCalculator = container.firstChild as HTMLElement;
    expect(dutyCalculator).toHaveClass('custom-class');
  });

  it('has proper responsive grid layout', () => {
    const { container } = render(<DutyCalculator />);
    
    const gridContainer = container.querySelector('.grid');
    expect(gridContainer).toHaveClass('grid-cols-1');
    expect(gridContainer).toHaveClass('md:grid-cols-2');
  });

  it('has proper styling and layout classes', () => {
    const { container } = render(<DutyCalculator />);
    
    const mainContainer = container.firstChild as HTMLElement;
    expect(mainContainer).toHaveClass('bg-white');
    expect(mainContainer).toHaveClass('rounded-lg');
    expect(mainContainer).toHaveClass('shadow-md');
    expect(mainContainer).toHaveClass('p-6');
    
    const resultsSection = container.querySelector('.bg-gray-50');
    expect(resultsSection).toHaveClass('mt-6');
    expect(resultsSection).toHaveClass('p-4');
    expect(resultsSection).toHaveClass('rounded-lg');
  });

  it('meets accessibility requirements', () => {
    const { container } = render(<DutyCalculator />);
    
    const audit = AccessibilityHelpers.auditAccessibility(container);
    expect(audit.passed).toBe(true);
    
    // Check that all form controls have proper labels
    const formIssues = AccessibilityHelpers.checkFormLabels(container);
    expect(formIssues).toHaveLength(0);
    
    // Check button accessibility
    const buttonIssues = AccessibilityHelpers.checkButtonAccessibility(container);
    expect(buttonIssues).toHaveLength(0);
  });

  it('has proper heading hierarchy', () => {
    const { container } = render(<DutyCalculator />);
    
    const headingIssues = AccessibilityHelpers.checkHeadingHierarchy(container);
    expect(headingIssues).toHaveLength(0);
    
    const mainHeading = screen.getByRole('heading', { level: 2 });
    const resultsHeading = screen.getByRole('heading', { level: 3 });
    
    expect(mainHeading).toBeInTheDocument();
    expect(resultsHeading).toBeInTheDocument();
  });

  it('supports keyboard navigation', async () => {
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<DutyCalculator />);
    
    const hsCodeInput = screen.getByLabelText(/hs code/i);
    const countryInput = screen.getByLabelText(/country of origin/i);
    const valueInput = screen.getByLabelText(/customs value/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    const calculateButton = screen.getByRole('button', { name: /calculate duty/i });
    
    // Test tab navigation
    await user.tab();
    expect(hsCodeInput).toHaveFocus();
    
    await user.tab();
    expect(countryInput).toHaveFocus();
    
    await user.tab();
    expect(valueInput).toHaveFocus();
    
    await user.tab();
    expect(quantityInput).toHaveFocus();
    
    await user.tab();
    expect(calculateButton).toHaveFocus();
  });

  it('handles form validation states', () => {
    render(<DutyCalculator />);
    
    // All required fields should have required attribute
    const allTextboxes = screen.getAllByRole('textbox');
    const allSpinbuttons = screen.getAllByRole('spinbutton');
    const allInputs = [...allTextboxes, ...allSpinbuttons];
    
    allInputs.forEach(input => {
      expect(input).toBeRequired();
    });
    
    // Number inputs should have proper type
    const numberInputs = screen.getAllByRole('spinbutton');
    expect(numberInputs).toHaveLength(2);
  });

  it('renders with proper semantic structure', () => {
    render(<DutyCalculator />);
    
    // Should have proper headings
    expect(screen.getByRole('heading', { level: 2, name: /duty calculator/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 3, name: /calculation results/i })).toBeInTheDocument();
    
    // Should have form elements
    expect(screen.getAllByRole('textbox')).toHaveLength(4);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});