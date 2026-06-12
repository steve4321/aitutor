'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, Feather, TrendingUp, Clock, ChevronRight, Loader2, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

const MODULE_INFO = {
  composition: {
    icon: FileText,
    title: '作文',
    subtitle: '写作练习',
    color: 'amber',
    path: '/chinese/composition',
    description: '记叙文/描写文/想象作文/应用文',
  },
  poetry: {
    icon: Feather,
    title: '古诗词',
    subtitle: '诗词赏析',
    color: 'emerald',
    path: '/chinese/poetry',
    description: '课标必背古诗词核心篇目',
  },
};

const COLOR_CLASSES = {
  amber: {
    bg: 'bg-amber-50 dark:bg-amber-950',
    border: 'border-amber-200 dark:border-amber-800',
    icon: 'text-amber-600 dark:text-amber-400',
    progress: 'bg-amber-500',
    text: 'text-amber-700 dark:text-amber-300',
  },
  emerald: {
    bg: 'bg-emerald-50 dark:bg-emerald-950',
    border: 'border-emerald-200 dark:border-emerald-800',
    icon: 'text-emerald-600 dark:text-emerald-400',
    progress: 'bg-emerald-500',
    text: 'text-emerald-700 dark:text-emerald-300',
  },
};

const MODULES = ['composition', 'poetry'] as const;

interface CompositionTask {
  id: string;
  writing_type: string;
}

interface PoetryListResponse {
  items: Array<{ id: string; title: string }>;
  total: number;
}

export default function ChinesePage() {
  const { data: compositionTasks, isLoading: compositionLoading } = useQuery({
    queryKey: ['chinese', 'composition', 'tasks'],
    queryFn: () => api.get<CompositionTask[]>('/chinese/composition/tasks', { limit: '1' }),
  });

  const { data: poetryData, isLoading: poetryLoading } = useQuery({
    queryKey: ['chinese', 'poetry', 'list'],
    queryFn: () => api.get<PoetryListResponse>('/chinese/poetry', { limit: '1' }),
  });

  const compositionCount = compositionTasks?.length ?? 0;
  const poetryCount = poetryData?.total ?? 0;

  const questionCounts = {
    composition: compositionCount,
    poetry: poetryCount,
  };

  const isLoading = compositionLoading || poetryLoading;

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-emerald-500" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">语文</h1>
              <p className="text-slate-600 dark:text-slate-400">小学4-6年级语文素养训练</p>
            </div>
          </div>
        </header>

        <section className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-2">
          {MODULES.map((module) => {
            const info = MODULE_INFO[module];
            const colors = COLOR_CLASSES[info.color as keyof typeof COLOR_CLASSES];
            const Icon = info.icon;
            const count = questionCounts[module];
            const hasContent = count > 0;

            return (
              <a
                key={module}
                href={info.path}
                className={cn(
                  'group relative overflow-hidden rounded-2xl border p-6 transition-all hover:shadow-lg',
                  colors.bg,
                  colors.border
                )}
              >
                <Icon className={cn('mb-4 h-10 w-10', colors.icon)} />
                <h3 className="mb-1 font-semibold text-slate-900 dark:text-white">{info.title}</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">{info.description}</p>
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
                    <span className="text-sm text-slate-400">加载中...</span>
                  </div>
                ) : hasContent ? (
                  <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">
                    {count}
                    <span className="text-sm font-normal text-slate-400"> 个任务</span>
                  </p>
                ) : (
                  <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">
                    —
                    <span className="text-sm font-normal text-slate-400"> 个任务</span>
                  </p>
                )}
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className={cn('h-full rounded-full transition-all', colors.progress)}
                    style={{ width: '0%' }}
                  />
                </div>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  {hasContent ? `${count} 个任务` : '0% 完成'}
                </p>
                <ChevronRight className="absolute bottom-6 right-6 h-5 w-5 text-slate-300 transition-transform group-hover:translate-x-1 group-hover:text-slate-400" />
              </a>
            );
          })}
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
            <TrendingUp className="h-5 w-5 text-emerald-500" />
            综合进度
          </h2>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
            </div>
          ) : (
            <div className="flex items-center justify-center py-8">
              <p className="text-center text-slate-500 dark:text-slate-400">暂无练习记录</p>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <Clock className="h-5 w-5 text-slate-400" />
              最近练习记录
            </h2>
          </div>
          <div className="flex items-center justify-center py-12">
            <p className="text-center text-slate-500 dark:text-slate-400">暂无练习记录</p>
          </div>
        </section>
      </div>
    </div>
  );
}