'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  ArrowLeft,
  Calendar,
  Clock,
  Target,
  TrendingUp,
  TrendingDown,
  BarChart3,
  AlertTriangle,
  Lightbulb,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import type { ParentWeeklyReport, LinkedChild } from '@/types/parent';

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

function getWeekStart(offsetWeeks: number = 0): string {
  const now = new Date();
  const day = now.getDay();
  const diff = now.getDate() - day + (day === 0 ? -6 : 1) - offsetWeeks * 7;
  const monday = new Date(now.setDate(diff));
  return monday.toISOString().split('T')[0];
}

function formatWeekRange(weekStart: string): string {
  const start = new Date(weekStart);
  const end = new Date(start);
  end.setDate(end.getDate() + 6);
  return `${start.getMonth() + 1}月${start.getDate()}日 - ${end.getMonth() + 1}月${end.getDate()}日`;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-8 h-12 w-48 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="mb-6 flex gap-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-10 w-24 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
          ))}
        </div>
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
          ))}
        </div>
        <div className="h-64 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  );
}

function NoDataState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <BarChart3 className="mb-4 h-16 w-16 text-slate-300 dark:text-slate-600" />
      <p className="text-lg font-medium text-slate-600 dark:text-slate-400">暂无报告数据</p>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-500">孩子开始学习后查看每周报告</p>
    </div>
  );
}

