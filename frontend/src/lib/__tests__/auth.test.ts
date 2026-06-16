import { describe, it, expect } from 'vitest';
import { clearTokens } from '../auth';

describe('auth utilities', () => {
  describe('clearTokens', () => {
    it('does not throw (cookie-based auth no-op)', () => {
      expect(() => clearTokens()).not.toThrow();
    });
  });
});
