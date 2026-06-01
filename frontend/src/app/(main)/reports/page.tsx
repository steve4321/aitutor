'use client';

import { useState } from 'react';
import { BarChart3, Clock, Target, TrendingUp, BookOpen, Calculator, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

type TimeRange = 'weekly' | 'monthly' | 'all';

interface DailyXP {
  day: string;
  xp: number;
}

interface SubjectStats {
  name: string;
  xp: number;
  problems: number;
  accuracy: number;
  color: string;
}

const SAMPLE_XP_DATA: DailyXP[] = [
  { day: '周一', xp: 120 },
  { day: '周二', xp: 85 },
  { day: '周三', xp: 150 },
  { day: '周四', xp: 90 },
  { day: '周五', xp: 200 },
  { day: '周六', xp: 180 },
  { day: '周日', xp: 160 },
];

const SUBJECT_STATS: SubjectStats[] = [
  { name: '数学', xp: 2450, problems: 156, accuracy: 78, color: 'blue' },
  { name: '英语', xp: 1820, problems: 124, accuracy: 82, color: 'emerald' },
];

export default function ReportsPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>('weekly');

  const totalXP = SAMPLE_XP_DATA.reduce((sum, d) => sum + d.xp, 0);
  const maxXP = Math.max(...SAMPLE_XP_DATA.map((d) => d.xp));
  const avgXP = Math.round(totalXP / SAMPLE_XP_DATA.length);

  const totalProblems = SUBJECT_STATS.reduce((sum, s) => sum + s.problems, 0);
  const totalAccuracy = Math.round(
    SUBJECT_STATS.reduce((sum, s) => sum + s.accuracy * s.problems, 0) / totalProblems
  );
  const totalTimeMinutes = Math.round(totalXP * 0.8);

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-violet-600 dark:text-violet-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">学习报告</h1>
              <p className="text-slate-600 dark:text-slate-400">追踪你的学习进度和表现</p>
            </div>
          </div>
        </header>

        <div className="mb-6 flex gap-2">
          {(['weekly', 'monthly', 'all'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={cn(
                'rounded-lg px-4 py-2 text-sm font-medium transition-all',
                timeRange === range
                  ? 'bg-violet-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
              )}
            >
              {range === 'weekly' && '本周'}
              {range === 'monthly' && '本月'}
              {range === 'all' && '全部'}
            </button>
          ))}
        </div>

        <section className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 dark:bg-amber-900/30">
              <Award className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">获得 XP</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalXP}</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 dark:bg-blue-900/30">
              <Target className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">完成题目</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalProblems}</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 dark:bg-emerald-900/30">
              <TrendingUp className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">正确率</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalAccuracy}%</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 dark:bg-violet-900/30">
              <Clock className="h-5 w-5 text-violet-600 dark:text-violet-400" />
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">学习时间</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalTimeMinutes}分钟</p>
          </div>
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-6 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
            <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            XP 统计
          </h2>
          <div className="mb-4 flex items-end justify-between gap-2">
            {SAMPLE_XP_DATA.map((data) => (
              <div key={data.day} className="flex flex-1 flex-col items-center gap-2">
                <div
                  className="w-full max-w-12 rounded-t-lg bg-gradient-to-t from-blue-600 to-violet-600 transition-all"
                  style={{ height: `${(data.xp / maxXP) * 120}px` }}
                />
                <span className="text-xs text-slate-500 dark:text-slate-400">{data.day}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-between border-t border-slate-100 pt-4 dark:border-slate-700">
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">总计</p>
              <p className="font-semibold text-slate-900 dark:text-white">{totalXP} XP</p>
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">日均</p>
              <p className="font-semibold text-slate-900 dark:text-white">{avgXP} XP</p>
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">最高</p>
              <p className="font-semibold text-slate-900 dark:text-white">{maxXP} XP</p>
            </div>
          </div>
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              科目 breakdown
            </h2>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {SUBJECT_STATS.map((subject) => (
              <div key={subject.name} className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center gap-4">
                  <div
                    className={cn(
                      'flex h-10 w-10 items-center justify-center rounded-xl',
                      subject.color === 'blue'
                        ? 'bg-blue-100 dark:bg-blue-900/30'
                        : 'bg-emerald-100 dark:bg-emerald-900/30'
                    )}
                  >
                    {subject.color === 'blue' ? (
                      <Calculator className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    ) : (
                      <BookOpen className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">{subject.name}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {subject.problems} 题 · {subject.accuracy}% 正确率
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-slate-900 dark:text-white">{subject.xp} XP</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
            <Clock className="h-5 w-5 text-slate-400" />
            学习时间分布
          </h2>
          <div className="space-y-3">
            <div>
              <div className="mb-1 flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">数学</span>
                <span className="text-slate-500 dark:text-slate-400">57%</span>
              </div>
              <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                <div className="h-full w-[57%] rounded-full bg-blue-500" />
              </div>
            </div>
            <div>
              <div className="mb-1 flex justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-300">英语</span>
                <span className="text-slate-500 dark:text-slate-400">43%</span>
              </div>
              <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                <div className="h-full w-[43%] rounded-full bg-emerald-500" />
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}