export default function ParentReportsPage() {
  const [weekOffset, setWeekOffset] = useState(0);
  const [selectedChildId, setSelectedChildId] = useState<string | null>(null);

  const { data: children } = useQuery<LinkedChild[]>({
    queryKey: ['parent-children'],
    queryFn: () => api.get<LinkedChild[]>('/parent/children'),
  });

  const activeChildId = selectedChildId ?? children?.[0]?.id;

  const weekStart = getWeekStart(weekOffset);

  const { data: report, isLoading: reportLoading } = useQuery<ParentWeeklyReport>({
    queryKey: ['parent-weekly-report', activeChildId, weekStart],
    queryFn: () =>
      api.get<ParentWeeklyReport>(`/parent/children/${activeChildId}/report`, {
        week_start: weekStart,
      }),
    enabled: !!activeChildId,
  });

  const isLoading = reportLoading;

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const totalAccuracy =
    report && report.total_problems > 0
      ? Math.round((report.total_correct / report.total_problems) * 100)
      : 0;

  const xpChange = report?.previous_week_comparison?.xp_change ?? 0;
  const timeChange = report?.previous_week_comparison?.time_change ?? 0;
  const accuracyChange = report?.previous_week_comparison?.accuracy_change ?? 0;

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <Link
            href={ROUTES.PARENT}
            className="mb-4 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
          >
            <ArrowLeft className="h-4 w-4" />
            返回
          </Link>
          <div className="flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-violet-600 dark:text-violet-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">学习报告</h1>
              <p className="text-slate-600 dark:text-slate-400">查看孩子的每周学习情况</p>
            </div>
          </div>
        </header>

        <div className="mb-6 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={() => setWeekOffset((w) => w + 1)}
              disabled={weekOffset >= 4}
              className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              上一周
            </button>
            <button
              onClick={() => setWeekOffset((w) => Math.max(0, w - 1))}
              disabled={weekOffset === 0}
              className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              下一周
            </button>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Calendar className="h-4 w-4" />
            {formatWeekRange(weekStart)}
          </div>
        </div>

        {children && children.length > 1 && (
          <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
            {children.map((child) => (
              <button
                key={child.id}
                onClick={() => setSelectedChildId(child.id)}
                className={cn(
                  'shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-all',
                  activeChildId === child.id
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                )}
              >
                {child.name}
              </button>
            ))}
          </div>
        )}

        {!report || report.total_sessions === 0 ? (
          <NoDataState />
        ) : (
          <>
            <section className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 dark:bg-amber-900/30">
                  <TrendingUp className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">获得 XP</p>
                <div className="mt-1 flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {report.total_xp}
                  </p>
                  {xpChange !== 0 && (
                    <span
                      className={cn(
                        'flex items-center text-xs',
                        xpChange > 0 ? 'text-emerald-600' : 'text-rose-600'
                      )}
                    >
                      {xpChange > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {Math.abs(xpChange)}
                    </span>
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 dark:bg-blue-900/30">
                  <Target className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">完成题目</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {report.total_problems}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 dark:bg-emerald-900/30">
                  <BarChart3 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">正确率</p>
                <div className="mt-1 flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalAccuracy}%</p>
                  {accuracyChange !== 0 && (
                    <span
                      className={cn(
                        'flex items-center text-xs',
                        accuracyChange > 0 ? 'text-emerald-600' : 'text-rose-600'
                      )}
                    >
                      {accuracyChange > 0 ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      {Math.abs(accuracyChange)}%
                    </span>
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 dark:bg-violet-900/30">
                  <Clock className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">学习时间</p>
                <div className="mt-1 flex items-baseline gap-1">
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {report.total_time_minutes}
                  </p>
                  <span className="text-sm text-slate-500 dark:text-slate-400">分钟</span>
                  {timeChange !== 0 && (
                    <span
                      className={cn(
                        'flex items-center text-xs',
                        timeChange > 0 ? 'text-emerald-600' : 'text-rose-600'
                      )}
                    >
                      {timeChange > 0 ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      {Math.abs(timeChange)}分钟
                    </span>
                  )}
                </div>
              </div>
            </section>

            {report.concerns && report.concerns.length > 0 && (
              <section className="mb-8 rounded-2xl border border-rose-200 bg-rose-50 p-6 dark:border-rose-800 dark:bg-rose-900/20">
                <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-rose-700 dark:text-rose-400">
                  <AlertTriangle className="h-5 w-5" />
                  需要关注
                </h2>
                <ul className="space-y-2">
                  {report.concerns.map((concern, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-rose-700 dark:text-rose-300">
                      <span className="mt-1 text-rose-500">•</span>
                      {concern}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {report.insights && report.insights.length > 0 && (
              <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
                <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                  <Lightbulb className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  AI 分析建议
                </h2>
                <ul className="space-y-3">
                  {report.insights.map((insight, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                      <span className="text-sm text-slate-600 dark:text-slate-300">{insight}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {report.mastery_changes && Object.keys(report.mastery_changes).length > 0 && (
              <section className="mb-8 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
                <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
                  <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                    知识掌握变化
                  </h2>
                </div>
                <div className="divide-y divide-slate-100 px-6 py-4 dark:divide-slate-700">
                  {Object.entries(report.mastery_changes)
                    .sort(([, a], [, b]) => b - a)
                    .map(([topic, change]) => (
                      <div key={topic} className="flex items-center justify-between py-3">
                        <span className="text-sm text-slate-700 dark:text-slate-300">{topic}</span>
                        <span
                          className={cn(
                            'flex items-center gap-1 text-sm font-medium',
                            change > 0
                              ? 'text-emerald-600 dark:text-emerald-400'
                              : change < 0
                                ? 'text-rose-600 dark:text-rose-400'
                                : 'text-slate-500 dark:text-slate-400'
                          )}
                        >
                          {change > 0 ? (
                            <TrendingUp className="h-4 w-4" />
                          ) : change < 0 ? (
                            <TrendingDown className="h-4 w-4" />
                          ) : null}
                          {change > 0 ? '+' : ''}
                          {change.toFixed(1)}%
                        </span>
                      </div>
                    ))}
                </div>
              </section>
            )}

            <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                <Clock className="h-5 w-5 text-slate-400" />
                学习时间分布
              </h2>
              <div className="space-y-3">
                {report.subject_breakdown && Object.keys(report.subject_breakdown).length > 0 ? (
                  Object.entries(report.subject_breakdown).map(([subject, data]) => {
                    const maxTime = Math.max(
                      ...Object.values(report.subject_breakdown ?? {}).map((d) => d.total_time_minutes),
                      1
                    );
                    const colors =
                      subject === 'math'
                        ? 'bg-blue-500'
                        : subject === 'english'
                          ? 'bg-emerald-500'
                          : 'bg-amber-500';
                    return (
                      <div key={subject}>
                        <div className="mb-1 flex justify-between text-sm">
                          <span className="text-slate-600 dark:text-slate-300">
                            {subject === 'math'
                              ? '数学'
                              : subject === 'english'
                                ? '英语'
                                : subject === 'chinese'
                                  ? '语文'
                                  : subject}
                          </span>
                          <span className="text-slate-500 dark:text-slate-400">
                            {data.total_time_minutes}分钟
                          </span>
                        </div>
                        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                          <div
                            className={cn('h-full rounded-full transition-all', colors)}
                            style={{ width: `${(data.total_time_minutes / maxTime) * 100}%` }}
                          />
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-center text-sm text-slate-500 dark:text-slate-400">暂无数据</p>
                )}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}