"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StudentProfile } from "@/types/user";
import { useAuthStore } from "@/stores/authStore";

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

export function useXP() {
  const { token } = useAuthStore();
  const [xpData, setXpData] = useState<XPData>({
    xp: 0,
    level: 1,
    streak: 0,
    dailyGoalProgress: 0,
    dailyGoalMinutes: 30,
  });
  const [loading, setLoading] = useState(false);

  const fetchXPData = useCallback(async () => {
    if (!token) return;

    setLoading(true);
    try {
      const profile = await api.get<StudentProfile>("/users/me/profile");
      const level = calculateLevel(profile.xp);
      const dailyGoalProgress = calculateDailyGoalProgress(
        0,
        profile.daily_goal_minutes
      );

      setXpData({
        xp: profile.xp,
        level,
        streak: profile.streak,
        dailyGoalProgress,
        dailyGoalMinutes: profile.daily_goal_minutes,
      });
    } catch {
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      setLoading(true);
      api.get<StudentProfile>("/users/me/profile").then((profile) => {
        setXpData({
          xp: profile.xp,
          level: calculateLevel(profile.xp),
          streak: profile.streak,
          dailyGoalProgress: calculateDailyGoalProgress(0, profile.daily_goal_minutes),
          dailyGoalMinutes: profile.daily_goal_minutes,
        });
      }).catch(() => undefined).finally(() => {
        setLoading(false);
      });
    }
  }, [token]);

  return {
    ...xpData,
    loading,
    refetch: fetchXPData,
  };
}
