'use client';

import { Video, BookOpen, Pen, Lock, CheckCircle2, Clock, Star } from 'lucide-react';
import { cn } from '@/lib/utils';

type LessonType = 'video' | 'interactive' | 'practice' | 'reading' | 'mixed';
type LessonStatus = 'locked' | 'not_started' | 'in_progress' | 'completed';

interface LessonCardProps {
  title: string;
  type: LessonType;
  durationMinutes: number;
  status: LessonStatus;
  score?: number;
  xpReward: number;
  onClick?: () => void;
  isLocked?: boolean;
}

const TYPE_CONFIG: Record<LessonType, { icon: typeof Video; label: string; color: string }> = {
  video: { icon: Video, label: '视频', color: 'blue' },
  interactive: { icon: BookOpen, label: '互动', color: 'violet' },
  practice: { icon: Pen, label: '练习', color: 'amber' },
  reading: { icon: BookOpen, label: '阅读', color: 'emerald' },
  mixed: { icon: Star, label: '混合', color: 'rose' },
};

const COLOR_CLASSES: Record<string, { bg: string; icon: string }> = {
  blue: { bg: 'bg-blue-100 dark:bg-blue-900/30', icon: 'text-blue-600 dark:text-blue-400' },
  violet: {
    bg: 'bg-violet-100 dark:bg-violet-900/30',
    icon: 'text-violet-600 dark:text-violet-400',
  },
  amber: {
    bg: 'bg-amber-100 dark:bg-amber-900/30',
    icon: 'text-amber-600 dark:text-amber-400',
  },
  emerald: {
    bg: 'bg-emerald-100 dark:bg-emerald-900/30',
    icon: 'text-emerald-600 dark:text-emerald-400',
  },
  rose: { bg: 'bg-rose-100 dark:bg-rose-900/30', icon: 'text-rose-600 dark:text-rose-400' },
};

export function LessonCard({
  title,
  type,
  durationMinutes,
  status,
  score,
  xpReward,
  onClick,
  isLocked,
}: LessonCardProps) {
  const config = TYPE_CONFIG[type];
  const colors = COLOR_CLASSES[config.color];
  const Icon = config.icon;

  const isClickable = !isLocked && status !== 'locked';

  return (
    <button
      onClick={onClick}
      disabled={!isClickable}
      className={cn(
        'group flex w-full items-center gap-4 rounded-xl border-2 p-4 text-left transition-all',
        isClickable
          ? 'border-slate-200 hover:border-slate-300 hover:shadow-md dark:border-slate-700 dark:hover:border-slate-600'
          : 'cursor-not-allowed border-slate-100 bg-slate-50 dark:border-slate-800 dark:bg-slate-900/50',
        status === 'completed' && 'border-emerald-200 bg-emerald-50/50 dark:border-emerald-800 dark:bg-emerald-900/10',
        status === 'in_progress' && 'border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-900/10'
      )}
    >
      <div
        className={cn(
          'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl transition-colors',
          colors.bg,
          !isClickable && 'opacity-50'
        )}
      >
        {status === 'locked' || isLocked ? (
          <Lock className={cn('h-5 w-5', colors.icon, 'opacity-50')} />
        ) : status === 'completed' ? (
          <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
        ) : (
          <Icon className={cn('h-5 w-5', colors.icon)} />
        )}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h4
            className={cn(
              'truncate font-medium text-slate-900 dark:text-white',
              !isClickable && 'text-slate-400 dark:text-slate-500'
            )}
          >
            {title}
          </h4>
          {status === 'in_progress' && (
            <span className="shrink-0 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-600 dark:bg-blue-900/50 dark:text-blue-400">
              进行中
            </span>
          )}
        </div>
        <div className="mt-1 flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {durationMinutes}分钟
          </span>
          <span className="flex items-center gap-1">
            <Star className="h-3 w-3" />
            {xpReward} XP
          </span>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-3">
        {score !== undefined && (
          <div
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold',
              score >= 80
                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400'
                : score >= 60
                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400'
                  : 'bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-400'
            )}
          >
            {score}
          </div>
        )}

        {isClickable && (
          <span className="text-slate-300 transition-colors group-hover:text-slate-400 dark:text-slate-600">
            →
          </span>
        )}
      </div>
    </button>
  );
}