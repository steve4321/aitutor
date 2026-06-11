'use client';

import { cn } from '@/lib/utils';
import { renderWithLatex } from '@/lib/render-content';
import { LessonCard } from './lesson-card';

interface CoursePathProps {
  lessons: {
    id: string;
    title: string;
    order_index: number;
    is_completed: boolean;
    is_locked: boolean;
    type?: 'video' | 'interactive' | 'practice' | 'reading' | 'mixed';
    duration_minutes?: number;
    xp_reward?: number;
    score?: number;
  }[];
  onLessonClick?: (lessonId: string) => void;
  className?: string;
}

export function CoursePath({ lessons, onLessonClick, className }: CoursePathProps) {
  const activeIndex = lessons.findIndex(
    (l) => !l.is_completed && !l.is_locked
  );

  return (
    <div className={cn('flex flex-col items-center gap-6 py-8', className)}>
      {lessons.map((lesson, index) => {
        const isLeft = index % 2 === 0;

        const status = lesson.is_locked
          ? 'locked' as const
          : lesson.is_completed
            ? 'completed' as const
            : index === activeIndex
              ? 'in_progress' as const
              : 'not_started' as const;

        return (
          <div key={lesson.id} className="flex flex-col items-center">
            {index > 0 && (
              <div className="mb-2 h-8 w-0.5 bg-gray-300" />
            )}
            <div
              className={cn(
                'flex items-center gap-4',
                isLeft ? 'flex-row' : 'flex-row-reverse'
              )}
            >
              <div className={cn('w-28', isLeft ? 'text-right' : 'text-left')}>
                <p className="text-sm font-medium text-gray-700">
                  {renderWithLatex(lesson.title)}
                </p>
              </div>
              <LessonCard
                title={lesson.title}
                type={lesson.type ?? 'mixed'}
                durationMinutes={lesson.duration_minutes ?? 15}
                status={status}
                score={lesson.score}
                xpReward={lesson.xp_reward ?? 50}
                onClick={() => onLessonClick?.(lesson.id)}
                isLocked={lesson.is_locked}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
