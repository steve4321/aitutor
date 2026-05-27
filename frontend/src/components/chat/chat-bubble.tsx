'use client';

import { cn } from '@/lib/utils';

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
        <div className="rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-500 dark:bg-slate-800 dark:text-slate-400">
          {content}
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
            ? 'bg-gradient-to-br from-blue-500 to-violet-500 text-white'
            : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
        )}
      >
        {isUser ? '我' : 'AI'}
      </div>
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-3',
          isUser
            ? 'rounded-tr-sm bg-blue-600 text-white'
            : 'rounded-tl-sm bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
        )}
      >
        {metadata?.latex ? (
          <div className="text-sm">
            <code className="bg-slate-200 px-1 py-0.5 dark:bg-slate-700">{content}</code>
          </div>
        ) : (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>
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
              ▶
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