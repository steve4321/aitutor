'use client';

import { useState, useCallback, useRef } from 'react';

interface VoiceState {
  isRecording: boolean;
  isPlaying: boolean;
  audioLevel: number;
}

export function useVoice() {
  const [state, setState] = useState<VoiceState>({
    isRecording: false,
    isPlaying: false,
    audioLevel: 0,
  });
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const stopResolveRef = useRef<((blob: Blob) => void) | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        stopResolveRef.current?.(blob);
        stopResolveRef.current = null;
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setState((prev) => ({ ...prev, isRecording: true }));
    } catch {
      setState((prev) => ({ ...prev, isRecording: false }));
    }
  }, []);

  const stopRecording = useCallback((): Promise<Blob | null> => {
    if (!mediaRecorderRef.current || !state.isRecording) {
      return Promise.resolve(null);
    }

    const promise = new Promise<Blob | null>((resolve) => {
      stopResolveRef.current = resolve;
    });

    mediaRecorderRef.current.stop();
    setState((prev) => ({ ...prev, isRecording: false, audioLevel: 0 }));

    return promise;
  }, [state.isRecording]);

  const playAudio = useCallback(async (url: string) => {
    try {
      const audio = new Audio(url);
      setState((prev) => ({ ...prev, isPlaying: true }));
      audio.onended = () => {
        setState((prev) => ({ ...prev, isPlaying: false }));
      };
      await audio.play();
    } catch {
      setState((prev) => ({ ...prev, isPlaying: false }));
    }
  }, []);

  const speak = useCallback((text: string, lang = 'en-US') => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.onstart = () => setState((prev) => ({ ...prev, isPlaying: true }));
    utterance.onend = () => setState((prev) => ({ ...prev, isPlaying: false }));
    window.speechSynthesis.speak(utterance);
  }, []);

  return {
    ...state,
    startRecording,
    stopRecording,
    playAudio,
    speak,
  };
}
