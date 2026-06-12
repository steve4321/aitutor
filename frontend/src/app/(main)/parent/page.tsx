'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  Users,
  Flame,
  Clock,
  Target,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Bell,
  ChevronRight,
  Loader2,
  AlertCircle,
  Award,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import type {
  LinkedChild,
  ChildOverview,
  MasteryTrendsResponse,
  ParentNotification,
} from '@/types/parent';

const PILLAR_LABELS: Record<string, string> = {
  algebra: '代数',
  geometry: '几何',
  counting: '计数',
  number_theory: '数论',
};

const PILLAR_COLORS: Record<string, string> = {
  algebra: 'bg-blue-500',
  geometry: 'bg-emerald-500',
  counting: 'bg-amber-500',
  number_theory: 'bg-violet-500',
};

const PILLAR_COLORS_LIGHT: Record<string, string> = {
  algebra: 'bg-blue-100 dark:bg-blue-900/30',
  geometry: 'bg-emerald-100 dark:bg-emerald-900/30',
  counting: 'bg-amber-100 dark:bg-amber-900/30',
  number_theory: 'bg-violet-100 dark:bg-violet-900/30',
};

const PILLAR_ICONS: Record<string, string> = {
  algebra: '📐',
  geometry: '📏',
  counting: '🎲',
  number_theory: '🔢',
};

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-8 h-12 w-48 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
          ))}
        </div>
        <div className="h-64 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  );
}

function NoChildrenState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Users className="mb-4 h-16 w-16 text-slate-300 dark:text-slate-600" />
      <p className="text-lg font-medium text-slate-600 dark:text-slate-400">暂无关联孩子</p>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-500">请使用绑定码关联孩子的学习账号</p>
      <Link
        href={ROUTES.PARENT_SETTINGS}
        className="mt-4 rounded-lg bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--color-primary-hover)]"
      >
        去绑定
      </Link>
    </div>
  );
}

function NoDataState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <BarChart3 className="mb-4 h-16 w-16 text-slate-300 dark:text-slate-600" />
      <p className="text-lg font-medium text-slate-600 dark:text-slate-400">暂无学习数据</p>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-500">孩子开始学习后查看知识掌握趋势</p>
    </div>
  );
}

interface MasteryBarProps {
  label: string;
  value: number;
  previousValue?: number;
  color: string;
  colorLight: string;
  icon: string;
}

