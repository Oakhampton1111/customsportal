import React from 'react';
import { render, screen } from '../../../__tests__/utils/test-utils';
import { AccessibilityHelpers } from '../../../__tests__/utils/accessibility-helpers';
import { Input } from '../Input';

describe('Input Component', () => {
  it('renders input with label', () => {
    render(<Input label="Test Label" />);
    
    const input = screen.getByLabelText(/test label/i);
    const label = screen.getByText(/test label/i);
    
    expect(input).toBeInTheDocument();
    expect(label).toBeInTheDocument();
    expect(label).toHaveAttribute('for', input.id);
  });

  it('renders input without label', () => {
    render(<Input placeholder="Enter text" />);
    
    const input = screen.getByPlaceholderText(/enter text/i);
    expect(input).toBeInTheDocument();
    expect(screen.queryByText(/test label/i)).not.toBeInTheDocument();
  });

  it('displays error message when error prop is provided', () => {
    render(<Input label="Test Input" error="This field is required" />);
    
    const input = screen.getByLabelText(/test input/i);
    const errorMessage = screen.getByText(/this field is required/i);
    
    expect(input).toBeInTheDocument();
    expect(errorMessage).toBeInTheDocument();
    expect(input).toHaveClass('border-red-500');
  });

  it('displays helper text when provided and no error', () => {
    render(<Input label="Test Input" helperText="Enter your information here" />);
    
    const helperText = screen.getByText(/enter your information here/i);
    expect(helperText).toBeInTheDocument();
    expect(helperText).toHaveClass('text-gray-500');
  });

  it('hides helper text when error is present', () => {
    render(
      <Input 
        label="Test Input" 
        helperText="Helper text" 
        error="Error message" 
      />
    );
    
    expect(screen.getByText(/error message/i)).toBeInTheDocument();
    expect(screen.queryByText(/helper text/i)).not.toBeInTheDocument();
  });

  it('applies different variants correctly', () => {
    const { rerender } = render(<Input variant="default" />);
    let input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-gray-300');

    rerender(<Input variant="filled" />);
    input = screen.getByRole('textbox');
    expect(input).toHaveClass('bg-gray-50');

    rerender(<Input variant="outlined" />);
    input = screen.getByRole('textbox');
    expect(input).toHaveClass('border-2');
  });

  it('applies different sizes correctly', () => {
    const { rerender } = render(<Input size="sm" />);
    let input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-3');
    expect(input).toHaveClass('py-1.5');
    expect(input).toHaveClass('text-sm');

    rerender(<Input size="md" />);
    input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-3');
    expect(input).toHaveClass('py-2');
    expect(input).toHaveClass('text-base');

    rerender(<Input size="lg" />);
    input = screen.getByRole('textbox');
    expect(input).toHaveClass('px-4');
    expect(input).toHaveClass('py-3');
    expect(input).toHaveClass('text-lg');
  });

  it('handles user input correctly', async () => {
    const handleChange = jest.fn();
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<Input label="Test Input" onChange={handleChange} />);
    
    const input = screen.getByLabelText(/test input/i);
    await user.type(input, 'Hello World');
    
    expect(input).toHaveValue('Hello World');
    expect(handleChange).toHaveBeenCalled();
  });

  it('can be disabled', () => {
    render(<Input label="Disabled Input" disabled />);
    
    const input = screen.getByLabelText(/disabled input/i);
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:opacity-50');
    expect(input).toHaveClass('disabled:cursor-not-allowed');
  });

  it('applies custom className', () => {
    render(<Input className="custom-class" />);
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('custom-class');
  });

  it('generates unique IDs when not provided', () => {
    render(
      <div>
        <Input label="Input 1" />
        <Input label="Input 2" />
      </div>
    );
    
    const input1 = screen.getByLabelText(/input 1/i);
    const input2 = screen.getByLabelText(/input 2/i);
    
    expect(input1.id).toBeTruthy();
    expect(input2.id).toBeTruthy();
    expect(input1.id).not.toBe(input2.id);
  });

  it('uses provided ID when given', () => {
    render(<Input id="custom-id" label="Custom ID Input" />);
    
    const input = screen.getByLabelText(/custom id input/i);
    expect(input).toHaveAttribute('id', 'custom-id');
  });

  it('supports all standard input attributes', () => {
    render(
      <Input 
        type="email"
        placeholder="Enter email"
        required
        maxLength={50}
        data-testid="email-input"
      />
    );
    
    const input = screen.getByTestId('email-input');
    expect(input).toHaveAttribute('type', 'email');
    expect(input).toHaveAttribute('placeholder', 'Enter email');
    expect(input).toHaveAttribute('required');
    expect(input).toHaveAttribute('maxLength', '50');
  });

  it('maintains focus styles correctly', async () => {
    const userEvent = (await import('@testing-library/user-event')).default;
    const user = userEvent.setup();
    
    render(<Input label="Focus Test" />);
    
    const input = screen.getByLabelText(/focus test/i);
    await user.click(input);
    
    expect(input).toHaveFocus();
    expect(input).toHaveClass('focus:ring-2');
    expect(input).toHaveClass('focus:ring-offset-2');
  });

  it('meets accessibility requirements', async () => {
    const { container } = render(
      <Input
        label="Accessible Input"
        error="Error message"
        helperText="Helper text"
      />
    );
    
    const audit = AccessibilityHelpers.auditAccessibility(container);
    expect(audit.passed).toBe(true);
    
    const input = screen.getByLabelText(/accessible input/i);
    const label = screen.getByText(/accessible input/i);
    
    expect(label).toHaveAttribute('for', input.id);
    expect(input).toHaveAccessibleName();
  });

  it('handles error state accessibility', () => {
    render(<Input label="Error Input" error="This field has an error" />);
    
    const input = screen.getByLabelText(/error input/i);
    const errorMessage = screen.getByText(/this field has an error/i);
    
    expect(input).toBeInTheDocument();
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveClass('text-red-600');
  });
});