'use client';

import { BookOpen, Pen, Headphones, Mic, TrendingUp, Clock, Award, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

const SKILL_INFO = {
  reading: {
    icon: BookOpen,
    title: '阅读',
    color: 'blue',
    path: '/ket/reading',
  },
  writing: {
    icon: Pen,
    title: '写作',
    color: 'amber',
    path: '/ket/writing',
  },
  listening: {
    icon: Headphones,
    title: '听力',
    color: 'emerald',
    path: '/ket/listening',
  },
  speaking: {
    icon: Mic,
    title: '口语',
    color: 'rose',
    path: '/ket/speaking',
  },
};

const COLOR_CLASSES = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-950',
    border: 'border-blue-200 dark:border-blue-800',
    icon: 'text-blue-600 dark:text-blue-400',
    progress: 'bg-blue-500',
    text: 'text-blue-700 dark:text-blue-300',
  },
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
  rose: {
    bg: 'bg-rose-50 dark:bg-rose-950',
    border: 'border-rose-200 dark:border-rose-800',
    icon: 'text-rose-600 dark:text-rose-400',
    progress: 'bg-rose-500',
    text: 'text-rose-700 dark:text-rose-300',
  },
};

const SKILLS = ['reading', 'writing', 'listening', 'speaking'] as const;

export default function KETPage() {
  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <Award className="h-8 w-8 text-amber-500" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">KET 英语</h1>
              <p className="text-slate-600 dark:text-slate-400">Cambridge A2 Key 备考训练</p>
            </div>
          </div>
        </header>

        <section className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {SKILLS.map((skill) => {
            const info = SKILL_INFO[skill];
            const colors = COLOR_CLASSES[info.color as keyof typeof COLOR_CLASSES];
            const Icon = info.icon;

            return (
              <a
                key={skill}
                href={info.path}
                className={cn(
                  'group relative overflow-hidden rounded-2xl border p-6 transition-all hover:shadow-lg',
                  colors.bg,
                  colors.border
                )}
              >
                <Icon className={cn('mb-4 h-10 w-10', colors.icon)} />
                <h3 className="mb-1 font-semibold text-slate-900 dark:text-white">{info.title}</h3>
                <p className="mb-4 text-2xl font-bold text-slate-700 dark:text-slate-200">
                  —
                  <span className="text-sm font-normal text-slate-400">分</span>
                </p>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className={cn('h-full rounded-full transition-all', colors.progress)}
                    style={{ width: '0%' }}
                  />
                </div>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  0% 完成
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
          <div className="flex items-center justify-center py-8">
            <p className="text-center text-slate-500 dark:text-slate-400">暂无练习记录</p>
          </div>
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