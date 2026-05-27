'use client';

import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ListeningPlayerProps {
  audioUrl?: string;
  transcript?: string;
  title?: string;
}

export function ListeningPlayer({ audioUrl, transcript, title }: ListeningPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [showTranscript, setShowTranscript] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.onloadedmetadata = () => {
        setDuration(audioRef.current?.duration || 0);
      };
      audioRef.current.onended = () => {
        setIsPlaying(false);
        setProgress(0);
        setCurrentTime(0);
      };
    }
  }, []);

  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    } else {
      audioRef.current.play();
      progressIntervalRef.current = setInterval(() => {
        if (audioRef.current) {
          const current = audioRef.current.currentTime;
          const dur = audioRef.current.duration || 1;
          setCurrentTime(current);
          setProgress((current / dur) * 100);
        }
      }, 100);
    }
    setIsPlaying(!isPlaying);
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
    setProgress(percent * 100);
  };

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleRetry = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      setProgress(0);
      setCurrentTime(0);
      if (!isPlaying) {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
      {title && (
        <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h3 className="font-semibold text-slate-900 dark:text-white">{title}</h3>
        </div>
      )}

      <div className="p-6">
        {audioUrl && <audio ref={audioRef} src={audioUrl} />}

        <div className="mb-6 flex items-center justify-center gap-6">
          <button
            onClick={handleRetry}
            className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition-all hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
          >
            <RefreshCw className="h-5 w-5" />
          </button>

          <button
            onClick={togglePlay}
            className="flex h-20 w-20 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg transition-all hover:bg-emerald-700 hover:scale-105"
          >
            {isPlaying ? (
              <Pause className="h-8 w-8" />
            ) : (
              <Play className="h-8 w-8 pl-1" />
            )}
          </button>

          <div className="w-14" />
        </div>

        <div className="mb-4">
          <div
            onClick={handleProgressClick}
            className="group relative h-2 w-full cursor-pointer rounded-full bg-slate-200 dark:bg-slate-700"
          >
            <div
              className="absolute inset-y-0 left-0 rounded-full bg-emerald-500 transition-all"
              style={{ width: `${progress}%` }}
            />
            <div
              className="absolute h-4 w-4 -translate-x-1/2 -translate-y-1/4 rounded-full bg-emerald-600 opacity-0 shadow transition-opacity group-hover:opacity-100"
              style={{ left: `${progress}%` }}
            />
          </div>
          <div className="mt-2 flex justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Volume2 className="h-4 w-4" />
            <span>听力材料</span>
          </div>

          {transcript && (
            <button
              onClick={() => setShowTranscript(!showTranscript)}
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
            >
              {showTranscript ? (
                <>
                  隐藏原文 <ChevronUp className="h-4 w-4" />
                </>
              ) : (
                <>
                  查看原文 <ChevronDown className="h-4 w-4" />
                </>
              )}
            </button>
          )}
        </div>

        {showTranscript && transcript && (
          <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
            <p className="whitespace-pre-line text-sm leading-relaxed text-slate-700 dark:text-slate-300">
              {transcript}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}