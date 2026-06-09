// Types derived from backend Pydantic schemas:
//   backend/app/schemas/session.py
//   backend/app/models/learning.py

/** Backend: SessionCreate – POST /sessions */
export interface SessionCreate {
  session_type?: string;
  subject?: string;
  knowledge_point_id?: string | null;
}

/** Backend: SessionResponse – GET /sessions/:id, POST /sessions response */
export interface SessionResponse {
  id: string;
  student_id: string;
  session_type: string;
  subject: string;
  knowledge_point_id: string | null;
  started_at: string;
  ended_at: string | null;
  duration_sec: number | null;
  problems_total: number | null;
  problems_correct: number | null;
  score_pct: number | null;
  xp_earned: number;
  summary: string | null;
}

/** Minimal session shape returned by POST /sessions (for page navigation) */
export interface SessionBrief {
  id: string;
  session_type: string;
  subject: string;
  started_at: string;
}
