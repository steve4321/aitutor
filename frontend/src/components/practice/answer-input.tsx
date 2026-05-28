'use client';

import { useState } from 'react';
import { Mic } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnswerInputProps {
  type: 'text' | 'voice' | 'draw';
  placeholder?: string;
  onSubmit?: (answer: string) => void;
  className?: string;
}

export function AnswerInput({
  type = 'text',
  placeholder = '输入你的答案...',
  onSubmit,
  className,
}: AnswerInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = () => {
    if (value.trim()) {
      onSubmit?.(value.trim());
      setValue('');
    }
  };

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="relative flex-1">
        <input
          type={type === 'text' ? 'text' : 'hidden'}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder={placeholder}
          className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
        />
      </div>

      {type === 'voice' && (
        <button className="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200">
          <Mic className="h-5 w-5" />
        </button>
      )}

      <button
        onClick={handleSubmit}
        disabled={!value.trim()}
        className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        提交
      </button>
    </div>
  );
}
