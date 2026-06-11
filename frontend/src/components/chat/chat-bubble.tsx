'use client';

import { Play } from 'lucide-react';
import { cn } from '@/lib/utils';
import { renderWithLatex } from '@/lib/render-content';

interface ChatBubbleProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: {
    latex?: string;
    image_url?: string;
    audio_url?: string;
  };
}

export function ChatBubble({ role, content, metadata }: ChatBubbleProps) {
  const isUser = role === 'user';
  const isSystem = role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="rounded-lg bg-[var(--color-surface-muted)] px-4 py-2 text-sm text-[var(--color-muted-foreground)]">
          {renderWithLatex(content)}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-medium',
          isUser
            ? 'bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] text-white'
            : 'bg-[var(--color-surface-muted)] text-[var(--color-muted-foreground)]'
        )}
      >
        {isUser ? '我' : 'AI'}
      </div>
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-3',
          isUser
            ? 'rounded-tr-sm bg-[var(--color-primary)] text-white'
            : 'rounded-tl-sm bg-[var(--color-surface-muted)] text-[var(--color-foreground)]'
        )}
      >
        {metadata?.latex ? (
          <div className="text-sm">
            {renderWithLatex(content)}
          </div>
        ) : (
          <div className="whitespace-pre-wrap text-sm leading-relaxed">{renderWithLatex(content)}</div>
        )}
        {metadata?.image_url && (
          <img
            src={metadata.image_url}
            alt=""
            className="mt-2 max-w-full rounded-lg"
          />
        )}
        {metadata?.audio_url && (
          <div className="mt-2 flex items-center gap-2">
            <button className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20 hover:bg-white/30">
              <Play className="h-4 w-4" />
            </button>
            <div className="h-1 w-32 rounded-full bg-white/30">
              <div className="h-full w-1/3 rounded-full bg-white" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}