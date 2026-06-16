'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Mic, ChevronLeft, Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type { KETSpeakingTask, KETSpeakingScoreResponse } from '@/types/ket';

export default function SpeakingPage() {
  const [selectedTask, setSelectedTask] = useState<KETSpeakingTask | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [hasRecording, setHasRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [transcript, setTranscript] = useState('');
  const [useTextFallback, setUseTextFallback] = useState(false);
  const [recognitionError, setRecognitionError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['ket', 'speaking', 'tasks'],
    queryFn: () => api.get<KETSpeakingTask[]>('/ket/speaking/tasks', { limit: '20' }),
  });

  const submitMutation = useMutation({
    mutationFn: (body: { task_id: string; transcript: string; audio_duration_sec: number }) =>
      api.post<KETSpeakingScoreResponse>('/ket/speaking/submit', body),
  });

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

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    clearTimer();
    setIsRecording(false);

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, [clearTimer]);

  const startRecording = useCallback(async () => {
    setRecognitionError(null);
    setRecordedBlob(null);
    setHasRecording(false);
    setSeconds(0);
    setTranscript('');

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
        cleanupStream();
      };

      recorder.start();
      setIsRecording(true);

      timerRef.current = setInterval(() => {
        setSeconds((prev) => {
          if (selectedTask && prev >= selectedTask.expected_duration_sec - 1) {
            stopRecording();
            return selectedTask.expected_duration_sec;
          }
          return prev + 1;
        });
      }, 1000);

      if (!useTextFallback) {
        const SR = window.SpeechRecognition ?? window.webkitSpeechRecognition;
        if (SR) {
          const recognition = new SR();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
              const transcriptPiece = event.results[i][0].transcript;
              if (event.results[i].isFinal) {
                finalTranscript += transcriptPiece;
              } else {
                interimTranscript += transcriptPiece;
              }
            }
            setTranscript((prev) => {
              const base = prev.replace(/\[.*?\]$/, '').trim();
              return finalTranscript
                ? (base ? base + ' ' : '') + finalTranscript + (interimTranscript ? ` [${interimTranscript}]` : '')
                : prev;
            });
          };

          recognition.onerror = (event) => {
            if (event.error !== 'no-speech') {
              console.warn('Speech recognition error:', event.error);
            }
          };

          recognition.onend = () => {
            if (isRecording) {
              try {
                recognition.start();
              } catch {
                // Recognition might already be stopped
              }
            }
          };

          recognition.start();
          recognitionRef.current = recognition;
        }
      }
    } catch (err) {
      cleanupStream();
      if (err instanceof DOMException && err.name === 'NotAllowedError') {
        setRecognitionError('麦克风权限被拒绝，请在浏览器设置中允许访问麦克风。');
      } else {
        setRecognitionError('无法启动录音，请检查麦克风是否正常连接。');
      }
    }
  }, [selectedTask, stopRecording, cleanupStream, useTextFallback, isRecording]);

  const resetRecording = useCallback(() => {
    stopRecording();
    setRecordedBlob(null);
    setHasRecording(false);
    setSeconds(0);
    setTranscript('');
    setRecognitionError(null);
  }, [stopRecording]);

  const handleSubmit = () => {
    if (!selectedTask) return;

    const finalTranscript = transcript.trim();
    if (!finalTranscript) return;

    submitMutation.mutate({
      task_id: selectedTask.id,
      transcript: finalTranscript,
      audio_duration_sec: seconds,
    });
  };

  const handleBackToTasks = () => {
    resetRecording();
    setSelectedTask(null);
  };

  useEffect(() => {
    return () => {
      clearTimer();
      cleanupStream();
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [clearTimer, cleanupStream]);

  const formatTime = (s: number) => {
    const min = Math.floor(s / 60);
    const sec = s % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  if (tasksLoading) {
    return (
      <div className="space-y-6">
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
                <p className="text-sm text-slate-500 dark:text-slate-400">KET 口语练习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Loader2 className="h-8 w-8 animate-spin text-rose-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">加载题目中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="space-y-6">
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
                <p className="text-sm text-slate-500 dark:text-slate-400">KET 口语练习</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Mic className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">暂无题目</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              口语题库正在开发中<br />
              请稍后再来练习
            </p>
            <a
              href="/ket"
              className="flex items-center gap-2 rounded-xl bg-rose-600 px-6 py-3 font-medium text-white transition-all hover:bg-rose-700"
            >
              返回 KET 主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (submitMutation.data) {
    const score = submitMutation.data;
    const maxScore = 5;
    const overallPercent = (score.band / maxScore) * 100;

    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <button
              onClick={handleBackToTasks}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </button>
            <div className="flex items-center gap-3">
              <Mic className="h-7 w-7 text-rose-600 dark:text-rose-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">口语练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">评分结果</p>
              </div>
            </div>
          </header>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-6 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">总体评分</p>
              <p className="mt-2 text-5xl font-bold text-rose-600 dark:text-rose-400">
                {score.band.toFixed(1)}
              </p>
              <p className="text-sm text-slate-400">满分 5.0</p>
            </div>

            <div className="mb-6 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className="h-full rounded-full bg-rose-500 transition-all"
                style={{ width: `${overallPercent}%` }}
              />
            </div>

            <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 dark:border-rose-800 dark:bg-rose-950">
              <p className="font-medium text-rose-900 dark:text-rose-100">AI 评语</p>
              <p className="mt-2 text-sm text-rose-800 dark:text-rose-200 whitespace-pre-wrap">
                {score.feedback}
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-center gap-4">
            <button
              onClick={handleBackToTasks}
              className="flex items-center gap-2 rounded-xl border border-slate-200 px-6 py-3 font-medium text-slate-700 transition-all hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              再练一次
            </button>
            <a
              href="/ket"
              className="flex items-center gap-2 rounded-xl bg-rose-600 px-6 py-3 font-medium text-white transition-all hover:bg-rose-700"
            >
              返回 KET 主页
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (selectedTask) {
    const isSpeechRecognitionAvailable =
      typeof window !== 'undefined' &&
      ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);

    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <button
              onClick={handleBackToTasks}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </button>
            <div className="flex items-center gap-3">
              <Mic className="h-7 w-7 text-rose-600 dark:text-rose-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">口语练习</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {selectedTask.difficulty === 'easy' ? '简单' : selectedTask.difficulty === 'medium' ? '中等' : '困难'}
                </p>
              </div>
            </div>
          </header>

          <div className="rounded-xl bg-rose-50 border border-rose-200 px-4 py-3 dark:bg-rose-950 dark:border-rose-800">
            <p className="font-medium text-rose-900 dark:text-rose-100">{selectedTask.topic}</p>
            <p className="mt-2 text-sm text-rose-800 dark:text-rose-200">{selectedTask.question}</p>
            <p className="mt-2 text-xs text-rose-600 dark:text-rose-400">
              建议时长: {Math.floor(selectedTask.expected_duration_sec / 60)}分{selectedTask.expected_duration_sec % 60}秒
            </p>
          </div>

          {recognitionError && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 dark:border-red-800 dark:bg-red-950">
              <p className="flex items-center gap-2 text-sm text-red-700 dark:text-red-300">
                <AlertCircle className="h-4 w-4" />
                {recognitionError}
              </p>
            </div>
          )}

          <div className="flex flex-col items-center gap-4 py-6">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={!!recognitionError && !isRecording}
              className={cn(
                'relative flex h-20 w-20 items-center justify-center rounded-full transition-all',
                isRecording
                  ? 'bg-red-500 text-white shadow-lg shadow-red-200'
                  : 'bg-rose-600 text-white hover:bg-rose-700',
                recognitionError && !isRecording && 'cursor-not-allowed opacity-50'
              )}
            >
              {isRecording ? (
                <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
              ) : (
                <Mic className="h-8 w-8" />
              )}
              {isRecording && (
                <span className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-30" />
              )}
            </button>

            <div className="text-center">
              <p className="text-2xl font-mono font-bold text-slate-900 dark:text-white">
                {formatTime(seconds)}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {isRecording
                  ? '录音中...'
                  : hasRecording
                    ? '点击麦克风重录'
                    : '点击开始录音'}
              </p>
            </div>

            {hasRecording && !isRecording && (
              <div className="w-full space-y-4">
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
                  <p className="mb-2 text-sm font-medium text-slate-700 dark:text-slate-300">
                    语音识别结果:
                  </p>
                  {isSpeechRecognitionAvailable && !useTextFallback ? (
                    <p className="text-sm text-slate-600 dark:text-slate-400 whitespace-pre-wrap">
                      {transcript || '（未识别到语音，请使用文本输入）'}
                    </p>
                  ) : (
                    <textarea
                      value={transcript}
                      onChange={(e) => setTranscript(e.target.value)}
                      placeholder="请输入你说的内容..."
                      className="w-full rounded-lg border border-slate-300 bg-white p-3 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-white"
                      rows={4}
                    />
                  )}
                </div>

                <div className="flex justify-center gap-3">
                  <button
                    onClick={resetRecording}
                    className="flex items-center gap-1.5 rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
                  >
                    重录
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={!transcript.trim() || submitMutation.isPending}
                    className={cn(
                      'flex items-center gap-1.5 rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium text-white transition-all',
                      transcript.trim() && !submitMutation.isPending
                        ? 'hover:bg-rose-700'
                        : 'cursor-not-allowed opacity-50'
                    )}
                  >
                    {submitMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        评分中...
                      </>
                    ) : (
                      '提交评分'
                    )}
                  </button>
                </div>

                {!isSpeechRecognitionAvailable && (
                  <p className="text-center text-xs text-slate-500 dark:text-slate-400">
                    您的浏览器不支持语音识别，已启用文本输入模式
                  </p>
                )}
              </div>
            )}
          </div>

          {submitMutation.isError && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
              <p className="text-sm text-red-700 dark:text-red-300">提交失败，请稍后再试</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
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
              <p className="text-sm text-slate-500 dark:text-slate-400">选择口语任务</p>
            </div>
          </div>
        </header>

        <div className="space-y-4">
          {tasks.map((task) => (
            <button
              key={task.id}
              onClick={() => setSelectedTask(task)}
              className="w-full rounded-2xl border border-slate-200 bg-white p-6 text-left transition-all hover:border-rose-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <span className={cn(
                    'inline-block rounded-full px-3 py-1 text-xs font-medium',
                    task.difficulty === 'easy'
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200'
                      : task.difficulty === 'medium'
                        ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  )}>
                    {task.difficulty === 'easy' ? '简单' : task.difficulty === 'medium' ? '中等' : '困难'}
                  </span>
                  <p className="mt-3 font-medium text-slate-900 dark:text-white">{task.topic}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{task.question}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}