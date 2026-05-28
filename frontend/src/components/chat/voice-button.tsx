'use client';

import { useState } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VoiceButtonProps {
  onStart?: () => void;
  onStop?: () => void;
  disabled?: boolean;
  className?: string;
}

export function VoiceButton({
  onStart,
  onStop,
  disabled = false,
  className,
}: VoiceButtonProps) {
  const [isRecording, setIsRecording] = useState(false);

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      onStop?.();
    } else {
      setIsRecording(true);
      onStart?.();
    }
  };

  return (
    <button
      onClick={toggleRecording}
      disabled={disabled}
      className={cn(
        'relative flex h-12 w-12 items-center justify-center rounded-full transition-all duration-200',
        isRecording
          ? 'bg-red-500 text-white shadow-lg shadow-red-200 scale-110'
          : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm',
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      aria-label={isRecording ? '停止录音' : '开始录音'}
    >
      {isRecording ? (
        <>
          <MicOff className="h-5 w-5" />
          <span className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-30" />
        </>
      ) : (
        <Mic className="h-5 w-5" />
      )}
    </button>
  );
}
