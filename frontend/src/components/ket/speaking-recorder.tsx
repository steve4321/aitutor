'use client';

import { useState } from 'react';
import { Mic, Square, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SpeakingRecorderProps {
  prompt?: string;
  maxDuration?: number;
  onSubmit?: (blob: Blob) => void;
  className?: string;
}

export function SpeakingRecorder({
  prompt = 'Describe what you did last weekend.',
  maxDuration = 60,
  onSubmit,
  className,
}: SpeakingRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [hasRecording, setHasRecording] = useState(false);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setHasRecording(false);
      setSeconds(0);
    } else {
      setHasRecording(true);
    }
  };

  const formatTime = (s: number) => {
    const min = Math.floor(s / 60);
    const sec = s % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('flex flex-col gap-4', className)}>
      <div className="rounded-xl bg-violet-50 border border-violet-200 px-4 py-3">
        <p className="text-sm font-medium text-violet-900">{prompt}</p>
      </div>

      <div className="flex flex-col items-center gap-4 py-6">
        <button
          onClick={toggleRecording}
          className={cn(
            'relative flex h-20 w-20 items-center justify-center rounded-full transition-all',
            isRecording
              ? 'bg-red-500 text-white shadow-lg shadow-red-200'
              : 'bg-violet-600 text-white hover:bg-violet-700'
          )}
        >
          {isRecording ? (
            <Square className="h-8 w-8" />
          ) : (
            <Mic className="h-8 w-8" />
          )}
          {isRecording && (
            <span className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-30" />
          )}
        </button>

        <div className="text-center">
          <p className="text-2xl font-mono font-bold text-gray-900">
            {formatTime(seconds)}
          </p>
          <p className="text-sm text-gray-500">
            {isRecording ? '录音中...' : hasRecording ? '点击重录' : '点击开始录音'}
          </p>
        </div>

        {hasRecording && !isRecording && (
          <div className="flex gap-3">
            <button
              onClick={() => setHasRecording(false)}
              className="flex items-center gap-1.5 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <RotateCcw className="h-4 w-4" />
              重录
            </button>
            <button
              onClick={() => onSubmit?.(new Blob())}
              className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
            >
              提交录音
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
