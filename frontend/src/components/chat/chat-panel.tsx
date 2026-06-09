'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { ChatMessage } from '@/types/problem';

interface ChatPanelProps {
  messages: ChatMessage[];
  className?: string;
}

export function ChatPanel({ messages, className }: ChatPanelProps) {
  return (
    <div className={cn('flex flex-col gap-3 overflow-y-auto p-4', className)}>
      {messages.length === 0 && (
        <div className="flex flex-1 items-center justify-center">
          <p className="text-center text-sm text-[var(--color-muted-foreground)]">
            开始和AI老师对话吧
          </p>
        </div>
      )}
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={cn(
            'max-w-[85%] rounded-2xl px-4 py-2.5 text-sm',
            msg.role === 'user'
              ? 'ml-auto bg-[var(--color-primary)] text-white'
              : 'mr-auto bg-[var(--color-surface-muted)] text-[var(--color-foreground)]'
          )}
        >
          {msg.content}
        </div>
      ))}
    </div>
  );
}
