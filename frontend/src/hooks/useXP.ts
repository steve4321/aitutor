"use client";

import { useCallback, useState } from "react";
import { useAuthStore } from '@/stores/auth-store';
import { api } from "@/lib/api";
import type { StudentProfile } from "@/types/user";

interface XPData {
  xp: number;
  level: number;
  streak: number;
  dailyGoalProgress: number;
  dailyGoalMinutes: number;
}

const LEVEL_XP_THRESHOLD = 1000;

function calculateLevel(xp: number): number {
  return Math.floor(xp / LEVEL_XP_THRESHOLD) + 1;
}

function calculateDailyGoalProgress(
  minutesToday: number,
  dailyGoalMinutes: number
): number {
  if (dailyGoalMinutes <= 0) return 0;
  return Math.min((minutesToday / dailyGoalMinutes) * 100, 100);
}

function deriveXPData(profile: StudentProfile): XPData {
  return {
    xp: profile.xp_total,
    level: calculateLevel(profile.xp_total),
    streak: profile.streak_days,
    dailyGoalProgress: calculateDailyGoalProgress(profile.minutes_today, profile.daily_goal_minutes),
    dailyGoalMinutes: profile.daily_goal_minutes,
  };
}

export function useXP() {
  const { isAuthenticated, profile } = useAuthStore();
  const [xpData, setXpData] = useState<XPData>({
    xp: profile?.xp_total ?? 0,
    level: profile ? calculateLevel(profile.xp_total) : 1,
    streak: profile?.streak_days ?? 0,
    dailyGoalProgress: profile ? calculateDailyGoalProgress(profile.minutes_today, profile.daily_goal_minutes) : 0,
    dailyGoalMinutes: profile?.daily_goal_minutes ?? 30,
  });
  const [loading, setLoading] = useState(false);

  const refetch = useCallback(async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    try {
      const freshProfile = await api.get<StudentProfile>("/users/me/profile");
      useAuthStore.getState().setProfile(freshProfile);
      setXpData(deriveXPData(freshProfile));
    } catch (err) {
      console.warn('[useXP] Failed to fetch XP data:', err);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  return {
    ...xpData,
    loading,
    refetch,
  };
}
