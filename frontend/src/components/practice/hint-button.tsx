'use client';

import { useState } from 'react';
import { Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HintButtonProps {
  hints: string[];
  className?: string;
}

export function HintButton({ hints, className }: HintButtonProps) {
  const [currentLevel, setCurrentLevel] = useState(-1);
  const [isRevealed, setIsRevealed] = useState(false);

  const nextHint = () => {
    if (currentLevel < hints.length - 1) {
      setCurrentLevel((prev) => prev + 1);
      setIsRevealed(true);
    }
  };

  const hideHint = () => {
    setIsRevealed(false);
  };

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center gap-2">
        <button
          onClick={isRevealed ? hideHint : nextHint}
          disabled={currentLevel >= hints.length - 1 && isRevealed}
          className={cn(
            'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
            currentLevel >= 0
              ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          )}
        >
          <Lightbulb className="h-4 w-4" />
          {currentLevel < 0 ? '查看提示' : `提示 ${currentLevel + 1}/${hints.length}`}
        </button>
      </div>

      {isRevealed && currentLevel >= 0 && (
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 px-4 py-3 text-sm text-yellow-900">
          {hints[currentLevel]}
        </div>
      )}
    </div>
  );
}
