'use client';

import { Zap, Star } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProgressBar } from '../course/progress-bar';

interface XPDisplayProps {
  level: number;
  currentXP: number;
  xpToNextLevel: number;
  totalXP?: number;
}

export function XPDisplay({ level, currentXP, xpToNextLevel, totalXP }: XPDisplayProps) {
  const progress = Math.round((currentXP / (currentXP + xpToNextLevel)) * 100);

  return (
    <div className="rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 p-6 dark:border-amber-800 dark:from-amber-950 dark:to-orange-950">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg">
            <span className="text-lg font-bold text-white">{level}</span>
          </div>
          <div>
            <p className="text-sm text-amber-700 dark:text-amber-400">等级 {level}</p>
            <div className="flex items-center gap-1">
              <Zap className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              <span className="text-lg font-bold text-amber-800 dark:text-amber-200">
                {currentXP} XP
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-amber-600 dark:text-amber-400">距离下一级</p>
          <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
            {xpToNextLevel} XP
          </p>
        </div>
      </div>

      <ProgressBar progress={progress} color="amber" size="md" showPercentage={false} />

      {totalXP !== undefined && (
        <div className="mt-4 flex items-center justify-center gap-2 text-sm text-amber-700 dark:text-amber-400">
          <Star className="h-4 w-4" />
          <span>累计获得 {totalXP} XP</span>
        </div>
      )}
    </div>
  );
}