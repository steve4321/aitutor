import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  getToken,
  setToken,
  getRefreshToken,
  setRefreshToken,
  clearTokens,
  isAuthenticated,
} from '../auth';

class LocalStorageMock {
  private store = new Map<string, string>();
  getItem(key: string) { return this.store.get(key) ?? null; }
  setItem(key: string, value: string) { this.store.set(key, value); }
  removeItem(key: string) { this.store.delete(key); }
  clear() { this.store.clear(); }
  get length() { return this.store.size; }
  key(_index: number): string | null { return null; }
}

describe('auth utilities', () => {
  beforeEach(() => {
    vi.stubGlobal('localStorage', new LocalStorageMock());
  });

  describe('setToken / getToken', () => {
    it('stores and retrieves a token', () => {
      setToken('my-access-token');
      expect(getToken()).toBe('my-access-token');
    });

    it('returns null when no token is set', () => {
      expect(getToken()).toBeNull();
    });
  });

  describe('setRefreshToken / getRefreshToken', () => {
    it('stores and retrieves a refresh token', () => {
      setRefreshToken('my-refresh-token');
      expect(getRefreshToken()).toBe('my-refresh-token');
    });

    it('returns null when no refresh token is set', () => {
      expect(getRefreshToken()).toBeNull();
    });
  });

  describe('clearTokens', () => {
    it('removes both tokens from localStorage', () => {
      setToken('access');
      setRefreshToken('refresh');
      clearTokens();
      expect(getToken()).toBeNull();
      expect(getRefreshToken()).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('returns true when a token is set', () => {
      setToken('valid-token');
      expect(isAuthenticated()).toBe(true);
    });

    it('returns false when no token is set', () => {
      expect(isAuthenticated()).toBe(false);
    });
  });
});
