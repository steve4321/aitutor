'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/stores/auth-store';
import { api } from '@/lib/api';
import type { User, StudentProfile } from '@/types/user';
import type { LoginRequest, LoginResponse, RegisterRequest } from '@/types/api';

export function useAuth() {
  const {
    user,
    profile,
    isAuthenticated,
    isLoading,
    login,
    logout,
    setLoading,
  } = useAuthStore();

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const fetchUser = async () => {
      try {
        const [userData, profileData] = await Promise.all([
          api.get<User>('/users/me', undefined, { signal: controller.signal }),
          api.get<StudentProfile>('/users/me/profile', undefined, { signal: controller.signal }).catch((err) => {
            console.warn('[useAuth] Failed to fetch profile during init:', err);
            return null;
          }),
        ]);
        if (isMounted) {
          useAuthStore.getState().login(userData, profileData);
        }
      } catch {
        if (isMounted) {
          useAuthStore.getState().logout();
        }
      } finally {
        if (isMounted) useAuthStore.getState().setLoading(false);
      }
    };

    fetchUser();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  const signIn = async (credentials: LoginRequest) => {
    setLoading(true);
    try {
      await api.post<LoginResponse>('/auth/login', credentials);

      const [userData, profileData] = await Promise.all([
        api.get<User>('/users/me'),
        api.get<StudentProfile>('/users/me/profile').catch((err) => {
          console.warn('[useAuth] Failed to fetch profile during signIn:', err);
          return null;
        }),
      ]);
      login(userData, profileData);
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (data: RegisterRequest) => {
    setLoading(true);
    try {
      await api.post('/auth/register', data);
      await signIn({ username: data.username, password: data.password });
    } catch (error) {
      logout();
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      await api.post('/auth/logout');
    } catch {
    }
    logout();
  };

  const refreshProfile = async () => {
    if (!user) return;
    const profileData = await api.get<StudentProfile>('/users/me/profile');
    useAuthStore.getState().setProfile(profileData);
  };

  return {
    user,
    profile,
    isAuthenticated,
    isLoading,
    signIn,
    signUp,
    signOut,
    refreshProfile,
  };
}
