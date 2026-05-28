'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface WritingEditorProps {
  prompt?: string;
  wordLimit?: number;
  onSubmit?: (content: string) => void;
  className?: string;
}

export function WritingEditor({
  prompt = 'Write a short email to your friend about your weekend plans (35-45 words).',
  wordLimit = 45,
  onSubmit,
  className,
}: WritingEditorProps) {
  const [content, setContent] = useState('');
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;

  return (
    <div className={cn('flex flex-col gap-4', className)}>
      <div className="rounded-xl bg-blue-50 border border-blue-200 px-4 py-3">
        <p className="text-sm font-medium text-blue-900">{prompt}</p>
      </div>

      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Start writing here..."
        className="min-h-[200px] w-full rounded-xl border border-gray-300 bg-white p-4 text-sm leading-relaxed focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
      />

      <div className="flex items-center justify-between">
        <span
          className={cn(
            'text-sm',
            wordCount > wordLimit ? 'text-red-600 font-medium' : 'text-gray-500'
          )}
        >
          {wordCount} / {wordLimit} words
        </span>
        <button
          onClick={() => onSubmit?.(content)}
          disabled={wordCount === 0}
          className="rounded-xl bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          提交
        </button>
      </div>
    </div>
  );
}
