'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChatPanel } from '@/components/chat/chat-panel';
import { ChatInput } from '@/components/chat/chat-input';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Clock, BookOpen, AlertCircle, CheckCircle2, Target, Lightbulb, AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';
import type { LessonContent } from '@/types/course';

interface Lesson {
  id: string;
  unit_id: string;
  title: string;
  lesson_type: string | null;
  estimated_minutes: number | null;
  code: string | null;
  content: LessonContent | null;
}

interface Course {
  id: string;
  name: string;
  subject: string;
}

interface ProgressResponse {
  message: string;
  progress: number;
  xp_earned: number;
}

export default function LessonPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  const lessonId = params.lessonId as string;

  const [loading, setLoading] = useState(true);
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);

  useEffect(() => {
    setLoading(true);
    setLesson(null);
    setCourse(null);
    setError(null);

    const fetchData = async () => {
      try {
        const [lessonRes, courseRes] = await Promise.all([
          api.get<Lesson>(`/lessons/${lessonId}`),
          api.get<Course>(`/courses/${courseId}`),
        ]);
        setLesson(lessonRes);
        setCourse(courseRes);
      } catch {
        setError('加载课程失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [courseId, lessonId]);

  const handleComplete = async () => {
    if (!lesson || completing || completed) return;
    setCompleting(true);
    setError(null);
    try {
      const res = await api.post<ProgressResponse>(`/lessons/${lessonId}/progress`, {
        status: 'completed',
      });
      setXpEarned(res.xp_earned);
      setCompleted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '完成课程失败');
    } finally {
      setCompleting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-6 w-32 bg-muted rounded animate-pulse" />
        <div className="h-40 bg-muted rounded-xl animate-pulse" />
        <div className="h-64 bg-muted rounded-xl animate-pulse" />
      </div>
    );
  }

  if (error && !lesson) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
        <p className="text-muted-foreground">{error}</p>
        <button
          onClick={() => router.push(`/courses/${courseId}`)}
          className="mt-4 text-[var(--color-primary)] hover:underline"
        >
          返回课程
        </button>
      </div>
    );
  }

  if (!lesson) return null;

  const content = lesson.content;

  return (
    <div className="space-y-4">
      <button
        onClick={() => router.push(`/courses/${courseId}`)}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>{course?.name}</span>
      </button>

      <div className="bg-gradient-to-br from-[var(--color-primary)]/10 to-[var(--color-secondary)]/10 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">{lesson.title}</h1>
            <div className="flex items-center gap-2 mt-2">
              {lesson.lesson_type && (
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[var(--color-primary)]/20 text-[var(--color-primary)]">
                  {lesson.lesson_type === 'practice' ? '练习课' : lesson.lesson_type === 'lecture' ? '讲授课' : lesson.lesson_type}
                </span>
              )}
              {lesson.estimated_minutes && (
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  {lesson.estimated_minutes}min
                </span>
              )}
            </div>
          </div>
          <BookOpen className="w-8 h-8 text-[var(--color-primary)]/40" />
        </div>
      </div>

      {completed && (
        <div className="flex items-center gap-3 p-3 rounded-xl bg-[var(--color-success)]/10 border border-[var(--color-success)]/30">
          <CheckCircle2 className="w-5 h-5 text-[var(--color-success)] shrink-0" />
          <div>
            <p className="text-sm font-medium text-[var(--color-success)]">课程已完成！</p>
            {xpEarned > 0 && (
              <p className="text-xs text-[var(--color-success)]">+{xpEarned} XP</p>
            )}
          </div>
        </div>
      )}

      {content && (
        <div className="space-y-3">
          {content.objectives.length > 0 && (
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-5 h-5 text-[var(--color-primary)]" />
                <h2 className="font-semibold text-foreground">学习目标</h2>
              </div>
              <ul className="space-y-1.5">
                {content.objectives.map((obj, i) => (
                  <li key={i} className="text-sm text-foreground/90 flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-0.5">•</span>
                    <span>{obj}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {content.summary.key_points.length > 0 && (
            <Card className="p-4 bg-[var(--color-primary)]/5 border-[var(--color-primary)]/20">
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="w-5 h-5 text-[var(--color-primary)]" />
                <h2 className="font-semibold text-foreground">核心要点</h2>
              </div>
              <ul className="space-y-1.5">
                {content.summary.key_points.map((point, i) => (
                  <li key={i} className="text-sm text-foreground/90 flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-0.5">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {content.summary.common_mistakes.length > 0 && (
            <Card className="p-4 bg-[var(--color-warning)]/5 border-[var(--color-warning)]/30">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-[var(--color-warning)]" />
                <h2 className="font-semibold text-foreground">常见错误</h2>
              </div>
              <ul className="space-y-1.5">
                {content.summary.common_mistakes.map((mistake, i) => (
                  <li key={i} className="text-sm text-foreground/90 flex items-start gap-2">
                    <span className="text-[var(--color-warning)] mt-0.5">•</span>
                    <span>{mistake}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}

      <div className="space-y-3">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">
            点击下方对话框开始学习，AI 老师会引导你完成这节课。
          </p>
        </Card>

        <ChatPanel messages={[]} className="h-64 rounded-xl border border-border bg-muted/50" />
        <ChatInput onSend={() => {}} />

        {error && (
          <p className="text-sm text-[var(--color-danger)]">{error}</p>
        )}

        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={() => router.push(`/courses/${courseId}`)}>
            返回课程
          </Button>
          <Button
            className="flex-1"
            onClick={handleComplete}
            disabled={completing || completed}
          >
            {completing ? '提交中...' : completed ? '已完成' : '完成课程'}
          </Button>
        </div>
      </div>
    </div>
  );
}
