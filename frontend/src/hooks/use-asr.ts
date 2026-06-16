'use client';

import { useState, useCallback } from 'react';
import { useAuthStore } from '@/stores/auth-store';
import { fetchBinary } from '@/lib/api';

export interface UseASRReturn {
  transcribe: (audioBlob: Blob, language?: string) => Promise<string>;
  isTranscribing: boolean;
  error: string | null;
}

export function useASR(): UseASRReturn {
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const transcribe = useCallback(
    async (audioBlob: Blob, language = 'zh'): Promise<string> => {
      setError(null);
      setIsTranscribing(true);

      try {
        if (!useAuthStore.getState().isAuthenticated) {
          throw new Error('未登录，无法使用语音识别功能');
        }

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('language', language);

        const response = await fetchBinary('/voice/asr', {
          method: 'POST',
          body: formData,
        });

        const result = JSON.parse(await response.text());
        return result.transcript as string;
      } catch (err) {
        const message = err instanceof Error ? err.message : '语音识别失败';
        setError(message);
        throw new Error(message);
      } finally {
        setIsTranscribing(false);
      }
    },
    []
  );

  return {
    transcribe,
    isTranscribing,
    error,
  };
}