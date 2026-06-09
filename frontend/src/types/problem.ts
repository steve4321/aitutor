// Types derived from backend Pydantic schemas:
//   backend/app/schemas/problem.py
//   backend/app/schemas/chat.py
//   backend/app/models/problem.py
//   backend/app/models/message.py

// ── API Response Types (match backend exactly) ──────────────────────────

/** Backend: ProblemResponse – GET /problems/:id, GET /practice/next */
export interface ProblemResponse {
  id: string;
  source: string | null;
  subject: string;
  format: string;
  question_markdown: string;
  options: Record<string, unknown> | null;
  difficulty: number | null;
  estimated_time_sec: number | null;
}

/** Backend: AttemptRequest – POST /problems/:id/attempts */
export interface AttemptRequest {
  answer: string;
  session_id?: string | null;
  time_spent_sec?: number | null;
}

/** Backend: AttemptResponse – POST /problems/:id/attempts response */
export interface AttemptResponse {
  id: string;
  is_correct: boolean | null;
  ai_feedback: string | null;
  error_type?: string | null;
  attempt_number: number;
  xp_earned: number;
}

/** Backend: ChatMessageResponse – chat messages */
export interface ChatMessageResponse {
  id: string;
  role: string;
  content: string;
  session_id: string | null;
}

// ── Backward-compatible aliases / extended types ─────────────────────────

export interface ChatMessage extends Omit<ChatMessageResponse, 'session_id'> {
  session_id?: string | null;
  timestamp?: string;
  metadata?: {
    latex?: string;
    image_url?: string;
    audio_url?: string;
  };
}

// ── Frontend-only types ─────────────────────────────────────────────────

/** Backend: ChatMessageRequest – POST /chat */
export interface ChatMessageRequest {
  session_id?: string | null;
  content: string;
  media?: Record<string, unknown> | null;
}

/** UI-only problem type used by practice-session component */
export interface Problem {
  id: string;
  type: string;
  content: string;
  latexContent?: string;
  options?: string[];
  correctAnswer: string;
  explanation: string;
  hintLevels: string[];
  xpReward: number;
}

export interface KnowledgeState {
  knowledge_point_id: string;
  name: string;
  p_correct: number;
  attempts: number;
  last_practiced?: string;
}
