'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

type Trend = 'up' | 'down' | 'neutral';
type IconComponent = React.ComponentType<{ className?: string }>;

interface StatsCardProps {
  icon: IconComponent;
  label: string;
  value: string | number;
  trend?: Trend;
  trendValue?: string;
  color?: 'blue' | 'violet' | 'emerald' | 'amber' | 'rose';
}

const COLOR_CLASSES = {
  blue: {
    bg: 'bg-blue-100 dark:bg-blue-900/30',
    icon: 'text-blue-600 dark:text-blue-400',
  },
  violet: {
    bg: 'bg-violet-100 dark:bg-violet-900/30',
    icon: 'text-violet-600 dark:text-violet-400',
  },
  emerald: {
    bg: 'bg-emerald-100 dark:bg-emerald-900/30',
    icon: 'text-emerald-600 dark:text-emerald-400',
  },
  amber: {
    bg: 'bg-amber-100 dark:bg-amber-900/30',
    icon: 'text-amber-600 dark:text-amber-400',
  },
  rose: {
    bg: 'bg-rose-100 dark:bg-rose-900/30',
    icon: 'text-rose-600 dark:text-rose-400',
  },
};

const TREND_ICONS = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
};

const TREND_COLORS = {
  up: 'text-emerald-600 dark:text-emerald-400',
  down: 'text-rose-600 dark:text-rose-400',
  neutral: 'text-slate-400 dark:text-slate-500',
};

export function StatsCard({
  icon: Icon,
  label,
  value,
  trend,
  trendValue,
  color = 'blue',
}: StatsCardProps) {
  const colors = COLOR_CLASSES[color];
  const TrendIcon = trend ? TREND_ICONS[trend] : null;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
      <div className="mb-3 flex items-center justify-between">
        <div
          className={cn('flex h-10 w-10 items-center justify-center rounded-xl', colors.bg)}
        >
          <Icon className={cn('h-5 w-5', colors.icon)} />
        </div>
        {TrendIcon && trend && (
          <div className="flex items-center gap-1">
            <TrendIcon className={cn('h-4 w-4', TREND_COLORS[trend])} />
            {trendValue && (
              <span className={cn('text-xs font-medium', TREND_COLORS[trend])}>
                {trendValue}
              </span>
            )}
          </div>
        )}
      </div>
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
    </div>
  );
}