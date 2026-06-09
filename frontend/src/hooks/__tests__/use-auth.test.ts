import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useAuth } from '../use-auth';
import { api } from '@/lib/api';
import type { User, StudentProfile } from '@/types/user';

const mockUser: User = {
  id: 'user-1',
  email: 'test@example.com',
  phone: null,
  name: 'Test User',
  role: 'student',
  avatar_url: null,
  created_at: '2024-01-01T00:00:00Z',
};

const mockProfile: StudentProfile = {
  id: 'profile-1',
  user_id: 'user-1',
  grade_level: 5,
  target_exam: null,
  target_date: null,
  daily_goal_minutes: 30,
  timezone: 'Asia/Shanghai',
  preferred_lang: 'zh-CN',
  diagnostic_done: false,
  xp_total: 0,
  streak_days: 0,
  longest_streak: 0,
  minutes_today: 0,
};

const { mockStore, useAuthStoreFn } = vi.hoisted(() => {
  const store: Record<string, unknown> = {
    user: null,
    profile: null,
    isAuthenticated: false,
    isLoading: true,
    setUser: (user: unknown) => {
      store.user = user;
      store.isAuthenticated = !!user;
    },
    setProfile: (profile: unknown) => {
      store.profile = profile;
    },
    setLoading: (loading: boolean) => {
      store.isLoading = loading;
    },
    login: (user: unknown, profile: unknown) => {
      store.user = user;
      store.profile = profile;
      store.isAuthenticated = true;
      store.isLoading = false;
    },
    logout: () => {
      store.user = null;
      store.profile = null;
      store.isAuthenticated = false;
      store.isLoading = false;
    },
  };
  const fn = Object.assign(() => store, { getState: () => store });
  return { mockStore: store, useAuthStoreFn: fn };
});

vi.mock('@/stores/auth-store', () => ({
  useAuthStore: useAuthStoreFn,
}));

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock('@/lib/auth', () => ({
  getToken: vi.fn(),
  setToken: vi.fn(),
  setRefreshToken: vi.fn(),
  clearTokens: vi.fn(),
}));

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.user = null;
    mockStore.profile = null;
    mockStore.isAuthenticated = false;
    mockStore.isLoading = true;
  });

  it('sets loading to false when no token exists', async () => {
    const { getToken } = await import('@/lib/auth');
    (getToken as ReturnType<typeof vi.fn>).mockReturnValue(null);

    renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.isLoading).toBe(false);
    });
  });

  it('fetches user and profile when token exists', async () => {
    const { getToken } = await import('@/lib/auth');
    (getToken as ReturnType<typeof vi.fn>).mockReturnValue('valid-token');
    (api.get as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(mockUser)
      .mockResolvedValueOnce(mockProfile);

    renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.user).toEqual(mockUser);
      expect(mockStore.profile).toEqual(mockProfile);
      expect(mockStore.isAuthenticated).toBe(true);
    });
  });

  it('logs in with null profile when profile fetch fails', async () => {
    const { getToken } = await import('@/lib/auth');
    (getToken as ReturnType<typeof vi.fn>).mockReturnValue('valid-token');
    (api.get as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(mockUser)
      .mockRejectedValueOnce(new Error('Profile not found'));

    renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.user).toEqual(mockUser);
      expect(mockStore.profile).toBeNull();
      expect(mockStore.isAuthenticated).toBe(true);
    });
  });

  it('clears tokens and logs out on /users/me failure', async () => {
    const { getToken, clearTokens } = await import('@/lib/auth');
    (getToken as ReturnType<typeof vi.fn>).mockReturnValue('bad-token');
    (api.get as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Unauthorized'));

    renderHook(() => useAuth());

    await waitFor(() => {
      expect(clearTokens).toHaveBeenCalled();
    });

    expect(mockStore.user).toBeNull();
    expect(mockStore.isAuthenticated).toBe(false);
  });

  it('signIn calls API and logs in user', async () => {
    const { getToken, setToken } = await import('@/lib/auth');
    (getToken as ReturnType<typeof vi.fn>).mockReturnValue(null);

    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ access_token: 'new-token', refresh_token: null, token_type: 'bearer' });
    (api.get as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(mockUser)
      .mockResolvedValueOnce(mockProfile);

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.signIn({ username: 'test', password: 'pass' });
    });

    expect(api.post).toHaveBeenCalledWith('/auth/login', { username: 'test', password: 'pass' });
    expect(setToken).toHaveBeenCalledWith('new-token');

    expect(mockStore.user).toEqual(mockUser);
    expect(mockStore.profile).toEqual(mockProfile);
    expect(mockStore.isAuthenticated).toBe(true);
  });

  it('signOut clears tokens and resets state', async () => {
    const { clearTokens } = await import('@/lib/auth');

    const { result } = renderHook(() => useAuth());

    act(() => {
      result.current.signOut();
    });

    expect(clearTokens).toHaveBeenCalled();

    expect(mockStore.user).toBeNull();
    expect(mockStore.isAuthenticated).toBe(false);
  });

  it('refreshProfile fetches and sets profile', async () => {
    const { getToken } = await import('@/lib/auth');
    (getToken as ReturnType<typeof vi.fn>).mockReturnValue(null);
    mockStore.user = mockUser;
    (api.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockProfile);

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.refreshProfile();
    });

    expect(api.get).toHaveBeenCalledWith('/users/me/profile');
    expect(mockStore.profile).toEqual(mockProfile);
  });

  it('refreshProfile does nothing when user is null', async () => {
    mockStore.user = null;

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.refreshProfile();
    });

    expect(api.get).not.toHaveBeenCalledWith(expect.stringContaining('/students/'));
  });
});
