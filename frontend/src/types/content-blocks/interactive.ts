/**
 * Interactive content blocks: problem, input, quiz, English, Chinese language.
 */

import type { ImageBlock } from './media';

// ─── Interactive Blocks — General ───────────────────────────────────────────

export interface ProblemBlock {
  type: 'problem';
  /** Problem ID (links to problems table) */
  problem_id?: string;
  /** Question format */
  problem_type: 'multiple_choice' | 'fill_blank' | 'short_answer';
  /** Difficulty 1-5 */
  difficulty: 1 | 2 | 3 | 4 | 5;
  /** Question stem (Markdown, supports LaTeX) */
  question: string;
  /** Options (for multiple_choice) */
  options?: Array<{
    label: string;
    content: string;
  }>;
  /** Correct answer */
  correct_answer: string;
  /** Solution explanation (shown after answer) */
  explanation?: string;
  /** 5-level hints */
  hints: Array<{
    level: 0 | 1 | 2 | 3 | 4;
    text: string;
    audio_url?: string;
  }>;
  /** Linked knowledge point codes */
  knowledge_point_codes: string[];
  /** XP reward */
  xp_reward: number;
  /** Attached figure */
  figure?: ImageBlock;
  /** Attached LaTeX expressions */
  latex_expressions?: string[];
}

export interface InteractiveTableBlock {
  type: 'interactive_table';
  /** Column headers */
  headers: string[];
  /** Data rows; null = student fills in */
  rows: Array<Array<string | null>>;
  /** Fill instructions */
  instructions?: string;
  /** Correct answers for validation */
  answer_rows?: Array<Array<string>>;
  /** Allow partial credit */
  partial_credit?: boolean;
}

export interface ScratchpadBlock {
  type: 'scratchpad';
  /** Canvas width */
  width?: number;
  /** Canvas height */
  height?: number;
  /** Placeholder text */
  placeholder?: string;
  /** Submit to AI for scoring/feedback */
  submit_to_ai?: boolean;
}

export interface VoiceInputBlock {
  type: 'voice_input';
  /** Prompt / question */
  prompt: string;
  /** Audio URL for spoken prompt */
  prompt_audio_url?: string;
  /** Max recording duration in seconds */
  max_duration?: number;
  /** Expected text answer (for ASR validation) */
  expected_answer?: string;
  /** Expected LaTeX result (math voice recognition) */
  expected_latex?: string;
  /** Allowed input modes */
  input_modes: Array<'voice' | 'text' | 'drawing'>;
}

export interface PhotoUploadBlock {
  type: 'photo_upload';
  /** Instructions */
  instructions: string;
  /** Accepted file types */
  accept?: 'image' | 'image_and_pdf';
  /** Max file size in MB */
  max_size_mb?: number;
  /** AI processing action */
  ai_action?: 'ocr_math' | 'ocr_text' | 'describe_image';
}

// ─── Interactive Blocks — KET English ───────────────────────────────────────

export interface WritingBlock {
  type: 'writing';
  /** Task description */
  task: string;
  /** Required points to cover */
  required_points: string[];
  /** Minimum word count */
  min_words: number;
  /** Maximum word count */
  max_words: number;
  /** Target word count */
  target_words: number;
  /** Writing format */
  writing_type: 'email' | 'short_story' | 'message';
  /** Cambridge rubric (Band 0-5) */
  rubric?: {
    content_max: 5;
    organisation_max: 5;
    language_max: 5;
  };
}

export interface ListeningQuestion {
  id: string;
  question_type: 'multiple_choice' | 'fill_blank' | 'matching' | 'true_false';
  question: string;
  options?: string[];
  correct_answer: string | string[];
  /** Reference in transcript */
  transcript_reference?: string;
}

export interface ListeningBlock {
  type: 'listening';
  /** Audio URL */
  audio_url: string;
  /** Audio duration */
  duration_sec: number;
  /** Play mode */
  play_mode: 'unlimited' | 'twice' | 'once';
  /** Speed multiplier */
  speed?: 0.8 | 1.0 | 1.2;
  /** Transcript (shown after answering) */
  transcript?: string;
  /** Comprehension questions */
  questions: ListeningQuestion[];
}

export interface SpeakingBlock {
  type: 'speaking';
  /** Speaking task type */
  speaking_type: 'personal_questions' | 'discussion' | 'picture_description';
  /** AI examiner's first prompt */
  initial_prompt: string;
  /** Audio URL for spoken prompt */
  prompt_audio_url?: string;
  /** Max recording duration in seconds */
  max_duration_sec: number;
  /** Discussion image */
  discussion_image?: ImageBlock;
  /** Follow-up prompts */
  follow_up_prompts?: Array<{
    condition?: 'always' | 'if_short_answer' | 'if_correct' | 'if_incorrect';
    prompt: string;
  }>;
  /** Assessment dimensions */
  assessment_criteria?: Array<
    'grammar_vocabulary' | 'pronunciation' | 'interactive_communication' | 'global_achievement'
  >;
  /** E-ink fallback (waveform unavailable) */
  eink_fallback?: {
    status_text: string;
  };
}

export interface MatchingBlock {
  type: 'matching';
  /** Instructions */
  instructions: string;
  /** Left column items */
  left_items: Array<{ id: string; content: string }>;
  /** Right column items (will be shuffled) */
  right_items: Array<{ id: string; content: string }>;
  /** Correct pairs: left_id → right_id */
  correct_pairs: Record<string, string>;
}