function MasteryBar({ label, value, previousValue, color, colorLight, icon }: MasteryBarProps) {
  const change = previousValue !== undefined ? value - previousValue : 0;
  const isPositive = change >= 0;
  const maxHeight = 120;

  return (
    <div className="flex flex-1 flex-col items-center gap-2">
      <div className="flex w-full items-end justify-center gap-1">
        {previousValue !== undefined && (
          <div
            className={cn('w-4 rounded-t transition-all', color, 'opacity-40')}
            style={{ height: `${(previousValue / 100) * maxHeight}px` }}
          />
        )}
        <div
          className={cn('w-6 rounded-t transition-all', color)}
          style={{ height: `${Math.max((value / 100) * maxHeight, 4)}px` }}
        />
      </div>
      <span className="text-lg">{icon}</span>
      <span className="text-xs text-slate-500 dark:text-slate-400">{label}</span>
      <div className="flex items-center gap-1">
        <span className="text-sm font-semibold text-slate-900 dark:text-white">{value}%</span>
        {previousValue !== undefined && change !== 0 && (
          <span className={cn('flex items-center text-xs', isPositive ? 'text-emerald-600' : 'text-rose-600')}>
            {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
    </div>
  );
}

export default function ParentOverviewPage() {
  const [selectedChildId, setSelectedChildId] = useState<string | null>(null);

  const { data: children, isLoading: childrenLoading } = useQuery<LinkedChild[]>({
    queryKey: ['parent-children'],
    queryFn: () => api.get<LinkedChild[]>('/parent/children'),
  });

  const activeChildId = selectedChildId ?? children?.[0]?.id;
  const activeChild = children?.find((c) => c.id === activeChildId);

  const { data: overview, isLoading: overviewLoading } = useQuery<ChildOverview>({
    queryKey: ['child-overview', activeChildId],
    queryFn: () => api.get<ChildOverview>(`/parent/children/${activeChildId}/overview`),
    enabled: !!activeChildId,
  });

  const { data: masteryTrends, isLoading: masteryLoading } = useQuery<MasteryTrendsResponse>({
    queryKey: ['child-mastery', activeChildId],
    queryFn: () => api.get<MasteryTrendsResponse>(`/parent/children/${activeChildId}/mastery`),
    enabled: !!activeChildId,
  });

  const { data: notifications, isLoading: notificationsLoading } = useQuery<ParentNotification[]>({
    queryKey: ['parent-notifications', activeChildId],
    queryFn: () => api.get<ParentNotification[]>(`/parent/children/${activeChildId}/notifications`),
    enabled: !!activeChildId,
  });

  const isLoading = childrenLoading || overviewLoading || masteryLoading || notificationsLoading;

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (!children || children.length === 0) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <Users className="h-8 w-8 text-violet-600 dark:text-violet-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">家长端</h1>
              <p className="text-slate-600 dark:text-slate-400">查看孩子的学习情况</p>
            </div>
          </div>
        </header>
        <NoChildrenState />
      </div>
    );
  }

  const latestMastery = masteryTrends?.trends[masteryTrends.trends.length - 1];
  const previousMastery = masteryTrends?.trends[masteryTrends.trends.length - 2];
  const pillars = latestMastery?.pillars ?? { algebra: 0, geometry: 0, counting: 0, number_theory: 0 };

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <Users className="h-8 w-8 text-violet-600 dark:text-violet-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">家长端</h1>
              <p className="text-slate-600 dark:text-slate-400">查看孩子的学习情况</p>
            </div>
          </div>
        </header>

        {children.length > 1 && (
          <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
            {children.map((child) => (
              <button
                key={child.id}
                onClick={() => setSelectedChildId(child.id)}
                className={cn(
                  'shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-all',
                  activeChildId === child.id
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                )}
              >
                {child.name}
              </button>
            ))}
          </div>
        )}

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-xl font-bold text-white">
                {activeChild?.name?.charAt(0) ?? '?'}
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                  {activeChild?.name ?? '学生'}
                </h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {activeChild?.target_exam ?? '未设置目标'} ·{' '}
                  {activeChild?.grade_level ? `年级${activeChild.grade_level}` : ''}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-amber-500" />
              <span className="font-semibold text-slate-900 dark:text-white">
                {overview?.streak_days ?? activeChild?.streak_days ?? 0}天
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <Clock className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">本周学习</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {overview?.weekly_study_minutes ?? 0}分钟
              </p>
            </div>

            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
                <Target className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">目标完成</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {overview?.weekly_goal_completion ?? 0}%
              </p>
            </div>

            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-violet-100 dark:bg-violet-900/30">
                <BarChart3 className="h-4 w-4 text-violet-600 dark:text-violet-400" />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">总 XP</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {activeChild?.xp_total ?? 0}
              </p>
            </div>

            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
                <Clock className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">今日学习</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">
                {overview?.minutes_today ?? 0}/{overview?.daily_goal_minutes ?? 30}分钟
              </p>
            </div>
          </div>
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-6 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
            <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            知识掌握趋势（本周）
          </h2>
          {!masteryTrends || masteryTrends.trends.length === 0 ? (
            <NoDataState />
          ) : (
            <div className="flex items-end justify-around gap-2">
              {Object.entries(pillars).map(([key, value]) => (
                <MasteryBar
                  key={key}
                  label={PILLAR_LABELS[key] ?? key}
                  value={Math.round(value)}
                  previousValue={previousMastery?.pillars[key as keyof typeof pillars]}
                  color={PILLAR_COLORS[key]}
                  colorLight={PILLAR_COLORS_LIGHT[key]}
                  icon={PILLAR_ICONS[key]}
                />
              ))}
            </div>
          )}
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <Bell className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              通知
            </h2>
            <Link
              href={ROUTES.PARENT_REPORTS}
              className="flex items-center gap-1 text-sm text-violet-600 hover:text-violet-700 dark:text-violet-400"
            >
              查看全部
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {!notifications || notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Bell className="mb-2 h-12 w-12 text-slate-300 dark:text-slate-600" />
                <p className="text-sm text-slate-500 dark:text-slate-400">暂无新通知</p>
              </div>
            ) : (
              notifications.slice(0, 5).map((notification) => (
                <div
                  key={notification.id}
                  className="flex items-start gap-4 px-6 py-4"
                >
                  <div
                    className={cn(
                      'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
                      notification.type === 'concern'
                        ? 'bg-rose-100 dark:bg-rose-900/30'
                        : notification.type === 'achievement'
                          ? 'bg-amber-100 dark:bg-amber-900/30'
                          : 'bg-blue-100 dark:bg-blue-900/30'
                    )}
                  >
                    {notification.type === 'concern' ? (
                      <AlertCircle className="h-4 w-4 text-rose-600 dark:text-rose-400" />
                    ) : notification.type === 'achievement' ? (
                      <Award className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                    ) : (
                      <Bell className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-slate-900 dark:text-white">{notification.title}</p>
                    <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
                      {notification.message}
                    </p>
                    <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
                      {new Date(notification.created_at).toLocaleDateString('zh-CN')}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        <div className="grid grid-cols-2 gap-4">
          <Link
            href={ROUTES.PARENT_REPORTS}
            className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-5 transition-all hover:border-violet-300 hover:bg-violet-50 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-violet-600"
          >
            <div>
              <p className="font-semibold text-slate-900 dark:text-white">周报</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">查看详细学习报告</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-400" />
          </Link>
          <Link
            href={ROUTES.PARENT_SETTINGS}
            className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-5 transition-all hover:border-violet-300 hover:bg-violet-50 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-violet-600"
          >
            <div>
              <p className="font-semibold text-slate-900 dark:text-white">设置</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">通知和学习限制</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-400" />
          </Link>
        </div>
      </div>
    </div>
  );
}