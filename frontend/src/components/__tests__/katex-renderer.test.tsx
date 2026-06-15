import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KatexRenderer } from '../math/katex-renderer';

vi.mock('katex', () => ({
  default: {
    render: vi.fn((_latex: string, el: HTMLElement) => {
      el.textContent = _latex;
    }),
  },
}));

import katex from 'katex';

const mockedRender = vi.mocked(katex.render);

describe('KatexRenderer', () => {
  beforeEach(() => {
    mockedRender.mockClear();
  });

  it('calls katex.render with the provided latex string', () => {
    render(<KatexRenderer latex="x^2" />);
    expect(mockedRender).toHaveBeenCalledTimes(1);
    expect(mockedRender).toHaveBeenCalledWith(
      'x^2',
      expect.any(HTMLElement),
      expect.objectContaining({ displayMode: true, throwOnError: false, trust: true }),
    );
  });

  it('applies custom className to the container span', () => {
    const { container } = render(<KatexRenderer latex="x^2" className="my-math" />);
    const el = container.querySelector('.my-math');
    expect(el).toBeInTheDocument();
  });

  it('renders different latex strings on re-render', () => {
    const { rerender } = render(<KatexRenderer latex="a+b" />);
    expect(mockedRender).toHaveBeenLastCalledWith(
      'a+b',
      expect.any(HTMLElement),
      expect.any(Object),
    );

    rerender(<KatexRenderer latex="c^2" />);
    expect(mockedRender).toHaveBeenLastCalledWith(
      'c^2',
      expect.any(HTMLElement),
      expect.any(Object),
    );
  });

  it('uses default displayMode of true', () => {
    render(<KatexRenderer latex="y=mx+b" />);
    expect(mockedRender).toHaveBeenCalledWith(
      'y=mx+b',
      expect.any(HTMLElement),
      expect.objectContaining({ displayMode: true }),
    );
  });

  it('passes displayMode=false when specified', () => {
    render(<KatexRenderer latex="x^2" displayMode={false} />);
    expect(mockedRender).toHaveBeenCalledWith(
      'x^2',
      expect.any(HTMLElement),
      expect.objectContaining({ displayMode: false }),
    );
  });
});
