'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, ChevronLeft, Loader2, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface CompositionTask {
  id: string;
  title: string;
  writing_type: string;
  prompt: string;
  min_chars: number;
  max_chars: number;
  status?: 'not_started' | 'in_progress' | 'completed';
}

const WRITING_TYPE_LABELS: Record<string, string> = {
  narrative: '记叙文',
  descriptive: '描写文',
  imaginative: '想象作文',
  practical: '应用文',
};

const WRITING_TYPE_COLORS: Record<string, string> = {
  narrative: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  descriptive: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  imaginative: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
  practical: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
};

export default function CompositionPage() {
  const { data: tasks, isLoading, error } = useQuery({
    queryKey: ['chinese', 'composition', 'tasks'],
    queryFn: () => api.get<CompositionTask[]>('/chinese/composition/tasks', { limit: '50' }),
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
              <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">语文作文训练</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">作文题目加载中...</p>
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
              <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">语文作文训练</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-red-200 bg-red-50 p-12 dark:border-red-800 dark:bg-red-950">
            <BookOpen className="h-12 w-12 text-red-600 dark:text-red-400" />
            <h2 className="mb-2 mt-4 text-xl font-semibold text-red-900 dark:text-red-100">加载失败</h2>
            <p className="mb-6 text-center text-red-700 dark:text-red-300">无法加载作文题目，请稍后再试</p>
            <a
              href="/chinese"
              className="flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700"
            >
              返回语文主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
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
              <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">语文作文训练</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <FileText className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">暂无题目</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              作文题库正在开发中<br />
              请稍后再来练习
            </p>
            <a
              href="/chinese"
              className="flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700"
            >
              返回语文主页
            </a>
          </div>
        </div>
      </div>
    );
  }

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
            <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">选择写作任务</p>
            </div>
          </div>
        </header>

        <div className="mb-4 flex flex-wrap gap-2">
          {Object.entries(WRITING_TYPE_LABELS).map(([key, label]) => (
            <span
              key={key}
              className={cn(
                'rounded-full px-3 py-1 text-xs font-medium',
                WRITING_TYPE_COLORS[key]
              )}
            >
              {label}
            </span>
          ))}
        </div>

        <div className="space-y-4">
          {tasks.map((task) => (
            <a
              key={task.id}
              href={`/chinese/composition/${task.id}`}
              className="block w-full rounded-2xl border border-slate-200 bg-white p-6 text-left transition-all hover:border-amber-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <span
                    className={cn(
                      'inline-block rounded-full px-3 py-1 text-xs font-medium',
                      WRITING_TYPE_COLORS[task.writing_type] || 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
                    )}
                  >
                    {WRITING_TYPE_LABELS[task.writing_type] || task.writing_type}
                  </span>
                  <p className="mt-3 font-medium text-slate-900 dark:text-white">{task.title}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    字数要求: {task.min_chars}-{task.max_chars}字
                  </p>
                </div>
                {task.status && (
                  <span
                    className={cn(
                      'rounded-full px-2 py-1 text-xs font-medium',
                      task.status === 'completed'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200'
                        : task.status === 'in_progress'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
                          : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                    )}
                  >
                    {task.status === 'completed' ? '已完成' : task.status === 'in_progress' ? '进行中' : '未开始'}
                  </span>
                )}
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}