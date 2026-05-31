# 课程内容 Schema 规范

> 版本：v1.0 | 日期：2026-05-31
>
> 本文档定义 `lessons.content` JSONB 字段的完整数据结构。
> 目标：**前端确定性渲染 + AI Agent 可驱动 + 多学科可扩展**。

---

## 目录

1. [设计原则](#1-设计原则)
2. [顶层结构 LessonContent](#2-顶层结构-lessoncontent)
3. [Step 定义](#3-step-定义)
4. [ContentBlock 完整类型](#4-contentblock-完整类型)
5. [Step 流程模板](#5-step-流程模板)
   - [5.1 AMC 数学 — 概念新授](#51-amc-数学--概念新授)
   - [5.2 AMC 数学 — 练习/刷题](#52-amc-数学--练习刷题)
   - [5.3 AMC 数学 — 阶段测试](#53-amc-数学--阶段测试)
   - [5.4 KET 英语 — 阅读课](#54-ket-英语--阅读课)
   - [5.5 KET 英语 — 写作课](#55-ket-英语--写作课)
   - [5.6 KET 英语 — 听力课](#56-ket-英语--听力课)
   - [5.7 KET 英语 — 口语课](#57-ket-英语--口语课)
   - [5.8 KET 英语 — 词汇](#58-ket-英语--词汇)
   - [5.9 语文 — 作文课](#59-语文--作文课)
   - [5.10 语文 — 古诗词赏析课](#510-语文--古诗词赏析课)
6. [完整示例](#6-完整示例)
7. [前端组件映射](#7-前端组件映射)
8. [AI Agent 驱动约定](#8-ai-agent-驱动约定)
   - [8.4.1 语文作文 Agent Instruction 示例](#841-语文作文-agent-instruction-示例)
   - [8.4.2 古诗词 Agent Instruction 示例](#842-古诗词-agent-instruction-示例)
- [附录 A: Block 字段完整参考](#附录-a-block-字段完整参考)
- [附录 C: 评估范式对照表](#附录-c-评估范式对照表)
- [附录 D: Schema 版本迁移策略](#附录-d-schema-版本迁移策略)

---

## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **Block 组合** | 每个 Step 由一组 ContentBlock 组成，Block 是最小渲染单元 |
| **类型判别** | 所有 Block 使用 `type` 字段做 discriminated union，前端按 type 路由到对应组件 |
| **渐进交互** | Block 分为「展示型」和「交互型」，Agent 按顺序推进 |
| **学科无关** | Schema 本身不绑定学科，通过 Step 的 `phase` 和 Block 类型体现差异 |
| **版本控制** | 顶层 `schema_version` 字段，支持未来迁移 |

---

## 2. 顶层结构 LessonContent

```typescript
interface LessonContent {
  /** Schema 版本，用于前端兼容性判断 */
  schema_version: "1.0";

  /** 学科 */
  subject: "amc_math" | "ket_english" | "chn_composition" | "chn_poetry";

  /** 课程类型 */
  lesson_type:
    | "concept"       // 概念新授（AMC/KET 通用）
    | "practice"      // 引导练习
    | "assessment"    // 阶段测验
    | "review"        // 复习巩固
    | "diagnostic"    // 入学诊断
    | "mock_exam"     // 模拟考试
    | "vocab_drill"   // 词汇训练（KET 专用）
    | "grammar_drill" // 语法训练（KET 专用）
    | "mock_speaking" // 口语模拟（KET 专用）
    | "mock_listening"   // 听力模拟（KET 专用）
    | "composition"         // 作文课（语文专用）
    | "poetry_reading"      // 古诗词赏析（语文专用）
    | "poetry_dictation";    // 诗词默写训练（语文专用）

  /** 学习目标（2-5 条） */
  objectives: string[];

  /** 前置知识点 code 列表（应全部 mastered 才能开始） */
  prerequisite_codes: string[];

  /** 本课关联的知识点 code */
  knowledge_point_codes: string[];

  /** AMC 级别标记（仅 AMC 数学） */
  amc_level?: 8 | 10 | 12;

  /** KET 技能标记（仅 KET 英语） */
  ket_skill?: "reading" | "writing" | "listening" | "speaking" | "vocabulary" | "grammar";

  /** 语文年级标记（仅语文课程） */
  chn_grade?: 4 | 5 | 6;

  /** 预计时长（分钟） */
  estimated_minutes: number;

  /** XP 奖励基数 */
  xp_base: number;

  /** 通过标准 */
  passing_criteria: {
    /** 需要达到的掌握度 */
    min_mastery: number;        // 0.0 - 1.0
    /**
     * 评估题正确率。
     * - AMC 数学：题目正确率
     * - chn_composition：最低得分百分比 min_score_pct（100分制，如 0.6 = 60/100）
     * - chn_poetry：默写正确率
     */
    min_accuracy: number;       // 0.0 - 1.0
    /** 评估题最少完成数 */
    min_problems: number;
    /** 诗词赏析最低理解率（仅 chn_poetry） */
    min_appreciation_score?: number;  // 0.0 - 1.0
  };

  /** 课程步骤序列 */
  steps: LessonStep[];

  /** 课程总结 */
  summary: LessonSummary;

  /** 课程元数据（可选扩展） */
  metadata?: Record<string, unknown>;
}
```

### LessonSummary

```typescript
interface LessonSummary {
  /** 关键要点（3-5 条） */
  key_points: string[];

  /** AMC 考试提示（仅数学） */
  amc_tip?: string;

  /** 常见错误提醒 */
  common_mistakes?: string[];

  /** 下一节课 code */
  next_lesson_code?: string;
}
```

---

## 3. Step 定义

一个 Lesson 由 3-7 个 Step 有序组成。Step 是 Agent 驱动的基本推进单元。

```typescript
interface LessonStep {
  /** 步骤唯一 ID（在 lesson 内唯一） */
  id: string;                  // e.g. "engage-1", "explore-1", "evaluate-1"

  /** 教学阶段 */
  phase: StepPhase;

  /** 步骤标题（显示给学生的标题） */
  title: string;

  /** 预计时长（秒） */
  estimated_seconds: number;

  /** 内容块序列 */
  blocks: ContentBlock[];

  /**
   * 步骤完成条件
   * - "all_viewed": 学生浏览完所有 block 即可（展示型步骤）
   * - "interaction_complete": 学生完成了所有交互 block（交互型步骤）
   * - "score_threshold": 评分达到阈值（评估型步骤）
   */
  completion_mode: "all_viewed" | "interaction_complete" | "score_threshold";

  /** Agent 在此步骤的行为提示 */
  agent_instruction?: string;

  /** 步骤跳过条件（满足则自动跳过） */
  skip_if?: {
    /** 如果知识点已达到指定掌握度 */
    mastery_above?: number;
    /** 如果前置步骤全部正确 */
    previous_all_correct?: boolean;
  };
}
```

### StepPhase 枚举

```typescript
/**
 * AMC 数学使用 5E 教学模型:
 *   engage → explore → explain → elaborate → evaluate
 *
 * KET 英语使用 PPP+模型:
 *   introduce → present → practice → produce → review
 *
 * assessment / review / diagnostic 等类型可自由组合 phase
 */
type StepPhase =
  // ---- AMC 数学 5E ----
  | "engage"      // 引入：激发兴趣，建立联系
  | "explore"     // 探索：动手发现规律
  | "explain"     // 讲解：概念、定理、公式
  | "elaborate"   // 练习：引导练习，加深理解
  | "evaluate"    // 评估：检测掌握程度

  // ---- KET 英语 ----
  | "introduce"   // 导入：情境引入，激活背景知识
  | "present"     // 呈现：新语言点呈现
  | "practice"    // 练习：控制性/半控制性练习
  | "produce"     // 产出：自由表达
  | "review"      // 复习：总结归纳

  // ---- 通用 ----
  | "warmup"      // 热身
  | "transition"  // 过渡
  | "reflection"  // 反思
  | "assessment"  // 测验（用于 assessment 类型课程）
  | "diagnostic"  // 诊断（用于 diagnostic 类型课程）
  | "test"        // 模拟考试（用于 mock_exam 类型课程）
  | "summary"     // 总结

  // ---- 语文作文（写作过程模型 Writing Process Model）----
  | "observe"      // 观察：用五官感受，积累素材
  | "conceive"     // 构思：确定主题、选材、列提纲
  | "express"      // 表达：起草初稿
  | "polish"       // 润色：修改语言、调整结构
  | "assess_write" // 评估：AI评分+反思

  // ---- 语文古诗词（分层深化模型 Iterative Deepening）----
  | "read_poem"    // 读：朗读节奏、整体感知
  | "decipher"     // 解：字词释义、疏通大意
  | "appreciate"   // 赏：意象分析、手法识别
  | "comprehend"   // 悟：情感把握、主旨理解
  | "verify";      // 测：默写检测、理解性填空
```

---

## 4. ContentBlock 完整类型

每个 ContentBlock 是一个独立的渲染/交互单元。使用 `type` 字段做类型判别。

### 4.1 展示型 Block（学生被动接收）

#### TextBlock — 文本段落

```typescript
interface TextBlock {
  type: "text";
  /** Markdown 格式文本（支持 $...$ 行内 LaTeX） */
  content: string;
  /** 样式变体 */
  variant?: "body" | "caption" | "quote" | "callout" | "note" | "tip" | "warning";
}
```

#### AudioBlock — 音频播放

```typescript
interface AudioBlock {
  type: "audio";
  /** 音频 URL（TTS 生成的 .mp3） */
  url: string;
  /** 时长（秒） */
  duration_sec: number;
  /** 对应文本（用于语音+文字同步高亮） */
  transcript?: string;
  /** 朗读速度倍率 */
  speed?: 0.8 | 1.0 | 1.2;
  /** 播放器标签 */
  label?: string;
  /** 是否自动播放（课程讲解场景） */
  autoplay?: boolean;
}
```

#### ImageBlock — 图片

```typescript
interface ImageBlock {
  type: "image";
  /** 图片 URL */
  url: string;
  /** 替代文本（无障碍） */
  alt: string;
  /** 标题 */
  caption?: string;
  /** 最大宽度（px），不设则自适应 */
  max_width?: number;
}
```

#### FormulaBlock — 公式卡片

```typescript
interface FormulaBlock {
  type: "formula";
  /** LaTeX 公式 */
  latex: string;
  /** 公式标题/名称 */
  title?: string;
  /** 颜色标注 */
  color_coding?: Record<string, string>;  // e.g. { "a_b": "#4A90D9", "c": "#E74C3C" }
  /** 注释说明 */
  note?: string;
  /** 显示方式 */
  display?: "inline" | "block" | "card";
}
```

#### GeoGebraBlock — GeoGebra 交互图形

```typescript
interface GeoGebraBlock {
  type: "geogebra";
  /** GeoGebra 材料 ID 或 applet ID */
  material_id?: string;
  /** 自定义 GeoGebra XML 配置（可选） */
  applet_config?: string;
  /** 操作说明 */
  instructions: string;
  /** 宽度 */
  width?: number;
  /** 高度 */
  height?: number;
}
```

#### VideoBlock — 视频

```typescript
interface VideoBlock {
  type: "video";
  /** 视频 URL（MP4 / HLS） */
  url: string;
  /** 封面图 */
  thumbnail_url?: string;
  /** 时长（秒） */
  duration_sec: number;
  /** 标题 */
  title?: string;
  /** 是否自动播放 */
  autoplay?: boolean;
}
```

#### AnimationBlock — 动画演示

```typescript
interface AnimationBlock {
  type: "animation";
  /** 动画类型 */
  animation_type: "manim" | "lottie" | "css" | "canvas";
  /** 动画资源 URL（MP4 / JSON / 无） */
  url?: string;
  /** 标题 */
  title: string;
  /** 时长（秒） */
  duration_sec?: number;
  /** 封面图 */
  thumbnail_url?: string;
  /** CSS/Canvas 动画的内联配置 */
  inline_config?: Record<string, unknown>;
}
```

#### ExpandableBlock — 可展开/折叠内容

```typescript
interface ExpandableBlock {
  type: "expandable";
  /** 折叠时显示的标题 */
  title: string;
  /** 展开后的内容块（递归 ContentBlock） */
  content: ContentBlock[];
  /** 默认展开状态 */
  default_expanded?: boolean;
}
```

#### DividerBlock — 分隔线

```typescript
interface DividerBlock {
  type: "divider";
  /** 样式 */
  variant?: "line" | "spacing" | "dots" | "label";
  /** label 模式的文本 */
  label?: string;
}
```

#### IllustrationBlock — 插图/图解

```typescript
interface IllustrationBlock {
  type: "illustration";
  /** 图解标题 */
  title: string;
  /** 描述文字 */
  description?: string;
  /** 图片 */
  image: {
    url: string;
    alt: string;
  };
  /** 标注列表（在图片上高亮的关键区域） */
  annotations?: Array<{
    label: string;
    description: string;
    /** 相对位置 (0-1) */
    position: { x: number; y: number };
  }>;
}
```

#### CodeBlock — 代码块

```typescript
interface CodeBlock {
  type: "code";
  /** 代码内容 */
  code: string;
  /** 编程语言 */
  language?: string;
  /** 标题 */
  title?: string;
  /** 是否可运行（如 Python 计算验证） */
  runnable?: boolean;
}
```

#### TableBlock — 静态表格

```typescript
interface TableBlock {
  type: "table";
  /** 表头 */
  headers: string[];
  /** 数据行 */
  rows: Array<string[]>;
  /** 标题 */
  title?: string;
}
```

---

### 4.2 交互型 Block（学生需要操作）

#### ProblemBlock — 数学题目（AMC 通用）

```typescript
interface ProblemBlock {
  type: "problem";
  /** 题目 ID（关联 problems 表，可选） */
  problem_id?: string;
  /** 题目类型 */
  problem_type: "multiple_choice" | "fill_blank" | "short_answer";
  /** 难度 1-5 */
  difficulty: 1 | 2 | 3 | 4 | 5;
  /** 题干（Markdown，支持 LaTeX） */
  question: string;
  /** 选项（multiple_choice 时使用） */
  options?: Array<{
    label: string;    // "A", "B", "C", "D", "E"
    content: string;
  }>;
  /** 正确答案 */
  correct_answer: string;
  /** 解题过程（答错或完成后显示） */
  explanation?: string;
  /** 5 级提示 */
  hints: Array<{
    level: 0 | 1 | 2 | 3 | 4;
    text: string;
    audio_url?: string;
  }>;
  /** 关联知识点 code */
  knowledge_point_codes: string[];
  /** XP 奖励 */
  xp_reward: number;
  /** 附属图形/配图 */
  figure?: ImageBlock;
  /** 附属 LaTeX 内容 */
  latex_expressions?: string[];
}
```

#### InteractiveTableBlock — 交互式填表

```typescript
interface InteractiveTableBlock {
  type: "interactive_table";
  /** 表头 */
  headers: string[];
  /** 数据行，null 表示需要学生填写 */
  rows: Array<Array<string | null>>;
  /** 填写提示 */
  instructions?: string;
  /** 正确答案（用于校验） */
  answer_rows?: Array<Array<string>>;
  /** 是否允许部分正确 */
  partial_credit?: boolean;
}
```

#### ScratchpadBlock — 草稿板/手写板

```typescript
interface ScratchpadBlock {
  type: "scratchpad";
  /** 宽度 */
  width?: number;
  /** 高度 */
  height?: number;
  /** 提示文字 */
  placeholder?: string;
  /** 是否提交内容到 AI（用于评分/反馈） */
  submit_to_ai?: boolean;
}
```

#### VoiceInputBlock — 语音输入

```typescript
interface VoiceInputBlock {
  type: "voice_input";
  /** 提示/问题 */
  prompt: string;
  /** 语音播放提示的音频 URL */
  prompt_audio_url?: string;
  /** 最大录音时长（秒） */
  max_duration?: number;
  /** 期望的答案模式（用于 ASR 后验证） */
  expected_answer?: string;
  /** 数学语音识别：期望的 LaTeX 结果 */
  expected_latex?: string;
  /** 输入模式 */
  input_modes: Array<"voice" | "text" | "drawing">;
}
```

#### WritingBlock — 写作编辑器（KET）

```typescript
interface WritingBlock {
  type: "writing";
  /** 写作任务描述 */
  task: string;
  /** 必须包含的要点 */
  required_points: string[];
  /** 最少字数 */
  min_words: number;
  /** 最多字数 */
  max_words: number;
  /** 字数建议 */
  target_words: number;
  /** 写作类型 */
  writing_type: "email" | "short_story" | "message";
  /** 评分标准（Cambridge Band 0-5） */
  rubric?: {
    content_max: 5;
    organisation_max: 5;
    language_max: 5;
  };
}
```

#### ChineseWritingBlock — 中文作文编辑器（语文）

```typescript
interface ChineseWritingBlock {
  type: "chn_writing";
  /** 写作任务描述 */
  task: string;
  /** 题目要求/提示 */
  prompt?: string;
  /** 写作类型 */
  writing_type: "narrative" | "descriptive" | "imaginative" | "practical" | "expository";
  /** 目标字数 */
  target_chars: number;
  /** 最少字数 */
  min_chars: number;
  /** 最多字数 */
  max_chars: number;
  /** 评分标准（100分制，4维度） */
  rubric: {
    content_max: 40;        // 内容分
    structure_max: 20;      // 结构分
    language_max: 30;       // 语言分
    handwriting_max: 10;    // 书写分
  };
  /** 是否允许修改重写 */
  allow_revision: boolean;
  /** 最多修改次数 */
  max_revisions?: number;
  /** 作文评分 Prompt ID（引用 system-design.md 中的 Prompt） */
  scoring_prompt_id: string;
}
```

#### PoetryDictationBlock — 诗词默写（语文）

```typescript
interface PoetryDictationBlock {
  type: "poetry_dictation";
  /** 诗歌标题 */
  poem_title: string;
  /** 诗人 */
  poet: string;
  /** 默写模式 */
  dictation_mode: "full" | "partial" | "fill_blank";
  /** 完整原文（用于对照） */
  full_text: string;
  /** 填空模式的模板，用 {{gap:N}} 标记空缺 */
  template?: string;
  /** 每个空缺的配置 */
  gaps?: Array<{
    index: number;
    /** 正确答案（严格匹配） */
    answer: string;
    /** 可接受的异体字/通假字 */
    acceptable_variants?: string[];
  }>;
  /** 藏字模式：哪些字需要填写 */
  hidden_indices?: number[];
  /** 关联知识点 code */
  knowledge_point_codes: string[];
  /** XP 奖励 */
  xp_reward: number;
}
```

#### PoetryAppreciationBlock — 诗词赏析（语文）

```typescript
interface PoetryAppreciationBlock {
  type: "poetry_appreciation";
  /** 诗歌标题 */
  poem_title: string;
  /** 诗人 */
  poet: string;
  /** 朝代 */
  dynasty: string;
  /** 完整原文（带注释标注） */
  full_text: string;
  /** 赏析题目 */
  questions: Array<{
    id: string;
    /** 题目类型 */
    question_type: "imagery_analysis" | "technique_identification" | "emotion_understanding" | "language_appreciation" | "comparison";
    /** 题目 */
    question: string;
    /** 参考答案要点（非精确匹配，AI评估） */
    reference_points: string[];
    /** 分值 */
    score: number;
  }>;
  /** 关联知识点 code */
  knowledge_point_codes: string[];
  /** XP 奖励 */
  xp_reward: number;
}
```

#### PoetryRecitationBlock — 诗词朗读/背诵（语文）

```typescript
interface PoetryRecitationBlock {
  type: "poetry_recitation";
  /** 诗歌标题 */
  poem_title: string;
  /** 诗人 */
  poet: string;
  /** 原文（用于语音对比） */
  full_text: string;
  /** 朗读模式 */
  recitation_mode: "read_aloud" | "recite_from_memory";
  /** 节奏标注（用于高亮引导） */
  rhythm_marks?: Array<{
    position: number;     // 字的位置
    type: "pause" | "emphasis" | "prolong";
  }>;
  /** 是否要求声调评分 */
  assess_tone?: boolean;
  /** 参考朗读音频 URL */
  reference_audio_url?: string;
  /** 关联知识点 code */
  knowledge_point_codes: string[];
  /** XP 奖励 */
  xp_reward: number;
}
```

#### DraftBlock — 草稿版本管理（语文作文专用）

```typescript
interface DraftBlock {
  type: "draft";
  /** 草稿用途 */
  draft_purpose: "composition_planning" | "composition_draft" | "composition_revision";
  /** 提示文字 */
  instructions: string;
  /** 关联的 ChineseWritingBlock 的 ID */
  target_writing_id?: string;
  /** 版本号（每次修改递增） */
  version?: number;
  /** AI 反馈摘要（修改后由 AI 填充） */
  ai_feedback?: string;
  /** 是否提交到 AI 评分 */
  submit_to_ai: boolean;
}
```

#### ListeningBlock — 听力练习（KET）

```typescript
interface ListeningBlock {
  type: "listening";
  /** 音频 URL */
  audio_url: string;
  /** 音频时长 */
  duration_sec: number;
  /** 播放模式 */
  play_mode: "unlimited" | "twice" | "once";
  /** 语速倍率 */
  speed?: 0.8 | 1.0 | 1.2;
  /** 听力原文（答题后展示） */
  transcript?: string;
  /** 配套题目 */
  questions: ListeningQuestion[];
}

interface ListeningQuestion {
  id: string;
  question_type: "multiple_choice" | "fill_blank" | "matching" | "true_false";
  question: string;
  options?: string[];
  correct_answer: string | string[];
  /** 答案在原文中的出处 */
  transcript_reference?: string;
}
```

#### SpeakingBlock — 口语练习（KET）

```typescript
interface SpeakingBlock {
  type: "speaking";
  /** 口语任务类型 */
  speaking_type: "personal_questions" | "discussion" | "picture_description";
  /** AI 考官的第一个问题/提示 */
  initial_prompt: string;
  /** 语音提示的音频 URL */
  prompt_audio_url?: string;
  /** 最大录音时长（秒） */
  max_duration_sec: number;
  /** 讨论用的图片（discussion / picture_description） */
  discussion_image?: ImageBlock;
  /** 后续追问列表（AI 依次或根据回答选择） */
  follow_up_prompts?: Array<{
    condition?: "always" | "if_short_answer" | "if_correct" | "if_incorrect";
    prompt: string;
  }>;
  /** 评分维度 */
  assessment_criteria?: Array<"grammar_vocabulary" | "pronunciation" | "interactive_communication" | "global_achievement">;
}
```

#### MatchingBlock — 拖拽匹配（KET）

```typescript
interface MatchingBlock {
  type: "matching";
  /** 指令 */
  instructions: string;
  /** 左侧项目 */
  left_items: Array<{ id: string; content: string }>;
  /** 右侧项目（会被打乱顺序） */
  right_items: Array<{ id: string; content: string }>;
  /** 正确配对 left_id → right_id */
  correct_pairs: Record<string, string>;
}
```

#### GapFillBlock — 完形填空（KET）

```typescript
interface GapFillBlock {
  type: "gap_fill";
  /** 文本模板，用 {{gap:N}} 标记空格 */
  template: string;
  /** 每个 gap 的配置 */
  gaps: Array<{
    index: number;
    /** 下拉选项（有则下拉选择，无则手填） */
    options?: string[];
    /** 正确答案 */
    answer: string;
    /** 可接受的替代答案（大小写等） */
    acceptable_answers?: string[];
  }>;
  /** 标题 */
  title?: string;
}
```

#### ReadingPassageBlock — 阅读文章（KET）

```typescript
interface ReadingPassageBlock {
  type: "reading_passage";
  /** 文章标题 */
  title: string;
  /** 文章段落 */
  paragraphs: string[];
  /** 词汇提示（点击查看释义） */
  vocabulary_tips?: Array<{
    word: string;
    definition: string;
    paragraph_index: number;
  }>;
  /** 理解题目 */
  questions: Array<{
    id: string;
    question: string;
    type: "multiple_choice" | "true_false" | "open_ended";
    options?: string[];
    correct_answer?: string;
    /** 答案出处（段落索引） */
    reference_paragraph?: number;
  }>;
}
```

#### VocabCardBlock — 词汇卡片（KET）

```typescript
interface VocabCardBlock {
  type: "vocab_card";
  /** 单词 */
  word: string;
  /** 音标 */
  phonetic?: string;
  /** 释义（英文，不用中文） */
  definition: string;
  /** 例句 */
  example_sentence: string;
  /** 配图 */
  image_url?: string;
  /** 语音 URL */
  audio_url?: string;
  /** 练习模式 */
  practice_mode: "recognize" | "recall" | "spell" | "use_in_sentence";
}
```

#### PhotoUploadBlock — 拍照上传

```typescript
interface PhotoUploadBlock {
  type: "photo_upload";
  /** 提示文字 */
  instructions: string;
  /** 支持的文件类型 */
  accept?: "image" | "image_and_pdf";
  /** 最大文件大小（MB） */
  max_size_mb?: number;
  /** AI 处理方式 */
  ai_action?: "ocr_math" | "ocr_text" | "describe_image";
}
```

---

### 4.3 ContentBlock 联合类型汇总

```typescript
type ContentBlock =
  // 展示型
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
  // 交互型 — 通用
  | ProblemBlock
  | InteractiveTableBlock
  | ScratchpadBlock
  | VoiceInputBlock
  | PhotoUploadBlock
  // 交互型 — KET 英语
  | WritingBlock
  | ListeningBlock
  | SpeakingBlock
  | MatchingBlock
  | GapFillBlock
  | ReadingPassageBlock
  | VocabCardBlock
  // 交互型 — 语文
  | ChineseWritingBlock
  | PoetryDictationBlock
  | PoetryAppreciationBlock
  | PoetryRecitationBlock
  | DraftBlock;
```

---

## 5. Step 流程模板

不同课程类型使用不同的 Step 序列模板。

### 5.1 AMC 数学 — 概念新授 (`lesson_type: "concept"`)

```
Step 1: engage        (2-3 min)  引入：1 个场景/问题激发兴趣
Step 2: explore       (4-6 min)  探索：1-2 个交互活动发现规律
Step 3: explain       (4-6 min)  讲解：概念 + 公式 + 图示
Step 4: elaborate     (6-10 min) 练习：2-4 道引导练习题
Step 5: evaluate      (3-5 min)  评估：3 道检测题
```

**Steps 结构示例**：

```typescript
steps: [
  {
    id: "engage",
    phase: "engage",
    title: "引入",
    estimated_seconds: 180,
    completion_mode: "all_viewed",
    blocks: [
      { type: "audio", url: "...", transcript: "...", autoplay: true },
      { type: "geogebra", material_id: "pythagoras_explore", instructions: "..." },
      { type: "voice_input", prompt: "...", input_modes: ["voice", "text"] }
    ],
    agent_instruction: "用轻松的口吻引入主题，引导学生观察图形"
  },
  {
    id: "explore",
    phase: "explore",
    title: "探索发现",
    estimated_seconds: 300,
    completion_mode: "interaction_complete",
    blocks: [
      { type: "text", content: "再试试这个..." },
      { type: "interactive_table", headers: [...], rows: [...], answer_rows: [...] },
      { type: "voice_input", prompt: "你发现了什么规律？", input_modes: ["voice", "text"] }
    ]
  },
  // ... explain, elaborate, evaluate
]
```

### 5.2 AMC 数学 — 练习/刷题 (`lesson_type: "practice"`)

```
Step 1: warmup        (1-2 min)  热身：回顾相关知识点
Step 2: assessment    (15-25 min) 练习：5-10 道题，苏格拉底式引导
Step 3: reflection    (2-3 min)  反思：总结关键技能
```

### 5.3 AMC 数学 — 阶段测试 (`lesson_type: "assessment"`)

```
Step 1: warmup        (1 min)    提示测试规则
Step 2: test          (15-20 min) 8-10 道题，限时，不给提示
Step 3: summary       (3-5 min)  结果 + 错题分析
```

### 5.4 KET 英语 — 阅读课 (`ket_skill: "reading"`)

```
Step 1: introduce     (2-3 min)  导入：情境/图片/问题激活背景知识
Step 2: present       (5-8 min)  阅读：展示文章，指导阅读策略
Step 3: practice      (8-12 min) 练习：按题型逐一练习（7 种题型）
Step 4: review        (3-5 min)  复习：总结词汇/语法点
```

### 5.5 KET 英语 — 写作课 (`ket_skill: "writing"`)

```
Step 1: introduce     (2-3 min)  导入：展示题目要求，分析要点
Step 2: present       (3-5 min)  呈现：展示范文，标注结构
Step 3: practice      (3-5 min)  练习：关键句型/词汇练习
Step 4: produce       (8-12 min) 产出：学生独立写作
Step 5: review        (3-5 min)  复习：AI 评分 + 反馈 + 修改
```

### 5.6 KET 英语 — 听力课 (`ket_skill: "listening"`)

```
Step 1: introduce     (2-3 min)  导入：话题/关键词预教
Step 2: practice      (10-15 min)练习：按题型播放音频 + 答题
Step 3: review        (3-5 min)  复习：对答案 + 原文对照
```

### 5.7 KET 英语 — 口语课 (`ket_skill: "speaking"`)

```
Step 1: introduce     (2-3 min)  导入：介绍口语考试流程
Step 2: present       (3-5 min)  呈现：展示优秀回答范例
Step 3: practice      (5-8 min)  练习：模拟 Part 1 个人问答
Step 4: produce       (5-8 min)  产出：模拟 Part 2 讨论
Step 5: review        (3-5 min)  复习：AI 评分 + 发音反馈
```

### 5.8 KET 英语 — 词汇 (`lesson_type: "vocab_drill"`)

```
Step 1: present       (5-8 min)  呈现：5-10 个新词（卡片 + 图片 + 发音）
Step 2: practice      (8-12 min) 练习：认词 → 回忆 → 拼写 → 造句
Step 3: review        (2-3 min)  复习：间隔重复安排
```

### 5.9 语文 — 作文课 (`subject: "chn_composition"`)

```
Step 1: observe       (3-5 min)  观察：展示场景/图片/文字，引导学生用五官感受
Step 2: conceive      (3-5 min)  构思：确定主题，选择素材，列写作提纲
Step 3: express       (8-15 min) 表达：学生独立写作初稿（目标300-500字）
Step 4: polish        (5-8 min)  润色：AI反馈后修改语言和结构
Step 5: assess_write  (3-5 min)  评估：AI多维评分+优秀段落展示+总结
```

> 作文课总时长 30-45 分钟。`express` 步骤支持跨会话续写（通过 DraftBlock 版本管理）。
> 与数学不同：语文作文的 AI 教学**必须主动示范**（展示范文、好句），而非苏格拉底式引导。

### 5.10 语文 — 古诗词赏析课 (`subject: "chn_poetry"`)

```
Step 1: read_poem    (3-4 min)  读：节奏标注+朗读指导+AI朗读示范
Step 2: decipher     (3-5 min)  解：关键字词释义+背景故事+疏通大意
Step 3: appreciate   (5-8 min)  赏：意象解读+手法分析+名句品鉴
Step 4: comprehend   (3-5 min)  悟：情感把握+主旨归纳+联系生活
Step 5: verify       (3-5 min)  测：默写检测+理解性填空+赏析题
```

> 古诗词采用**分层深化**学习：背诵(机械) → 理解(语义) → 赏析(审美)逐层递进。
> 掌握度分两个维度追踪：背诵掌握度（FSRS二元）和赏析能力（等级制）。

---

## 6. 完整示例

### 6.1 AMC 勾股定理 B3 — 概念新授

```json
{
  "schema_version": "1.0",
  "subject": "amc_math",
  "lesson_type": "concept",
  "objectives": [
    "理解勾股定理 a² + b² = c² 的含义",
    "能用勾股定理求直角三角形的边长",
    "识别勾股定理的适用条件（仅直角三角形）"
  ],
  "prerequisite_codes": ["AMC-GEO-B2"],
  "knowledge_point_codes": ["AMC-GEO-B3"],
  "amc_level": 8,
  "estimated_minutes": 25,
  "xp_base": 100,
  "passing_criteria": {
    "min_mastery": 0.6,
    "min_accuracy": 0.8,
    "min_problems": 3
  },
  "steps": [
    {
      "id": "engage",
      "phase": "engage",
      "title": "引入：一个古老的发现",
      "estimated_seconds": 180,
      "completion_mode": "all_viewed",
      "blocks": [
        {
          "type": "audio",
          "url": "s3://lessons/B3/engage-intro.mp3",
          "duration_sec": 15,
          "transcript": "今天我们来学一个有3000年历史的定理。先看这个直角三角形……",
          "autoplay": true
        },
        {
          "type": "geogebra",
          "material_id": "pythagoras_explore",
          "instructions": "拖动三角形顶点，观察三边长度的变化。猜猜斜边和两条直角边有什么关系？",
          "width": 600,
          "height": 400
        },
        {
          "type": "voice_input",
          "prompt": "你能量出斜边多长吗？试试拖动测量工具。",
          "input_modes": ["voice", "text"]
        }
      ],
      "agent_instruction": "用轻松的口吻引入。引导学生观察图形。不要直接说出公式。"
    },
    {
      "id": "explore",
      "phase": "explore",
      "title": "探索：发现规律",
      "estimated_seconds": 300,
      "completion_mode": "interaction_complete",
      "blocks": [
        {
          "type": "text",
          "content": "好，再试试不同的直角三角形，填一下这个表格："
        },
        {
          "type": "interactive_table",
          "headers": ["a", "b", "c", "a² + b²"],
          "rows": [
            ["3", "4", "5", "9 + 16 = 25"],
            ["5", "12", null, "25 + 144 = ?"],
            ["8", "15", null, null],
            ["6", "8", null, null]
          ],
          "answer_rows": [
            ["3", "4", "5", "9 + 16 = 25"],
            ["5", "12", "13", "25 + 144 = 169"],
            ["8", "15", "17", "64 + 225 = 289"],
            ["6", "8", "10", "36 + 64 = 100"]
          ],
          "instructions": "填写缺失的 c 值和 a²+b² 的计算结果"
        },
        {
          "type": "voice_input",
          "prompt": "你发现规律了吗？a²+b² 和 c 有什么关系？",
          "input_modes": ["voice", "text"]
        }
      ],
      "agent_instruction": "引导学生填写表格并发现 a²+b²=c² 的规律。如果学生没发现，追问'看看 a²+b² 和 c²'。"
    },
    {
      "id": "explain",
      "phase": "explain",
      "title": "讲解：勾股定理",
      "estimated_seconds": 300,
      "completion_mode": "all_viewed",
      "blocks": [
        {
          "type": "text",
          "content": "你刚重新发现了**勾股定理**！",
          "variant": "callout"
        },
        {
          "type": "formula",
          "latex": "a^2 + b^2 = c^2",
          "title": "勾股定理 (Pythagorean Theorem)",
          "color_coding": {
            "a_b": "#4A90D9",
            "c": "#E74C3C"
          },
          "note": "⚠️ 只适用于直角三角形！",
          "display": "card"
        },
        {
          "type": "text",
          "content": "- **a, b** = 直角边 (legs)\n- **c** = 斜边 (hypotenuse)，最长的那条边"
        },
        {
          "type": "illustration",
          "title": "经典面积图解",
          "description": "直角三角形三边上的正方形面积关系：a² + b² = c²",
          "image": {
            "url": "s3://lessons/B3/pythagorean_squares.png",
            "alt": "勾股定理面积图解：直角三角形三边各有一个正方形，两个小正方形面积等于大正方形面积"
          },
          "annotations": [
            { "label": "a²", "description": "直角边 a 上的正方形", "position": { "x": 0.2, "y": 0.3 } },
            { "label": "b²", "description": "直角边 b 上的正方形", "position": { "x": 0.5, "y": 0.7 } },
            { "label": "c²", "description": "斜边 c 上的正方形", "position": { "x": 0.8, "y": 0.2 } }
          ]
        },
        {
          "type": "audio",
          "url": "s3://lessons/B3/explain-amc-tip.mp3",
          "duration_sec": 8,
          "transcript": "这个定理在 AMC 大约 50% 的几何题中都会用到！"
        },
        {
          "type": "expandable",
          "title": "📐 面积证明动画",
          "content": [
            {
              "type": "animation",
              "animation_type": "manim",
              "url": "s3://lessons/B3/area_proof.mp4",
              "title": "面积证明：a² + b² = c²",
              "duration_sec": 45,
              "thumbnail_url": "s3://lessons/B3/area_proof_thumb.png"
            }
          ]
        },
        {
          "type": "expandable",
          "title": "📝 代数证明",
          "content": [
            {
              "type": "text",
              "content": "设直角三角形两直角边为 a, b，斜边为 c。\n\n利用正方形的重新排列可以证明：\n\n(a + b)² = c² + 4 × (½ab)\na² + 2ab + b² = c² + 2ab\n\n∴ **a² + b² = c²**"
            }
          ]
        }
      ],
      "agent_instruction": "确认学生的发现。展示公式卡片。强调只适用于直角三角形。"
    },
    {
      "id": "elaborate",
      "phase": "elaborate",
      "title": "练习：巩固运用",
      "estimated_seconds": 480,
      "completion_mode": "interaction_complete",
      "blocks": [
        {
          "type": "text",
          "content": "来做几道练习巩固一下！",
          "variant": "callout"
        },
        {
          "type": "problem",
          "problem_type": "fill_blank",
          "difficulty": 1,
          "question": "直角三角形的两条直角边分别是 **6** 和 **8**，斜边长度是多少？",
          "correct_answer": "10",
          "explanation": "6² + 8² = 36 + 64 = 100，所以 c = √100 = 10",
          "hints": [
            { "level": 0, "text": "你觉得第一步应该做什么？" },
            { "level": 1, "text": "这是一个直角三角形，试试勾股定理" },
            { "level": 2, "text": "a² + b² = c²，代入 a=6, b=8" },
            { "level": 3, "text": "6² + 8² = 36 + 64 = 100，c = √100 = ?" },
            { "level": 4, "text": "类似题：3² + 4² = 9 + 16 = 25，c = √25 = 5" }
          ],
          "knowledge_point_codes": ["AMC-GEO-B3"],
          "xp_reward": 20,
          "scratchpad": true
        },
        {
          "type": "problem",
          "problem_type": "fill_blank",
          "difficulty": 2,
          "question": "直角三角形的斜边是 **13**，一条直角边是 **5**，另一条直角边是多少？",
          "correct_answer": "12",
          "explanation": "c² - a² = b² → 13² - 5² = 169 - 25 = 144，b = √144 = 12",
          "hints": [
            { "level": 0, "text": "这次已知斜边和一条直角边，怎么求另一条？" },
            { "level": 1, "text": "勾股定理可以变形：b² = c² - a²" },
            { "level": 2, "text": "b² = 13² - 5² = 169 - 25" },
            { "level": 3, "text": "b² = 144，所以 b = ?" },
            { "level": 4, "text": "类似题：斜边 5，一条边 3 → b² = 25 - 9 = 16，b = 4" }
          ],
          "knowledge_point_codes": ["AMC-GEO-B3"],
          "xp_reward": 25,
          "scratchpad": true
        },
        {
          "type": "problem",
          "problem_type": "multiple_choice",
          "difficulty": 3,
          "question": "正方形的对角线长为 **10√2**，正方形的边长是多少？",
          "options": [
            { "label": "A", "content": "10" },
            { "label": "B", "content": "10√2" },
            { "label": "C", "content": "5√2" },
            { "label": "D", "content": "20" },
            { "label": "E", "content": "5" }
          ],
          "correct_answer": "A",
          "explanation": "正方形对角线把正方形分成两个等腰直角三角形。设边长为 s，则 s² + s² = (10√2)² → 2s² = 200 → s² = 100 → s = 10",
          "hints": [
            { "level": 0, "text": "正方形的对角线有什么特殊性质？" },
            { "level": 1, "text": "对角线把正方形分成两个直角三角形，两条直角边相等" },
            { "level": 2, "text": "设边长 s，则 s² + s² = (10√2)²" },
            { "level": 3, "text": "2s² = 200，所以 s² = ?" },
            { "level": 4, "text": "类似题：对角线 5√2 → 2s² = 50 → s² = 25 → s = 5" }
          ],
          "knowledge_point_codes": ["AMC-GEO-B3", "AMC-GEO-B5"],
          "xp_reward": 35
        }
      ],
      "agent_instruction": "苏格拉底式引导，不要直接给答案。每次只问一个问题。如果学生用提示，XP 相应减少。"
    },
    {
      "id": "evaluate",
      "phase": "evaluate",
      "title": "小测验",
      "estimated_seconds": 240,
      "completion_mode": "score_threshold",
      "blocks": [
        {
          "type": "text",
          "content": "最后来做 3 道检测题，通过后就能解锁下一课 **B4 组合图形面积**！",
          "variant": "callout"
        },
        {
          "type": "problem",
          "problem_type": "multiple_choice",
          "difficulty": 2,
          "question": "一个直角三角形三边为 7, 24, 25。下面哪个是斜边？",
          "options": [
            { "label": "A", "content": "7" },
            { "label": "B", "content": "24" },
            { "label": "C", "content": "25" },
            { "label": "D", "content": "无法确定" }
          ],
          "correct_answer": "C",
          "explanation": "7² + 24² = 49 + 576 = 625 = 25²，所以斜边是最长的 25",
          "hints": [
            { "level": 0, "text": "斜边是直角三角形中最长的边" },
            { "level": 1, "text": "验证 7² + 24² 是否等于 25²" }
          ],
          "knowledge_point_codes": ["AMC-GEO-B3"],
          "xp_reward": 15
        },
        {
          "type": "problem",
          "problem_type": "fill_blank",
          "difficulty": 2,
          "question": "等腰直角三角形的斜边为 8，则直角边长为多少？（保留根号）",
          "correct_answer": "4√2",
          "explanation": "设直角边 a，则 a² + a² = 8² → 2a² = 64 → a² = 32 → a = 4√2",
          "hints": [
            { "level": 0, "text": "等腰直角三角形的两条直角边相等" },
            { "level": 1, "text": "2a² = 64，a² = ?" }
          ],
          "knowledge_point_codes": ["AMC-GEO-B3"],
          "xp_reward": 15
        },
        {
          "type": "problem",
          "problem_type": "multiple_choice",
          "difficulty": 3,
          "question": "下面哪组数可以是直角三角形的三边？",
          "options": [
            { "label": "A", "content": "4, 5, 6" },
            { "label": "B", "content": "5, 12, 14" },
            { "label": "C", "content": "8, 15, 17" },
            { "label": "D", "content": "9, 10, 12" }
          ],
          "correct_answer": "C",
          "explanation": "8² + 15² = 64 + 225 = 289 = 17² ✅。其他选项不满足勾股定理。",
          "hints": [
            { "level": 0, "text": "验证每组的 a² + b² 是否等于 c²（c 取最大的数）" },
            { "level": 1, "text": "8² + 15² = ?" }
          ],
          "knowledge_point_codes": ["AMC-GEO-B3"],
          "xp_reward": 20
        }
      ],
      "agent_instruction": "这是正式评估，不给提示（除非学生请求）。记录每题的对错和用时。80% 正确率通过。"
    }
  ],
  "summary": {
    "key_points": [
      "勾股定理：a² + b² = c²（仅适用于直角三角形）",
      "已知两条边可以求第三条边",
      "常见勾股数：(3,4,5), (5,12,13), (8,15,17)"
    ],
    "amc_tip": "AMC 约 50% 几何题涉及勾股定理，务必熟练",
    "common_mistakes": [
      "忘记勾股定理只适用于直角三角形",
      "混淆直角边和斜边（斜边是最长边）",
      "忘记开根号：a²+b² 算完之后要取 √"
    ],
    "next_lesson_code": "AMC-GEO-B7"
  }
}
```

### 6.2 KET 写作 Part 6 — 邮件写作

```json
{
  "schema_version": "1.0",
  "subject": "ket_english",
  "lesson_type": "concept",
  "ket_skill": "writing",
  "objectives": [
    "理解 KET Part 6 邮件写作的题目要求",
    "掌握 25-35 词短邮件的结构",
    "确保覆盖题目要求的 3 个要点"
  ],
  "prerequisite_codes": ["KET-GRAM-PRESENT", "KET-VOC-DAILY"],
  "knowledge_point_codes": ["KET-WRITE-PART6"],
  "estimated_minutes": 25,
  "xp_base": 80,
  "passing_criteria": {
    "min_mastery": 0.5,
    "min_accuracy": 0.6,
    "min_problems": 1
  },
  "steps": [
    {
      "id": "introduce",
      "phase": "introduce",
      "title": "导入：认识 KET 写作",
      "estimated_seconds": 180,
      "completion_mode": "all_viewed",
      "blocks": [
        {
          "type": "audio",
          "url": "s3://lessons/KET-W6/intro.mp3",
          "duration_sec": 20,
          "transcript": "KET 写作 Part 6 要求你写一封短邮件，大约 25-35 个词。你需要包含题目要求的 3 个要点。"
        },
        {
          "type": "text",
          "content": "**KET Part 6 邮件写作要点：**\n- 写一封回复邮件\n- 必须包含 **3 个要点**\n- 字数：**25 词以上**\n- 时间：约 8 分钟"
        },
        {
          "type": "text",
          "content": "评分标准：\n| 维度 | 说明 |\n|------|------|\n| **Content** | 3 个要点是否都传达了 |\n| **Organisation** | 结构是否清晰连贯 |\n| **Language** | 语法和拼写错误程度 |",
          "variant": "note"
        }
      ],
      "agent_instruction": "用中文讲解，英文术语保留。强调 3 个要点是最重要的评分标准。"
    },
    {
      "id": "present",
      "phase": "present",
      "title": "呈现：分析范文",
      "estimated_seconds": 300,
      "completion_mode": "all_viewed",
      "blocks": [
        {
          "type": "text",
          "content": "**题目示例：**\n你收到了英国笔友 Sam 的邮件。请写一封回复，包含：\n1. 告诉 Sam 你的年龄\n2. 描述你最喜欢的科目\n3. 你周末通常做什么",
          "variant": "callout"
        },
        {
          "type": "text",
          "content": "**范文：**\n\n> Hi Sam,\n>\n> I'm 13 years old. My favorite subject is math because it is interesting. On weekends I usually play basketball with my friends.\n>\n> Best wishes,\n> Li Ming"
        },
        {
          "type": "text",
          "content": "分析：\n- ✅ 要点 1 (年龄)：\"I'm 13 years old.\"\n- ✅ 要点 2 (科目)：\"My favorite subject is math...\"\n- ✅ 要点 3 (周末)：\"On weekends I usually play basketball...\"\n- 📏 字数：27 词 ✓\n- 🏗️ 结构：开场 → 三个要点 → 结尾",
          "variant": "tip"
        }
      ]
    },
    {
      "id": "practice",
      "phase": "practice",
      "title": "练习：关键句型",
      "estimated_seconds": 300,
      "completion_mode": "interaction_complete",
      "blocks": [
        {
          "type": "text",
          "content": "先练习几个写作常用的句型："
        },
        {
          "type": "gap_fill",
          "template": "I am {{gap:0}} years old. My favorite {{gap:1}} is English. On weekends I usually {{gap:2}} with my friends.",
          "gaps": [
            { "index": 0, "answer": "13", "acceptable_answers": ["12","14","15","11"] },
            { "index": 1, "answer": "subject", "acceptable_answers": ["Subject"] },
            { "index": 2, "answer": "play football", "acceptable_answers": ["play soccer", "watch TV", "read books"] }
          ],
          "title": "填空练习"
        },
        {
          "type": "problem",
          "problem_type": "multiple_choice",
          "difficulty": 1,
          "question": "Which opening is best for a KET email to a pen friend?",
          "options": [
            { "label": "A", "content": "Dear Sir or Madam," },
            { "label": "B", "content": "Hi Sam," },
            { "label": "C", "content": "To whom it may concern," },
            { "label": "D", "content": "Hey what's up!!!" }
          ],
          "correct_answer": "B",
          "explanation": "\"Hi + 名字\" 是给笔友写信最合适的开头，既友好又得体。",
          "hints": [
            { "level": 0, "text": "Think about the relationship - this is a pen friend, not a formal letter." },
            { "level": 1, "text": "For friends, use informal greetings like \"Hi\" or \"Dear\" + first name." }
          ],
          "knowledge_point_codes": ["KET-WRITE-PART6"],
          "xp_reward": 10
        }
      ],
      "agent_instruction": "讲解句型时用中英双语。纠正语法错误时要具体指出位置。"
    },
    {
      "id": "produce",
      "phase": "produce",
      "title": "产出：独立写作",
      "estimated_seconds": 480,
      "completion_mode": "interaction_complete",
      "blocks": [
        {
          "type": "text",
          "content": "现在轮到你来写了！",
          "variant": "callout"
        },
        {
          "type": "writing",
          "task": "你的英国笔友 Emma 给你发了一封邮件，问你关于你的学校生活。请写一封回复邮件。",
          "required_points": [
            "Tell Emma what you study at school",
            "Say what you like about your school",
            "Ask Emma about her school"
          ],
          "min_words": 25,
          "max_words": 50,
          "target_words": 35,
          "writing_type": "email",
          "rubric": {
            "content_max": 5,
            "organisation_max": 5,
            "language_max": 5
          }
        }
      ],
      "agent_instruction": "学生写作时不打扰。提交后使用 KET 写作评分 Prompt 进行评分。给出具体的错误标注和修改建议。如果 Band < 3，建议修改后重新提交。"
    },
    {
      "id": "review",
      "phase": "review",
      "title": "复习：总结要点",
      "estimated_seconds": 180,
      "completion_mode": "all_viewed",
      "skip_if": {
        "previous_all_correct": true
      },
      "blocks": [
        {
          "type": "text",
          "content": "**KET 邮件写作检查清单：**\n- [ ] 包含了 3 个要点？\n- [ ] 字数 25+ 词？\n- [ ] 用了 \"Hi + 名字\" 开头？\n- [ ] 用了 \"Best wishes\" 结尾？\n- [ ] 没有严重的语法错误？",
          "variant": "tip"
        }
      ],
      "agent_instruction": "简要总结。鼓励学生。"
    }
  ],
  "summary": {
    "key_points": [
      "KET 邮件写作必须覆盖 3 个要点",
      "字数至少 25 词，目标 35 词左右",
      "使用友好的开头 (Hi...) 和结尾 (Best wishes...)"
    ],
    "common_mistakes": [
      "遗漏某个要点",
      "\"I want go\" → \"I want to go\"",
      "\"On weekend\" → \"On weekends\""
    ],
    "next_lesson_code": "KET-WRITE-PART7"
  }
}
```

---

## 7. 前端组件映射

每个 `ContentBlock.type` 对应一个前端 React 组件。

### 7.1 映射表

| Block type | 前端组件 | 现有状态 |
|------------|---------|---------|
| `text` | `<MarkdownRenderer />` | 需新建（支持 Markdown + 行内 LaTeX） |
| `audio` | `<AudioPlayer />` | ✅ `components/ket/audio-player.tsx` |
| `image` | `<ImageBlock />` | 需新建（Next.js Image + caption） |
| `formula` | `<FormulaCard />` | 需新建（基于 `KatexRenderer`） |
| `geogebra` | `<GeoGebraEmbed />` | ✅ `components/math/geogebra-embed.tsx` |
| `video` | `<VideoPlayer />` | 需新建 |
| `animation` | `<AnimationPlayer />` | 需新建（Manim/Lottie 播放器） |
| `expandable` | `<ExpandableSection />` | 需新建（基于 `<Dialog />` 或自定义折叠） |
| `divider` | `<Divider />` | 需新建 |
| `illustration` | `<Illustration />` | 需新建（Image + annotations overlay） |
| `code` | `<CodeBlock />` | 需新建 |
| `table` | `<DataTable />` | 需新建 |
| `problem` | `<ProblemCard />` | ✅ `components/math/problem-card.tsx` |
| `interactive_table` | `<InteractiveTable />` | 需新建 |
| `scratchpad` | `<Scratchpad />` | ✅ `components/math/scratchpad.tsx` |
| `voice_input` | `<VoiceInput />` | 部分有（`voice-button.tsx` + ASR 接入） |
| `photo_upload` | `<PhotoUpload />` | 需新建 |
| `writing` | `<WritingEditor />` | ✅ `components/ket/writing-editor.tsx` |
| `listening` | `<ListeningPlayer />` | ✅ `components/ket/listening-player.tsx`（需扩展 questions） |
| `speaking` | `<SpeakingRecorder />` | ✅ `components/ket/speaking-recorder.tsx`（需扩展 follow-up） |
| `matching` | `<MatchingExercise />` | 需新建（拖拽组件） |
| `gap_fill` | `<GapFillExercise />` | 需新建 |
| `reading_passage` | `<ReadingPassage />` | 需新建 |
| `vocab_card` | `<VocabCard />` | 需新建 |
| `chn_writing` | `<ChineseWritingEditor />` | 需新建（中文写作编辑器+多维评分展示） |
| `poetry_dictation` | `<PoetryDictation />` | 需新建（默写填空+异体字容错） |
| `poetry_appreciation` | `<PoetryAppreciation />` | 需新建（赏析题目+AI评估） |
| `poetry_recitation` | `<PoetryRecitation />` | 需新建（朗读评分+节奏标注） |
| `draft` | `<DraftEditor />` | 需新建（草稿编辑+版本对比） |

### 7.2 Block 渲染器（核心路由组件）

需要一个统一的 Block 渲染器来按 `type` 分发：

```typescript
// components/lesson/BlockRenderer.tsx

import { ContentBlock } from '@/types/lesson';

const BLOCK_RENDERERS: Record<ContentBlock['type'], React.ComponentType<any>> = {
  text: MarkdownRenderer,
  audio: AudioPlayer,
  image: ImageBlock,
  formula: FormulaCard,
  geogebra: GeoGebraEmbed,
  video: VideoPlayer,
  animation: AnimationPlayer,
  expandable: ExpandableSection,
  divider: Divider,
  illustration: Illustration,
  code: CodeBlock,
  table: DataTable,
  problem: ProblemCard,
  interactive_table: InteractiveTable,
  scratchpad: Scratchpad,
  voice_input: VoiceInput,
  photo_upload: PhotoUpload,
  writing: WritingEditor,
  listening: ListeningExercise,   // 扩展版
  speaking: SpeakingExercise,     // 扩展版
  matching: MatchingExercise,
  gap_fill: GapFillExercise,
  reading_passage: ReadingPassage,
  vocab_card: VocabCard,
  chn_writing: ChineseWritingEditor,
  poetry_dictation: PoetryDictation,
  poetry_appreciation: PoetryAppreciation,
  poetry_recitation: PoetryRecitation,
  draft: DraftEditor,
};

export function BlockRenderer({ block }: { block: ContentBlock }) {
  const Component = BLOCK_RENDERERS[block.type];
  if (!Component) {
    console.warn(`Unknown block type: ${block.type}`);
    return null;
  }
  return <Component {...block} />;
}
```

### 7.3 Step 渲染器

```typescript
// components/lesson/StepRenderer.tsx

export function StepRenderer({ step }: { step: LessonStep }) {
  return (
    <div className="lesson-step" data-phase={step.phase}>
      <h2 className="step-title">{step.title}</h2>
      {step.blocks.map((block, i) => (
        <BlockRenderer key={`${block.type}-${i}`} block={block} />
      ))}
    </div>
  );
}
```

---

## 8. AI Agent 驱动约定

### 8.1 Agent 读取 LessonContent 的方式

Tutor Agent 通过 LangGraph State 维护课程进度：

```python
class LessonState(TypedDict):
    lesson_content: dict          # 完整的 LessonContent JSON
    current_step_index: int       # 当前步骤索引
    current_block_index: int      # 当前 block 索引（在当前 step 内）
    student_responses: list       # 学生的所有交互记录
    hint_levels: dict             # 每题的提示级别 { problem_id: level }
    mastery_updates: list         # 掌握度更新事件
```

### 8.2 Agent 推进逻辑

```
收到学生消息
    │
    ├── 检查当前 step 的 completion_mode
    │   ├── "all_viewed" → 自动推进到下一个 block
    │   ├── "interaction_complete" → 等待学生完成交互 block
    │   └── "score_threshold" → 评估所有 problem block 的得分
    │
    ├── 当前 step 完成？
    │   ├── 是 → 推进到下一个 step
    │   │         发送 step 标题 + 第一个 block 的内容
    │   └── 否 → 继续当前 step 的下一个 block
    │
    └── 所有 step 完成？
        ├── 是 → 发送 summary，计算掌握度更新
        └── 否 → 继续
```

### 8.3 Block 交互规则

| Block 类型 | Agent 行为 |
|-----------|-----------|
| `text`, `audio`, `image`, `formula`, `geogebra`, `video`, `animation`, `divider`, `illustration`, `table`, `code` | 展示型，自动推进。音频/视频等播放完毕后继续。 |
| `expandable` | 展示折叠标题，学生可展开。不阻塞流程。 |
| `problem` | **阻塞**。等待学生提交答案。根据对错更新掌握度。苏格拉底式引导。 |
| `interactive_table` | **阻塞**。等待学生填写完毕。校验答案。 |
| `voice_input` | **阻塞**。等待学生语音/文字输入。ASR 转录后处理。 |
| `scratchpad` | 不阻塞。学生可随时使用。如 `submit_to_ai=true` 则等待提交。 |
| `writing` | **阻塞**。等待学生写作并提交。调用 Assessor Agent 评分。 |
| `listening` | **阻塞**。播放音频后等待答题。 |
| `speaking` | **阻塞**。等待录音。ASR 转录后评估。可多轮 follow-up。 |
| `matching` | **阻塞**。等待配对完成。 |
| `gap_fill` | **阻塞**。等待所有空格填写。 |
| `reading_passage` | 展示型 + 内嵌 questions 阻塞。 |
| `vocab_card` | 展示型。配合间隔重复系统。 |
| `photo_upload` | **阻塞**。等待上传。OCR 处理后继续。 |
| `chn_writing` | **阻塞**。等待学生写作并提交。支持多轮修改（通过 DraftBlock）。调用 Assessor Agent 使用4维度100分制评分。 |
| `poetry_dictation` | **阻塞**。等待默写完成。逐字/逐句校验，支持异体字容错。更新背诵掌握度（FSRS）。 |
| `poetry_appreciation` | **阻塞**。等待赏析题作答。AI 评估参考答案要点覆盖率。更新赏析能力等级。 |
| `poetry_recitation` | **阻塞**。等待朗读/背诵录音。ASR 转录后与原文对比，评估完整度和节奏。 |
| `draft` | **阻塞**（当 submit_to_ai=true）。不阻塞（当 submit_to_ai=false）。记录草稿版本。 |

### 8.4 Agent Instruction 使用

每个 Step 的 `agent_instruction` 字段注入到 System Prompt 中：

```
你正在教授 AMC 数学课 "B3 勾股定理" 的 "explore" 阶段。

## Agent 指令
引导学生填写表格并发现 a²+b²=c² 的规律。如果学生没发现，追问"看看 a²+b² 和 c²"。

## 当前步骤
探索：发现规律
学生需要完成 1 个交互任务。

## 通用教学规则
- 苏格拉底式引导，不直接给答案
- 每次只问一个问题
- 学生说对了要肯定，追问"为什么"
```

### 8.4.1 语文作文 Agent Instruction 示例

```
你正在教授语文作文课 "把句子写生动" 的 "express" 阶段。

## Agent 指令
学生正在练习使用比喻和拟人修辞。请主动展示好的例子，不要等学生犯错才纠正。
如果学生的句子比较平淡，给出具体的改进建议和示范。

## 当前步骤
表达：学生独立写作初稿
学生需要完成 1 个写作任务。

## 通用教学规则（语文作文专用）
- **主动示范**：展示好词好句、范文片段，不要隐藏
- **鼓励为主**：先肯定写得好的地方，再建议改进
- **具体反馈**：不说"写得不够生动"，而是说"试试把'风很大'改成'风像一只大手猛推着窗户'"
- **不要求完美**：小学作文允许有小毛病，关注进步
```

### 8.4.2 古诗词 Agent Instruction 示例

```
你正在教授古诗词课 "春之声" 的 "appreciate" 阶段。

## Agent 指令
引导学生赏析《春晓》的意象和情感。先展示赏析的角度（意象→手法→情感），再引导学生自己发现。

## 当前步骤
赏析：意象解读+手法分析+名句品鉴
学生需要完成 1-2 道赏析题。

## 通用教学规则（古诗词专用）
- **展示赏析框架**：给学生思考的脚手架，而非直接给答案
- **联系生活**："你有没有春天早上被鸟叫醒的经历？"
- **朗读引导**：标注节奏，鼓励有感情地朗读
- **允许个性化理解**：同一首诗可以有不同的感受
```

---

## 附录 C: 评估范式对照表

| 维度 | AMC 数学 | KET 英语写作 | 语文作文 | 古诗词 |
|------|---------|------------|---------|--------|
| **评分模型** | 二元（对/错） | Band 0-5 | 100分制（4维度） | 分层制 |
| **评分维度** | 正确性 | Content/Organisation/Language | 内容40/结构20/语言30/书写10 | 背诵(二元) + 理解(正确率) + 赏析(等级) |
| **掌握度追踪** | FSRS + mastery | FSRS + Band | 多维追踪（内容/结构/语言分列） | 分层追踪（背诵FSRS + 理解渐进度 + 赏析等级） |
| **AI 教学策略** | 苏格拉底式（永不给答案） | 范文展示+修改反馈 | **必须示范**（范文/好句/技巧） | 示范+引导（展示赏析角度+引导发现） |
| **知识结构** | 严格 DAG | 模块化 | 螺旋式（反复练习提升） | 分层式（背诵→理解→赏析） |
| **错误类型** | 计算/概念/方法/误解 | 语法/拼写/结构 | 偏题/空洞/结构差/语言平淡/字数不足 | 错别字/漏句/意象误解/赏析浅 |
| **课时长度** | 20-30 min | 20-30 min | 30-45 min | 20-30 min |
| **草稿/修改** | 草稿板辅助 | 单次提交+可选修改 | **核心流程**（构思→初稿→修改→定稿） | 默写可重做 |
| **XP 基准** | 80-120 | 60-100 | 100-150 | 60-100 |

---

## 附录 A: Block 字段完整参考

### ProblemBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"problem"` | ✅ | |
| `problem_id` | `string?` | | 关联 problems 表 |
| `problem_type` | `enum` | ✅ | `"multiple_choice"` \| `"fill_blank"` \| `"short_answer"` |
| `difficulty` | `1\|2\|3\|4\|5` | ✅ | |
| `question` | `string` | ✅ | Markdown + LaTeX |
| `options` | `Array<{label, content}>?` | | multiple_choice 时必填 |
| `correct_answer` | `string` | ✅ | |
| `explanation` | `string?` | | 答错或完成后展示 |
| `hints` | `Array<{level, text, audio_url?}>` | ✅ | 0-4 级提示 |
| `knowledge_point_codes` | `string[]` | ✅ | |
| `xp_reward` | `number` | ✅ | |
| `figure` | `ImageBlock?` | | 配图 |
| `latex_expressions` | `string[]?` | | 题目中的 LaTeX 片段 |

### WritingBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"writing"` | ✅ | |
| `task` | `string` | ✅ | 写作任务描述 |
| `required_points` | `string[]` | ✅ | 必须包含的 3 个要点 |
| `min_words` | `number` | ✅ | 最少字数 |
| `max_words` | `number` | ✅ | 最多字数 |
| `target_words` | `number` | ✅ | 建议字数 |
| `writing_type` | `enum` | ✅ | `"email"` \| `"short_story"` \| `"message"` |
| `rubric` | `object?` | | 评分标准 |

### ListeningBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"listening"` | ✅ | |
| `audio_url` | `string` | ✅ | 音频 URL |
| `duration_sec` | `number` | ✅ | 时长 |
| `play_mode` | `enum` | ✅ | `"unlimited"` \| `"twice"` \| `"once"` |
| `speed` | `number?` | | 0.8 / 1.0 / 1.2 |
| `transcript` | `string?` | | 答题后展示 |
| `questions` | `ListeningQuestion[]` | ✅ | 配套题目 |

### ChineseWritingBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"chn_writing"` | ✅ | |
| `task` | `string` | ✅ | 写作任务描述 |
| `prompt` | `string?` | | 题目要求/提示 |
| `writing_type` | `enum` | ✅ | `"narrative"` \| `"descriptive"` \| `"imaginative"` \| `"practical"` \| `"expository"` |
| `target_chars` | `number` | ✅ | 目标字数 |
| `min_chars` | `number` | ✅ | 最少字数 |
| `max_chars` | `number` | ✅ | 最多字数 |
| `rubric` | `object` | ✅ | 100分制4维度评分标准 |
| `allow_revision` | `boolean` | ✅ | 是否允许修改重写 |
| `max_revisions` | `number?` | | 最多修改次数 |
| `scoring_prompt_id` | `string` | ✅ | 作文评分 Prompt ID |

### PoetryDictationBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"poetry_dictation"` | ✅ | |
| `poem_title` | `string` | ✅ | 诗歌标题 |
| `poet` | `string` | ✅ | 诗人 |
| `dictation_mode` | `enum` | ✅ | `"full"` \| `"partial"` \| `"fill_blank"` |
| `full_text` | `string` | ✅ | 完整原文（用于对照） |
| `template` | `string?` | | 填空模式的模板 |
| `gaps` | `Array?` | | 每个空缺的配置（含 answer、acceptable_variants） |
| `hidden_indices` | `number[]?` | | 藏字模式需填写的字位置 |
| `knowledge_point_codes` | `string[]` | ✅ | 关联知识点 |
| `xp_reward` | `number` | ✅ | XP 奖励 |

### PoetryAppreciationBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"poetry_appreciation"` | ✅ | |
| `poem_title` | `string` | ✅ | 诗歌标题 |
| `poet` | `string` | ✅ | 诗人 |
| `dynasty` | `string` | ✅ | 朝代 |
| `full_text` | `string` | ✅ | 完整原文（带注释标注） |
| `questions` | `Array` | ✅ | 赏析题目（含 question_type、reference_points、score） |
| `knowledge_point_codes` | `string[]` | ✅ | 关联知识点 |
| `xp_reward` | `number` | ✅ | XP 奖励 |

### PoetryRecitationBlock 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"poetry_recitation"` | ✅ | |
| `poem_title` | `string` | ✅ | 诗歌标题 |
| `poet` | `string` | ✅ | 诗人 |
| `full_text` | `string` | ✅ | 原文（用于语音对比） |
| `recitation_mode` | `enum` | ✅ | `"read_aloud"` \| `"recite_from_memory"` |
| `rhythm_marks` | `Array?` | | 节奏标注（含 position、type） |
| `assess_tone` | `boolean?` | | 是否要求声调评分 |
| `reference_audio_url` | `string?` | | 参考朗读音频 URL |
| `knowledge_point_codes` | `string[]` | ✅ | 关联知识点 |
| `xp_reward` | `number` | ✅ | XP 奖励 |

---

## 附录 D: Schema 版本迁移策略

```typescript
// 前端渲染时检查版本
function loadLessonContent(raw: unknown): LessonContent {
  const content = raw as LessonContent;

  if (content.schema_version === "1.0") {
    return content;  // 当前版本，直接使用
  }

  // 未来版本迁移
  // if (content.schema_version === "2.0") {
  //   return migrateV2ToV1(content);
  // }

  throw new Error(`Unsupported lesson schema version: ${content.schema_version}`);
}
```

数据库中的存量课程数据通过后台迁移脚本批量升级 `schema_version`。
