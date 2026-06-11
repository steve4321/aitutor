'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, ChevronLeft, CheckCircle, XCircle, ArrowRight, Loader2 } from 'lucide-react';
import { renderWithLatex } from '@/lib/render-content';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface KETQuestion {
  id: string;
  skill: string;
  level: string;
  question_type: string;
  prompt: string;
  audio_url: string | null;
  image_url: string | null;
  options: Record<string, string> | null;
  correct_answer: string;
  explanation: string | null;
  points: number;
}

interface KETQuestionListResponse {
  items: KETQuestion[];
  total: number;
  limit: number;
  offset: number;
}

interface QuizState {
  currentIndex: number;
  answers: Record<string, string>;
  submitted: Record<string, boolean>;
  showExplanation: Record<string, boolean>;
}

export default function ReadingPage() {
  const [quizState, setQuizState] = useState<QuizState>({
    currentIndex: 0,
    answers: {},
    submitted: {},
    showExplanation: {},
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['ket', 'questions', 'reading'],
    queryFn: () => api.get<KETQuestionListResponse>('/ket/questions', { skill: 'reading', limit: '20' }),
  });

  const questions = data?.items ?? [];
  const currentQuestion = questions[quizState.currentIndex];
  const isCurrentSubmitted = currentQuestion ? quizState.submitted[currentQuestion.id] : false;

  const handleSelectAnswer = (questionId: string, optionKey: string) => {
    if (quizState.submitted[questionId]) return;
    setQuizState((prev) => ({
      ...prev,
      answers: { ...prev.answers, [questionId]: optionKey },
    }));
  };

  const handleSubmitAnswer = (questionId: string) => {
    setQuizState((prev) => ({
      ...prev,
      submitted: { ...prev.submitted, [questionId]: true },
      showExplanation: { ...prev.showExplanation, [questionId]: true },
    }));
  };

  const handleNext = () => {
    if (quizState.currentIndex < questions.length - 1) {
      setQuizState((prev) => ({
        ...prev,
        currentIndex: prev.currentIndex + 1,
      }));
    }
  };

  const handlePrev = () => {
    if (quizState.currentIndex > 0) {
      setQuizState((prev) => ({
        ...prev,
        currentIndex: prev.currentIndex - 1,
      }));
    }
  };

  const score = questions.reduce((acc, q) => {
    if (quizState.submitted[q.id] && quizState.answers[q.id] === q.correct_answer) {
      return acc + 1;
    }
    return acc;
  }, 0);

  const totalAnswered = Object.keys(quizState.submitted).length;
  const allAnswered = totalAnswered === questions.length && questions.length > 0;
  const isReviewing = questions.length > 0 && allAnswered;

  if (isLoading) {
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
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">加载题目中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
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
          <div className="flex flex-col items-center justify-center rounded-2xl border border-red-200 bg-red-50 p-12 dark:border-red-800 dark:bg-red-950">
            <XCircle className="h-12 w-12 text-red-600 dark:text-red-400" />
            <h2 className="mb-2 mt-4 text-xl font-semibold text-red-900 dark:text-red-100">加载失败</h2>
            <p className="mb-6 text-center text-red-700 dark:text-red-300">无法加载题目，请稍后再试</p>
            <a
              href="/ket"
              className="flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 font-medium text-white transition-all hover:bg-red-700"
            >
              返回 KET 主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
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
            <BookOpen className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">暂无题目</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              阅读理解题库正在开发中<br />
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

  if (isReviewing) {
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
                <p className="text-sm text-slate-500 dark:text-slate-400">练习结果</p>
              </div>
            </div>
          </header>

          <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">最终得分</p>
              <p className="mt-2 text-5xl font-bold text-blue-600 dark:text-blue-400">
                {score}/{questions.length}
              </p>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className="h-full rounded-full bg-blue-500 transition-all"
                style={{ width: `${(score / questions.length) * 100}%` }}
              />
            </div>
          </div>

          <div className="space-y-4">
            {questions.map((q, index) => {
              const isCorrect = quizState.answers[q.id] === q.correct_answer;
              return (
                <div
                  key={q.id}
                  className={cn(
                    'rounded-xl border p-4',
                    isCorrect
                      ? 'border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950'
                      : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950'
                  )}
                >
                  <div className="flex items-start gap-3">
                    {isCorrect ? (
                      <CheckCircle className="h-5 w-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
                    ) : (
                      <XCircle className="h-5 w-5 shrink-0 text-red-600 dark:text-red-400" />
                    )}
                    <div className="flex-1">
                      <p className="mb-2 font-medium text-slate-900 dark:text-white">
                        {index + 1}. {renderWithLatex(q.prompt)}
                      </p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        你的答案: {quizState.answers[q.id] || '未作答'} | 正确答案: {q.correct_answer}
                      </p>
                      {q.explanation && (
                        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                          解析: {renderWithLatex(q.explanation)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 flex justify-center">
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
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {quizState.currentIndex + 1} / {questions.length}
              </p>
            </div>
          </div>
        </header>

        <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <div
            className="h-full rounded-full bg-blue-500 transition-all"
            style={{ width: `${((quizState.currentIndex + 1) / questions.length) * 100}%` }}
          />
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <p className="mb-6 text-lg leading-relaxed text-slate-900 dark:text-white">
            {renderWithLatex(currentQuestion.prompt)}
          </p>

          {currentQuestion.options && (
            <div className="space-y-3">
              {Object.entries(currentQuestion.options).map(([key, value]) => {
                const isSelected = quizState.answers[currentQuestion.id] === key;
                const isCorrectAnswer = key === currentQuestion.correct_answer;
                const showResult = isCurrentSubmitted;

                let optionClass = 'border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900';
                if (showResult) {
                  if (isCorrectAnswer) {
                    optionClass = 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950';
                  } else if (isSelected && !isCorrectAnswer) {
                    optionClass = 'border-red-500 bg-red-50 dark:bg-red-950';
                  }
                } else if (isSelected) {
                  optionClass = 'border-blue-500 bg-blue-50 dark:bg-blue-950';
                }

                return (
                  <button
                    key={key}
                    onClick={() => handleSelectAnswer(currentQuestion.id, key)}
                    disabled={isCurrentSubmitted}
                    className={cn(
                      'flex w-full items-center gap-3 rounded-xl border-2 p-4 text-left transition-all',
                      optionClass,
                      !isCurrentSubmitted && 'hover:border-blue-300 cursor-pointer',
                      isCurrentSubmitted && 'cursor-default'
                    )}
                  >
                    <span
                      className={cn(
                        'flex h-8 w-8 items-center justify-center rounded-full font-medium',
                        showResult
                          ? isCorrectAnswer
                            ? 'bg-emerald-500 text-white'
                            : isSelected
                              ? 'bg-red-500 text-white'
                              : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                          : isSelected
                            ? 'bg-blue-500 text-white'
                            : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
                      )}
                    >
                      {key}
                    </span>
                    <span className="flex-1 text-slate-900 dark:text-white">{renderWithLatex(value)}</span>
                    {showResult && isCorrectAnswer && (
                      <CheckCircle className="h-5 w-5 text-emerald-500" />
                    )}
                    {showResult && isSelected && !isCorrectAnswer && (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                  </button>
                );
              })}
            </div>
          )}

          {isCurrentSubmitted && quizState.showExplanation[currentQuestion.id] && currentQuestion.explanation && (
            <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
              <p className="font-medium text-blue-900 dark:text-blue-100">解析</p>
              <p className="mt-1 text-sm text-blue-800 dark:text-blue-200">
                {currentQuestion.explanation}
              </p>
            </div>
          )}
        </div>

        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={handlePrev}
            disabled={quizState.currentIndex === 0}
            className={cn(
              'rounded-xl border border-slate-200 px-4 py-2 font-medium transition-all',
              quizState.currentIndex === 0
                ? 'cursor-not-allowed opacity-50'
                : 'hover:bg-slate-50 dark:hover:bg-slate-800'
            )}
          >
            上一题
          </button>

          {!isCurrentSubmitted ? (
            <button
              onClick={() => handleSubmitAnswer(currentQuestion.id)}
              disabled={!quizState.answers[currentQuestion.id]}
              className={cn(
                'rounded-xl bg-blue-600 px-6 py-2 font-medium text-white transition-all',
                quizState.answers[currentQuestion.id]
                  ? 'hover:bg-blue-700'
                  : 'cursor-not-allowed opacity-50'
              )}
            >
              提交答案
            </button>
          ) : quizState.currentIndex < questions.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2 font-medium text-white transition-all hover:bg-blue-700"
            >
              下一题
              <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={() => {}}
              className="flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-2 font-medium text-white transition-all hover:bg-emerald-700"
            >
              查看结果
            </button>
          )}
        </div>

        <div className="mt-4 flex justify-center gap-2">
          {questions.map((q, index) => (
            <button
              key={q.id}
              onClick={() => setQuizState((prev) => ({ ...prev, currentIndex: index }))}
              className={cn(
                'h-3 w-3 rounded-full transition-all',
                index === quizState.currentIndex
                  ? 'bg-blue-600'
                  : quizState.submitted[q.id]
                    ? quizState.answers[q.id] === q.correct_answer
                      ? 'bg-emerald-500'
                      : 'bg-red-500'
                    : 'bg-slate-300 dark:bg-slate-600'
              )}
            />
          ))}
        </div>
      </div>
    </div>
  );
}