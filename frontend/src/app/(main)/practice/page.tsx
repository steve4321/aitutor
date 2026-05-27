'use client';

import { useState } from 'react';
import { BookOpen, Calculator, Target, Clock, ChevronRight, Play } from 'lucide-react';
import { cn } from '@/lib/utils';

type Subject = 'math' | 'english';
type Difficulty = 1 | 2 | 3 | 4 | 5;

interface PracticeTopic {
  id: string;
  name: string;
  problemCount: number;
}

const MATH_TOPICS: PracticeTopic[] = [
  { id: 'algebra', name: '代数', problemCount: 24 },
  { id: 'geometry', name: '几何', problemCount: 18 },
  { id: 'number-theory', name: '数论', problemCount: 12 },
  { id: 'combinatorics', name: '组合数学', problemCount: 15 },
  { id: 'statistics', name: '统计与概率', problemCount: 10 },
];

const ENGLISH_TOPICS: PracticeTopic[] = [
  { id: 'vocabulary', name: '词汇', problemCount: 30 },
  { id: 'grammar', name: '语法', problemCount: 25 },
  { id: 'reading', name: '阅读理解', problemCount: 20 },
  { id: 'writing', name: '写作', problemCount: 15 },
];

export default function PracticePage() {
  const [subject, setSubject] = useState<Subject>('math');
  const [difficulty, setDifficulty] = useState<Difficulty | null>(null);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);

  const topics = subject === 'math' ? MATH_TOPICS : ENGLISH_TOPICS;

  const toggleTopic = (topicId: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topicId)
        ? prev.filter((id) => id !== topicId)
        : [...prev, topicId]
    );
  };

  const toggleDifficulty = (d: Difficulty) => {
    setDifficulty((prev) => (prev === d ? null : d));
  };

  const handleStartPractice = () => {
    console.log('Starting practice with:', { subject, difficulty, selectedTopics });
  };

  const totalProblems = selectedTopics.reduce(
    (sum, topicId) => sum + (topics.find((t) => t.id === topicId)?.problemCount || 0),
    0
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">练习</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            选择科目和难度，开始针对性练习
          </p>
        </header>

        <section className="mb-8">
          <h2 className="mb-4 text-lg font-semibold text-slate-700 dark:text-slate-200">
            选择科目
          </h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <button
              onClick={() => {
                setSubject('math');
                setSelectedTopics([]);
              }}
              className={cn(
                'flex flex-col items-center gap-3 rounded-xl border-2 p-6 transition-all',
                subject === 'math'
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                  : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800'
              )}
            >
              <Calculator
                className={cn(
                  'h-10 w-10',
                  subject === 'math'
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-slate-400 dark:text-slate-500'
                )}
              />
              <span
                className={cn(
                  'font-medium',
                  subject === 'math'
                    ? 'text-blue-700 dark:text-blue-300'
                    : 'text-slate-600 dark:text-slate-400'
                )}
              >
                数学
              </span>
            </button>

            <button
              onClick={() => {
                setSubject('english');
                setSelectedTopics([]);
              }}
              className={cn(
                'flex flex-col items-center gap-3 rounded-xl border-2 p-6 transition-all',
                subject === 'english'
                  ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
                  : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800'
              )}
            >
              <BookOpen
                className={cn(
                  'h-10 w-10',
                  subject === 'english'
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-slate-400 dark:text-slate-500'
                )}
              />
              <span
                className={cn(
                  'font-medium',
                  subject === 'english'
                    ? 'text-emerald-700 dark:text-emerald-300'
                    : 'text-slate-600 dark:text-slate-400'
                )}
              >
                英语
              </span>
            </button>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-lg font-semibold text-slate-700 dark:text-slate-200">
            选择难度
          </h2>
          <div className="flex flex-wrap gap-3">
            {([1, 2, 3, 4, 5] as Difficulty[]).map((d) => (
              <button
                key={d}
                onClick={() => toggleDifficulty(d)}
                className={cn(
                  'rounded-lg px-4 py-2 font-medium transition-all',
                  difficulty === d
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                )}
              >
                {d === 1 && '入门'}
                {d === 2 && '基础'}
                {d === 3 && '进阶'}
                {d === 4 && '挑战'}
                {d === 5 && '竞赛'}
              </button>
            ))}
          </div>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-lg font-semibold text-slate-700 dark:text-slate-200">
            选择专题
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {topics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => toggleTopic(topic.id)}
                className={cn(
                  'flex items-center justify-between rounded-lg border px-4 py-3 transition-all',
                  selectedTopics.includes(topic.id)
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                    : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800'
                )}
              >
                <span
                  className={cn(
                    'text-sm font-medium',
                    selectedTopics.includes(topic.id)
                      ? 'text-blue-700 dark:text-blue-300'
                      : 'text-slate-700 dark:text-slate-300'
                  )}
                >
                  {topic.name}
                </span>
                <span
                  className={cn(
                    'text-xs',
                    selectedTopics.includes(topic.id)
                      ? 'text-blue-500 dark:text-blue-400'
                      : 'text-slate-400 dark:text-slate-500'
                  )}
                >
                  {topic.problemCount}题
                </span>
              </button>
            ))}
          </div>
        </section>

        <section className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-slate-400" />
                <span className="text-slate-600 dark:text-slate-400">题目数量</span>
              </div>
              <span className="text-2xl font-bold text-slate-900 dark:text-white">
                {totalProblems}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-slate-400" />
              <span className="text-slate-600 dark:text-slate-400">预计</span>
              <span className="font-medium text-slate-900 dark:text-white">
                {Math.max(5, Math.round(totalProblems * 1.5))}分钟
              </span>
            </div>
          </div>

          {selectedTopics.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {selectedTopics.map((topicId) => {
                const topic = topics.find((t) => t.id === topicId);
                return (
                  <span
                    key={topicId}
                    className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/50 dark:text-blue-300"
                  >
                    {topic?.name}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleTopic(topicId);
                      }}
                      className="ml-1 hover:text-blue-900 dark:hover:text-blue-200"
                    >
                      ×
                    </button>
                  </span>
                );
              })}
            </div>
          )}
        </section>

        <button
          onClick={handleStartPractice}
          disabled={selectedTopics.length === 0}
          className={cn(
            'flex w-full items-center justify-center gap-2 rounded-xl py-4 font-semibold transition-all',
            selectedTopics.length > 0
              ? 'bg-gradient-to-r from-blue-600 to-violet-600 text-white hover:from-blue-700 hover:to-violet-700'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed dark:bg-slate-700 dark:text-slate-500'
          )}
        >
          <Play className="h-5 w-5" />
          开始练习
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}