export interface User {
  id: string;
  username: string;
  email: string;
  display_name: string;
  avatar_url?: string;
  role: 'student' | 'parent' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface StudentProfile {
  user_id: string;
  grade_level: number;
  xp: number;
  streak: number;
  longest_streak: number;
  daily_goal_minutes: number;
  preferred_subjects: string[];
  ket_level?: 'A2' | 'B1';
  parent_linked: boolean;
  parent_id?: string;
}

export interface ParentLink {
  id: string;
  parent_id: string;
  student_id: string;
  relationship: 'father' | 'mother' | 'guardian' | 'other';
  verified: boolean;
  created_at: string;
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'zh-CN' | 'en';
  sound_enabled: boolean;
  notifications_enabled: boolean;
  dyslexia_font: boolean;
  font_size: 'small' | 'medium' | 'large';
}
