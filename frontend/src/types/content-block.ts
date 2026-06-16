/**
 * ContentBlock Types — Source of truth: docs/lesson-content-schema.md v1.0
 *
 * Discriminated union types for all lesson content blocks.
 * Each block uses a `type` field for type discrimination.
 *
 * Block interfaces are split into domain sub-modules under ./content-blocks/.
 * This file re-exports them and defines the discriminated union + lesson types.
 */

// ─── Re-export all block interfaces (barrel) ───────────────────────────────

export type {
  TextBlock,
  ExpandableBlock,
  DividerBlock,
  IllustrationBlock,
  CodeBlock,
  TableBlock,
} from './content-blocks/text';

export type {
  FormulaBlock,
  GeoGebraBlock,
  AnimationBlock,
} from './content-blocks/math';

export type {
  AudioBlock,
  ImageBlock,
  VideoBlock,
} from './content-blocks/media';

export type {
  ProblemBlock,
  InteractiveTableBlock,
  ScratchpadBlock,
  VoiceInputBlock,
  PhotoUploadBlock,
  WritingBlock,
  ListeningQuestion,
  ListeningBlock,
  SpeakingBlock,
  MatchingBlock,
  GapFillBlock,
  ReadingPassageBlock,
  VocabCardBlock,
  ChineseWritingBlock,
  PoetryDictationBlock,
  PoetryAppreciationBlock,
  PoetryRecitationBlock,
  DraftBlock,
} from './content-blocks/interactive';

// ─── Import for union definition ───────────────────────────────────────────

import type {
  TextBlock,
  ExpandableBlock,
  DividerBlock,
  IllustrationBlock,
  CodeBlock,
  TableBlock,
} from './content-blocks/text';

import type {
  FormulaBlock,
  GeoGebraBlock,
  AnimationBlock,
} from './content-blocks/math';

import type {
  AudioBlock,
  ImageBlock,
  VideoBlock,
} from './content-blocks/media';

import type {
  ProblemBlock,
  InteractiveTableBlock,
  ScratchpadBlock,
  VoiceInputBlock,
  PhotoUploadBlock,
  WritingBlock,
  ListeningBlock,
  SpeakingBlock,
  MatchingBlock,
  GapFillBlock,
  ReadingPassageBlock,
  VocabCardBlock,
  ChineseWritingBlock,
  PoetryDictationBlock,
  PoetryAppreciationBlock,
  PoetryRecitationBlock,
  DraftBlock,
} from './content-blocks/interactive';

// ─── Discriminated Union ───────────────────────────────────────────────────

export type ContentBlock =
  // Display
  | TextBlock
  | AudioBlock
  | ImageBlock
  | FormulaBlock
  | GeoGebraBlock
  | VideoBlock
  | AnimationBlock
  | ExpandableBlock
  | DividerBlock
  | IllustrationBlock
  | CodeBlock
  | TableBlock
  // Interactive — General
  | ProblemBlock
  | InteractiveTableBlock
  | ScratchpadBlock
  | VoiceInputBlock
  | PhotoUploadBlock
  // Interactive — KET English
  | WritingBlock
  | ListeningBlock
  | SpeakingBlock
  | MatchingBlock
  | GapFillBlock
  | ReadingPassageBlock
  | VocabCardBlock
  // Interactive — Chinese Language
  | ChineseWritingBlock
  | PoetryDictationBlock
  | PoetryAppreciationBlock
  | PoetryRecitationBlock
  | DraftBlock;

// ─── Step & Lesson Types ───────────────────────────────────────────────────

export type StepPhase =
  // AMC Math 5E
  | 'engage'
  | 'explore'
  | 'explain'
  | 'elaborate'
  | 'evaluate'
  // KET English
  | 'introduce'
  | 'present'
  | 'practice'
  | 'produce'
  | 'review'
  // General
  | 'warmup'
  | 'transition'
  | 'reflection'
  | 'assessment'
  | 'diagnostic'
  | 'test'
  | 'summary'
  // Chinese Composition (Writing Process Model)
  | 'observe'
  | 'conceive'
  | 'express'
  | 'polish'
  | 'assess_write'
  // Chinese Poetry (Iterative Deepening)
  | 'read_poem'
  | 'decipher'
  | 'appreciate'
  | 'comprehend'
  | 'verify';

export interface LessonStep {
  /** Unique step ID (unique within lesson) */
  id: string;
  /** Teaching phase */
  phase: StepPhase;
  /** Step title (shown to student) */
  title: string;
  /** Estimated duration in seconds */
  estimated_seconds: number;
  /** Content blocks */
  blocks: ContentBlock[];
  /** Completion mode */
  completion_mode: 'all_viewed' | 'interaction_complete' | 'score_threshold';
  /** Agent behavior hint for this step */
  agent_instruction?: string;
  /** Auto-skip conditions */
  skip_if?: {
    mastery_above?: number;
    previous_all_correct?: boolean;
  };
}

export interface LessonSummary {
  /** Key takeaways (3-5) */
  key_points: string[];
  /** AMC exam tip (math only) */
  amc_tip?: string;
  /** Common mistakes */
  common_mistakes?: string[];
  /** Next lesson code */
  next_lesson_code?: string;
}

export interface LessonContent {
  /** Schema version for compatibility */
  schema_version: '1.0';
  /** Subject */
  subject: 'amc_math' | 'ket_english' | 'chn_composition' | 'chn_poetry';
  /** Lesson type */
  lesson_type:
    | 'concept'
    | 'practice'
    | 'assessment'
    | 'review'
    | 'diagnostic'
    | 'mock_exam'
    | 'vocab_drill'
    | 'grammar_drill'
    | 'mock_speaking'
    | 'mock_listening'
    | 'composition'
    | 'poetry_reading'
    | 'poetry_dictation';
  /** Learning objectives (2-5) */
  objectives: string[];
  /** Prerequisite knowledge point codes */
  prerequisite_codes: string[];
  /** Linked knowledge point codes */
  knowledge_point_codes: string[];
  /** AMC level (math only) */
  amc_level?: 8 | 10 | 12;
  /** KET skill (English only) */
  ket_skill?: 'reading' | 'writing' | 'listening' | 'speaking' | 'vocabulary' | 'grammar';
  /** Chinese grade level (Chinese only) */
  chn_grade?: 4 | 5 | 6;
  /** Estimated duration in minutes */
  estimated_minutes: number;
  /** XP reward base */
  xp_base: number;
  /** Passing criteria */
  passing_criteria: {
    min_mastery: number;
    min_accuracy: number;
    min_problems: number;
    min_appreciation_score?: number;
  };
  /** Lesson steps */
  steps: LessonStep[];
  /** Lesson summary */
  summary: LessonSummary;
  /** Optional metadata */
  metadata?: Record<string, unknown>;
}
