'use client';

import { useState } from 'react';
import { Pen, ChevronLeft, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WritingTask {
  id: string;
  type: 'email' | 'story' | 'article';
  title: string;
  prompt: string;
  wordLimit: number;
  example?: string;
}

const TASKS: WritingTask[] = [
  {
    id: '1',
    type: 'email',
    title: '写一封电子邮件',
    prompt: '你的英国朋友 Tom 想要了解你最近的学校生活。请给他写一封邮件，介绍：\n1. 你最喜欢的科目\n2. 你的课后活动\n3. 你最近参加的学校活动\n\n邮件需要 25-35 词。',
    wordLimit: 35,
    example: 'Dear Tom,\nI am happy to share my school life with you. My favorite subject is English because...',
  },
  {
    id: '2',
    type: 'story',
    title: '看图写故事',
    prompt: '根据以下图片，写一个不超过 35 词的故事。故事需要包含图中发生的事以及你的感受。',
    wordLimit: 35,
  },
];

export default function WritingPage() {
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [text, setText] = useState('');
  const [showExample, setShowExample] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState<number | null>(null);

  const task = TASKS[currentTaskIndex];
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const isOverLimit = wordCount > task.wordLimit;

  const handleSubmit = () => {
    setSubmitted(true);
    setScore(Math.min(5, Math.round(3 + Math.random() * 2)));
  };

  const handleNext = () => {
    if (currentTaskIndex < TASKS.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
      setText('');
      setSubmitted(false);
      setScore(null);
      setShowExample(false);
    }
  };

  const handleReset = () => {
    setText('');
    setSubmitted(false);
    setScore(null);
  };

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
              <p className="text-sm text-slate-500 dark:text-slate-400">
                第 {currentTaskIndex + 1} / {TASKS.length} 题
              </p>
            </div>
          </div>
        </header>

        <div className="mb-6 flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <div className="flex items-center gap-3">
            <Clock className="h-5 w-5 text-slate-400" />
            <span className="text-sm text-slate-600 dark:text-slate-300">建议时间</span>
            <span className="font-medium text-slate-900 dark:text-white">10 分钟</span>
          </div>
          <div
            className={cn(
              'flex items-center gap-2 text-sm font-medium',
              isOverLimit ? 'text-rose-500' : 'text-slate-500 dark:text-slate-400'
            )}
          >
            <span>
              {wordCount} / {task.wordLimit} 词
            </span>
            {isOverLimit && <AlertCircle className="h-4 w-4" />}
          </div>
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-2 font-semibold text-slate-900 dark:text-white">{task.title}</h2>
          <p className="whitespace-pre-line text-sm leading-relaxed text-slate-600 dark:text-slate-300">
            {task.prompt}
          </p>

          {task.type === 'story' && (
            <div className="mt-4 flex h-40 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-700">
              <span className="text-slate-400">图片区域</span>
            </div>
          )}

          {task.example && (
            <button
              onClick={() => setShowExample(!showExample)}
              className="mt-4 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
            >
              {showExample ? '隐藏范文' : '查看范文'}
            </button>
          )}

          {showExample && task.example && (
            <div className="mt-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700 dark:border-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
              {task.example}
            </div>
          )}
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <textarea
            value={text}
            onChange={(e) => !submitted && setText(e.target.value)}
            placeholder="在这里输入你的写作内容..."
            disabled={submitted}
            className={cn(
              'min-h-[200px] w-full resize-none rounded-xl border-2 bg-transparent p-4 text-slate-700 dark:text-slate-200',
              isOverLimit
                ? 'border-rose-300 focus:border-rose-500'
                : 'border-slate-200 focus:border-blue-500',
              'focus:outline-none transition-colors'
            )}
          />
        </div>

        {submitted && score !== null && (
          <div className="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-900/30">
            <div className="flex items-center gap-2 font-semibold text-emerald-700 dark:text-emerald-300">
              <CheckCircle2 className="h-5 w-5" />
              提交成功！得分：{score}/5
            </div>
            <p className="mt-2 text-sm text-emerald-600 dark:text-emerald-400">
              你的作文已提交，老师会尽快批改。
            </p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            onClick={handleReset}
            disabled={!text || submitted}
            className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 py-3 px-6 font-medium text-slate-600 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            重置
          </button>
          {submitted ? (
            currentTaskIndex < TASKS.length - 1 ? (
              <button
                onClick={handleNext}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 font-medium text-white transition-all hover:bg-blue-700"
              >
                下一题
              </button>
            ) : (
              <a
                href="/ket"
                className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-medium text-white transition-all hover:bg-emerald-700"
              >
                完成练习
              </a>
            )
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!text || isOverLimit}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-amber-600 py-3 font-medium text-white transition-all hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              提交作文
            </button>
          )}
        </div>
      </div>
    </div>
  );
}