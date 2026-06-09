'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-3">
      <div className="relative flex-1">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || '输入消息...'}
          disabled={disabled}
          rows={1}
          className={cn(
            'w-full resize-none rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 pr-12 text-[var(--color-foreground)] transition-colors focus:border-[var(--color-primary)] focus:outline-none placeholder:text-[var(--color-muted-foreground)]',
            disabled && 'opacity-50'
          )}
        />
      </div>
      <button
        onClick={handleSend}
        disabled={!message.trim() || disabled}
        className={cn(
          'flex h-12 w-12 items-center justify-center rounded-xl transition-all',
          message.trim() && !disabled
            ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]'
            : 'bg-[var(--color-surface-muted)] text-[var(--color-muted-foreground)] cursor-not-allowed'
        )}
      >
        <Send className="h-5 w-5" />
      </button>
    </div>
  );
}