'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Play, Pause, RotateCcw, Maximize, Minimize, Volume2, VolumeX } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AnimationPlayerProps {
  url?: string;
  title: string;
  thumbnailUrl?: string;
  durationSec?: number;
  animationType?: 'manim' | 'lottie' | 'css' | 'canvas';
  autoplay?: boolean;
  className?: string;
}

export function AnimationPlayer({
  url,
  title,
  thumbnailUrl,
  durationSec,
  animationType,
  autoplay = false,
  className,
}: AnimationPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(durationSec || 0);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const togglePlay = useCallback(() => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  }, [isPlaying]);

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const replay = () => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = 0;
    videoRef.current.play();
  };

  const toggleFullscreen = useCallback(async () => {
    if (!containerRef.current) return;

    if (!document.fullscreenElement) {
      await containerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      await document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!videoRef.current || !progressRef.current || duration === 0) return;
    const rect = progressRef.current.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    videoRef.current.currentTime = percent * duration;
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setCurrentTime(videoRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    setDuration(videoRef.current.duration);
    setIsLoading(false);
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
  };

  const handleCanPlay = () => {
    setIsLoading(false);
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  useEffect(() => {
    if (autoplay && videoRef.current && url) {
      videoRef.current.play().catch(() => {
        setHasError(true);
      });
    }
  }, [autoplay, url]);

  if (!url) {
    return (
      <div
        className={cn(
          'overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 text-center',
          className
        )}
      >
        <p className="text-[var(--color-muted-foreground)]">No animation available</p>
      </div>
    );
  }

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      className={cn(
        'overflow-hidden rounded-xl border border-[var(--color-border)] bg-[#1a1a2e]',
        className
      )}
    >
      <div className="relative">
        <div className="flex items-center gap-2 px-4 py-3">
          <span className="text-sm font-medium text-white">{title}</span>
          {animationType && (
            <span className="rounded bg-white/10 px-2 py-0.5 text-xs text-white/70">
              {animationType}
            </span>
          )}
        </div>

        <div className="relative aspect-video bg-[#1a1a2e]">
          {hasError ? (
            <div className="flex h-full items-center justify-center">
              <p className="text-white/60">Failed to load animation</p>
            </div>
          ) : (
            <>
              <video
                ref={videoRef}
                src={url}
                poster={thumbnailUrl}
                className="h-full w-full"
                muted={isMuted}
                playsInline
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={handleEnded}
                onError={handleError}
                onCanPlay={handleCanPlay}
              />

              {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white" />
                </div>
              )}

              <button
                onClick={togglePlay}
                className="absolute inset-0 flex h-full w-full items-center justify-center bg-black/20 opacity-0 hover:opacity-100 focus:opacity-100"
                style={{ backgroundColor: isPlaying ? 'transparent' : 'rgba(0,0,0,0.3)' }}
              >
                {!isPlaying && (
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 text-gray-900">
                    <Play className="h-8 w-8 ml-1" />
                  </div>
                )}
              </button>
            </>
          )}
        </div>

        <div className="bg-[#1a1a2e] p-4">
          <div className="mb-3 flex items-center gap-4">
            <button
              onClick={togglePlay}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20"
            >
              {isPlaying ? (
                <Pause className="h-5 w-5" />
              ) : (
                <Play className="h-5 w-5 ml-0.5" />
              )}
            </button>

            <div className="flex flex-1 items-center gap-3">
              <span className="text-xs text-white/60">{formatTime(currentTime)}</span>
              <div
                ref={progressRef}
                onClick={handleProgressClick}
                className="relative h-1 flex-1 cursor-pointer rounded-full bg-white/20"
              >
                <div
                  className="absolute h-full rounded-full bg-white/60"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <span className="text-xs text-white/60">{formatTime(duration)}</span>
            </div>

            <button
              onClick={toggleMute}
              className="rounded-lg p-1.5 text-white/60 hover:bg-white/10 hover:text-white"
            >
              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </button>

            <button
              onClick={replay}
              className="rounded-lg p-1.5 text-white/60 hover:bg-white/10 hover:text-white"
            >
              <RotateCcw className="h-4 w-4" />
            </button>

            <button
              onClick={toggleFullscreen}
              className="rounded-lg p-1.5 text-white/60 hover:bg-white/10 hover:text-white"
            >
              {isFullscreen ? (
                <Minimize className="h-4 w-4" />
              ) : (
                <Maximize className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}