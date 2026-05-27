'use client';

import { useState, useRef, useEffect } from 'react';
import { Calculator, Send } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MathInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

const LATEX_SYMBOLS = [
  { symbol: 'π', latex: '\\pi' },
  { symbol: '√', latex: '\\sqrt{}' },
  { symbol: '²', latex: '^2' },
  { symbol: '³', latex: '^3' },
  { symbol: '÷', latex: '\\div' },
  { symbol: '×', latex: '\\times' },
  { symbol: '±', latex: '\\pm' },
  { symbol: '≠', latex: '\\neq' },
  { symbol: '≤', latex: '\\leq' },
  { symbol: '≥', latex: '\\geq' },
  { symbol: '∞', latex: '\\infty' },
  { symbol: '½', latex: '\\frac{}{}' },
];

export function MathInput({
  value,
  onChange,
  onSubmit,
  placeholder = '输入数学表达式...',
  disabled,
}: MathInputProps) {
  const [showPreview, setShowPreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  const insertSymbol = (latex: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newValue = value.substring(0, start) + latex + value.substring(end);
    onChange(newValue);

    setTimeout(() => {
      const cursorPos = start + latex.indexOf('}');
      textarea.focus();
      textarea.setSelectionRange(cursorPos, cursorPos);
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && onSubmit) {
      e.preventDefault();
      onSubmit(value);
    }
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
      <div className="flex flex-wrap gap-2 border-b border-slate-200 p-2 dark:border-slate-700">
        {LATEX_SYMBOLS.map(({ symbol, latex }) => (
          <button
            key={symbol}
            onClick={() => insertSymbol(latex)}
            disabled={disabled}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
          >
            {symbol}
          </button>
        ))}
      </div>

      <div className="relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={2}
          className={cn(
            'w-full resize-none rounded-t-xl border-0 bg-transparent p-4 pr-12 text-slate-900 focus:outline-none dark:text-white dark:placeholder:text-slate-500',
            disabled && 'opacity-50'
          )}
        />
        <button
          onClick={() => setShowPreview(!showPreview)}
          className={cn(
            'absolute right-3 top-3 rounded-lg p-2 transition-col',
            showPreview
              ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
              : 'text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
          )}
        >
          <Calculator className="h-5 w-5" />
        </button>
      </div>

      {showPreview && value && (
        <div className="border-t border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
          <p className="mb-2 text-xs text-slate-500 dark:text-slate-400">预览</p>
          <div className="rounded-lg bg-white p-3 dark:bg-slate-800">
            <code className="text-lg text-slate-700 dark:text-slate-200">{value}</code>
          </div>
        </div>
      )}

      {onSubmit && (
        <div className="flex justify-end border-t border-slate-200 p-2 dark:border-slate-700">
          <button
            onClick={() => onSubmit(value)}
            disabled={!value.trim() || disabled}
            className={cn(
              'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
              value.trim() && !disabled
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed dark:bg-slate-700 dark:text-slate-500'
            )}
          >
            提交
            <Send className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}