// Types derived from backend Pydantic schemas:
//   backend/app/schemas/user.py
//   backend/app/models/user.py

// ── API Response Types (match backend exactly) ──────────────────────────

/** Backend: UserResponse – GET /auth/me, GET /users/:id */
export interface UserResponse {
  id: string;
  email: string | null;
  phone: string | null;
  name: string;
  role: string;
  avatar_url: string | null;
  created_at: string;
}

/** Backend: StudentProfileResponse – GET /users/me/profile */
export interface StudentProfileResponse {
  id: string;
  user_id: string;
  grade_level: number | null;
  target_exam: string | null;
  target_date: string | null;
  daily_goal_minutes: number;
  timezone: string;
  preferred_lang: string;
  diagnostic_done: boolean;
  xp_total: number;
  streak_days: number;
  longest_streak: number;
}

// ── Backward-compatible aliases ─────────────────────────────────────────

export type User = UserResponse;
export type StudentProfile = StudentProfileResponse;
