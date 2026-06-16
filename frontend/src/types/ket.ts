/**
 * Shared KET (Cambridge A2 Key) type definitions.
 *
 * These types are used across all KET skill pages:
 * reading, writing, listening, and speaking.
 */

/** KET multiple-choice question (reading / listening) */
export interface KETQuestion {
  id: string;
  skill: string;
  level: string;
  question_type: string;
  prompt: string;
  audio_url: string | null;
  image_url: string | null;
  options: Record<string, string> | null;
  correct_answer: string;
  explanation: string | null;
  points: number;
}

/** Paginated response wrapper for the KET questions list endpoint */
export interface KETQuestionListResponse {
  items: KETQuestion[];
  total: number;
  limit: number;
  offset: number;
}

/** Shared quiz state for reading / listening pages.
 *  `audioPlayed` is optional — only the listening page tracks audio playback. */
export interface QuizState {
  currentIndex: number;
  answers: Record<string, string>;
  submitted: Record<string, boolean>;
  showExplanation: Record<string, boolean>;
  audioPlayed?: Record<string, boolean>;
}

/** KET writing task */
export interface KETWritingTask {
  id: string;
  task_type: string;
  prompt: string;
  image_url: string | null;
  word_limit_min: number;
  word_limit_max: number;
  sample_response: string | null;
}

/** AI scoring response for a KET writing submission */
export interface KETWritingScoreResponse {
  score: number;
  content_score: number;
  organization_score: number;
  language_score: number;
  feedback: string;
  band: number;
}

/** KET speaking task */
export interface KETSpeakingTask {
  id: string;
  topic: string;
  question: string;
  difficulty: string;
  expected_duration_sec: number;
}

/** AI scoring response for a KET speaking submission */
export interface KETSpeakingScoreResponse {
  score: number;
  band: number;
  feedback: string;
}
