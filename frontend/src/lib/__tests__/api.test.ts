import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, ApiError, AuthError } from '../api';

// Mock the auth module
vi.mock('../auth', () => ({
  getToken: vi.fn(),
  clearTokens: vi.fn(),
  getRefreshToken: vi.fn(),
  setToken: vi.fn(),
  setRefreshToken: vi.fn(),
}));

describe('api client', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.stubGlobal('fetch', vi.fn());
  });

  describe('api.get', () => {
    it('calls fetch with correct URL and default headers', async () => {
      const { getToken } = await import('../auth');
      (getToken as ReturnType<typeof vi.fn>).mockReturnValue('test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: 'test' }),
      });

      const result = await api.get('/users');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/users',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          }),
        }),
      );
      expect(result).toEqual({ data: 'test' });
    });

    it('appends query params when provided', async () => {
      const { getToken } = await import('../auth');
      (getToken as ReturnType<typeof vi.fn>).mockReturnValue(null);

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });

      await api.get('/items', { page: '1', limit: '10' });

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/items?page=1&limit=10',
        expect.any(Object),
      );
    });
  });

  describe('api.post', () => {
    it('sends POST request with correct body', async () => {
      const { getToken } = await import('../auth');
      (getToken as ReturnType<typeof vi.fn>).mockReturnValue(null);

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ id: 1 }),
      });

      const body = { name: 'test', value: 42 };
      const result = await api.post('/items', body);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/items',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(body),
        }),
      );
      expect(result).toEqual({ id: 1 });
    });
  });

  describe('error handling', () => {
    it('throws AuthError on 401 response', async () => {
      const { getToken, clearTokens } = await import('../auth');
      (getToken as ReturnType<typeof vi.fn>).mockReturnValue('expired-token');
      (clearTokens as ReturnType<typeof vi.fn>).mockImplementation(() => {});

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: () => Promise.resolve({ detail: 'Invalid token' }),
      });

      await expect(api.get('/protected')).rejects.toThrow(AuthError);
      await expect(api.get('/protected')).rejects.toMatchObject({
        name: 'AuthError',
        status: 401,
      });
    });

    it('clears tokens on 401', async () => {
      const { getToken, clearTokens } = await import('../auth');
      (getToken as ReturnType<typeof vi.fn>).mockReturnValue('token');
      (clearTokens as ReturnType<typeof vi.fn>).mockImplementation(() => {});

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: () => Promise.resolve({}),
      });

      await expect(api.get('/me')).rejects.toThrow();
      expect(clearTokens).toHaveBeenCalled();
    });

    it('throws ApiError on non-401 error', async () => {
      const { getToken } = await import('../auth');
      (getToken as ReturnType<typeof vi.fn>).mockReturnValue(null);

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ detail: 'Not found' }),
      });

      try {
        await api.get('/missing');
        expect.unreachable('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(404);
        expect((error as ApiError).data).toEqual({ detail: 'Not found' });
      }
    });
  });
});
