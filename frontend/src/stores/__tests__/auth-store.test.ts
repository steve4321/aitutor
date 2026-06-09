import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from '../auth-store';
import type { User, StudentProfile } from '@/types/user';

vi.mock('zustand/middleware', async (importOriginal) => {
  const actual = await importOriginal<typeof import('zustand/middleware')>();
  return {
    ...actual,
    persist: (fn: unknown) => fn,
  };
});

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
  target_exam: 'AMC8',
  target_date: null,
  daily_goal_minutes: 30,
  timezone: 'Asia/Shanghai',
  preferred_lang: 'zh-CN',
  diagnostic_done: false,
  xp_total: 100,
  streak_days: 3,
  longest_streak: 7,
};

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      profile: null,
      isAuthenticated: false,
      isLoading: true,
    });
  });

  it('has correct initial state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.profile).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(true);
  });

  it('setUser sets user and isAuthenticated=true', () => {
    useAuthStore.getState().setUser(mockUser);
    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it('setUser(null) sets isAuthenticated=false', () => {
    useAuthStore.getState().setUser(mockUser);
    useAuthStore.getState().setUser(null);
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('setProfile sets profile', () => {
    useAuthStore.getState().setProfile(mockProfile);
    expect(useAuthStore.getState().profile).toEqual(mockProfile);
  });

  it('setLoading sets isLoading', () => {
    useAuthStore.getState().setLoading(false);
    expect(useAuthStore.getState().isLoading).toBe(false);
  });

  it('login sets all auth fields and isLoading=false', () => {
    useAuthStore.getState().login(mockUser, mockProfile);
    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.profile).toEqual(mockProfile);
    expect(state.isAuthenticated).toBe(true);
    expect(state.isLoading).toBe(false);
  });

  it('login with null profile sets profile to null', () => {
    useAuthStore.getState().login(mockUser, null);
    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.profile).toBeNull();
    expect(state.isAuthenticated).toBe(true);
  });

  it('logout resets everything to null/false', () => {
    useAuthStore.getState().login(mockUser, mockProfile);
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.profile).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });
});
