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

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.user = null;
    mockStore.profile = null;
    mockStore.isAuthenticated = false;
    mockStore.isLoading = true;
    (api.get as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Unauthorized'));
    (api.post as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Not found'));
  });

  it('sets loading to false and logs out when user fetch fails', async () => {
    renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.isLoading).toBe(false);
    });

    expect(mockStore.user).toBeNull();
    expect(mockStore.isAuthenticated).toBe(false);
  });

  it('fetches user and profile on mount', async () => {
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
    (api.get as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(mockUser);

    renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.user).toEqual(mockUser);
      expect(mockStore.profile).toBeNull();
      expect(mockStore.isAuthenticated).toBe(true);
    });
  });

  it('logs out when user fetch fails on mount', async () => {
    renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.user).toBeNull();
      expect(mockStore.isAuthenticated).toBe(false);
    });
  });

  it('signIn calls API and logs in user', async () => {
    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.isLoading).toBe(false);
    });

    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      access_token: 'cookie-set',
      refresh_token: null,
      token_type: 'bearer',
    });
    (api.get as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(mockUser)
      .mockResolvedValueOnce(mockProfile);

    await act(async () => {
      await result.current.signIn({ username: 'test', password: 'pass' });
    });

    expect(api.post).toHaveBeenCalledWith('/auth/login', { username: 'test', password: 'pass' });
    expect(mockStore.user).toEqual(mockUser);
    expect(mockStore.profile).toEqual(mockProfile);
    expect(mockStore.isAuthenticated).toBe(true);
  });

  it('signOut calls logout endpoint and resets state', async () => {
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.isLoading).toBe(false);
    });

    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce(undefined);

    await act(async () => {
      await result.current.signOut();
    });

    expect(api.post).toHaveBeenCalledWith('/auth/logout');
    expect(mockStore.user).toBeNull();
    expect(mockStore.isAuthenticated).toBe(false);
  });

  it('refreshProfile fetches and sets profile', async () => {
    mockStore.user = mockUser;

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.isLoading).toBe(false);
    });

    (api.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockProfile);

    await act(async () => {
      await result.current.refreshProfile();
    });

    expect(mockStore.profile).toEqual(mockProfile);
  });

  it('refreshProfile does nothing when user is null', async () => {
    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(mockStore.isLoading).toBe(false);
    });

    const callCount = (api.get as ReturnType<typeof vi.fn>).mock.calls.length;

    await act(async () => {
      await result.current.refreshProfile();
    });

    expect((api.get as ReturnType<typeof vi.fn>).mock.calls.length).toBe(callCount);
  });
});
