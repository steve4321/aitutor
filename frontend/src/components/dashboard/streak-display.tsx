'use client';

import { Flame, Star } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DayInfo {
  day: string;
  short: string;
  isToday?: boolean;
}

interface StreakDisplayProps {
  currentStreak: number;
  longestStreak: number;
  weekData?: boolean[];
}

const DAYS: DayInfo[] = [
  { day: '星期一', short: '一' },
  { day: '星期二', short: '二' },
  { day: '星期三', short: '三' },
  { day: '星期四', short: '四' },
  { day: '星期五', short: '五' },
  { day: '星期六', short: '六' },
  { day: '星期日', short: '日' },
];

export function StreakDisplay({
  currentStreak,
  longestStreak,
  weekData = [true, true, true, true, false, true, true],
}: StreakDisplayProps) {
  const todayIndex = new Date().getDay() === 0 ? 6 : new Date().getDay() - 1;

  return (
    <div className="rounded-2xl border border-rose-200 bg-gradient-to-br from-rose-50 to-orange-50 p-6 dark:border-rose-800 dark:from-rose-950 dark:to-orange-950">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-transform',
              currentStreak > 0
                ? 'bg-gradient-to-br from-orange-500 to-rose-500 animate-pulse'
                : 'bg-slate-200 dark:bg-slate-700'
            )}
          >
            <Flame
              className={cn(
                'h-7 w-7',
                currentStreak > 0 ? 'text-white' : 'text-slate-400'
              )}
            />
          </div>
          <div>
            <p className="text-sm text-rose-700 dark:text-rose-400">连续学习</p>
            <p className="flex items-baseline gap-1">
              <span className="text-3xl font-bold text-rose-800 dark:text-rose-200">
                {currentStreak}
              </span>
              <span className="text-sm text-rose-600 dark:text-rose-400">天</span>
            </p>
          </div>
        </div>

        <div className="text-right">
          <p className="text-xs text-rose-600 dark:text-rose-400">最长连续</p>
          <p className="flex items-baseline gap-1">
            <span className="text-lg font-bold text-rose-800 dark:text-rose-200">
              {longestStreak}
            </span>
            <span className="text-xs text-rose-600 dark:text-rose-400">天</span>
          </p>
        </div>
      </div>

      <div className="mb-4 flex justify-between">
        {DAYS.map((day, index) => {
          const isActive = weekData[index];
          const isToday = index === todayIndex;

          return (
            <div key={day.day} className="flex flex-col items-center gap-1">
              <span className="text-xs text-rose-600 dark:text-rose-400">{day.short}</span>
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium transition-all',
                  isToday && 'ring-2 ring-rose-400 ring-offset-2 dark:ring-offset-slate-900',
                  isActive
                    ? 'bg-gradient-to-br from-orange-500 to-rose-500 text-white'
                    : 'bg-slate-200 text-slate-500 dark:bg-slate-700 dark:text-slate-400'
                )}
              >
                {isActive ? '✓' : '×'}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center justify-center gap-2 text-sm text-rose-700 dark:text-rose-400">
        <Star className="h-4 w-4" />
        <span>
          {currentStreak >= 7
            ? '太棒了！已连续学习一周！'
            : currentStreak >= 3
              ? '继续保持！'
              : '开始你的连续学习之旅吧！'}
        </span>
      </div>
    </div>
  );
}