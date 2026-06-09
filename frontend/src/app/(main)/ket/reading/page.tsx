'use client';

import { BookOpen, ChevronLeft } from 'lucide-react';

export default function ReadingPage() {
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
            <BookOpen className="h-7 w-7 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">阅读理解</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">KET 阅读练习</p>
            </div>
          </div>
        </header>

        <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-blue-50 dark:bg-blue-950">
            <BookOpen className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">阅读题库开发中</h2>
          <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
            阅读理解题库正在紧张开发中<br />
            请稍后再来练习
          </p>
          <a
            href="/ket"
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-medium text-white transition-all hover:bg-blue-700"
          >
            返回 KET 主页
          </a>
        </div>
      </div>
    </div>
  );
}