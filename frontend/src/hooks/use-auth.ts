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
    let isMounted = true;
    const controller = new AbortController();

    const fetchUser = async () => {
      const token = getToken();
      if (!token) {
        useAuthStore.getState().setLoading(false);
        return;
      }
      try {
        const userData = await api.get<User>('/auth/me', undefined, { signal: controller.signal });
        if (isMounted) {
          try {
            const profileData = await api.get<StudentProfile>(`/students/${userData.id}/profile`, undefined, { signal: controller.signal });
            if (isMounted) useAuthStore.getState().login(userData, profileData);
          } catch {
            if (isMounted) useAuthStore.getState().login(userData, null);
          }
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

      const userData = await api.get<User>('/auth/me');
      const profileData = await api.get<StudentProfile>(`/students/${userData.id}/profile`);
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
    const profileData = await api.get<StudentProfile>(`/students/${user.id}/profile`);
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
