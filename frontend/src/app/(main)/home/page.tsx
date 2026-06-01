'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Flame, Trophy, BookOpen, Play, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import { cn } from '@/lib/utils';

interface User {
  display_name: string;
  xp: number;
  streak: number;
}

interface UserMeResponse {
  id: string;
  name: string;
}

interface ProfileResponse {
  xp_total: number;
  streak_days: number;
}

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
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userRes, profileRes] = await Promise.all([
          api.get<UserMeResponse>('/users/me'),
          api.get<ProfileResponse>('/users/me/profile'),
        ]);
        setUser({
          display_name: userRes.name,
          xp: profileRes.xp_total,
          streak: profileRes.streak_days,
        });
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Welcome back, {user?.display_name || 'Learner'}!
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
            <StatCard icon={Trophy} label="XP" value={user?.xp || 0} color="bg-[var(--color-primary)]" />
            <StatCard icon={Flame} label="Streak" value={`${user?.streak || 0} days`} color="bg-[var(--color-accent)]" />
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
            <span className="text-sm font-medium text-foreground">2/3 Lessons</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-[var(--color-primary)] rounded-full w-[66%] transition-all" />
          </div>
        </div>
      </div>
    </div>
  );
}
