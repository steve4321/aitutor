'use client';

import { useRef, useEffect, useState } from 'react';
import { MessageSquare, ChevronDown, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useChat } from '@/hooks/use-chat';
import type { ChatMessage as UseChatMessage } from '@/hooks/use-chat';
import { ChatBubble } from './chat-bubble';
import { ChatInput } from './chat-input';

interface TutorChatProps {
  title?: string;
  sessionId?: string | null;
  disabled?: boolean;
}

export function TutorChat({
  title = 'AI 辅导',
  sessionId,
  disabled,
}: TutorChatProps) {
  const { messages, isLoading, error, send } = useChat({
    sessionId,
  });
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      setShowScrollButton(scrollHeight - scrollTop - clientHeight > 100);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="flex h-full flex-col rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)]">
      <div className="flex items-center gap-3 border-b border-[var(--color-border)] px-6 py-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)]">
          <Bot className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-[var(--color-foreground)]">{title}</h3>
          <p className="text-xs text-[var(--color-muted-foreground)]">在线</p>
        </div>
      </div>

      <div
        ref={messagesContainerRef}
        className="flex-1 space-y-4 overflow-y-auto p-6"
      >
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <MessageSquare className="mb-4 h-12 w-12 text-[var(--color-muted)]" />
            <p className="text-[var(--color-muted-foreground)]">
              发送消息开始与 AI 导师对话
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatBubble key={msg.id} role={msg.role as 'user' | 'assistant' | 'system'} content={msg.content} />
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-surface-muted)]">
              <Bot className="h-4 w-4 text-[var(--color-muted-foreground)]" />
            </div>
            <div className="rounded-2xl rounded-tl-sm bg-[var(--color-surface-muted)] px-4 py-3">
              <div className="flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--color-muted)] [animation-delay:0ms]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--color-muted)] [animation-delay:150ms]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--color-muted)] [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="text-center text-sm text-[var(--color-danger)]">{error}</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {showScrollButton && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-24 right-8 flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-surface)] shadow-lg hover:bg-[var(--color-surface-muted)]"
        >
          <ChevronDown className="h-4 w-4 text-[var(--color-muted-foreground)]" />
        </button>
      )}

      <div className="border-t border-[var(--color-border)] p-4">
        <ChatInput onSend={send} disabled={disabled || isLoading} />
      </div>
    </div>
  );
}