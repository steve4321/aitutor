'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChatPanel } from '@/components/chat/chat-panel';
import { ChatInput } from '@/components/chat/chat-input';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Clock, BookOpen, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface Lesson {
  id: string;
  unit_id: string;
  title: string;
  lesson_type: string | null;
  estimated_minutes: number | null;
  code: string | null;
}

interface Course {
  id: string;
  name: string;
  subject: string;
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

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-6 w-32 bg-muted rounded animate-pulse" />
        <div className="h-40 bg-muted rounded-xl animate-pulse" />
        <div className="h-64 bg-muted rounded-xl animate-pulse" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
        <p className="text-muted-foreground">{error}</p>
        <button
          onClick={() => {
            setError(null);
            setLoading(true);
          }}
          className="mt-4 text-[var(--color-primary)] hover:underline"
        >
          重试
        </button>
        <button onClick={() => router.back()} className="mt-2 block mx-auto text-muted-foreground hover:underline">
          返回
        </button>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Lesson not found</p>
        <button onClick={() => router.back()} className="mt-4 text-[var(--color-primary)] hover:underline">
          Go back
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <button onClick={() => router.push(`/courses/${courseId}`)} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
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

      <div className="space-y-3">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">
            点击下方对话框开始学习，AI 老师会引导你完成这节课。
          </p>
        </Card>

        <ChatPanel messages={[]} className="h-64 rounded-xl border border-border bg-muted/50" />
        <ChatInput onSend={() => {}} />

        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={() => router.push(`/courses/${courseId}`)}>返回课程</Button>
          <Button className="flex-1">完成课程</Button>
        </div>
      </div>
    </div>
  );
}
