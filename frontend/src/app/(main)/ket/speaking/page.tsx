'use client';

import { Mic, ChevronLeft } from 'lucide-react';

export default function SpeakingPage() {
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
            <Mic className="h-7 w-7 text-rose-600 dark:text-rose-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">口语练习</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">KET 口语练习</p>
            </div>
          </div>
        </header>

        <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-rose-50 dark:bg-rose-950">
            <Mic className="h-8 w-8 text-rose-600 dark:text-rose-400" />
          </div>
          <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">口语评测功能开发中</h2>
          <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
            口语评测功能正在紧张开发中<br />
            请稍后再来练习口语
          </p>
          <a
            href="/ket"
            className="flex items-center gap-2 rounded-xl bg-rose-600 px-6 py-3 font-medium text-white transition-all hover:bg-rose-700"
          >
            返回 KET 主页
          </a>
        </div>
      </div>
    </div>
  );
}