export interface GapFillBlock {
  type: 'gap_fill';
  /** Text template with {{gap:N}} markers */
  template: string;
  /** Gap configurations */
  gaps: Array<{
    index: number;
    /** Dropdown options (if present → select; absent → free text) */
    options?: string[];
    /** Correct answer */
    answer: string;
    /** Acceptable alternatives (case, etc.) */
    acceptable_answers?: string[];
  }>;
  /** Title */
  title?: string;
}

export interface ReadingPassageBlock {
  type: 'reading_passage';
  /** Passage title */
  title: string;
  /** Paragraphs */
  paragraphs: string[];
  /** Clickable vocabulary hints */
  vocabulary_tips?: Array<{
    word: string;
    definition: string;
    paragraph_index: number;
  }>;
  /** Comprehension questions */
  questions: Array<{
    id: string;
    question: string;
    type: 'multiple_choice' | 'true_false' | 'open_ended';
    options?: string[];
    correct_answer?: string;
    /** Source paragraph index */
    reference_paragraph?: number;
  }>;
}

export interface VocabCardBlock {
  type: 'vocab_card';
  /** Word */
  word: string;
  /** Phonetic transcription */
  phonetic?: string;
  /** Definition (English, not Chinese) */
  definition: string;
  /** Example sentence */
  example_sentence: string;
  /** Illustration */
  image_url?: string;
  /** Pronunciation audio */
  audio_url?: string;
  /** Practice mode */
  practice_mode: 'recognize' | 'recall' | 'spell' | 'use_in_sentence';
}

// ─── Interactive Blocks — Chinese Language ──────────────────────────────────

export interface ChineseWritingBlock {
  type: 'chn_writing';
  /** Task description */
  task: string;
  /** Prompt / requirements */
  prompt?: string;
  /** Writing genre */
  writing_type: 'narrative' | 'descriptive' | 'imaginative' | 'practical' | 'expository';
  /** Target character count */
  target_chars: number;
  /** Minimum characters */
  min_chars: number;
  /** Maximum characters */
  max_chars: number;
  /** Scoring rubric (100-point scale, 4 dimensions) */
  rubric: {
    content_max: 40;
    structure_max: 20;
    language_max: 30;
    handwriting_max: 10;
  };
  /** Allow revision */
  allow_revision: boolean;
  /** Max revision rounds */
  max_revisions?: number;
  /** Essay scoring prompt ID */
  scoring_prompt_id: string;
}

export interface PoetryDictationBlock {
  type: 'poetry_dictation';
  /** Poem title */
  poem_title: string;
  /** Poet name */
  poet: string;
  /** Dictation mode */
  dictation_mode: 'full' | 'partial' | 'fill_blank';
  /** Full original text (for comparison) */
  full_text: string;
  /** Fill-blank template with {{gap:N}} markers */
  template?: string;
  /** Gap configurations */
  gaps?: Array<{
    index: number;
    /** Correct answer (exact match) */
    answer: string;
    /** Acceptable variant characters */
    acceptable_variants?: string[];
  }>;
  /** Character indices to hide */
  hidden_indices?: number[];
  /** Linked knowledge point codes */
  knowledge_point_codes: string[];
  /** XP reward */
  xp_reward: number;
}

export interface PoetryAppreciationBlock {
  type: 'poetry_appreciation';
  /** Poem title */
  poem_title: string;
  /** Poet name */
  poet: string;
  /** Dynasty */
  dynasty: string;
  /** Full text with annotation markers */
  full_text: string;
  /** Appreciation questions */
  questions: Array<{
    id: string;
    question_type:
      | 'imagery_analysis'
      | 'technique_identification'
      | 'emotion_understanding'
      | 'language_appreciation'
      | 'comparison';
    question: string;
    /** Reference answer points (AI-evaluated, not exact match) */
    reference_points: string[];
    score: number;
  }>;
  /** Linked knowledge point codes */
  knowledge_point_codes: string[];
  /** XP reward */
  xp_reward: number;
}

export interface PoetryRecitationBlock {
  type: 'poetry_recitation';
  /** Poem title */
  poem_title: string;
  /** Poet name */
  poet: string;
  /** Full text (for voice comparison) */
  full_text: string;
  /** Recitation mode */
  recitation_mode: 'read_aloud' | 'recite_from_memory';
  /** Rhythm annotations for guided highlighting */
  rhythm_marks?: Array<{
    position: number;
    type: 'pause' | 'emphasis' | 'prolong';
  }>;
  /** Assess tone accuracy */
  assess_tone?: boolean;
  /** Reference recitation audio URL */
  reference_audio_url?: string;
  /** Linked knowledge point codes */
  knowledge_point_codes: string[];
  /** XP reward */
  xp_reward: number;
}

export interface DraftBlock {
  type: 'draft';
  /** Draft purpose */
  draft_purpose: 'composition_planning' | 'composition_draft' | 'composition_revision';
  /** Instructions */
  instructions: string;
  /** Linked ChineseWritingBlock ID */
  target_writing_id?: string;
  /** Version number (increments on each edit) */
  version?: number;
  /** AI feedback summary (filled by AI after revision) */
  ai_feedback?: string;
  /** Submit to AI scoring */
  submit_to_ai: boolean;
}
