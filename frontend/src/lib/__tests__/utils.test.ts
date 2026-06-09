import { describe, it, expect } from 'vitest';
import { cn, formatNumber, formatDate, sleep } from '../utils';

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', 'active')).toBe('base active');
  });

  it('deduplicates tailwind classes', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4');
  });

  it('handles undefined and null inputs', () => {
    expect(cn('base', undefined, null, 'end')).toBe('base end');
  });

  it('returns empty string for no inputs', () => {
    expect(cn()).toBe('');
  });
});

describe('formatNumber', () => {
  it('formats numbers >= 1000 with k suffix', () => {
    expect(formatNumber(1500)).toBe('1.5k');
  });

  it('formats exactly 1000', () => {
    expect(formatNumber(1000)).toBe('1.0k');
  });

  it('formats large numbers', () => {
    expect(formatNumber(10500)).toBe('10.5k');
  });

  it('returns string for numbers < 1000', () => {
    expect(formatNumber(999)).toBe('999');
  });

  it('returns string for 0', () => {
    expect(formatNumber(0)).toBe('0');
  });

  it('returns string for negative numbers', () => {
    expect(formatNumber(-5)).toBe('-5');
  });
});

describe('formatDate', () => {
  it('formats a Date object', () => {
    const result = formatDate(new Date('2024-03-15'));
    expect(result).toContain('2024');
    expect(result).toContain('3');
    expect(result).toContain('15');
  });

  it('formats a date string', () => {
    const result = formatDate('2024-06-20');
    expect(result).toContain('2024');
    expect(result).toContain('6');
    expect(result).toContain('20');
  });
});

describe('sleep', () => {
  it('resolves after the given time', async () => {
    vi.useFakeTimers();
    const promise = sleep(1000);
    vi.advanceTimersByTime(1000);
    await expect(promise).resolves.toBeUndefined();
    vi.useRealTimers();
  });
});
