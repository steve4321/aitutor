'use client';

import { Lightbulb, Lock, Eye, EyeOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HintDisplayProps {
  hints: string[];
  maxLevel: number;
  currentLevel?: number;
}

const LEVEL_LABELS = ['提示 1', '提示 2', '提示 3', '提示 4', '提示 5'];

export function HintDisplay({ hints, maxLevel, currentLevel = hints.length }: HintDisplayProps) {
  const availableHints = maxLevel - hints.length;

  if (hints.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">
        <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
          <Lightbulb className="h-5 w-5" />
          <span className="text-sm">暂无提示</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <span className="font-medium text-amber-700 dark:text-amber-300">解题提示</span>
        </div>
        <span className="text-xs text-amber-600 dark:text-amber-400">
          {hints.length} / {maxLevel} 提示已解锁
        </span>
      </div>

      <div className="space-y-3">
        {hints.map((hint, index) => (
          <div
            key={index}
            className="rounded-lg border border-amber-200 bg-white p-3 dark:border-amber-700 dark:bg-slate-900"
          >
            <div className="mb-1 flex items-center gap-2">
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-900/50 dark:text-amber-400">
                {LEVEL_LABELS[index] || `提示 ${index + 1}`}
              </span>
            </div>
            <p className="text-sm text-slate-700 dark:text-slate-300">{hint}</p>
          </div>
        ))}

        {availableHints > 0 && (
          <div className="flex items-center justify-center gap-2 py-2 text-sm text-amber-600 dark:text-amber-400">
            <Lock className="h-4 w-4" />
            <span>还有 {availableHints} 个提示未解锁</span>
          </div>
        )}
      </div>
    </div>
  );
}