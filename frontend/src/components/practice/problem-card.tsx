'use client';

import { cn } from '@/lib/utils';
import { renderWithLatex } from '@/lib/render-content';

interface ProblemCardProps {
  questionNumber: number;
  totalQuestions: number;
  content: string;
  latexContent?: string;
  options?: string[];
  selectedAnswer?: string;
  onAnswerSelect?: (answer: string) => void;
  className?: string;
}

export function ProblemCard({
  questionNumber,
  totalQuestions,
  content,
  options,
  selectedAnswer,
  onAnswerSelect,
  className,
}: ProblemCardProps) {
  return (
    <div className={cn('rounded-xl bg-white p-5 shadow-sm', className)}>
      <div className="mb-4 flex items-center justify-between text-sm text-gray-500">
        <span className="font-medium">
          第 {questionNumber} 题 / 共 {totalQuestions} 题
        </span>
      </div>

      <div className="mb-6 text-lg leading-relaxed text-gray-900">
        {renderWithLatex(content)}
      </div>

      {options && (
        <div className="flex flex-col gap-3">
          {options.map((option, index) => {
            const label = String.fromCharCode(65 + index);
            const isSelected = selectedAnswer === option;

            return (
              <button
                key={index}
                onClick={() => onAnswerSelect?.(option)}
                className={cn(
                  'flex items-start gap-3 rounded-xl border-2 p-4 text-left text-sm transition-all',
                  isSelected
                    ? 'border-blue-500 bg-blue-50 text-blue-900'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                )}
              >
                <span
                  className={cn(
                    'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                    isSelected
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-600'
                  )}
                >
                  {label}
                </span>
                <span>{renderWithLatex(option)}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
