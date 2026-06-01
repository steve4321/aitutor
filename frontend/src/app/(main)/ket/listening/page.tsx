'use client';

import { useState } from 'react';
import { Headphones, ChevronLeft, Play, Pause, Volume2, CheckCircle2, X, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ListeningQuestion {
  id: string;
  audioText?: string;
  question: string;
  options: string[];
  correctIndex: number;
}

const QUESTIONS: ListeningQuestion[] = [
  {
    id: '1',
    audioText: 'Man: How do you come to school every day?\nWoman: I usually take the bus. Sometimes my father drives me.\nMan: What about when it rains?\nWoman: Then my mother always takes me. She says it is safer.',
    question: 'How does the woman usually come to school?',
    options: ['By car', 'By bus', 'By bike', 'On foot'],
    correctIndex: 1,
  },
  {
    id: '2',
    audioText: 'Woman: What time does the movie start?\nMan: It starts at 7:30. But we should be there early.\nWoman: Why?\nMan: Because it will be very busy on Saturday night.',
    question: 'When should they arrive at the movie theater?',
    options: ['At 7:00', 'At 7:30', 'Before 7:30', 'After 7:30'],
    correctIndex: 2,
  },
  {
    id: '3',
    audioText: 'Girl: I want to buy a new jacket. Do you know any good shops?\nBoy: Yes, there is a big shop on Main Street.\nGirl: Is it expensive?\nBoy: Not really. They have very good prices. And everything is on sale this week!',
    question: 'What is special about the shop this week?',
    options: ['It is closed', 'It has a sale', 'It is new', 'It is expensive'],
    correctIndex: 1,
  },
];

export default function ListeningPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [answers, setAnswers] = useState<Record<string, number>>({});

  const question = QUESTIONS[currentIndex];
  const isCorrect = selectedAnswer === question.correctIndex;

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSubmit = () => {
    if (selectedAnswer === null) return;
    setAnswers((prev) => ({ ...prev, [question.id]: selectedAnswer }));
    setShowResult(true);
    setIsPlaying(false);
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
            <Headphones className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">听力练习</h1>
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
                    ? 'bg-emerald-500'
                    : 'bg-slate-200 dark:bg-slate-700'
              )}
            />
          ))}
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <div className="mb-6 flex items-center justify-center gap-4">
            <button
              onClick={togglePlay}
              className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg transition-all hover:bg-emerald-700 hover:scale-105"
            >
              {isPlaying ? (
                <Pause className="h-8 w-8" />
              ) : (
                <Play className="h-8 w-8 pl-1" />
              )}
            </button>
          </div>

          <div className="mb-4 flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400">
            <Volume2 className="h-5 w-5" />
            <span className="text-sm">点击播放听力内容</span>
          </div>

          {isPlaying && (
            <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
              <p className="whitespace-pre-line text-sm italic text-slate-600 dark:text-slate-300">
                {question.audioText}
              </p>
            </div>
          )}
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
                      ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
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
                        ? 'bg-emerald-500 text-white'
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
            上一题
          </button>
          {!showResult ? (
            <button
              onClick={handleSubmit}
              disabled={selectedAnswer === null}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-medium text-white transition-all hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              提交答案
            </button>
          ) : currentIndex < QUESTIONS.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-medium text-white transition-all hover:bg-emerald-700"
            >
              下一题
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