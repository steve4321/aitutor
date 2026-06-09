'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { ChatPanel } from '@/components/chat/chat-panel';
import { ChatInput } from '@/components/chat/chat-input';
import { LessonContent } from '@/components/lesson/lesson-content';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import type { LessonDetailResponse, LessonProgressResponse } from '@/types/course';

interface SessionResponse {
  id: string;
  session_type: string;
  subject: string;
  lesson_id: string | null;
  started_at: string;
}

export default function LessonPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  const lessonId = params.lessonId as string;

  const [lesson, setLesson] = useState<LessonDetailResponse | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function fetchLesson() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.get<LessonDetailResponse>(`/lessons/${lessonId}`);
        if (cancelled) return;
        setLesson(data);
        setCompleted(data.status === 'completed');
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : '加载课程失败');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchLesson();
    return () => { cancelled = true; };
  }, [lessonId]);

  useEffect(() => {
    if (!lesson) return;
    let cancelled = false;

    async function createSession() {
      try {
        const session = await api.post<SessionResponse>('/sessions', {
          session_type: 'lesson',
          subject: 'math',
          lesson_id: lessonId,
        });
        if (!cancelled) {
          setSessionId(session.id);
        }
      } catch {
        // Session creation is non-critical — chat won't work but lesson still renders
      }
    }

    createSession();
    return () => { cancelled = true; };
  }, [lesson, lessonId]);

  useEffect(() => {
    return () => {
      if (sessionId) {
        api.post(`/sessions/${sessionId}/close`).catch(() => {});
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const handleAnswer = useCallback((_problemIndex: number, _isCorrect: boolean) => {}, []);

  const handleComplete = useCallback(async () => {
    if (!lesson || completing || completed) return;
    setCompleting(true);
    try {
      const res = await api.post<LessonProgressResponse>(`/lessons/${lessonId}/progress`, {
        status: 'completed',
      });

      if (sessionId) {
        await api.post(`/sessions/${sessionId}/close`).catch(() => {});
      }

      setCompleted(true);

      if (lesson.next_lesson_id) {
        setTimeout(() => {
          router.push(ROUTES.LESSON(courseId, lesson.next_lesson_id!));
        }, 1500);
      } else {
        setTimeout(() => {
          router.push(ROUTES.COURSE_DETAIL(courseId));
        }, 1500);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '完成课程失败');
    } finally {
      setCompleting(false);
    }
  }, [lesson, lessonId, courseId, sessionId, completing, completed, router]);

  const handlePrevLesson = useCallback(() => {
    if (!lesson?.prev_lesson_id) return;
    router.push(ROUTES.LESSON(courseId, lesson.prev_lesson_id!));
  }, [lesson, courseId, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-background)]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-[var(--color-primary)]" />
          <p className="text-sm text-[var(--color-muted-foreground)]">加载课程中...</p>
        </div>
      </div>
    );
  }

  if (error && !lesson) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-background)]">
        <div className="flex flex-col items-center gap-3 text-center px-6">
          <AlertCircle className="h-10 w-10 text-[var(--color-danger)]" />
          <p className="text-base font-medium text-[var(--color-foreground)]">{error}</p>
          <Button variant="outline" onClick={() => router.push(ROUTES.COURSE_DETAIL(courseId))}>
            返回课程
          </Button>
        </div>
      </div>
    );
  }

  if (!lesson) return null;

  return (
    <div className="flex min-h-screen flex-col bg-[var(--color-background)]">
      <header className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[var(--color-surface)]/95 backdrop-blur-sm">
        <div className="flex items-center gap-3 px-4 py-3">
          <button
            onClick={() => router.push(ROUTES.COURSE_DETAIL(courseId))}
            className="flex h-9 w-9 items-center justify-center rounded-full hover:bg-[var(--color-primary-light)]"
          >
            <ArrowLeft className="h-5 w-5 text-[var(--color-foreground)]" />
          </button>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg font-bold text-[var(--color-foreground)] truncate">
              {lesson.title}
            </h1>
            <p className="text-xs text-[var(--color-muted-foreground)]">
              {lesson.unit_title} · {lesson.course_name}
            </p>
          </div>
          {lesson.estimated_minutes && (
            <span className="shrink-0 text-xs text-[var(--color-muted-foreground)] bg-[var(--color-surface-muted)] px-2 py-1 rounded-full">
              约 {lesson.estimated_minutes} 分钟
            </span>
          )}
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-4 p-4 pb-24">
        {completed && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-[var(--color-success-light)] border border-[var(--color-success)]/30 animate-slide-up">
            <CheckCircle2 className="h-5 w-5 text-[var(--color-success)] shrink-0" />
            <p className="text-sm font-medium text-[var(--color-success)]">
              课程已完成！{lesson.next_lesson_id ? '即将跳转下一课...' : '即将返回课程...'}
            </p>
          </div>
        )}

        {error && lesson && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-[var(--color-danger-light)] border border-[var(--color-danger)]/30">
            <AlertCircle className="h-5 w-5 text-[var(--color-danger)] shrink-0" />
            <p className="text-sm text-[var(--color-danger)]">{error}</p>
          </div>
        )}

        <LessonContent
          sections={lesson.content.sections}
          onAnswer={handleAnswer}
        />

        <div className="mt-2">
          <h3 className="text-base font-bold text-[var(--color-foreground)] mb-2">AI 老师</h3>
          <ChatPanel
            messages={[]}
            className="h-48 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)]"
          />
          <div className="mt-2">
            <ChatInput onSend={() => {}} disabled placeholder="AI 对话功能即将上线..." />
          </div>
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 border-t border-[var(--color-border)] bg-[var(--color-surface)]/95 backdrop-blur-sm safe-area-inset-bottom">
        <div className="flex gap-3 p-4">
          <Button
            variant="outline"
            className="flex-1"
            disabled={!lesson.prev_lesson_id}
            onClick={handlePrevLesson}
          >
            上一课
          </Button>
          <Button
            className="flex-1"
            disabled={completing || completed}
            onClick={handleComplete}
          >
            {completing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                提交中...
              </>
            ) : completed ? (
              '已完成'
            ) : (
              '完成课程'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
