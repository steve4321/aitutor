export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? 'AI私人家教';

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export const ROUTES = {
  HOME: '/home',
  COURSES: '/courses',
  COURSE_DETAIL: (id: string) => `/courses/${id}`,
  LESSON: (courseId: string, lessonId: string) =>
    `/courses/${courseId}/lesson/${lessonId}`,
  PRACTICE: '/practice',
  KET: '/ket',
  KET_READING: '/ket/reading',
  KET_WRITING: '/ket/writing',
  KET_LISTENING: '/ket/listening',
  KET_SPEAKING: '/ket/speaking',
  REPORTS: '/reports',
  SETTINGS: '/settings',
  PARENT: '/parent',
  PARENT_REPORTS: '/parent/reports',
  PARENT_SETTINGS: '/parent/settings',
  LOGIN: '/login',
  REGISTER: '/register',
} as const;

export const BOTTOM_NAV_TABS = [
  { href: '/home', label: '首页' },
  { href: '/courses', label: '课程' },
  { href: '/practice', label: '练习' },
  { href: '/settings', label: '我的' },
] as const;

export const XP_PER_LESSON = 50;
export const XP_PER_PRACTICE = 20;
export const STREAK_RESET_HOUR = 4;
