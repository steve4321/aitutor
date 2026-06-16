'use client';

import { useState, useMemo, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { ArrowLeft, Play, ChevronDown, ChevronRight, BookOpen, Loader2, Check } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import { renderWithLatex } from '@/lib/render-content';
import { Button } from '@/components/ui/button';
import type { Course, Unit, Lesson, UnitWithLessons } from '@/types/course';

const SUBJECT_LABELS: Record<string, string> = {
  math: 'AMC',
  english: 'KET',
  chinese: '语文',
};

function SkeletonBlock() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-32 bg-muted rounded-xl" />
      <div className="h-8 w-2/3 bg-muted rounded" />
      <div className="h-4 w-full bg-muted rounded" />
      <div className="h-12 bg-muted rounded-xl" />
      <div className="h-12 bg-muted rounded-xl" />
    </div>
  );
}

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;

  const [expandedUnits, setExpandedUnits] = useState<Set<string>>(new Set());
  const [isEnrolled, setIsEnrolled] = useState(false);

  const enrollMutation = useMutation({
    mutationFn: () => api.post<{ message: string; enrollment_id: string }>(`/courses/${courseId}/enroll`),
    onSuccess: () => {
      setIsEnrolled(true);
    },
  });

  const { data: course, isLoading: courseLoading } = useQuery<Course>({
    queryKey: ['course', courseId],
    queryFn: () => api.get<Course>(`/courses/${courseId}`),
  });

  const { data: unitsData = [] } = useQuery<Unit[]>({
    queryKey: ['course-units', courseId],
    queryFn: () => api.get<Unit[]>(`/courses/${courseId}/units`),
  });

  const { data: lessonsData = [] } = useQuery<Lesson[]>({
    queryKey: ['course-lessons', courseId],
    queryFn: () => api.get<Lesson[]>(`/courses/${courseId}/lessons`),
  });

  const units = useMemo<UnitWithLessons[]>(() => {
    return unitsData.map((u) => ({
      ...u,
      lessons: lessonsData.filter((l) => l.unit_id === u.id),
    }));
  }, [unitsData, lessonsData]);

  useEffect(() => {
    if (units.length > 0 && expandedUnits.size === 0) {
      setExpandedUnits(new Set(units.map((u) => u.id)));
    }
  }, [units, expandedUnits, setExpandedUnits]);

  const loading = courseLoading;

  const toggleUnit = (unitId: string) => {
    setExpandedUnits((prev) => {
      const next = new Set(prev);
      if (next.has(unitId)) {
        next.delete(unitId);
      } else {
        next.add(unitId);
      }
      return next;
    });
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>
        <SkeletonBlock />
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
            {SUBJECT_LABELS[course.subject] || course.subject}
          </span>
          {course.target_exam && (
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600">
              {course.target_exam}
            </span>
          )}
        </div>
        <h1 className="text-2xl font-bold text-foreground mb-2">{course.name}</h1>
        <p className="text-muted-foreground">{course.description}</p>
        {course.estimated_hours && (
          <p className="text-sm text-muted-foreground mt-2">~{course.estimated_hours} hours</p>
        )}
        <div className="mt-4">
          {!isEnrolled ? (
            <Button
              onClick={() => enrollMutation.mutate()}
              disabled={enrollMutation.isPending}
              className="w-full"
            >
              {enrollMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  报名中...
                </>
              ) : (
                '开始学习'
              )}
            </Button>
          ) : (
            <Button disabled className="w-full opacity-70">
              已报名 <Check className="ml-1 h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Course Content</h2>
        {units.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-40" />
            <p>No units available yet</p>
          </div>
        ) : (
          units.map((unit) => (
            <div key={unit.id} className="border border-border rounded-xl overflow-hidden">
              <button
                onClick={() => toggleUnit(unit.id)}
                className="w-full p-4 flex items-center justify-between hover:bg-accent/50 transition-colors"
              >
                <div className="text-left">
                  <span className="font-medium text-foreground">{unit.name}</span>
                  <span className="text-sm text-muted-foreground ml-2">
                    ({unit.lessons.length} lessons)
                  </span>
                </div>
                {expandedUnits.has(unit.id) ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                )}
              </button>

              {expandedUnits.has(unit.id) && (
                <div className="border-t border-border">
                  {unit.lessons.map((lesson, index) => (
                    <div
                      key={lesson.id}
                      className="flex items-center gap-3 p-4 hover:bg-accent/50 transition-colors cursor-pointer"
                      onClick={() =>
                        router.push(`/courses/${courseId}/lesson/${lesson.id}`)
                      }
                    >
                      <Play className="w-4 h-4 text-[var(--color-primary)]" />
                      <span className="flex-1 text-foreground">{renderWithLatex(lesson.title)}</span>
                      {lesson.estimated_minutes && (
                        <span className="text-xs text-muted-foreground">
                          {lesson.estimated_minutes}min
                        </span>
                      )}
                    </div>
                  ))}
                  {unit.lessons.length === 0 && (
                    <p className="p-4 text-sm text-muted-foreground text-center">
                      No lessons in this unit
                    </p>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
