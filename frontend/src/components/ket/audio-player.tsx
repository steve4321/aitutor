'use client';

import { useState } from 'react';
import { Play, Pause, RotateCcw, Volume2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { renderWithLatex } from '@/lib/render-content';

interface AudioPlayerProps {
  audioUrl?: string;
  title?: string;
  className?: string;
}

export function AudioPlayer({
  audioUrl,
  title = 'Listening Exercise',
  className,
}: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playCount, setPlayCount] = useState(0);
  const maxPlays = 3;

  const togglePlay = () => {
    if (playCount >= maxPlays && !isPlaying) return;
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      setPlayCount((prev) => prev + 1);
    }
  };

  const replay = () => {
    setPlayCount(0);
    setIsPlaying(true);
  };

  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white p-4', className)}>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Volume2 className="h-5 w-5 text-blue-600" />
          <span className="text-sm font-medium text-gray-900">{renderWithLatex(title || '')}</span>
        </div>
        <span className="text-xs text-gray-500">
          {playCount}/{maxPlays} 次
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={togglePlay}
          disabled={playCount >= maxPlays && !isPlaying}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPlaying ? (
            <Pause className="h-4 w-4" />
          ) : (
            <Play className="h-4 w-4 ml-0.5" />
          )}
        </button>

        <div className="flex-1">
          <div className="h-2 rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-300"
              style={{ width: '0%' }}
            />
          </div>
        </div>

        <button
          onClick={replay}
          className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
