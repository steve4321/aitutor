'use client';

import { useQuery } from '@tanstack/react-query';
import { Feather, ChevronLeft, Loader2, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface PoetryPoem {
  id: string;
  title: string;
  poet: string;
  dynasty: string;
  theme: string;
  mastery_status?: 'memorizing' | 'understanding' | 'appreciating';
}

const THEME_LABELS: Record<string, string> = {
  seasonal: '四季',
  landscape: '山水',
  emotions: '情感',
  masters: '名家',
};

const THEME_COLORS: Record<string, string> = {
  seasonal: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  landscape: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  emotions: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
  masters: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
};

const MASTERY_LABELS: Record<string, string> = {
  memorizing: '背诵',
  understanding: '理解',
  appreciating: '赏析',
};

const MASTERY_COLORS: Record<string, string> = {
  memorizing: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
  understanding: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  appreciating: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
};

export default function PoetryPage() {
  const { data: poems, isLoading, error } = useQuery({
    queryKey: ['chinese', 'poetry', 'list'],
    queryFn: () => api.get<{ items: PoetryPoem[]; total: number }>('/chinese/poetry', { limit: '100' }),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <a
              href="/chinese"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </a>
            <div className="flex items-center gap-3">
              <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">古诗词</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">诗词赏析学习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">诗词加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <a
              href="/chinese"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </a>
            <div className="flex items-center gap-3">
              <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">古诗词</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">诗词赏析学习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-red-200 bg-red-50 p-12 dark:border-red-800 dark:bg-red-950">
            <BookOpen className="h-12 w-12 text-red-600 dark:text-red-400" />
            <h2 className="mb-2 mt-4 text-xl font-semibold text-red-900 dark:text-red-100">加载失败</h2>
            <p className="mb-6 text-center text-red-700 dark:text-red-300">无法加载诗词列表，请稍后再试</p>
            <a
              href="/chinese"
              className="flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 font-medium text-white transition-all hover:bg-emerald-700"
            >
              返回语文主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (!poems || poems.items.length === 0) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <a
              href="/chinese"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </a>
            <div className="flex items-center gap-3">
              <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">古诗词</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">诗词赏析学习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Feather className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">暂无诗词</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              诗词库正在开发中<br />
              请稍后再来学习
            </p>
            <a
              href="/chinese"
              className="flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 font-medium text-white transition-all hover:bg-emerald-700"
            >
              返回语文主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  const groupedByTheme = poems.items.reduce((acc, poem) => {
    const theme = poem.theme || 'other';
    if (!acc[theme]) {
      acc[theme] = [];
    }
    acc[theme].push(poem);
    return acc;
  }, {} as Record<string, PoetryPoem[]>);

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <header className="mb-6 flex items-center gap-4">
          <a
            href="/chinese"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
          >
            <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
          </a>
          <div className="flex items-center gap-3">
            <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">古诗词</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">选择诗词学习</p>
            </div>
          </div>
        </header>

        <div className="mb-4 flex flex-wrap gap-2">
          {Object.entries(THEME_LABELS).map(([key, label]) => (
            <span
              key={key}
              className={cn(
                'rounded-full px-3 py-1 text-xs font-medium',
                THEME_COLORS[key] || 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
              )}
            >
              {label}
            </span>
          ))}
        </div>

        <div className="space-y-8">
          {Object.entries(groupedByTheme).map(([theme, themePoems]) => (
            <section key={theme}>
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                <span
                  className={cn(
                    'rounded-full px-3 py-1 text-xs font-medium',
                    THEME_COLORS[theme] || 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
                  )}
                >
                  {THEME_LABELS[theme] || theme}
                </span>
              </h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {themePoems.map((poem) => (
                  <a
                    key={poem.id}
                    href={`/chinese/poetry/${poem.id}`}
                    className="block rounded-2xl border border-slate-200 bg-white p-4 transition-all hover:border-emerald-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-slate-900 dark:text-white">{poem.title}</h3>
                        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                          {poem.poet} · {poem.dynasty}
                        </p>
                      </div>
                      {poem.mastery_status && (
                        <span
                          className={cn(
                            'rounded-full px-2 py-1 text-xs font-medium',
                            MASTERY_COLORS[poem.mastery_status]
                          )}
                        >
                          {MASTERY_LABELS[poem.mastery_status]}
                        </span>
                      )}
                    </div>
                  </a>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}