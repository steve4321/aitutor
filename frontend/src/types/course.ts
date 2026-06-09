// Types derived from backend Pydantic schemas:
//   backend/app/schemas/course.py
//   backend/app/models/course.py

// ── API Response Types (match backend exactly) ──────────────────────────

/** Backend: CourseResponse – GET /courses, GET /courses/:id */
export interface CourseResponse {
  id: string;
  code: string | null;
  subject: string;
  name: string;
  description: string | null;
  target_exam: string | null;
  estimated_hours: number | null;
  is_published: boolean;
}

/** Backend: UnitResponse – GET /courses/:id/units */
export interface UnitResponse {
  id: string;
  course_id: string;
  code: string | null;
  name: string;
  description: string | null;
  sort_order: number;
  required_mastery: number;
}

/** Backend: LessonResponse – GET /courses/:id/lessons, GET /lessons/:id */
export interface LessonResponse {
  id: string;
  unit_id: string;
  knowledge_point_id: string | null;
  code: string | null;
  title: string;
  lesson_type: string | null;
  estimated_minutes: number | null;
  sort_order: number;
  is_published: boolean;
  content: Record<string, unknown> | null;
}

// ── Backward-compatible aliases ─────────────────────────────────────────

export type Course = CourseResponse;
export type Unit = UnitResponse;
export type Lesson = LessonResponse;

// ── Composite / Frontend-only types ─────────────────────────────────────

export interface UnitWithLessons extends Unit {
  lessons: Lesson[];
}

export interface PracticeProblem {
  question: string;
  options: string[];
  answer: string;
}

export interface LessonSection {
  type: 'introduction' | 'concept' | 'example' | 'practice' | 'summary';
  title?: string;
  content?: string;
  problem?: string;
  solution?: string;
  problems?: PracticeProblem[];
}

/** Enriched lesson detail returned by GET /lessons/:id */
export interface LessonDetailResponse {
  id: string;
  title: string;
  lesson_type: string | null;
  estimated_minutes: number | null;
  content: { sections: LessonSection[] };
  unit_id: string;
  unit_title: string;
  course_id: string;
  course_name: string;
  prev_lesson_id: string | null;
  next_lesson_id: string | null;
  is_enrolled: boolean;
  status: 'locked' | 'in_progress' | 'completed';
}

export interface LessonProgressResponse {
  message: string;
  progress: number;
  xp_earned: number;
}
