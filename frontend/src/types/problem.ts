export interface Problem {
  id: string;
  lesson_id: string;
  type:
    | 'multiple_choice'
    | 'fill_blank'
    | 'short_answer'
    | 'proof'
    | 'listening'
    | 'speaking'
    | 'writing';
  subject: 'math' | 'english';
  difficulty: 1 | 2 | 3 | 4 | 5;
  content: string;
  latex_content?: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
  hint_levels: string[];
  knowledge_points: string[];
  xp_reward: number;
}

export interface ProblemSolution {
  problem_id: string;
  answer: string;
  is_correct: boolean;
  score: number;
  feedback: string;
  time_spent_seconds: number;
  hints_used: number;
}

export interface KnowledgeState {
  knowledge_point_id: string;
  name: string;
  p_correct: number;
  attempts: number;
  last_practiced?: string;
}

export interface LearningSession {
  id: string;
  user_id: string;
  lesson_id?: string;
  type: 'lesson' | 'practice' | 'ket';
  started_at: string;
  ended_at?: string;
  problems_attempted: number;
  problems_correct: number;
  xp_earned: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    latex?: string;
    image_url?: string;
    audio_url?: string;
  };
}
