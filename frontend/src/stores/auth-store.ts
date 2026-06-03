'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, StudentProfile } from '@/types/user';

interface AuthState {
  user: User | null;
  profile: StudentProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  setUser: (user: User | null) => void;
  setProfile: (profile: StudentProfile | null) => void;
  setLoading: (loading: boolean) => void;
  login: (user: User, profile: StudentProfile | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      profile: null,
      isAuthenticated: false,
      isLoading: true,

      setUser: (user) =>
        set({ user, isAuthenticated: !!user }),

      setProfile: (profile) =>
        set({ profile }),

      setLoading: (isLoading) =>
        set({ isLoading }),

      login: (user, profile) =>
        set({
          user,
          profile,
          isAuthenticated: true,
          isLoading: false,
        }),

      logout: () =>
        set({
          user: null,
          profile: null,
          isAuthenticated: false,
          isLoading: false,
        }),
    }),
    {
      name: 'aitutor-auth',
      partialize: (state) => ({
        user: state.user,
        profile: state.profile,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
