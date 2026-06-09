import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { KatexRenderer } from '../math/katex-renderer';

describe('KatexRenderer', () => {
  it('shows loading state with latex text as content', () => {
    renderWithProviders(<KatexRenderer latex="x^2" />);
    expect(screen.getByText('x^2')).toBeInTheDocument();
  });

  it('applies animate-pulse class in loading state', () => {
    const { container } = renderWithProviders(<KatexRenderer latex="x^2" />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('renders different latex strings', () => {
    const { rerender } = renderWithProviders(<KatexRenderer latex="a+b" />);
    expect(screen.getByText('a+b')).toBeInTheDocument();

    rerender(<KatexRenderer latex="c^2" />);
    expect(screen.getByText('c^2')).toBeInTheDocument();
  });

  it('applies custom className in loading state', () => {
    const { container } = renderWithProviders(
      <KatexRenderer latex="x^2" className="my-math" />,
    );
    const el = container.querySelector('.my-math');
    expect(el).toBeInTheDocument();
    expect(el).toHaveTextContent('x^2');
  });

  it('uses default displayMode of true', () => {
    const { container } = renderWithProviders(<KatexRenderer latex="y=mx+b" />);
    expect(container.querySelector('.animate-pulse')).toHaveTextContent('y=mx+b');
  });
});
