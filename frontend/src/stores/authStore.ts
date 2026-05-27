"use client";

import { create } from "zustand";
import { User } from "@/types/user";
import { setToken, clearTokens, isAuthenticated } from "@/lib/auth";

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: isAuthenticated() ? "stored" : null,
  user: null,
  isAuthenticated: isAuthenticated(),

  setToken: (token: string) => {
    setToken(token);
    set({ token, isAuthenticated: true });
  },

  setUser: (user: User) => {
    set({ user });
  },

  clearAuth: () => {
    clearTokens();
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
