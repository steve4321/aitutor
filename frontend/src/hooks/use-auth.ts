'use client';

import { useAuthStore } from '@/stores/auth-store';
import { api } from '@/lib/api';
import { setToken, setRefreshToken, clearTokens } from '@/lib/auth';
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

  const signIn = async (credentials: LoginRequest) => {
    setLoading(true);
    try {
      const response = await api.post<LoginResponse>('/auth/login', credentials);
      setToken(response.access_token);
      setRefreshToken(response.refresh_token);

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
