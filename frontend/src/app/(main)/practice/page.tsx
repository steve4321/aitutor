'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Calculator, Target, Clock, ChevronRight, Play } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface Course {
  id: string;
  code: string | null;
  subject: string;
  name: string;
  description: string | null;
  estimated_hours: number | null;
}

interface Unit {
  id: string;
  name: string;
  description: string | null;
  sort_order: number;
}

interface Lesson {
  id: string;
  unit_id: string;
  title: string;
  estimated_minutes: number | null;
}

const SUBJECT_CONFIG: Record<string, { label: string; icon: typeof Calculator; activeColor: string; activeBg: string; activeText: string }> = {
  math: { label: '数学', icon: Calculator, activeColor: 'border-blue-500', activeBg: 'bg-blue-50 dark:bg-blue-900/30', activeText: 'text-blue-600 dark:text-blue-400' },
  english: { label: '英语', icon: BookOpen, activeColor: 'border-emerald-500', activeBg: 'bg-emerald-50 dark:bg-emerald-900/30', activeText: 'text-emerald-600 dark:text-emerald-400' },
  chinese: { label: '语文', icon: BookOpen, activeColor: 'border-orange-500', activeBg: 'bg-orange-50 dark:bg-orange-900/30', activeText: 'text-orange-600 dark:text-orange-400' },
};

export default function PracticePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [units, setUnits] = useState<Unit[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [selectedUnits, setSelectedUnits] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const res = await api.get<Course[]>('/courses');
        setCourses(res);
        if (res.length > 0) {
          setSelectedCourseId(res[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch courses:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCourses();
  }, []);

  useEffect(() => {
    if (!selectedCourseId) return;
    setSelectedUnits([]);

    const fetchUnitsAndLessons = async () => {
      try {
        const [unitsRes, lessonsRes] = await Promise.all([
          api.get<Unit[]>(`/courses/${selectedCourseId}/units`),
          api.get<Lesson[]>(`/courses/${selectedCourseId}/lessons`),
        ]);
        setUnits(unitsRes);
        setLessons(lessonsRes);
      } catch (err) {
        console.error('Failed to fetch course content:', err);
      }
    };
    fetchUnitsAndLessons();
  }, [selectedCourseId]);

  const toggleUnit = (unitId: string) => {
    setSelectedUnits((prev) =>
      prev.includes(unitId)
        ? prev.filter((id) => id !== unitId)
        : [...prev, unitId]
    );
  };

  const selectedCourse = courses.find((c) => c.id === selectedCourseId);
  const subject = selectedCourse?.subject || 'math';
  const config = SUBJECT_CONFIG[subject] || SUBJECT_CONFIG.math;
  const IconComponent = config.icon;

  const totalLessons = selectedUnits.reduce((sum, uid) => {
    return sum + lessons.filter((l) => l.unit_id === uid).length;
  }, 0);

  const totalMinutes = selectedUnits.reduce((sum, uid) => {
    return sum + lessons
      .filter((l) => l.unit_id === uid)
      .reduce((s, l) => s + (l.estimated_minutes || 15), 0);
  }, 0);

  const handleStartPractice = () => {
    console.log('Starting practice:', { courseId: selectedCourseId, selectedUnits, totalLessons });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-foreground">练习</h1>
        <div className="animate-pulse space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">{[1, 2, 3].map((i) => <div key={i} className="h-24 bg-muted rounded-xl" />)}</div>
          <div className="h-12 bg-muted rounded" />
          <div className="h-64 bg-muted rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">练习</h1>
        <p className="text-muted-foreground mt-1">选择课程和单元，开始针对性练习</p>
      </div>

      <section>
        <h2 className="text-lg font-semibold text-foreground mb-3">选择课程</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {courses.map((course) => {
            const cfg = SUBJECT_CONFIG[course.subject] || SUBJECT_CONFIG.math;
            const CIcon = cfg.icon;
            const isActive = selectedCourseId === course.id;
            return (
              <button
                key={course.id}
                onClick={() => setSelectedCourseId(course.id)}
                className={cn(
                  'flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all text-center',
                  isActive
                    ? `${cfg.activeColor} ${cfg.activeBg}`
                    : 'border-border bg-background hover:border-primary/50'
                )}
              >
                <CIcon className={cn('w-8 h-8', isActive ? cfg.activeText : 'text-muted-foreground')} />
                <span className={cn('text-sm font-medium', isActive ? cfg.activeText : 'text-foreground')}>
                  {course.name}
                </span>
                {course.estimated_hours && (
                  <span className="text-xs text-muted-foreground">~{course.estimated_hours}h</span>
                )}
              </button>
            );
          })}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-foreground mb-3">选择单元</h2>
        {units.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-40" />
            <p>该课程暂无单元</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {units.map((unit) => {
              const lessonCount = lessons.filter((l) => l.unit_id === unit.id).length;
              const isActive = selectedUnits.includes(unit.id);
              return (
                <button
                  key={unit.id}
                  onClick={() => toggleUnit(unit.id)}
                  className={cn(
                    'flex flex-col items-start rounded-lg border px-4 py-3 transition-all',
                    isActive
                      ? `${config.activeColor} ${config.activeBg}`
                      : 'border-border bg-background hover:border-primary/50'
                  )}
                >
                  <span className={cn('text-sm font-medium', isActive ? config.activeText : 'text-foreground')}>
                    {unit.name}
                  </span>
                  <span className={cn('text-xs mt-1', isActive ? config.activeText : 'text-muted-foreground')}>
                    {lessonCount} 个课时
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </section>

      <section className="rounded-xl border border-border bg-background p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">课时数量</span>
              <span className="text-lg font-bold text-foreground">{totalLessons}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">预计</span>
            <span className="text-sm font-medium text-foreground">{totalMinutes > 0 ? `${totalMinutes}分钟` : '--'}</span>
          </div>
        </div>

        {selectedUnits.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {selectedUnits.map((uid) => {
              const unit = units.find((u) => u.id === uid);
              return (
                <span key={uid} className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                  {unit?.name}
                  <button onClick={(e) => { e.stopPropagation(); toggleUnit(uid); }} className="ml-1 hover:text-primary/80">×</button>
                </span>
              );
            })}
          </div>
        )}
      </section>

      <button
        onClick={handleStartPractice}
        disabled={selectedUnits.length === 0}
        className={cn(
          'flex w-full items-center justify-center gap-2 rounded-xl py-4 font-semibold transition-all',
          selectedUnits.length > 0
            ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary)]/90'
            : 'bg-muted text-muted-foreground cursor-not-allowed'
        )}
      >
        <Play className="h-5 w-5" />
        开始练习
        <ChevronRight className="h-5 w-5" />
      </button>
    </div>
  );
}