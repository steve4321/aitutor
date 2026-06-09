'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { BookOpen } from 'lucide-react';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import { cn } from '@/lib/utils';
import type { Course } from '@/types/course';

const SUBJECT_LABELS: Record<string, string> = {
  math: 'AMC',
  english: 'KET',
  chinese: '语文',
};

const SUBJECT_FILTERS = [
  { label: 'All', value: '' },
  { label: 'AMC', value: 'math' },
  { label: 'KET', value: 'english' },
  { label: '语文', value: 'chinese' },
];

function CourseCardSkeleton() {
  return (
    <div className="bg-background rounded-xl border border-border overflow-hidden animate-pulse">
      <div className="h-32 bg-muted" />
      <div className="p-4">
        <div className="h-5 w-3/4 bg-muted rounded mb-2" />
        <div className="h-4 w-full bg-muted rounded mb-4" />
        <div className="h-8 bg-muted rounded" />
      </div>
    </div>
  );
}

export default function CoursesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [filter, setFilter] = useState(searchParams.get('filter') || '');

  const { data: courses = [], isLoading: loading } = useQuery<Course[]>({
    queryKey: ['courses', filter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filter) params.set('subject', filter);
      return api.get<Course[]>(`/courses?${params.toString()}`);
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Courses</h1>
        <p className="text-muted-foreground mt-1">Explore and enroll in courses</p>
      </div>

      <div className="flex gap-2">
        {SUBJECT_FILTERS.map((f) => (
          <button
            key={f.value || 'all'}
            onClick={() => setFilter(f.value)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filter === f.value
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-background border border-border text-foreground hover:border-[var(--color-primary)]/50'
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <CourseCardSkeleton key={i} />)}
        </div>
      ) : courses.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">No courses found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course) => (
            <div key={course.id} className="bg-background rounded-xl border border-border overflow-hidden">
              <div className="h-32 bg-gradient-to-br from-[var(--color-primary)]/20 to-[var(--color-secondary)]/20 flex items-center justify-center">
                <BookOpen className="w-10 h-10 text-[var(--color-primary)]/40" />
              </div>
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
                    {SUBJECT_LABELS[course.subject] || course.subject}
                  </span>
                  {course.target_exam && (
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600">
                      {course.target_exam}
                    </span>
                  )}
                </div>
                <h3 className="font-semibold text-foreground mb-1">{course.name}</h3>
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{course.description}</p>

                <div className="flex items-center justify-between">
                  {course.estimated_hours && (
                    <span className="text-xs text-muted-foreground">~{course.estimated_hours}h</span>
                  )}
                  <button
                    onClick={() => router.push(`${ROUTES.COURSES}/${course.id}`)}
                    className="px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--color-primary)]/90 transition-colors"
                  >
                    View Course
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}