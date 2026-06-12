export interface DailyTaskItem {
  id: string;
  title: string;
  type: 'lesson' | 'practice' | 'review';
  xp: number;
  completed: boolean;
  knowledge_point_id: string | null;
  lesson_id: string | null;
}

export interface DailyTasksResponse {
  tasks: DailyTaskItem[];
  total_xp_available: number;
  completed_count: number;
}

export interface PillarMastery {
  name: string;
  mastery: number;
  color: string;
}

export interface MasterySummaryResponse {
  subjects: PillarMastery[];
  overall_mastery: number;
}

export interface StreakResponse {
  current_streak: number;
  longest_streak: number;
  week_data: boolean[];
  total_xp: number;
  daily_goal_minutes: number;
}

export interface DashboardSummaryResponse {
  daily_tasks: DailyTasksResponse;
  mastery_summary: MasterySummaryResponse;
  streak: StreakResponse;
}
