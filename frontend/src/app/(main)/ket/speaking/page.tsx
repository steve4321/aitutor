'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, Square, Play, Pause, ChevronLeft, CheckCircle2, Volume2, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SpeakingTopic {
  id: string;
  type: 'read' | 'describe' | 'respond';
  title: string;
  prompt: string;
  imageUrl?: string;
}

const TOPICS: SpeakingTopic[] = [
  {
    id: '1',
    type: 'read',
    title: '朗读短文',
    prompt: '请朗读以下短文，注意发音和语调。',
    imageUrl: undefined,
  },
  {
    id: '2',
    type: 'describe',
    title: '描述图片',
    prompt: '请描述这张图片，包括图中的人物、活动和场景。',
    imageUrl: undefined,
  },
  {
    id: '3',
    type: 'respond',
    title: '回答问题',
    prompt: '请回答以下问题。用完整的句子表达。',
    imageUrl: undefined,
  },
];

const SAMPLE_TEXT = 'Last weekend was wonderful. I went to the park with my family. We had a picnic and played games. The weather was perfect and everyone was happy.';

const QUESTIONS = [
  'What did you do last weekend?',
  'What is your favorite hobby?',
  'Tell me about your best friend.',
];

export default function SpeakingPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecording, setHasRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [timeLeft, setTimeLeft] = useState(60);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const topic = TOPICS[currentIndex];

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  useEffect(() => {
    if (isRecording && timeLeft > 0) {
      timerRef.current = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    } else if (timeLeft === 0 && isRecording) {
      stopRecording();
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isRecording, timeLeft, stopRecording]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setRecordedBlob(blob);
        setHasRecording(true);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setTimeLeft(60);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const playRecording = () => {
    if (recordedBlob && audioRef.current) {
      audioRef.current.src = URL.createObjectURL(recordedBlob);
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const stopPlaying = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const handleSubmit = () => {
    setShowResult(true);
    setIsRecording(false);
  };

  const handleNext = () => {
    if (currentIndex < TOPICS.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setRecordedBlob(null);
      setHasRecording(false);
      setShowResult(false);
      setTimeLeft(60);
    }
  };

  const handleReset = () => {
    setRecordedBlob(null);
    setHasRecording(false);
    setShowResult(false);
    setTimeLeft(60);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderContent = () => {
    switch (topic.type) {
      case 'read':
        return (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 dark:border-slate-700 dark:bg-slate-900">
            <p className="whitespace-pre-line text-lg leading-relaxed text-slate-700 dark:text-slate-200">
              {SAMPLE_TEXT}
            </p>
          </div>
        );
      case 'describe':
        return (
          <div className="flex h-48 items-center justify-center rounded-xl border border-slate-200 bg-slate-100 dark:border-slate-700 dark:bg-slate-800">
            <div className="text-center text-slate-400">
              <p className="mb-2">图片描述区域</p>
              <p className="text-sm">请描述图中的人物、活动和场景</p>
            </div>
          </div>
        );
      case 'respond':
        return (
          <div className="space-y-4">
            {QUESTIONS.map((q, i) => (
              <div
                key={i}
                className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
              >
                <p className="font-medium text-slate-900 dark:text-white">{q}</p>
              </div>
            ))}
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      <audio ref={audioRef} onEnded={() => setIsPlaying(false)} />

      <div className="mx-auto max-w-3xl px-4 py-8">
        <header className="mb-6 flex items-center gap-4">
          <a
            href="/ket"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
          >
            <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
          </a>
          <div className="flex items-center gap-3">
            <Mic className="h-7 w-7 text-rose-600 dark:text-rose-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">口语练习</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                第 {currentIndex + 1} / {TOPICS.length} 题
              </p>
            </div>
          </div>
        </header>

        <div className="mb-6 flex h-2 gap-1">
          {TOPICS.map((t, i) => (
            <div
              key={t.id}
              className={cn(
                'h-full flex-1 rounded-full transition-all',
                i < currentIndex
                  ? 'bg-rose-500'
                  : i === currentIndex
                    ? 'bg-rose-500'
                    : 'bg-slate-200 dark:bg-slate-700'
              )}
            />
          ))}
        </div>

        <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-2 font-semibold text-slate-900 dark:text-white">{topic.title}</h2>
          <p className="mb-4 text-sm text-slate-600 dark:text-slate-300">{topic.prompt}</p>
          {renderContent()}
        </div>

        <div className="mb-6 flex flex-col items-center gap-6 rounded-2xl border border-slate-200 bg-white p-8 dark:border-slate-700 dark:bg-slate-800">
          <div
            className={cn(
              'relative flex h-24 w-24 items-center justify-center rounded-full transition-all',
              isRecording
                ? 'animate-pulse bg-rose-100 dark:bg-rose-900/30'
                : 'bg-slate-100 dark:bg-slate-800'
            )}
          >
            {isRecording ? (
              <Square
                className="h-8 w-8 text-rose-600 dark:text-rose-400"
                onClick={stopRecording}
              />
            ) : (
              <Mic
                className={cn(
                  'h-10 w-10',
                  hasRecording
                    ? 'text-rose-600 dark:text-rose-400'
                    : 'text-slate-400 dark:text-slate-500'
                )}
                onClick={!showResult && !isPlaying ? startRecording : undefined}
              />
            )}
          </div>

          {isRecording && (
            <div className="text-center">
              <p className="text-2xl font-bold text-rose-600 dark:text-rose-400">
                {formatTime(timeLeft)}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">剩余时间</p>
            </div>
          )}

          {!isRecording && hasRecording && !showResult && (
            <div className="flex gap-4">
              <button
                onClick={isPlaying ? stopPlaying : playRecording}
                className="flex items-center gap-2 rounded-xl bg-slate-100 px-6 py-3 font-medium text-slate-700 transition-all hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
              >
                {isPlaying ? (
                  <>
                    <Pause className="h-5 w-5" />
                    停止
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    播放录音
                  </>
                )}
              </button>
              <button
                onClick={handleReset}
                className="flex items-center gap-2 rounded-xl bg-slate-100 px-6 py-3 font-medium text-slate-700 transition-all hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
              >
                <RefreshCw className="h-5 w-5" />
                重新录制
              </button>
            </div>
          )}

          {showResult && (
            <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="h-6 w-6" />
              <span className="font-semibold">录音已提交！</span>
            </div>
          )}

          {!isRecording && !showResult && (
            <p className="text-center text-sm text-slate-500 dark:text-slate-400">
              点击麦克风开始录音
            </p>
          )}
        </div>

        <div className="flex gap-4">
          {!showResult ? (
            <>
              <button
                onClick={handleReset}
                disabled={!hasRecording}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 py-3 font-medium text-slate-600 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                重置
              </button>
              <button
                onClick={handleSubmit}
                disabled={!hasRecording || isRecording}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-rose-600 py-3 font-medium text-white transition-all hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                提交录音
              </button>
            </>
          ) : currentIndex < TOPICS.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-rose-600 py-3 font-medium text-white transition-all hover:bg-rose-700"
            >
              下一题
            </button>
          ) : (
            <a
              href="/ket"
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-medium text-white transition-all hover:bg-emerald-700"
            >
              完成练习
            </a>
          )}
        </div>
      </div>
    </div>
  );
}