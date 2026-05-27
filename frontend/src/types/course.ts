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
