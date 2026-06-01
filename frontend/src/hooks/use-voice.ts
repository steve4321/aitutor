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
  const audioContextRef = useRef<AudioContext | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        stream.getTracks().forEach((track) => track.stop());
        return blob;
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setState((prev) => ({ ...prev, isRecording: true }));
    } catch {
      // silently ignore
    }
  }, []);

  const stopRecording = useCallback((): Blob | null => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      setState((prev) => ({ ...prev, isRecording: false, audioLevel: 0 }));
    }
    return null;
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
