import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useXP } from '../useXP';
import type { StudentProfile } from '@/types/user';

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
  xp_total: 3500,
  streak_days: 7,
  longest_streak: 14,
  minutes_today: 15,
};

const mockAuthStore = {
  isAuthenticated: false,
  user: null,
  profile: null as StudentProfile | null,
  isLoading: false,
  setUser: vi.fn(),
  setProfile: vi.fn(),
  setLoading: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
};

vi.mock('@/stores/auth-store', () => ({
  useAuthStore: Object.assign(
    vi.fn(() => mockAuthStore),
    { getState: () => mockAuthStore },
  ),
}));

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

describe('useXP hook', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mockAuthStore.isAuthenticated = false;
    mockAuthStore.profile = null;
  });

  it('returns initial state when not authenticated', () => {
    mockAuthStore.isAuthenticated = false;

    const { result } = renderHook(() => useXP());

    expect(result.current.xp).toBe(0);
    expect(result.current.level).toBe(1);
    expect(result.current.streak).toBe(0);
    expect(result.current.loading).toBe(false);
  });

  it('derives XP data from auth store profile without extra fetch', () => {
    mockAuthStore.isAuthenticated = true;
    mockAuthStore.profile = mockProfile;

    const { result } = renderHook(() => useXP());

    expect(result.current.xp).toBe(3500);
    expect(result.current.level).toBe(4);
    expect(result.current.streak).toBe(7);
    expect(result.current.dailyGoalMinutes).toBe(30);
    expect(result.current.loading).toBe(false);
  });

  it('refetch fetches fresh profile and updates store', async () => {
    mockAuthStore.isAuthenticated = true;
    mockAuthStore.profile = null;

    const { api } = await import('@/lib/api');
    (api.get as ReturnType<typeof vi.fn>).mockResolvedValue(mockProfile);

    const { result } = renderHook(() => useXP());

    await result.current.refetch();

    await waitFor(() => {
      expect(mockAuthStore.setProfile).toHaveBeenCalledWith(mockProfile);
    });

    expect(api.get).toHaveBeenCalledWith('/users/me/profile');
  });

  it('refetch does nothing when not authenticated', async () => {
    mockAuthStore.isAuthenticated = false;

    const { api } = await import('@/lib/api');

    const { result } = renderHook(() => useXP());

    await result.current.refetch();

    expect(api.get).not.toHaveBeenCalled();
  });
});
