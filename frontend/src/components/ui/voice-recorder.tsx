'use client';

import { useState, useCallback, useEffect } from 'react';
import { Mic, Square, Loader2, Keyboard, Send } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useVoiceRecorder } from '@/hooks/use-voice-recorder';
import { useASR } from '@/hooks/use-asr';

export interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
  language?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showTranscript?: boolean;
}

const sizeMap = {
  sm: 'h-8 w-8',
  md: 'h-11 w-11',
  lg: 'h-14 w-14',
};

const iconSizeMap = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
};

export function VoiceRecorder({
  onTranscript,
  language = 'zh',
  disabled = false,
  size = 'md',
  className,
  showTranscript = false,
}: VoiceRecorderProps) {
  const [transcriptText, setTranscriptText] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'recording' | 'transcribing' | 'error'>('idle');
  const [micAvailable, setMicAvailable] = useState(true);
  const [textMode, setTextMode] = useState(false);
  const [textInput, setTextInput] = useState('');

  const { isRecording, audioLevel, error, startRecording, stopRecording, reset } =
    useVoiceRecorder();
  const { transcribe, isTranscribing, error: asrError } = useASR();

  useEffect(() => {
    if (
      typeof navigator === 'undefined' ||
      !navigator.mediaDevices ||
      typeof navigator.mediaDevices.getUserMedia !== 'function'
    ) {
      setMicAvailable(false);
      setTextMode(true);
    }
  }, []);

  const handleClick = useCallback(async () => {
    if (disabled) return;

    if (status === 'idle') {
      setTranscriptText(null);
      reset();
      const success = await startRecording();
      if (success) {
        setStatus('recording');
      } else {
        setStatus('error');
        setMicAvailable(false);
        setTextMode(true);
      }
    } else if (status === 'recording') {
      setStatus('transcribing');
      const blob = await stopRecording();
      if (blob) {
        try {
          const text = await transcribe(blob, language);
          setTranscriptText(text);
          onTranscript(text);
        } catch {
          setStatus('error');
          return;
        }
      }
      setStatus('idle');
    }
  }, [status, disabled, reset, startRecording, stopRecording, transcribe, language, onTranscript]);

  const handleTextSubmit = useCallback(() => {
    const trimmed = textInput.trim();
    if (!trimmed) return;
    setTranscriptText(trimmed);
    onTranscript(trimmed);
    setTextInput('');
  }, [textInput, onTranscript]);

  const handleTextKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleTextSubmit();
      }
    },
    [handleTextSubmit]
  );

  const displayError = error || (status === 'error' ? asrError : null);

  if (textMode) {
    return (
      <div className={cn('flex flex-col items-stretch gap-2 w-full max-w-md', className)}>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleTextKeyDown}
            disabled={disabled}
            placeholder="输入文字代替语音..."
            className="flex-1 rounded-lg border border-green-300 dark:border-green-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-[var(--color-foreground)] placeholder:text-[var(--color-muted-foreground)] focus:border-green-500 focus:outline-none"
          />
          <button
            onClick={handleTextSubmit}
            disabled={disabled || !textInput.trim()}
            className={cn(
              'flex items-center justify-center rounded-lg transition-all shrink-0',
              size === 'sm' ? 'h-8 px-2' : 'h-10 px-3',
              textInput.trim() && !disabled
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-[var(--color-surface-muted)] text-[var(--color-muted-foreground)] cursor-not-allowed'
            )}
            aria-label="发送文字"
          >
            <Send className={size === 'sm' ? 'h-4 w-4' : 'h-4 w-4'} />
          </button>
          {micAvailable && (
            <button
              onClick={() => setTextMode(false)}
              disabled={disabled}
              className="flex items-center justify-center rounded-lg bg-[var(--color-surface-muted)] text-[var(--color-muted-foreground)] hover:text-[var(--color-foreground)] transition-colors shrink-0"
              style={{ width: size === 'sm' ? 32 : 40, height: size === 'sm' ? 32 : 40 }}
              aria-label="切换到语音输入"
              title="切换到语音输入"
            >
              <Mic className={size === 'sm' ? 'h-4 w-4' : 'h-5 w-5'} />
            </button>
          )}
        </div>

        {!micAvailable && (
          <p className="text-xs text-[var(--color-muted-foreground)] text-center">
            未检测到麦克风，请使用文字输入
          </p>
        )}

        {showTranscript && transcriptText && (
          <p className="text-xs text-[var(--color-muted-foreground)] text-center line-clamp-2">
            {transcriptText}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col items-center gap-2', className)}>
      <div className="flex items-center gap-2">
        <div className="relative">
          <button
            onClick={handleClick}
            disabled={disabled || status === 'transcribing'}
            className={cn(
              'relative flex items-center justify-center rounded-full transition-all duration-200',
              sizeMap[size],
              status === 'recording'
                ? 'bg-[var(--color-danger)] text-white shadow-lg'
                : status === 'transcribing'
                ? 'bg-[var(--color-primary)] text-white cursor-wait'
                : 'bg-green-500 text-white hover:bg-green-600 shadow-sm',
              (disabled || status === 'transcribing') && 'opacity-50 cursor-not-allowed'
            )}
            style={
              status === 'recording'
                ? {
                    transform: `scale(1 + ${audioLevel * 0.15})`,
                    transition: 'transform 80ms ease-out',
                  }
                : undefined
            }
            aria-label={status === 'recording' ? '停止录音' : '开始录音'}
            title={displayError || undefined}
          >
            {status === 'transcribing' ? (
              <Loader2 className={cn(iconSizeMap[size], 'animate-spin')} />
            ) : status === 'recording' ? (
              <Square className={cn(iconSizeMap[size], 'fill-current')} />
            ) : (
              <Mic className={iconSizeMap[size]} />
            )}
          </button>

          {status === 'recording' && (
            <span
              className="absolute inset-0 rounded-full bg-[var(--color-danger)] opacity-30 animate-ping"
              style={{ animationDuration: `${1 + (1 - audioLevel) * 0.5}s` }}
            />
          )}

          {displayError && (
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-[var(--color-danger)] px-2 py-0.5 text-xs text-white">
              {displayError}
            </div>
          )}
        </div>

        <button
          onClick={() => setTextMode(true)}
          disabled={disabled}
          className={cn(
            'flex items-center justify-center rounded-full bg-[var(--color-surface-muted)] text-[var(--color-muted-foreground)] hover:text-[var(--color-foreground)] transition-colors',
            sizeMap[size]
          )}
          aria-label="切换到文字输入"
          title="切换到文字输入"
        >
          <Keyboard className={iconSizeMap[size]} />
        </button>
      </div>

      {showTranscript && transcriptText && (
        <div className="max-w-[200px] text-center">
          <p className="text-xs text-[var(--color-muted-foreground)] line-clamp-2">
            {transcriptText}
          </p>
        </div>
      )}
    </div>
  );
}
