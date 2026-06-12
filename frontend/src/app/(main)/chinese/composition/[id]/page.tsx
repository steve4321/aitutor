'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useQuery, useMutation } from '@tanstack/react-query';
import { FileText, ChevronLeft, Loader2, Send, RefreshCw, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface CompositionTask {
  id: string;
  title: string;
  writing_type: string;
  prompt: string;
  min_chars: number;
  max_chars: number;
  target_chars?: number;
}

interface CompositionScoreResponse {
  content_score: number;
  structure_score: number;
  language_score: number;
  handwriting_score: number;
  total_score: number;
  char_count: number;
  meets_word_count: boolean;
  feedback: {
    strengths: string[];
    improvements: string[];
    highlights: Array<{ text: string; comment: string }>;
    specific_suggestions: Array<{ original: string; suggestion: string; reason: string }>;
  };
  revision_plan: {
    priority: string;
    action_items: string[];
    encouragement: string;
  };
}

export default function CompositionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [content, setContent] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    params.then((p) => setTaskId(p.id));
  }, [params]);

  const { data: task, isLoading: taskLoading } = useQuery({
    queryKey: ['chinese', 'composition', 'task', taskId],
    queryFn: () => api.get<CompositionTask>(`/chinese/composition/tasks/${taskId}`),
    enabled: !!taskId,
  });

  const submitMutation = useMutation({
    mutationFn: (body: { task_id: string; content: string; char_count: number }) =>
      api.post<CompositionScoreResponse>('/chinese/composition/submit', body),
    onSuccess: () => {
      setSubmitted(true);
    },
  });

  const handleSubmit = () => {
    if (!task) return;
    submitMutation.mutate({
      task_id: task.id,
      content,
      char_count: wordCount,
    });
  };

  const handleReset = () => {
    setContent('');
    setSubmitted(false);
  };

  const wordCount = content.length;

  if (taskLoading) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <Link
              href="/chinese/composition"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </Link>
            <div className="flex items-center gap-3">
              <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">加载题目中...</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Loader2 className="h-8 w-8 animate-spin text-amber-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">题目加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <Link
              href="/chinese/composition"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </Link>
            <div className="flex items-center gap-3">
              <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">题目未找到</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <FileText className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">题目未找到</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              请返回重新选择作文题目
            </p>
            <Link
              href="/chinese/composition"
              className="flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700"
            >
              返回作文列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (submitted && submitMutation.data) {
    const score = submitMutation.data;
    const maxContent = 40;
    const maxStructure = 20;
    const maxLanguage = 30;
    const maxHandwriting = 10;
    const maxTotal = 100;

    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <button
              onClick={handleReset}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </button>
            <div className="flex items-center gap-3">
              <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">评分结果</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">{task.title}</p>
              </div>
            </div>
          </header>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-6 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">总体评分</p>
              <p className="mt-2 text-5xl font-bold text-amber-600 dark:text-amber-400">
                {score.total_score}
              </p>
              <p className="text-sm text-slate-400">满分 {maxTotal}</p>
            </div>

            <div className="mb-6 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className="h-full rounded-full bg-amber-500 transition-all"
                style={{ width: `${(score.total_score / maxTotal) * 100}%` }}
              />
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">内容 (40)</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.content_score}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${(score.content_score / maxContent) * 100}%` }}
                  />
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">结构 (20)</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.structure_score}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${(score.structure_score / maxStructure) * 100}%` }}
                  />
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">语言 (30)</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.language_score}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-amber-500"
                    style={{ width: `${(score.language_score / maxLanguage) * 100}%` }}
                  />
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                <p className="text-xs text-slate-500 dark:text-slate-400">书写 (10)</p>
                <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">
                  {score.handwriting_score}
                </p>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className="h-full rounded-full bg-purple-500"
                    style={{ width: `${(score.handwriting_score / maxHandwriting) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {score.feedback.strengths.length > 0 && (
              <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-950">
                <p className="font-medium text-emerald-900 dark:text-emerald-100">优点</p>
                <ul className="mt-2 space-y-1">
                  {score.feedback.strengths.map((strength, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-emerald-800 dark:text-emerald-200">
                      <CheckCircle className="mt-0.5 h-4 w-4 shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {score.feedback.improvements.length > 0 && (
              <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950">
                <p className="font-medium text-amber-900 dark:text-amber-100">改进建议</p>
                <ul className="mt-2 space-y-1">
                  {score.feedback.improvements.map((improvement, i) => (
                    <li key={i} className="text-sm text-amber-800 dark:text-amber-200">
                      {i + 1}. {improvement}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {score.revision_plan.encouragement && (
              <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  {score.revision_plan.encouragement}
                </p>
              </div>
            )}
          </div>

          <div className="mt-6 flex justify-center gap-4">
            <button
              onClick={handleReset}
              className="flex items-center gap-2 rounded-xl border border-slate-200 px-6 py-3 font-medium text-slate-700 transition-all hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <RefreshCw className="h-4 w-4" />
              重新写作
            </button>
            <Link
              href="/chinese/composition"
              className="flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700"
            >
              返回作文列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const isOverLimit = wordCount > task.max_chars;
  const isUnderLimit = wordCount < task.min_chars;
  const targetChars = task.target_chars || Math.floor((task.min_chars + task.max_chars) / 2);

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <header className="mb-6 flex items-center gap-4">
          <Link
              href="/chinese/composition"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </Link>
          <div className="flex items-center gap-3">
            <FileText className="h-7 w-7 text-amber-600 dark:text-amber-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">作文练习</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">{task.title}</p>
            </div>
          </div>
        </header>

        <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 dark:bg-amber-950 dark:border-amber-800">
          <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
            {task.prompt}
          </p>
          <p className="mt-1 text-xs text-amber-700 dark:text-amber-300">
            字数要求: {task.min_chars}-{task.max_chars}字（目标{targetChars}字）
          </p>
        </div>

        <div className="mt-6">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="请在这里写作文..."
            className="min-h-[400px] w-full rounded-xl border border-slate-300 bg-white p-4 text-sm leading-relaxed focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-200 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:focus:border-amber-500"
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
            {wordCount} / {task.min_chars}-{task.max_chars}字
            {isOverLimit && ' (超出上限)'}
            {isUnderLimit && wordCount > 0 && ' (未达下限)'}
            {!isUnderLimit && !isOverLimit && wordCount >= task.min_chars && ' (已达标)'}
          </span>
          <button
            onClick={handleSubmit}
            disabled={wordCount === 0 || submitMutation.isPending}
            className={cn(
              'flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-2 text-sm font-medium text-white transition-all',
              wordCount > 0 && !submitMutation.isPending
                ? 'hover:bg-amber-700'
                : 'cursor-not-allowed opacity-50'
            )}
          >
            {submitMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                评分中...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                提交评分
              </>
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