import { describe, it, expect } from 'vitest';
import {
  APP_NAME,
  API_BASE_URL,
  ROUTES,
  BOTTOM_NAV_TABS,
  XP_PER_LESSON,
  XP_PER_PRACTICE,
  STREAK_RESET_HOUR,
} from '../constants';

describe('APP_NAME', () => {
  it('is a non-empty string', () => {
    expect(typeof APP_NAME).toBe('string');
    expect(APP_NAME.length).toBeGreaterThan(0);
  });
});

describe('API_BASE_URL', () => {
  it('is a non-empty string', () => {
    expect(typeof API_BASE_URL).toBe('string');
    expect(API_BASE_URL.length).toBeGreaterThan(0);
  });

  it('contains a URL pattern', () => {
    expect(API_BASE_URL).toContain('http');
  });
});

describe('ROUTES', () => {
  it('has HOME route', () => {
    expect(ROUTES.HOME).toBe('/home');
  });

  it('has COURSES route', () => {
    expect(ROUTES.COURSES).toBe('/courses');
  });

  it('has COURSE_DETAIL as a function', () => {
    expect(typeof ROUTES.COURSE_DETAIL).toBe('function');
    expect(ROUTES.COURSE_DETAIL('123')).toBe('/courses/123');
  });

  it('has LESSON as a function', () => {
    expect(typeof ROUTES.LESSON).toBe('function');
    expect(ROUTES.LESSON('c1', 'l2')).toBe('/courses/c1/lesson/l2');
  });

  it('has PRACTICE route', () => {
    expect(ROUTES.PRACTICE).toBe('/practice');
  });

  it('has KET routes', () => {
    expect(ROUTES.KET).toBe('/ket');
    expect(ROUTES.KET_READING).toBe('/ket/reading');
    expect(ROUTES.KET_WRITING).toBe('/ket/writing');
    expect(ROUTES.KET_LISTENING).toBe('/ket/listening');
    expect(ROUTES.KET_SPEAKING).toBe('/ket/speaking');
  });

  it('has REPORTS route', () => {
    expect(ROUTES.REPORTS).toBe('/reports');
  });

  it('has SETTINGS route', () => {
    expect(ROUTES.SETTINGS).toBe('/settings');
  });

  it('has LOGIN route', () => {
    expect(ROUTES.LOGIN).toBe('/login');
  });

  it('has REGISTER route', () => {
    expect(ROUTES.REGISTER).toBe('/register');
  });

  it('all static routes start with /', () => {
    const staticRoutes = [
      ROUTES.HOME, ROUTES.COURSES, ROUTES.PRACTICE,
      ROUTES.KET, ROUTES.KET_READING, ROUTES.KET_WRITING,
      ROUTES.KET_LISTENING, ROUTES.KET_SPEAKING,
      ROUTES.REPORTS, ROUTES.SETTINGS, ROUTES.LOGIN, ROUTES.REGISTER,
    ];
    staticRoutes.forEach((route) => {
      expect(route.startsWith('/')).toBe(true);
    });
  });
});

describe('BOTTOM_NAV_TABS', () => {
  it('is an array with 4 tabs', () => {
    expect(BOTTOM_NAV_TABS).toHaveLength(4);
  });

  it('each tab has href and label', () => {
    BOTTOM_NAV_TABS.forEach((tab) => {
      expect(tab.href).toBeDefined();
      expect(tab.label).toBeDefined();
      expect(typeof tab.href).toBe('string');
      expect(typeof tab.label).toBe('string');
    });
  });
});

describe('XP constants', () => {
  it('XP_PER_LESSON is a positive number', () => {
    expect(XP_PER_LESSON).toBe(50);
    expect(XP_PER_LESSON).toBeGreaterThan(0);
  });

  it('XP_PER_PRACTICE is a positive number', () => {
    expect(XP_PER_PRACTICE).toBe(20);
    expect(XP_PER_PRACTICE).toBeGreaterThan(0);
  });

  it('STREAK_RESET_HOUR is a valid hour', () => {
    expect(STREAK_RESET_HOUR).toBe(4);
    expect(STREAK_RESET_HOUR).toBeGreaterThanOrEqual(0);
    expect(STREAK_RESET_HOUR).toBeLessThan(24);
  });
});
