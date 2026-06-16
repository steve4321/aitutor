'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { getToken } from '@/lib/auth';
import { fetchBinary } from '@/lib/api';


export interface UseTTSReturn {
  speak: (text: string, voice?: string) => Promise<void>;
  stop: () => void;
  isSpeaking: boolean;
  loading: boolean;
  error: string | null;
}

function detectLanguage(text: string): 'zh' | 'en' {
  const cjkRegex = /[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/;
  return cjkRegex.test(text) ? 'zh' : 'en';
}

function getDefaultVoice(lang: 'zh' | 'en'): string {
  return lang === 'zh' ? 'zh-CN-XiaoxiaoNeural' : 'en-US-JennyNeural';
}

const TTS_CACHE_MAX_SIZE = 20;

export function useTTS(): UseTTSReturn {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const cacheRef = useRef<Map<string, string>>(new Map());

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setIsSpeaking(false);
  }, []);

  const speak = useCallback(
    async (text: string, voice?: string) => {
      if (!text.trim()) return;

      stop();
      setError(null);
      setLoading(true);

      try {
        const lang = detectLanguage(text);
        const selectedVoice = voice || getDefaultVoice(lang);

        const cacheKey = `${text}:${selectedVoice}`;
        let audioUrl = cacheRef.current.get(cacheKey);

        if (!audioUrl) {
          const token = getToken();
          if (!token) {
            throw new Error('未登录，无法使用语音功能');
          }

          const audioBlob = await fetchBinary('/voice/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text,
              voice: selectedVoice,
              rate: '+0%',
            }),
          });
          audioUrl = URL.createObjectURL(audioBlob);
          cacheRef.current.set(cacheKey, audioUrl);

          while (cacheRef.current.size > TTS_CACHE_MAX_SIZE) {
            const oldestKey = cacheRef.current.keys().next().value;
            if (oldestKey === undefined) break;
            const evictedUrl = cacheRef.current.get(oldestKey);
            if (evictedUrl) {
              URL.revokeObjectURL(evictedUrl);
            }
            cacheRef.current.delete(oldestKey);
          }
        }

        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onended = () => {
          setIsSpeaking(false);
        };

        audio.onerror = () => {
          setError('音频播放失败');
          setIsSpeaking(false);
        };

        setIsSpeaking(true);
        setLoading(false);
        await audio.play();
      } catch (err) {
        setError(err instanceof Error ? err.message : '语音合成失败');
        setLoading(false);
        setIsSpeaking(false);
      }
    },
    [stop]
  );

  useEffect(() => {
    const cache = cacheRef.current;
    const audio = audioRef.current;
    return () => {
      if (audio) {
        audio.pause();
        audioRef.current = null;
      }
      cache.forEach((url) => URL.revokeObjectURL(url));
      cache.clear();
    };
  }, []);

  return {
    speak,
    stop,
    isSpeaking,
    loading,
    error,
  };
}