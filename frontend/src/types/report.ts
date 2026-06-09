// Types derived from backend Pydantic schemas:
//   backend/app/schemas/report.py

/** Backend: DailyReport – GET /reports/daily */
export interface DailyReport {
  date: string;
  sessions_count: number;
  problems_attempted: number;
  problems_correct: number;
  xp_earned: number;
  time_spent_minutes: number;
  knowledge_points_reviewed: string[];
}

/** Backend: WeeklyReport – GET /reports/weekly */
export interface WeeklyReport {
  week_start: string;
  week_end: string;
  total_sessions: number;
  total_problems: number;
  total_correct: number;
  total_xp: number;
  total_time_minutes: number;
  streak_days: number;
  mastery_changes: Record<string, number>;
}
