// Types for Parent Portal

import type { WeeklyReport } from './report';
import type { StudentProfileResponse, UserResponse } from './user';

/** Backend: GET /parent/children - List of linked children for parent */
export interface LinkedChild {
  id: string;
  name: string;
  grade_level: number | null;
  target_exam: string | null;
  streak_days: number;
  xp_total: number;
  linked_at: string;
}

/** Backend: GET /parent/children/{id}/overview - Quick overview stats */
export interface ChildOverview {
  child_id: string;
  child_name: string;
  target_exam: string | null;
  streak_days: number;
  weekly_study_minutes: number;
  weekly_goal_completion: number; // 0-100 percentage
  minutes_today: number;
  daily_goal_minutes: number;
}

/** Backend: GET /parent/children/{id}/mastery - 4-week mastery by pillar */
export interface MasteryTrend {
  week_start: string; // ISO date string
  pillars: {
    algebra: number;    // 0-100 percentage
    geometry: number;
    counting: number;
    number_theory: number;
  };
}

/** Weekly mastery trends response */
export interface MasteryTrendsResponse {
  child_id: string;
  trends: MasteryTrend[]; // Last 4 weeks
}

/** Backend: GET /parent/children/{id}/notifications */
export interface ParentNotification {
  id: string;
  type: 'milestone' | 'achievement' | 'concern' | 'weekly_report';
  title: string;
  message: string;
  created_at: string;
  read: boolean;
  metadata?: Record<string, unknown>;
}

/** Parent notification preferences */
export interface NotificationPreferences {
  milestone_notifications: boolean;
  achievement_notifications: boolean;
  concern_alerts: boolean;
  weekly_reports: boolean;
  weekly_report_day: number; // 0=Sunday, 1=Monday, etc.
  weekly_report_time: string; // HH:MM format
  study_time_limit_minutes: number | null;
}

/** Parent weekly report with AI insights - extended WeeklyReport */
export interface ParentWeeklyReport extends WeeklyReport {
  insights: string[]; // AI-generated insights
  concerns: string[]; // AI-generated concern alerts
  previous_week_comparison: {
    xp_change: number;
    time_change: number;
    accuracy_change: number;
  };
}

/** Link child request */
export interface LinkChildRequest {
  link_code: string;
}

/** Link child response */
export interface LinkChildResponse {
  status: 'linked' | 'already_linked';
  child_name?: string;
}