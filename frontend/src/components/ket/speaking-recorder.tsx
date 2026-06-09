'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, Square, RotateCcw, Play, Pause } from 'lucide-react';
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
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const blobUrlRef = useRef<string | null>(null);

  const cleanupStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, []);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const revokeBlobUrl = useCallback(() => {
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current);
      blobUrlRef.current = null;
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    clearTimer();
  }, [clearTimer]);

  const startRecording = useCallback(async () => {
    setError(null);
    revokeBlobUrl();
    setRecordedBlob(null);
    setHasRecording(false);
    setSeconds(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setRecordedBlob(blob);
        setHasRecording(true);
        setIsRecording(false);
        cleanupStream();
      };

      recorder.start();
      setIsRecording(true);

      timerRef.current = setInterval(() => {
        setSeconds((prev) => {
          if (prev >= maxDuration - 1) {
            stopRecording();
            return maxDuration;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err) {
      cleanupStream();
      if (err instanceof DOMException && err.name === 'NotAllowedError') {
        setError('麦克风权限被拒绝，请在浏览器设置中允许访问麦克风。');
      } else {
        setError('无法启动录音，请检查麦克风是否正常连接。');
      }
    }
  }, [maxDuration, stopRecording, cleanupStream, revokeBlobUrl]);

  const resetRecording = useCallback(() => {
    stopRecording();
    revokeBlobUrl();
    setRecordedBlob(null);
    setHasRecording(false);
    setSeconds(0);
    setError(null);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
  }, [stopRecording, revokeBlobUrl]);

  const playRecording = useCallback(() => {
    if (!recordedBlob || !audioRef.current) return;

    revokeBlobUrl();
    const url = URL.createObjectURL(recordedBlob);
    blobUrlRef.current = url;
    audioRef.current.src = url;
    audioRef.current.play();
    setIsPlaying(true);
  }, [recordedBlob, revokeBlobUrl]);

  const stopPlaying = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
  }, []);

  const handleSubmit = useCallback(() => {
    if (recordedBlob) {
      onSubmit?.(recordedBlob);
    }
  }, [recordedBlob, onSubmit]);

  useEffect(() => {
    return () => {
      clearTimer();
      cleanupStream();
      revokeBlobUrl();
    };
  }, [clearTimer, cleanupStream, revokeBlobUrl]);

  const formatTime = (s: number) => {
    const min = Math.floor(s / 60);
    const sec = s % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('flex flex-col gap-4', className)}>
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />

      <div className="rounded-xl bg-violet-50 border border-violet-200 px-4 py-3">
        <p className="text-sm font-medium text-violet-900">{prompt}</p>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 px-4 py-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="flex flex-col items-center gap-4 py-6">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!!error}
          className={cn(
            'relative flex h-20 w-20 items-center justify-center rounded-full transition-all',
            isRecording
              ? 'bg-red-500 text-white shadow-lg shadow-red-200'
              : 'bg-violet-600 text-white hover:bg-violet-700',
            error && 'cursor-not-allowed opacity-50'
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
            {isRecording
              ? '录音中...'
              : hasRecording
                ? '点击麦克风重录'
                : '点击开始录音'}
          </p>
        </div>

        {hasRecording && !isRecording && (
          <div className="flex gap-3">
            <button
              onClick={isPlaying ? stopPlaying : playRecording}
              className="flex items-center gap-1.5 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              {isPlaying ? (
                <>
                  <Pause className="h-4 w-4" />
                  停止
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  播放
                </>
              )}
            </button>
            <button
              onClick={resetRecording}
              className="flex items-center gap-1.5 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <RotateCcw className="h-4 w-4" />
              重录
            </button>
            <button
              onClick={handleSubmit}
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
