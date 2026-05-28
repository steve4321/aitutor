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
          <p className="text-center text-sm text-gray-400">
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
              ? 'ml-auto bg-blue-600 text-white'
              : 'mr-auto bg-gray-100 text-gray-900'
          )}
        >
          {msg.content}
        </div>
      ))}
    </div>
  );
}
