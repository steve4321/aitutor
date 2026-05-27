'use client';

import { BookOpen, Pen, Headphones, Mic, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProgressBar } from '../course/progress-bar';

type Skill = 'reading' | 'writing' | 'listening' | 'speaking';

interface KETCardProps {
  skill: Skill;
  score: number;
  progress: number;
  practiceCount: number;
  onClick?: () => void;
}

const SKILL_CONFIG: Record<
  Skill,
  { icon: typeof BookOpen; title: string; color: 'blue' | 'amber' | 'emerald' | 'rose' }
> = {
  reading: { icon: BookOpen, title: '阅读', color: 'blue' },
  writing: { icon: Pen, title: '写作', color: 'amber' },
  listening: { icon: Headphones, title: '听力', color: 'emerald' },
  speaking: { icon: Mic, title: '口语', color: 'rose' },
};

const COLOR_CLASSES = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-950',
    border: 'border-blue-200 dark:border-blue-800',
    icon: 'text-blue-600 dark:text-blue-400',
    progress: 'bg-blue-500',
    text: 'text-blue-700 dark:text-blue-300',
    hover: 'hover:border-blue-300 dark:hover:border-blue-700',
  },
  amber: {
    bg: 'bg-amber-50 dark:bg-amber-950',
    border: 'border-amber-200 dark:border-amber-800',
    icon: 'text-amber-600 dark:text-amber-400',
    progress: 'bg-amber-500',
    text: 'text-amber-700 dark:text-amber-300',
    hover: 'hover:border-amber-300 dark:hover:border-amber-700',
  },
  emerald: {
    bg: 'bg-emerald-50 dark:bg-emerald-950',
    border: 'border-emerald-200 dark:border-emerald-800',
    icon: 'text-emerald-600 dark:text-emerald-400',
    progress: 'bg-emerald-500',
    text: 'text-emerald-700 dark:text-emerald-300',
    hover: 'hover:border-emerald-300 dark:hover:border-emerald-700',
  },
  rose: {
    bg: 'bg-rose-50 dark:bg-rose-950',
    border: 'border-rose-200 dark:border-rose-800',
    icon: 'text-rose-600 dark:text-rose-400',
    progress: 'bg-rose-500',
    text: 'text-rose-700 dark:text-rose-300',
    hover: 'hover:border-rose-300 dark:hover:border-rose-700',
  },
};

export function KETCard({ skill, score, progress, practiceCount, onClick }: KETCardProps) {
  const config = SKILL_CONFIG[skill];
  const colors = COLOR_CLASSES[config.color];
  const Icon = config.icon;

  return (
    <button
      onClick={onClick}
      className={cn(
        'group relative w-full overflow-hidden rounded-2xl border-2 p-6 text-left transition-all',
        colors.bg,
        colors.border,
        colors.hover
      )}
    >
      <Icon className={cn('mb-4 h-10 w-10', colors.icon)} />
      <h3 className="mb-1 font-semibold text-slate-900 dark:text-white">{config.title}</h3>
      <p className="mb-4 text-2xl font-bold text-slate-700 dark:text-slate-200">
        {score}
        <span className="ml-1 text-sm font-normal text-slate-400">分</span>
      </p>
      <ProgressBar
        progress={progress}
        color={config.color}
        size="sm"
        showPercentage={false}
        className="mb-2"
      />
      <p className="text-xs text-slate-500 dark:text-slate-400">
        {progress}% 完成 · {practiceCount} 次练习
      </p>

      <div className="absolute right-4 top-4 opacity-0 transition-opacity group-hover:opacity-100">
        <TrendingUp className={cn('h-5 w-5', colors.icon)} />
      </div>
    </button>
  );
}