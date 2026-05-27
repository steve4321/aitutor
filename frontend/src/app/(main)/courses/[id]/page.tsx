'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Play, CheckCircle, Lock, ChevronDown, ChevronRight } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import { cn } from '@/lib/utils';

interface Lesson {
  id: string;
  title: string;
  status: 'locked' | 'in_progress' | 'completed';
}

interface Unit {
  id: string;
  title: string;
  lessons: Lesson[];
}

interface Course {
  id: string;
  title: string;
  description: string;
  cover_url: string;
  category: string;
  is_enrolled: boolean;
  progress: number;
  units: Unit[];
  current_lesson_id: string | null;
}

function CourseHeaderSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-40 bg-muted rounded-xl mb-4" />
      <div className="h-8 w-2/3 bg-muted rounded mb-2" />
      <div className="h-4 w-full bg-muted rounded" />
    </div>
  );
}

function UnitSkeleton() {
  return (
    <div className="border border-border rounded-xl overflow-hidden animate-pulse">
      <div className="p-4 flex items-center justify-between">
        <div className="h-6 w-1/2 bg-muted rounded" />
        <div className="w-6 h-6 bg-muted rounded" />
      </div>
    </div>
  );
}

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [course, setCourse] = useState<Course | null>(null);
  const [expandedUnits, setExpandedUnits] = useState<Set<string>>(new Set());
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const res = await api.get<Course>(`/courses/${courseId}`);
        setCourse(res);
        if (res.units.length > 0) {
          setExpandedUnits(new Set(res.units.map(u => u.id)));
        }
      } catch (err) {
        console.error('Failed to fetch course:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCourse();
  }, [courseId]);

  const toggleUnit = (unitId: string) => {
    setExpandedUnits(prev => {
      const next = new Set(prev);
      if (next.has(unitId)) {
        next.delete(unitId);
      } else {
        next.add(unitId);
      }
      return next;
    });
  };

  const handleEnroll = async () => {
    if (!course) return;
    setEnrolling(true);
    try {
      await api.post(`/courses/${courseId}/enroll`, {});
      setCourse({ ...course, is_enrolled: true });
    } catch (err) {
      console.error('Failed to enroll:', err);
    } finally {
      setEnrolling(false);
    }
  };

  const handleContinue = () => {
    if (course?.current_lesson_id) {
      router.push(`${ROUTES.COURSES}/${courseId}/lessons/${course.current_lesson_id}`);
    }
  };

  const getLessonIcon = (status: Lesson['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress':
        return <Play className="w-5 h-5 text-[var(--color-primary)]" />;
      case 'locked':
        return <Lock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>
        <CourseHeaderSkeleton />
        <UnitSkeleton />
        <UnitSkeleton />
        <UnitSkeleton />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Course not found</p>
        <button onClick={() => router.push(ROUTES.COURSES)} className="mt-4 text-[var(--color-primary)] hover:underline">
          Back to Courses
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back</span>
      </button>

      <div className="bg-gradient-to-br from-[var(--color-primary)]/10 to-[var(--color-secondary)]/10 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[var(--color-primary)]/20 text-[var(--color-primary)]">
            {course.category}
          </span>
        </div>
        <h1 className="text-2xl font-bold text-foreground mb-2">{course.title}</h1>
        <p className="text-muted-foreground">{course.description}</p>

        {course.is_enrolled && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-muted-foreground">Your Progress</span>
              <span className="font-medium text-foreground">{course.progress}%</span>
            </div>
            <div className="h-2 bg-background rounded-full overflow-hidden">
              <div
                className="h-full bg-[var(--color-primary)] rounded-full transition-all"
                style={{ width: `${course.progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {!course.is_enrolled ? (
        <button
          onClick={handleEnroll}
          disabled={enrolling}
          className={cn(
            'w-full py-3 bg-[var(--color-primary)] text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2',
            enrolling ? 'opacity-50 cursor-not-allowed' : 'hover:bg-[var(--color-primary)]/90'
          )}
        >
          {enrolling ? 'Enrolling...' : 'Enroll in Course'}
        </button>
      ) : course.current_lesson_id ? (
        <button
          onClick={handleContinue}
          className="w-full py-3 bg-[var(--color-primary)] text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2 hover:bg-[var(--color-primary)]/90"
        >
          <Play className="w-4 h-4" />
          Continue Learning
        </button>
      ) : null}

      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Course Content</h2>
        {course.units.map((unit) => (
          <div key={unit.id} className="border border-border rounded-xl overflow-hidden">
            <button
              onClick={() => toggleUnit(unit.id)}
              className="w-full p-4 flex items-center justify-between hover:bg-accent/50 transition-colors"
            >
              <span className="font-medium text-foreground">{unit.title}</span>
              {expandedUnits.has(unit.id) ? (
                <ChevronDown className="w-5 h-5 text-muted-foreground" />
              ) : (
                <ChevronRight className="w-5 h-5 text-muted-foreground" />
              )}
            </button>

            {expandedUnits.has(unit.id) && (
              <div className="border-t border-border">
                {unit.lessons.map((lesson, index) => (
                  <div
                    key={lesson.id}
                    className={cn(
                      'flex items-center gap-3 p-4 hover:bg-accent/50 transition-colors',
                      index < unit.lessons.length - 1 && 'border-b border-border'
                    )}
                  >
                    {getLessonIcon(lesson.status)}
                    <span className={cn(
                      'flex-1',
                      lesson.status === 'locked' && 'text-muted-foreground'
                    )}>
                      {lesson.title}
                    </span>
                    {lesson.status !== 'locked' && (
                      <button
                        onClick={() => router.push(`${ROUTES.COURSES}/${courseId}/lessons/${lesson.id}`)}
                        className="text-sm text-[var(--color-primary)] hover:underline"
                      >
                        {lesson.status === 'completed' ? 'Review' : 'Start'}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}