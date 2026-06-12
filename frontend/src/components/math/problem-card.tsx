'use client';

import { useState } from 'react';
import { CheckCircle2, X, AlertCircle, Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';

type ProblemType = 'multiple_choice' | 'fill_blank' | 'short_answer';
type Difficulty = 1 | 2 | 3 | 4 | 5;

interface ProblemCardProps {
  id: string;
  type: ProblemType;
  difficulty: Difficulty;
  content: string;
  latexContent?: string;
  options?: string[];
  correctAnswer?: string;
  explanation?: string;
  xpReward: number;
  onAnswer?: (answer: string) => void;
  onHintRequest?: () => void;
}

const DIFFICULTY_COLORS: Record<Difficulty, string> = {
  1: 'text-emerald-600 bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-900/30',
  2: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30',
  3: 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30',
  4: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30',
  5: 'text-rose-600 bg-rose-100 dark:text-rose-400 dark:bg-rose-900/30',
};

const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  1: '入门',
  2: '基础',
  3: '进阶',
  4: '挑战',
  5: '竞赛',
};

export function ProblemCard({
  type,
  difficulty,
  content,
  latexContent,
  options,
  correctAnswer,
  explanation,
  xpReward,
  onAnswer,
  onHintRequest,
}: ProblemCardProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [fillAnswer, setFillAnswer] = useState('');
  const [shortAnswer, setShortAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);

  const handleOptionSelect = (index: number) => {
    if (showResult || !onAnswer) return;
    setSelectedOption(index);
    setShowResult(true);
    onAnswer(options?.[index] || '');
  };

  const handleFillSubmit = () => {
    if (!fillAnswer.trim() || !onAnswer) return;
    setShowResult(true);
    onAnswer(fillAnswer.trim());
  };

  const handleShortSubmit = () => {
    if (!shortAnswer.trim() || !onAnswer) return;
    setShowResult(true);
    onAnswer(shortAnswer.trim());
  };

  const isCorrect =
    showResult &&
    ((type === 'multiple_choice' &&
      options?.[selectedOption!] === correctAnswer) ||
      fillAnswer.trim().toLowerCase() === correctAnswer?.toLowerCase());

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'rounded-full px-2.5 py-0.5 text-xs font-medium',
              DIFFICULTY_COLORS[difficulty]
            )}
          >
            {DIFFICULTY_LABELS[difficulty]}
          </span>
          <span className="text-xs text-slate-400 dark:text-slate-500">
            +{xpReward} XP
          </span>
        </div>
        {onHintRequest && !showResult && (
          <button
            onClick={onHintRequest}
            className="flex items-center gap-1 text-sm text-amber-600 hover:text-amber-700 dark:text-amber-400"
          >
            <Lightbulb className="h-4 w-4" />
            提示
          </button>
        )}
      </div>

      <div className="mb-6">
        <p className="text-lg font-medium text-slate-900 dark:text-white">{content}</p>
        {latexContent && (
          <div className="mt-2 rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
            <code className="text-base text-slate-700 dark:text-slate-300">
              {latexContent}
            </code>
          </div>
        )}
      </div>

      {type === 'multiple_choice' && options && (
        <div className="space-y-3">
          {options.map((option, i) => (
            <button
              key={i}
              onClick={() => handleOptionSelect(i)}
              disabled={showResult}
              className={cn(
                'flex w-full items-center gap-3 rounded-xl border-2 p-4 text-left transition-all',
                showResult
                  ? i === options.indexOf(correctAnswer!)
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
                    : i === selectedOption
                      ? 'border-rose-500 bg-rose-50 dark:bg-rose-900/30'
                      : 'border-slate-200 bg-slate-50 opacity-50 dark:border-slate-700 dark:bg-slate-800'
                  : selectedOption === i
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                    : 'border-slate-200 hover:border-slate-300 dark:border-slate-700 hover:border-slate-600'
              )}
            >
              <span
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium',
                  showResult
                    ? i === options.indexOf(correctAnswer!)
                        ? 'bg-emerald-500 text-white'
                        : i === selectedOption
                          ? 'bg-rose-500 text-white'
                          : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                    : selectedOption === i
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
                )}
              >
                {String.fromCharCode(65 + i)}
              </span>
              <span className="flex-1 text-slate-700 dark:text-slate-200">{option}</span>
              {showResult && i === options.indexOf(correctAnswer!) && (
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              )}
              {showResult && i === selectedOption && i !== options.indexOf(correctAnswer!) && (
                <X className="h-5 w-5 text-rose-500" />
              )}
            </button>
          ))}
        </div>
      )}

      {type === 'fill_blank' && (
        <div className="space-y-4">
          <input
            type="text"
            value={fillAnswer}
            onChange={(e) => !showResult && setFillAnswer(e.target.value)}
            disabled={showResult}
            placeholder="输入你的答案..."
            className={cn(
              'w-full rounded-xl border-2 px-4 py-3 text-slate-900 transition-colors focus:outline-none dark:text-white',
              showResult
                ? fillAnswer.trim().toLowerCase() === correctAnswer?.toLowerCase()
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

      {type === 'short_answer' && (
        <div className="space-y-4">
          <textarea
            value={shortAnswer}
            onChange={(e) => !showResult && setShortAnswer(e.target.value)}
            disabled={showResult}
            placeholder="输入你的答案..."
            rows={4}
            className={cn(
              'w-full resize-none rounded-xl border-2 px-4 py-3 text-slate-900 transition-colors focus:outline-none dark:text-white',
              showResult
                ? shortAnswer.trim().toLowerCase() === correctAnswer?.toLowerCase()
                  ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/30'
                  : 'border-rose-500 bg-rose-50 dark:bg-rose-900/30'
                : 'border-slate-200 focus:border-blue-500 dark:border-slate-700'
            )}
          />
          {!showResult && (
            <button
              onClick={handleShortSubmit}
              disabled={!shortAnswer.trim()}
              className="w-full rounded-xl bg-blue-600 py-3 font-medium text-white transition-all hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              提交答案
            </button>
          )}
        </div>
      )}

      {showResult && explanation && (
        <div
          className={cn(
            'mt-4 rounded-xl p-4',
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
          <p className="text-sm">{explanation}</p>
        </div>
      )}
    </div>
  );
}