'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { cn } from '@/lib/utils';
import { VoiceRecorder } from '@/components/ui/voice-recorder';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  language?: string;
}

export function ChatInput({ onSend, disabled, placeholder, language = 'zh' }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [voiceAvailable, setVoiceAvailable] = useState(false);

  useEffect(() => {
    if (typeof navigator !== 'undefined' && navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
      setVoiceAvailable(true);
    }
  }, []);
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
      <div className="flex shrink-0 gap-2">
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          aria-label="发送消息"
          className={cn(
            'flex h-12 w-12 items-center justify-center rounded-xl transition-all',
            message.trim() && !disabled
              ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]'
              : 'bg-[var(--color-surface-muted)] text-[var(--color-muted-foreground)] cursor-not-allowed'
          )}
        >
          <Send className="h-5 w-5" />
        </button>
        {voiceAvailable && (
          <VoiceRecorder
            onTranscript={(text) => setMessage(text)}
            language={language}
            disabled={disabled}
            size="sm"
          />
        )}
      </div>
    </div>
  );
}