'use client';

import { BookOpen, Lock, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CourseCardProps {
  title: string;
  description: string;
  coverImageUrl?: string;
  progress: number;
  totalLessons: number;
  enrolled: boolean;
  isLocked?: boolean;
  onClick?: () => void;
}

export function CourseCard({
  title,
  description,
  coverImageUrl,
  progress,
  totalLessons,
  enrolled,
  isLocked,
  onClick,
}: CourseCardProps) {
  const isCompleted = progress >= 100;

  return (
    <button
      onClick={onClick}
      disabled={isLocked}
      className={cn(
        'group relative w-full overflow-hidden rounded-2xl border text-left transition-all',
        isLocked
          ? 'cursor-not-allowed border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800/50'
          : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-lg dark:border-slate-700 dark:bg-slate-800'
      )}
    >
      <div className="relative h-40 overflow-hidden rounded-t-2xl bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800">
        {coverImageUrl ? (
          <img
            src={coverImageUrl}
            alt={title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <BookOpen className="h-12 w-12 text-slate-300 dark:text-slate-600" />
          </div>
        )}

        {isLocked && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50">
            <Lock className="h-8 w-8 text-white" />
          </div>
        )}

        {isCompleted && (
          <div className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500">
            <CheckCircle2 className="h-5 w-5 text-white" />
          </div>
        )}

        {progress > 0 && progress < 100 && (
          <div className="absolute inset-x-0 bottom-0 h-1 bg-slate-200 dark:bg-slate-700">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="mb-1 font-semibold text-slate-900 line-clamp-1 dark:text-white">
          {title}
        </h3>
        <p className="mb-3 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">
          {description}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400 dark:text-slate-500">
            {totalLessons} 课时
          </span>
          {enrolled && (
            <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
              {progress}% 完成
            </span>
          )}
        </div>
      </div>

      {enrolled && progress > 0 && (
        <div className="h-1 bg-slate-100 dark:bg-slate-700">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </button>
  );
}