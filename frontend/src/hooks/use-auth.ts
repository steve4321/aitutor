'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/stores/auth-store';
import { api } from '@/lib/api';
import { setToken, setRefreshToken, clearTokens, getToken } from '@/lib/auth';
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
    setUser,
  } = useAuthStore();

  useEffect(() => {
    // Already have user data from persisted store — skip refetch
    if (useAuthStore.getState().user) {
      useAuthStore.getState().setLoading(false);
      return;
    }

    let isMounted = true;
    const controller = new AbortController();

    const fetchUser = async () => {
      const token = getToken();
      if (!token) {
        useAuthStore.getState().setLoading(false);
        return;
      }
      try {
        // Parallel requests instead of sequential waterfall
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
          clearTokens();
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
      const response = await api.post<LoginResponse>('/auth/login', credentials);
      setToken(response.access_token);
      if (response.refresh_token) {
        setRefreshToken(response.refresh_token);
      }

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
      // If register succeeded but signIn failed, user is registered but not logged in
      // Clear any partial state and re-throw so the UI can show the error
      clearTokens();
      logout();
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    clearTokens();
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
