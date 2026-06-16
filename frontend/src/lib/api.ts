import { API_BASE_URL } from './constants';
import { getToken, getRefreshToken, setToken, setRefreshToken, clearTokens } from './auth';

// Refresh mutex - prevents concurrent 401s from triggering multiple refresh attempts
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!response.ok) return null;
      const data = await response.json();
      setToken(data.access_token);
      if (data.refresh_token) setRefreshToken(data.refresh_token);
      return data.access_token;
    } catch {
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

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

function buildAuthHeaders(custom?: HeadersInit): Record<string, string> {
  const headers: Record<string, string> = { ...(custom as Record<string, string>) };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function fetchWithAuthRetry(
  url: string,
  options: RequestOptions,
  headers: Record<string, string>,
): Promise<Response> {
  const { signal, ...restOptions } = options;
  let response = await fetch(url, { ...restOptions, headers, signal });

  if (response.status === 401 && !url.includes('/auth/refresh')) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      response = await fetch(url, { ...restOptions, headers, signal });
    } else {
      clearTokens();
    }
  }

  return response;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (getToken()) {
    headers['Authorization'] = `Bearer ${getToken()}`;
  }

  const response = await fetchWithAuthRetry(url, options, headers);

  if (!response.ok) {
    if (response.status === 401) {
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

export async function fetchBinary(endpoint: string, options: RequestOptions = {}): Promise<Blob> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = buildAuthHeaders(options.headers as HeadersInit);

  const response = await fetchWithAuthRetry(url, options, headers);

  if (!response.ok) {
    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }

    if (response.status === 401) {
      throw new AuthError('Authentication required', errorData);
    }

    throw new ApiError(`API Error: ${response.status}`, response.status, errorData);
  }

  return response.blob();
}

export { ApiError, AuthError };
export default api;
