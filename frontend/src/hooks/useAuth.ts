"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { User } from "@/types/user";
import { LoginRequest, LoginResponse, RegisterRequest } from "@/types/api";
import { useAuthStore } from "@/stores/authStore";

export function useAuth() {
  const router = useRouter();
  const { token, user, isAuthenticated, setToken, setUser, clearAuth } =
    useAuthStore();

  useEffect(() => {
    if (!token && isAuthenticated) {
      clearAuth();
    }
  }, [token, clearAuth]);

  const login = useCallback(
    async (credentials: LoginRequest): Promise<{ success: boolean; error?: string }> => {
      try {
        const response = await api.post<LoginResponse>("/auth/login", credentials);
        setToken(response.access_token);
        const userResponse = await api.get<User>("/auth/me");
        setUser(userResponse);
        router.push("/home");
        return { success: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Login failed";
        return { success: false, error: message };
      }
    },
    [router, setToken, setUser]
  );

  const register = useCallback(
    async (data: RegisterRequest): Promise<{ success: boolean; error?: string }> => {
      try {
        await api.post("/auth/register", data);
        return { success: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Registration failed";
        return { success: false, error: message };
      }
    },
    []
  );

  const logout = useCallback(() => {
    clearAuth();
    router.push("/login");
  }, [clearAuth, router]);

  const fetchUser = useCallback(async () => {
    if (!token) return;
    try {
      const userData = await api.get<User>("/auth/me");
      setUser(userData);
    } catch {
      clearAuth();
    }
  }, [token, setUser, clearAuth]);

  return {
    token,
    user,
    isAuthenticated: !!token && !!user,
    login,
    logout,
    register,
    fetchUser,
  };
}
