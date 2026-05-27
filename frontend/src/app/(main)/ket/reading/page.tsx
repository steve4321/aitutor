'use client';

import { useState } from 'react';
import { BookOpen, ChevronLeft, ChevronRight, CheckCircle2, X, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ReadingQuestion {
  id: string;
  passage: string;
  question: string;
  options: string[];
  correctIndex: number;
}

const SAMPLE_PASSAGE = `Last weekend, my family went to the beach. It was a beautiful sunny day. We arrived early in the morning and found a nice spot near the water.

We brought a lot of food for our picnic. There were sandwiches, fruits, and cold drinks. My mother also made some cookies. They were delicious!

I played in the water with my sister. The waves were not too big, so it was safe. We built a big sandcastle near our umbrella. My father helped us make towers and walls.

In the afternoon, we saw some dolphins! They were swimming near the shore. Everyone was excited to see them. We took many photos.

We stayed at the beach until sunset. It was one of the best weekends ever. We are planning to go back next month.`;

const QUESTIONS: ReadingQuestion[] = [
  {
    id: '1',
    passage: SAMPLE_PASSAGE,
    question: 'What did the family do last weekend?',
    options: ['Went to the mountains', 'Went to the beach', 'Stayed at home', 'Visited grandparents'],
    correctIndex: 1,
  },
  {
    id: '2',
    passage: SAMPLE_PASSAGE,
    question: 'What time did they arrive at the beach?',
    options: ['Late at night', 'Early in the morning', 'In the afternoon', 'In the evening'],
    correctIndex: 1,
  },
  {
    id: '3',
    passage: SAMPLE_PASSAGE,
    question: 'What did they NOT bring for the picnic?',
    options: ['Sandwiches', 'Fruits', 'Hot drinks', 'Cookies'],
    correctIndex: 2,
  },
  {
    id: '4',
    passage: SAMPLE_PASSAGE,
    question: 'What did they see in the afternoon?',
    options: ['Sharks', 'Whales', 'Dolphins', 'Seals'],
    correctIndex: 2,
  },
  {
    id: '5',
    passage: SAMPLE_PASSAGE,
    question: 'How was the day according to the passage?',
    options: ['Terrible', 'Just okay', 'One of the best weekends', 'Very boring'],
    correctIndex: 2,
  },
];

export default function ReadingPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [answers, setAnswers] = useState<Record<string, number>>({});

  const question = QUESTIONS[currentIndex];
  const isCorrect = selectedAnswer === question.correctIndex;
  const isAnswered = selectedAnswer !== null;

  const handleSubmit = () => {
    if (selectedAnswer === null) return;
    setAnswers((prev) => ({ ...prev, [question.id]: selectedAnswer }));
    setShowResult(true);
  };

  const handleNext = () => {
    if (currentIndex < QUESTIONS.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      const prevAnswer = answers[QUESTIONS[currentIndex - 1].id];
      setSelectedAnswer(prevAnswer ?? null);
      setShowResult(prevAnswer !== undefined);
    }
  };

  const correctCount = Object.entries(answers).filter(
    ([qid, ans]) => ans === QUESTIONS.find((q) => q.id === qid)?.correctIndex
  ).length;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
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
              <p className="text-sm text-slate-500 dark:text-slate-400">
                第 {currentIndex + 1} / {QUESTIONS.length} 题
              </p>
            </div>
          </div>
        </header>

        <div className="mb-6 flex h-2 gap-1">
          {QUESTIONS.map((q, i) => (
            <div
              key={q.id}
              className={cn(
                'h-full flex-1 rounded-full transition-all',
                answers[q.id] !== undefined
                  ? QUESTIONS.find((qq) => qq.id === q.id)?.correctIndex === answers[q.id]
                    ? 'bg-emerald-500'
                    : 'bg-rose-500'
                  : i === currentIndex
                    ? 'bg-blue-500'
                    : 'bg-slate-200 dark:bg-slate-700'
              )}
            />
          ))}
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
            阅读短文并回答问题
          </h2>
          <p className="whitespace-pre-line text-sm leading-relaxed text-slate-600 dark:text-slate-300">
            {question.passage}
          </p>
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-4 text-lg font-medium text-slate-900 dark:text-white">
            {question.question}
          </h3>
          <div className="space-y-3">
            {question.options.map((option, i) => (
              <button
                key={i}
                onClick={() => !showResult && setSelectedAnswer(i)}
                disabled={showResult}
                className={cn(
                  'flex w-full items-center gap-4 rounded-xl border-2 p-4 text-left transition-all',
                  showResult
                    ? i === question.correctIndex
                      ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
                      : i === selectedAnswer
                        ? 'border-rose-500 bg-rose-50 dark:bg-rose-900/30'
                        : 'border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800'
                    : selectedAnswer === i
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-700 hover:border-slate-600'
                )}
              >
                <span
                  className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium',
                    showResult
                      ? i === question.correctIndex
                        ? 'bg-emerald-500 text-white'
                        : i === selectedAnswer
                          ? 'bg-rose-500 text-white'
                          : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                      : selectedAnswer === i
                        ? 'bg-blue-500 text-white'
                        : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                  )}
                >
                  {String.fromCharCode(65 + i)}
                </span>
                <span className="flex-1 text-slate-700 dark:text-slate-200">{option}</span>
                {showResult && i === question.correctIndex && (
                  <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                )}
                {showResult && i === selectedAnswer && i !== question.correctIndex && (
                  <X className="h-6 w-6 text-rose-500" />
                )}
              </button>
            ))}
          </div>
        </div>

        {showResult && (
          <div
            className={cn(
              'mb-6 rounded-xl p-4',
              isCorrect
                ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
                : 'bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'
            )}
          >
            <div className="flex items-center gap-2 font-semibold">
              {isCorrect ? (
                <>
                  <CheckCircle2 className="h-5 w-5" />
                  回答正确！
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5" />
                  回答错误。正确答案是 {String.fromCharCode(65 + question.correctIndex)}.
                </>
              )}
            </div>
          </div>
        )}

        <div className="flex gap-4">
          <button
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <ChevronLeft className="h-5 w-5" />
            上一题
          </button>
          {!showResult ? (
            <button
              onClick={handleSubmit}
              disabled={selectedAnswer === null}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 font-medium text-white transition-all hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              提交答案
            </button>
          ) : currentIndex < QUESTIONS.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 font-medium text-white transition-all hover:bg-blue-700"
            >
              下一题
              <ChevronRight className="h-5 w-5" />
            </button>
          ) : (
            <a
              href="/ket"
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-medium text-white transition-all hover:bg-emerald-700"
            >
              完成练习 ({correctCount}/{QUESTIONS.length})
            </a>
          )}
        </div>
      </div>
    </div>
  );
}