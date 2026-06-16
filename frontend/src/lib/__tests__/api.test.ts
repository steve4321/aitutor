import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, ApiError } from '../api';

describe('api client', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.stubGlobal('fetch', vi.fn());
  });

  describe('api.get', () => {
    it('calls fetch with correct URL, default headers, and credentials include', async () => {
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
          }),
          credentials: 'include',
        }),
      );
      expect(result).toEqual({ data: 'test' });
    });

    it('appends query params when provided', async () => {
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
    it('sends POST request with correct body and credentials', async () => {
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
          credentials: 'include',
        }),
      );
      expect(result).toEqual({ id: 1 });
    });
  });

  describe('error handling', () => {
    it('throws AuthError on 401 after refresh fails', async () => {
      // 1st fetch: original request returns 401
      // 2nd fetch: refresh attempt returns 401 (fails)
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          statusText: 'Unauthorized',
          json: () => Promise.resolve({ detail: 'Invalid token' }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          statusText: 'Unauthorized',
          json: () => Promise.resolve({}),
        });

      await expect(api.get('/protected')).rejects.toMatchObject({
        name: 'AuthError',
        status: 401,
      });
    });

    it('retries original request after successful token refresh', async () => {
      // 1st fetch: original request returns 401
      // 2nd fetch: refresh attempt returns 200 (success)
      // 3rd fetch: retried original request returns 200
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          statusText: 'Unauthorized',
          json: () => Promise.resolve({}),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve({}),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ data: 'retried' }),
        });

      const result = await api.get('/users/me');

      expect(result).toEqual({ data: 'retried' });
      expect(fetch).toHaveBeenCalledTimes(3);
    });

    it('throws ApiError on non-401 error', async () => {
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
