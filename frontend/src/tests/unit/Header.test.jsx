import React from 'react';
import { render, screen } from '@testing-library/react';
import Header from '../../components/App/Header'; // Adjusted import path
import '@testing-library/jest-dom';

describe('Header Component', () => {
  test('renders the main heading "NoLyan"', () => {
    render(<Header />);
    // Use a flexible matcher, like a regex, to find the heading
    // This accounts for the emoji if it's part of the text node or a separate element.
    const headingElement = screen.getByRole('heading', { name: /NoLyan/i });
    expect(headingElement).toBeInTheDocument();
  });

  test('renders the subheading text', () => {
    render(<Header />);
    const subheadingElement = screen.getByText(/Advanced voice analysis with AI-powered deception detection/i);
    expect(subheadingElement).toBeInTheDocument();
  });

  test('applies correct CSS classes for styling', () => {
    const { container } = render(<Header />);
    // Check for a few key classes on the main div or h1
    expect(container.firstChild).toHaveClass('bg-black/20');
    expect(container.firstChild).toHaveClass('backdrop-blur-sm');

    const headingElement = screen.getByRole('heading', { name: /NoLyan/i });
    expect(headingElement).toHaveClass('bg-gradient-to-r');
    expect(headingElement).toHaveClass('text-transparent');
  });
});
