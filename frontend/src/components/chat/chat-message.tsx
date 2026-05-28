import { cn } from '@/lib/utils';
import type { ChatMessage } from '@/types/problem';

interface ChatMessageProps {
  message: ChatMessage;
  className?: string;
}

export function ChatMessage({ message, className }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-2',
        isUser ? 'flex-row-reverse' : 'flex-row',
        className
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
          AI
        </div>
      )}

      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
          isUser
            ? 'rounded-tr-sm bg-blue-600 text-white'
            : 'rounded-tl-sm bg-gray-100 text-gray-900'
        )}
      >
        <p>{message.content}</p>
        {message.metadata?.latex && (
          <div className="mt-2 rounded bg-white/10 p-2 font-mono text-xs">
            {message.metadata.latex}
          </div>
        )}
      </div>
    </div>
  );
}
