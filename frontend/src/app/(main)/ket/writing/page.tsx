'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Pen, ChevronLeft, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type { KETWritingTask, KETWritingScoreResponse } from '@/types/ket';

export default function WritingPage() {
  const [selectedTask, setSelectedTask] = useState<KETWritingTask | null>(null);
  const [content, setContent] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['ket', 'writing', 'tasks'],
    queryFn: () => api.get<KETWritingTask[]>('/ket/writing/tasks', { limit: '20' }),
  });

  const submitMutation = useMutation({
    mutationFn: (body: { task_id: string; content: string; word_count: number }) =>
      api.post<KETWritingScoreResponse>('/ket/writing/submit', body),
    onSuccess: () => {
      setSubmitted(true);
    },
  });

  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;

  const handleSubmit = () => {
    if (!selectedTask) return;
    submitMutation.mutate({
      task_id: selectedTask.id,
      content,
      word_count: wordCount,
    });
  };

  const handleBackToTasks = () => {
    setSelectedTask(null);
    setContent('');
    setSubmitted(false);
  };

  if (tasksLoading) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <a
              href="/ket"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </a>
            <div className="flex items-center gap-3">
              <Pen className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">写作练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">KET 写作练习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">加载题目中...</p>
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
              href="/ket"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </a>
            <div className="flex items-center gap-3">
              <Pen className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">写作练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">KET 写作练习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Pen className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">暂无题目</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              写作题库正在开发中<br />
              请稍后再来练习
            </p>
            <a
              href="/ket"
              className="flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700"
            >
              返回 KET 主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (submitted && submitMutation.data) {
    const score = submitMutation.data;
    const maxScore = 5;
    const overallPercent = (score.band / maxScore) * 100;

    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <button
              onClick={handleBackToTasks}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </button>
            <div className="flex items-center gap-3">
              <Pen className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">写作练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">评分结果</p>
              </div>
            </div>
          </header>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-6 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">总体评分</p>
              <p className="mt-2 text-5xl font-bold text-amber-600 dark:text-amber-400">
                {score.band.toFixed(1)}
              </p>
              <p className="text-sm text-slate-400">满分 5.0</p>
            </div>

            <div className="mb-6 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className="h-full rounded-full bg-amber-500 transition-all"
                style={{ width: `${overallPercent}%` }}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">内容</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.content_score.toFixed(1)}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${(score.content_score / maxScore) * 100}%` }}
                  />
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">组织</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.organization_score.toFixed(1)}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${(score.organization_score / maxScore) * 100}%` }}
                  />
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">语言</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.language_score.toFixed(1)}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-amber-500"
                    style={{ width: `${(score.language_score / maxScore) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950">
              <p className="font-medium text-amber-900 dark:text-amber-100">AI 评语</p>
              <p className="mt-2 text-sm text-amber-800 dark:text-amber-200 whitespace-pre-wrap">
                {score.feedback}
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-center gap-4">
            <button
              onClick={handleBackToTasks}
              className="flex items-center gap-2 rounded-xl border border-slate-200 px-6 py-3 font-medium text-slate-700 transition-all hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              再练一次
            </button>
            <a
              href="/ket"
              className="flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700"
            >
              返回 KET 主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (selectedTask) {
    const isOverLimit = wordCount > selectedTask.word_limit_max;
    const isUnderLimit = wordCount < selectedTask.word_limit_min;

    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <button
              onClick={handleBackToTasks}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </button>
            <div className="flex items-center gap-3">
              <Pen className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">写作练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {selectedTask.task_type === 'email' ? '邮件写作' : '故事写作'}
                </p>
              </div>
            </div>
          </header>

          <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 dark:bg-amber-950 dark:border-amber-800">
            <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
              {selectedTask.prompt}
            </p>
            <p className="mt-1 text-xs text-amber-700 dark:text-amber-300">
              字数要求: {selectedTask.word_limit_min}-{selectedTask.word_limit_max} 词
            </p>
          </div>

          <div className="mt-6">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="请在这里写作文..."
              className="min-h-[300px] w-full rounded-xl border border-slate-300 bg-white p-4 text-sm leading-relaxed focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-200 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:focus:border-amber-500"
            />
          </div>

          <div className="mt-4 flex items-center justify-between">
            <span
              className={cn(
                'text-sm',
                isOverLimit
                  ? 'text-red-600 font-medium'
                  : isUnderLimit
                    ? 'text-amber-600'
                    : 'text-emerald-600'
              )}
            >
              {wordCount} / {selectedTask.word_limit_min}-{selectedTask.word_limit_max} 词
              {isOverLimit && ' (超出上限)'}
              {isUnderLimit && wordCount > 0 && ' (未达下限)'}
            </span>
            <button
              onClick={handleSubmit}
              disabled={wordCount === 0 || submitMutation.isPending}
              className={cn(
                'rounded-xl bg-amber-600 px-6 py-2 text-sm font-medium text-white transition-all',
                wordCount > 0 && !submitMutation.isPending
                  ? 'hover:bg-amber-700'
                  : 'cursor-not-allowed opacity-50'
              )}
            >
              {submitMutation.isPending ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  评分中...
                </span>
              ) : (
                '提交评分'
              )}
            </button>
          </div>

          {submitMutation.isError && (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
              <p className="text-sm text-red-700 dark:text-red-300">
                提交失败，请稍后再试
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <header className="mb-6 flex items-center gap-4">
          <a
            href="/ket"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
          >
            <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
          </a>
          <div className="flex items-center gap-3">
            <Pen className="h-7 w-7 text-amber-600 dark:text-amber-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">写作练习</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">选择写作任务</p>
            </div>
          </div>
        </header>

        <div className="space-y-4">
          {tasks.map((task) => (
            <button
              key={task.id}
              onClick={() => setSelectedTask(task)}
              className="w-full rounded-2xl border border-slate-200 bg-white p-6 text-left transition-all hover:border-amber-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <span className="inline-block rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                    {task.task_type === 'email' ? '邮件' : '故事'}
                  </span>
                  <p className="mt-3 text-slate-900 dark:text-white">{task.prompt}</p>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    字数要求: {task.word_limit_min}-{task.word_limit_max} 词
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}