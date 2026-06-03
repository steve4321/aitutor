import { API_BASE_URL } from './constants';
import { getToken, getRefreshToken, setToken, setRefreshToken, clearTokens } from './auth';

class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

class AuthError extends ApiError {
  constructor(message: string, data?: unknown) {
    super(message, 401, data);
    this.name = 'AuthError';
  }
}

interface RequestOptions extends Omit<RequestInit, 'signal'> {
  signal?: AbortSignal;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getToken();
  const { signal, ...restOptions } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(restOptions.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...restOptions,
    headers,
    signal,
  });

  if (!response.ok) {
    if (response.status === 401) {
      const refreshToken = getRefreshToken();
      if (refreshToken && !endpoint.endsWith('/auth/refresh')) {
        try {
          const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });
          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            setToken(data.access_token);
            if (data.refresh_token) setRefreshToken(data.refresh_token);
            headers['Authorization'] = `Bearer ${data.access_token}`;
            const retryResponse = await fetch(url, { ...restOptions, headers, signal });
            if (!retryResponse.ok) {
              if (retryResponse.status === 401) {
                clearTokens();
              }
              let errorData: unknown;
              try {
                errorData = await retryResponse.json();
              } catch {
                errorData = await retryResponse.text();
              }
              throw new ApiError(`API Error: ${retryResponse.status}`, retryResponse.status, errorData);
            }
            if (retryResponse.status === 204) {
              return undefined as T;
            }
            return retryResponse.json();
          }
        } catch {
        }
      }
      clearTokens();
    }

    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }

    if (response.status === 401) {
      throw new AuthError(
        `Authentication required: ${response.statusText}`,
        errorData
      );
    }

    throw new ApiError(
      `API Error: ${response.status} ${response.statusText}`,
      response.status,
      errorData
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const api = {
  get<T>(endpoint: string, params?: Record<string, string>, options?: RequestOptions): Promise<T> {
    const searchParams = params
      ? `?${new URLSearchParams(params).toString()}`
      : '';
    return request<T>(`${endpoint}${searchParams}`, options);
  },

  post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  patch<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  },
};

export { ApiError, AuthError };
export default api;
