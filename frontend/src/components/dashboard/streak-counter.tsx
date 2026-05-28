'use client';

import { Flame } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StreakCounterProps {
  streak: number;
  longestStreak?: number;
  className?: string;
}

export function StreakCounter({
  streak,
  longestStreak = 0,
  className,
}: StreakCounterProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center rounded-xl bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 p-4',
        className
      )}
    >
      <div className="flex items-center gap-2">
        <Flame className="h-8 w-8 text-orange-500" />
        <span className="text-4xl font-bold text-orange-600">{streak}</span>
      </div>
      <p className="mt-1 text-sm font-medium text-orange-800">天连续学习</p>
      {longestStreak > 0 && (
        <p className="mt-0.5 text-xs text-orange-600">
          最长纪录: {longestStreak} 天
        </p>
      )}
    </div>
  );
}
