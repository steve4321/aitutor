export interface Course {
  id: string;
  title: string;
  description: string;
  subject: 'math' | 'english';
  grade_level: number;
  cover_image_url?: string;
  total_units: number;
  total_lessons: number;
  enrolled: boolean;
  progress: number;
  created_at: string;
}

export interface Unit {
  id: string;
  course_id: string;
  title: string;
  description: string;
  order_index: number;
  total_lessons: number;
  completed_lessons: number;
  is_locked: boolean;
}

export interface Lesson {
  id: string;
  unit_id: string;
  course_id: string;
  title: string;
  description: string;
  order_index: number;
  type: 'video' | 'interactive' | 'practice' | 'reading' | 'mixed';
  duration_minutes: number;
  xp_reward: number;
  is_completed: boolean;
  is_locked: boolean;
  score?: number;
}

export interface LessonProgress {
  lesson_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  score: number;
  time_spent_seconds: number;
  completed_at?: string;
  attempts: number;
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
