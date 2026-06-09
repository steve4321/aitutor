'use client';

import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Flame, Trophy, BookOpen, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import { cn } from '@/lib/utils';
import type { UserResponse, StudentProfileResponse } from '@/types/user';

function StatCard({ icon: Icon, label, value, color }: { icon: typeof Flame; label: string; value: string | number; color: string }) {
  return (
    <div className="bg-background rounded-xl border border-border p-4 flex items-center gap-3">
      <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', color)}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="text-xl font-bold text-foreground">{value}</p>
      </div>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-background rounded-xl border border-border p-4 animate-pulse">
      <div className="h-10 w-10 rounded-lg bg-muted" />
      <div className="mt-3 h-4 w-16 bg-muted rounded" />
      <div className="mt-2 h-6 w-12 bg-muted rounded" />
    </div>
  );
}

export default function HomePage() {
  const router = useRouter();

  const { data: userRes, isLoading: isLoadingUser } = useQuery({
    queryKey: ['user'],
    queryFn: () => api.get<UserResponse>('/users/me'),
  });

  const { data: profileRes, isLoading: isLoadingProfile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get<StudentProfileResponse>('/users/me/profile'),
  });

  const userName = userRes?.name ?? 'Learner';
  const xp = profileRes?.xp_total ?? 0;
  const streak = profileRes?.streak_days ?? 0;
  const dailyGoalMinutes = profileRes?.daily_goal_minutes ?? 30;
  const minutesToday = profileRes?.minutes_today ?? 0;
  const dailyProgress = dailyGoalMinutes > 0 ? Math.min((minutesToday / dailyGoalMinutes) * 100, 100) : 0;

  const loading = isLoadingUser || isLoadingProfile;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Welcome back, {userName}!
        </h1>
        <p className="text-muted-foreground mt-1">Continue your learning journey</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <StatCard icon={Trophy} label="XP" value={xp} color="bg-[var(--color-primary)]" />
            <StatCard icon={Flame} label="Streak" value={`${streak} days`} color="bg-[var(--color-accent)]" />
          </>
        )}
      </div>

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Quick Actions</h2>
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => router.push(ROUTES.PRACTICE)}
            className="flex flex-col items-center gap-2 p-4 bg-background rounded-xl border border-border hover:border-[var(--color-primary)]/50 transition-colors"
          >
            <div className="w-10 h-10 rounded-full bg-[var(--color-accent)]/10 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-[var(--color-accent)]" />
            </div>
            <span className="text-xs font-medium text-foreground">Practice</span>
          </button>
          <button
            onClick={() => router.push(`${ROUTES.COURSES}?filter=KET`)}
            className="flex flex-col items-center gap-2 p-4 bg-background rounded-xl border border-border hover:border-[var(--color-primary)]/50 transition-colors"
          >
            <div className="w-10 h-10 rounded-full bg-[var(--color-primary)]/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A7 7 0 0118 9.5M10 19h4" />
              </svg>
            </div>
            <span className="text-xs font-medium text-foreground">KET</span>
          </button>
          <button
            onClick={() => router.push(ROUTES.COURSES)}
            className="flex flex-col items-center gap-2 p-4 bg-background rounded-xl border border-border hover:border-[var(--color-primary)]/50 transition-colors"
          >
            <div className="w-10 h-10 rounded-full bg-[var(--color-secondary)]/10 flex items-center justify-center">
              <ArrowRight className="w-5 h-5 text-[var(--color-secondary)]" />
            </div>
            <span className="text-xs font-medium text-foreground">Browse</span>
          </button>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Daily Progress</h2>
        <div className="bg-background rounded-xl border border-border p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Today&apos;s Goal</span>
            <span className="text-sm font-medium text-foreground">
              {Math.round(minutesToday)}/{dailyGoalMinutes} min
            </span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--color-primary)] rounded-full transition-all"
              style={{ width: `${dailyProgress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
