'use client';

import { useState, useEffect, useCallback } from 'react';
import { Clock, ChevronLeft, ChevronRight, CheckCircle2, X, AlertCircle, Lightbulb, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProgressBar } from '../course/progress-bar';
import { HintDisplay } from './hint-display';

type ProblemType = 'multiple_choice' | 'fill_blank' | 'short_answer';

interface Problem {
  id: string;
  type: ProblemType;
  content: string;
  latexContent?: string;
  options?: string[];
  correctAnswer: string;
  explanation: string;
  hintLevels: string[];
  xpReward: number;
}

interface PracticeSessionProps {
  problems: Problem[];
  onComplete?: (results: {
    total: number;
    correct: number;
    xpEarned: number;
    timeSpent: number;
  }) => void;
  onExit?: () => void;
}

export function PracticeSession({ problems, onComplete, onExit }: PracticeSessionProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [fillAnswer, setFillAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, { correct: boolean; time: number }>>({});
  const [hintsUsed, setHintsUsed] = useState(0);
  const [currentHintLevel, setCurrentHintLevel] = useState(0);
  const [timeLeft, setTimeLeft] = useState(300);
  const [isActive, setIsActive] = useState(false);
  const [startTime, setStartTime] = useState<number | null>(null);

  const problem = problems[currentIndex];
  const progress = ((currentIndex + 1) / problems.length) * 100;
  const currentHints = problem?.hintLevels.slice(0, currentHintLevel + 1) || [];

  useEffect(() => {
    if (problems.length > 0 && !isActive) {
      setIsActive(true);
      setStartTime(Date.now());
    }
  }, [problems, isActive]);

  useEffect(() => {
    if (!isActive || showResult) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleComplete();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [isActive, showResult]);

  const handleComplete = useCallback(() => {
    if (!startTime) return;
    const timeSpent = Math.round((Date.now() - startTime) / 1000);
    const correctCount = Object.values(results).filter((r) => r.correct).length;
    const totalXP = problems.reduce((sum, p, i) => {
      const answer = answers[p.id];
      const isCorrect = p.correctAnswer.toLowerCase() === answer?.toLowerCase();
      return sum + (isCorrect ? p.xpReward : 0);
    }, 0);

    onComplete?.({
      total: problems.length,
      correct: correctCount,
      xpEarned: totalXP,
      timeSpent,
    });
    setIsActive(false);
  }, [startTime, results, problems, answers, onComplete]);

  const handleOptionSelect = (option: string) => {
    if (showResult) return;
    setSelectedAnswer(option);
    setShowResult(true);
    setAnswers((prev) => ({ ...prev, [problem.id]: option }));
    setResults((prev) => ({
      ...prev,
      [problem.id]: { correct: option === problem.correctAnswer, time: 0 },
    }));
  };

  const handleFillSubmit = () => {
    if (!fillAnswer.trim() || showResult) return;
    setShowResult(true);
    setAnswers((prev) => ({ ...prev, [problem.id]: fillAnswer.trim() }));
    setResults((prev) => ({
      ...prev,
      [problem.id]: {
        correct: problem.correctAnswer.toLowerCase() === fillAnswer.trim().toLowerCase(),
        time: 0,
      },
    }));
  };

  const handleNext = () => {
    if (currentIndex < problems.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setFillAnswer('');
      setShowResult(false);
      setCurrentHintLevel(0);
    } else {
      handleComplete();
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      const prevAnswer = answers[problems[currentIndex - 1].id];
      setSelectedAnswer(prevAnswer ?? null);
      setFillAnswer(prevAnswer ?? '');
      setShowResult(prevAnswer !== undefined);
    }
  };

  const handleHintRequest = () => {
    if (currentHintLevel < problem.hintLevels.length - 1) {
      setCurrentHintLevel((prev) => prev + 1);
      setHintsUsed((prev) => prev + 1);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const correctCount = Object.values(results).filter((r) => r.correct).length;
  const isCorrect =
    showResult &&
    (problem.type === 'multiple_choice'
      ? selectedAnswer === problem.correctAnswer
      : fillAnswer.trim().toLowerCase() === problem.correctAnswer.toLowerCase());

  if (problems.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">暂无题目</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center justify-between">
        <button
          onClick={onExit}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
        >
          <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
        </button>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-slate-400" />
            <span
              className={cn(
                'font-mono font-medium',
                timeLeft < 60 ? 'text-rose-500' : 'text-slate-600 dark:text-slate-300'
              )}
            >
              {formatTime(timeLeft)}
            </span>
          </div>
          <span className="text-sm text-slate-500 dark:text-slate-400">
            {currentIndex + 1} / {problems.length}
          </span>
        </div>

        <div className="h-10 w-10" />
      </div>

      <ProgressBar progress={progress} color="blue" className="mb-6" />

      <div className="mb-4 flex items-center justify-between">
        <span className="text-sm text-slate-500 dark:text-slate-400">
          {correctCount} 正确 · {Object.keys(answers).length - correctCount} 错误
        </span>
        <span className="text-sm text-slate-500 dark:text-slate-400">
          +{problem.xpReward} XP
        </span>
      </div>

      <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <p className="text-lg font-medium text-slate-900 dark:text-white">{problem.content}</p>
        {problem.latexContent && (
          <div className="mt-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
            <code className="text-slate-700 dark:text-slate-300">{problem.latexContent}</code>
          </div>
        )}
      </div>

      {problem.type === 'multiple_choice' && problem.options && (
        <div className="mb-6 space-y-3">
          {problem.options.map((option, i) => (
            <button
              key={i}
              onClick={() => handleOptionSelect(option)}
              disabled={showResult}
              className={cn(
                'flex w-full items-center gap-3 rounded-xl border-2 p-4 text-left transition-all',
                showResult
                  ? option === problem.correctAnswer
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
                    : option === selectedAnswer
                      ? 'border-rose-500 bg-rose-50 dark:bg-rose-900/30'
                      : 'border-slate-200 bg-slate-50 opacity-50 dark:border-slate-700 dark:bg-slate-800'
                  : selectedAnswer === option
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                    : 'border-slate-200 hover:border-slate-300 dark:border-slate-700 hover:border-slate-600'
              )}
            >
              <span
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium',
                  showResult
                    ? option === problem.correctAnswer
                        ? 'bg-emerald-500 text-white'
                        : option === selectedAnswer
                          ? 'bg-rose-500 text-white'
                          : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                    : selectedAnswer === option
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                )}
              >
                {String.fromCharCode(65 + i)}
              </span>
              <span className="flex-1 text-slate-700 dark:text-slate-200">{option}</span>
              {showResult && option === problem.correctAnswer && (
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              )}
              {showResult && option === selectedAnswer && option !== problem.correctAnswer && (
                <X className="h-5 w-5 text-rose-500" />
              )}
            </button>
          ))}
        </div>
      )}

      {problem.type === 'fill_blank' && (
        <div className="mb-6 space-y-4">
          <input
            type="text"
            value={fillAnswer}
            onChange={(e) => !showResult && setFillAnswer(e.target.value)}
            disabled={showResult}
            placeholder="输入你的答案..."
            className={cn(
              'w-full rounded-xl border-2 px-4 py-3 text-slate-900 transition-colors focus:outline-none dark:text-white dark:placeholder:text-slate-500',
              showResult
                ? problem.correctAnswer.toLowerCase() === fillAnswer.trim().toLowerCase()
                  ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
                  : 'border-rose-500 bg-rose-50 dark:bg-rose-900/30'
                : 'border-slate-200 focus:border-blue-500 dark:border-slate-700'
            )}
          />
          {!showResult && (
            <button
              onClick={handleFillSubmit}
              disabled={!fillAnswer.trim()}
              className="w-full rounded-xl bg-blue-600 py-3 font-medium text-white transition-all hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              提交答案
            </button>
          )}
        </div>
      )}

      {showResult && problem.hintLevels.length > 0 && (
        <HintDisplay hints={currentHints} maxLevel={problem.hintLevels.length} />
      )}

      {showResult && (
        <div
          className={cn(
            'mb-6 rounded-xl p-4',
            isCorrect
              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300'
              : 'bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'
          )}
        >
          <div className="mb-2 flex items-center gap-2 font-semibold">
            {isCorrect ? (
              <>
                <CheckCircle2 className="h-5 w-5" />
                回答正确！
              </>
            ) : (
              <>
                <AlertCircle className="h-5 w-5" />
                回答错误
              </>
            )}
          </div>
          <p className="text-sm">{problem.explanation}</p>
        </div>
      )}

      <div className="flex gap-4">
        {!showResult && currentHintLevel < problem.hintLevels.length - 1 && (
          <button
            onClick={handleHintRequest}
            className="flex items-center justify-center gap-2 rounded-xl border border-amber-200 py-3 px-4 font-medium text-amber-600 transition-all hover:bg-amber-50 dark:border-amber-800 dark:text-amber-400 dark:hover:bg-amber-900/20"
          >
            <Lightbulb className="h-5 w-5" />
            获取提示 ({problem.hintLevels.length - currentHintLevel - 1} 剩余)
          </button>
        )}

        <button
          onClick={handlePrev}
          disabled={currentIndex === 0}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <ChevronLeft className="h-5 w-5" />
          上一题
        </button>

        <button
          onClick={handleNext}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 font-medium text-white transition-all hover:bg-blue-700"
        >
          {currentIndex < problems.length - 1 ? '下一题' : '完成'}
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>

      {hintsUsed > 0 && (
        <p className="mt-4 text-center text-sm text-amber-600 dark:text-amber-400">
          已使用 {hintsUsed} 个提示，XP 奖励将相应减少
        </p>
      )}
    </div>
  );
}