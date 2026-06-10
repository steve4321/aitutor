"""Generate lesson content using LLM.

Usage:
    cd backend && python -m scripts.generate_lesson_content
    cd backend && python -m scripts.generate_lesson_content --subject amc_math
    cd backend && python -m scripts.generate_lesson_content --lesson-code A1
    cd backend && python -m scripts.generate_lesson_content --dry-run
"""
import argparse
import asyncio
import json
import logging

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.config import settings
from app.db.session import async_session_factory, engine
from app.models.course import Course, Lesson, Unit
from app.agents.llm import is_llm_available

logger = logging.getLogger(__name__)

# ============================================================
# KNOWN BLOCK TYPES (for validation)
# ============================================================
DISPLAY_BLOCK_TYPES = {
    "text", "audio", "image", "formula", "geogebra", "video",
    "animation", "expandable", "divider", "illustration", "code", "table",
    "callout", "tip", "note", "warning",
}
INTERACTIVE_BLOCK_TYPES = {
    "problem", "interactive_table", "scratchpad", "voice_input", "photo_upload",
    "writing", "listening", "speaking", "matching", "gap_fill",
    "reading_passage", "vocab_card",
    "chn_writing", "poetry_dictation", "poetry_appreciation",
    "poetry_recitation", "draft",
}
ALL_BLOCK_TYPES = DISPLAY_BLOCK_TYPES | INTERACTIVE_BLOCK_TYPES

VALID_SUBJECTS = {"amc_math", "ket_english", "chn_composition", "chn_poetry"}
VALID_LESSON_TYPES = {
    "concept", "practice", "assessment", "review", "diagnostic",
    "mock_exam", "vocab_drill", "grammar_drill", "mock_speaking",
    "mock_listening", "composition", "poetry_reading", "poetry_dictation",
}

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """你是一个专业的教育内容设计师，负责为AI家教系统生成结构化的课程内容。

你必须严格按照给定的 JSON Schema 生成内容。输出必须是合法的 JSON，不要包含任何额外文本。

关键规则：
1. 所有数学公式使用 LaTeX: 行内用 $...$，独立行用 $$...$$
2. 每个 Step 包含 2-6 个 ContentBlock
3. hints 必须有 5 个级别 (0-4)，从最模糊到最明确
4. 所有文本使用中文，数学/英语术语保留原文
5. AMC 数学使用 5E 模型: engage → explore → explain → elaborate → evaluate
6. KET 英语使用 PPP 模型: introduce → present → practice → produce → review
7. 语文作文使用写作过程模型: observe → conceive → express → polish → assess_write
8. 语文古诗词使用分层深化模型: read_poem → decipher → appreciate → comprehend → verify
9. audio/video 的 url 字段用 "placeholder" 占位，后续由系统填充
10. 生成内容要有教育价值，题目要有原创性，不要照搬常见例题
11. AMC 数学的 explain 步骤中，对于涉及函数图像、几何变换、面积证明等可视化概念，应使用 animation block 代替 illustration。url 用 "placeholder"，后续由渲染管线生成。
12. 每个 block 的 content 控制在 200 字以内，agent_instruction 控制在 100 字以内。避免 JSON 过长被截断。"""

# ============================================================
# SHARED BLOCK TYPE REFERENCE
# ============================================================

BLOCK_TYPES_REF = """
## ContentBlock 类型说明（按需选用）
- text: {type:"text", content:"Markdown文本", variant?:"body"|"callout"|"tip"|"note"|"warning"}
- formula: {type:"formula", latex:"LaTeX公式", title:"公式名", note?:"注释", display:"card"}
- problem: {type:"problem", problem_type:"multiple_choice"|"fill_blank", difficulty:1-5, question:"题干", options?:[{label:"A",content:"..."}], correct_answer:"答案", hints:[{level:0-4,text:"..."}], knowledge_point_codes:[...], xp_reward:数字}
- voice_input: {type:"voice_input", prompt:"问题", input_modes:["voice","text"]}
- interactive_table: {type:"interactive_table", headers:[...], rows:[[...]], answer_rows:[[...]]}
- illustration: {type:"illustration", title:"图解标题", description:"...", image:{url:"placeholder",alt:"描述"}}
- expandable: {type:"expandable", title:"展开标题", content:[子blocks]}
- geogebra: {type:"geogebra", instructions:"操作说明", width:600, height:400}
- animation: {type:"animation", animation_type:"manim", url:"placeholder", title:"动画标题", duration_sec:数字}
- audio: {type:"audio", url:"placeholder", duration_sec:数字, transcript:"文本"}
- image: {type:"image", url:"placeholder", alt:"描述", caption?:"标题"}
- scratchpad: {type:"scratchpad", placeholder:"提示文字", submit_to_ai:true}
- writing: {type:"writing", task:"任务", required_points:[...], min_words:数字, max_words:数字, target_words:数字, writing_type:"email"|"short_story"|"message"}
- listening: {type:"listening", audio_url:"placeholder", duration_sec:数字, play_mode:"twice", questions:[{id:"...", question_type:"multiple_choice", question:"...", options:[...], correct_answer:"..."}]}
- speaking: {type:"speaking", speaking_type:"personal_questions"|"discussion"|"picture_description", initial_prompt:"...", max_duration_sec:数字}
- matching: {type:"matching", instructions:"指令", left_items:[{id:"...",content:"..."}], right_items:[{id:"...",content:"..."}], correct_pairs:{"L1":"R1"}}
- gap_fill: {type:"gap_fill", template:"文本{{gap:0}}...", gaps:[{index:0,answer:"...",options?:[...]}]}
- reading_passage: {type:"reading_passage", title:"标题", paragraphs:["段落1"], questions:[...]}
- vocab_card: {type:"vocab_card", word:"单词", phonetic:"音标", definition:"释义", example_sentence:"例句", practice_mode:"recognize"|"recall"}
- chn_writing: {type:"chn_writing", task:"任务", writing_type:"narrative"|"descriptive"|"imaginative", target_chars:数字, min_chars:数字, max_chars:数字, rubric:{content_max:40,structure_max:20,language_max:30,handwriting_max:10}, allow_revision:true, scoring_prompt_id:"default"}
- poetry_dictation: {type:"poetry_dictation", poem_title:"标题", poet:"诗人", dictation_mode:"fill_blank", full_text:"原文", template:"用{{gap:N}}标记", gaps:[{index:0,answer:"..."}], knowledge_point_codes:[...], xp_reward:数字}
- poetry_appreciation: {type:"poetry_appreciation", poem_title:"标题", poet:"诗人", dynasty:"朝代", full_text:"原文", questions:[{id:"...",question_type:"imagery_analysis",question:"...",reference_points:["..."],score:数字}], knowledge_point_codes:[...], xp_reward:数字}
- poetry_recitation: {type:"poetry_recitation", poem_title:"标题", poet:"诗人", full_text:"原文", recitation_mode:"read_aloud"|"recite_from_memory", knowledge_point_codes:[...], xp_reward:数字}
- draft: {type:"draft", draft_purpose:"composition_planning"|"composition_draft"|"composition_revision", instructions:"提示", submit_to_ai:true}
"""

# ============================================================
# SCHEMA OUTPUT FORMAT (simplified)
# ============================================================

OUTPUT_FORMAT = """
## 输出格式
直接输出合法 JSON，结构如下:
{
  "schema_version": "1.0",
  "subject": "{subject}",
  "lesson_type": "{lesson_type}",
  "objectives": ["目标1", "目标2", "目标3"],
  "prerequisite_codes": ["..."],
  "knowledge_point_codes": ["{kp_codes}"],
  "estimated_minutes": {estimated_minutes},
  "xp_base": 数字,
  "passing_criteria": {
    "min_mastery": 0.6,
    "min_accuracy": 0.7,
    "min_problems": 3
  },
  "steps": [
    {
      "id": "phase-name",
      "phase": "phase-name",
      "title": "步骤标题",
      "estimated_seconds": 数字,
      "completion_mode": "all_viewed"|"interaction_complete"|"score_threshold",
      "blocks": [ ... ],
      "agent_instruction": "Agent行为提示"
    }
  ],
  "summary": {
    "key_points": ["要点1", "要点2", "要点3"],
    "common_mistakes": ["错误1", "错误2"],
    "next_lesson_code": "..."
  }
}

不要包含任何 markdown 代码块标记或额外文本。只输出纯 JSON。
"""

# ============================================================
# PROMPT TEMPLATES
# ============================================================

CONCEPT_TEMPLATE = """请为以下 AMC 数学概念课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程 (5E 教学模型)
必须按以下顺序生成 5 个 Step:
1. engage (引入): 2-3 分钟, completion_mode: "all_viewed"
   - 用一个有趣的问题或场景引入主题
   - blocks: 1个 text/callout + 1个 voice_input, 可选 geogebra 或 illustration
2. explore (探索): 4-6 分钟, completion_mode: "interaction_complete"
   - 让学生通过活动发现规律
   - blocks: 1个 text + 1个 interactive_table + 1个 voice_input
3. explain (讲解): 4-6 分钟, completion_mode: "all_viewed"
   - 讲解概念、公式、定理
   - blocks: 1个 text/callout + 1个 formula + 1个 animation(函数图像/几何变换类) 或 illustration + 可选 expandable
   - animation block 的 animation_type 用 "manim"，url 用 "placeholder"
   - 适用场景: 函数图像变换、几何证明、面积关系、坐标变换、三角函数
4. elaborate (练习): 6-10 分钟, completion_mode: "interaction_complete"
   - 2-3 道 ProblemBlock (填空题+选择题)
   - 每题 5 级 hint (level 0-4)
5. evaluate (评估): 3-5 分钟, completion_mode: "score_threshold"
   - 3 道 ProblemBlock (选择题为主)
   - 每题 2 级 hint (评估时少给提示)
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

PRACTICE_TEMPLATE = """请为以下 AMC 数学练习课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
必须按以下顺序生成 3 个 Step:
1. warmup (热身): 1-2 分钟, completion_mode: "all_viewed"
   - 回顾相关知识点和公式
   - blocks: 1个 text/callout + 1个 formula(回顾公式) + 可选 animation(动态回顾)
2. assessment (练习): 15-25 分钟, completion_mode: "interaction_complete"
   - 5-10 道题，由易到难排列
   - 苏格拉底式引导
   - blocks: 5-10 个 ProblemBlock (mix: multiple_choice + fill_blank)
   - 每题 5 级 hint
3. reflection (反思): 2-3 分钟, completion_mode: "all_viewed"
   - 总结关键技能和常见错误
   - blocks: 1个 text/tip + 可选 expandable(错题分析)
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

ASSESSMENT_TEMPLATE = """请为以下 AMC 数学阶段测试生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
必须按以下顺序生成 3 个 Step:
1. warmup (热身): 1 分钟, completion_mode: "all_viewed"
   - 提示测试规则和注意事项
   - blocks: 1个 text/callout
2. test (测试): 15-20 分钟, completion_mode: "score_threshold"
   - 8-10 道题，限时，不给提示
   - blocks: 8-10 个 ProblemBlock (选择题+填空题混合)
   - 每题 hints 只给 2 级 (level 0-1)
3. summary (总结): 3-5 分钟, completion_mode: "all_viewed"
   - 结果分析 + 错题解析
   - blocks: 1个 text/note(总体评价) + 1个 text/tip(错题建议)
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

DIAGNOSTIC_TEMPLATE = """请为以下入学诊断测试生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
必须按以下顺序生成 2 个 Step:
1. diagnostic (诊断): 15-20 分钟, completion_mode: "score_threshold"
   - 10 道题覆盖各个知识领域，由易到难
   - blocks: 10 个 ProblemBlock (multiple_choice 为主, 少量 fill_blank)
   - 每题 2 级 hint
2. summary (总结): 2-3 分钟, completion_mode: "all_viewed"
   - 诊断结果分析和学习建议
   - blocks: 1个 text/note(诊断结果) + 1个 text/tip(学习建议)
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

VOCAB_TEMPLATE = """请为以下 KET 英语词汇训练课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程 (PPP 模型)
必须按以下顺序生成 3 个 Step:
1. present (呈现): 5-8 分钟, completion_mode: "all_viewed"
   - 5-10 个新词的词汇卡片
   - blocks: 5-10 个 vocab_card (包含 word, phonetic, definition, example_sentence, practice_mode)
   - 1个 text/note 总结词根词缀规律
2. practice (练习): 8-12 分钟, completion_mode: "interaction_complete"
   - 认词 → 回忆 → 拼写 → 造句练习
   - blocks: 2-3 个 gap_fill + 1-2 个 matching + 2-3 个 ProblemBlock(multiple_choice)
3. review (复习): 2-3 分钟, completion_mode: "all_viewed"
   - 间隔重复安排 + 今日词汇总结
   - blocks: 1个 text/tip(记忆技巧) + 1个 text(今日词汇列表)

注意：所有英文教学内容保留英文，说明用中英双语。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

GRAMMAR_TEMPLATE = """请为以下 KET 英语语法训练课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程 (PPP 模型)
必须按以下顺序生成 4 个 Step:
1. introduce (导入): 2-3 分钟, completion_mode: "all_viewed"
   - 情境引入，展示语法在真实场景中的使用
   - blocks: 1个 text/callout(情境对话) + 1个 text/note(观察规律)
2. present (呈现): 3-5 分钟, completion_mode: "all_viewed"
   - 讲解语法规则和结构
   - blocks: 1个 text(规则讲解) + 1个 table(肯定/否定/疑问句式) + 可选 text/tip(常见错误)
3. practice (练习): 8-12 分钟, completion_mode: "interaction_complete"
   - 控制性练习到半自由练习
   - blocks: 2-3 个 gap_fill + 2-3 个 ProblemBlock(multiple_choice, 语法选择)
4. review (复习): 2-3 分钟, completion_mode: "all_viewed"
   - 语法总结 + 要点提醒
   - blocks: 1个 text/tip(语法要点) + 1个 text(常见错误提醒)

注意：所有英文教学内容保留英文，说明用中英双语。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

LISTENING_TEMPLATE = """请为以下 KET 英语听力模拟课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
必须按以下顺序生成 3 个 Step:
1. introduce (导入): 2-3 分钟, completion_mode: "all_viewed"
   - 话题引入 + 关键词预教
   - blocks: 1个 text/callout(话题介绍) + 1个 text(关键词列表)
2. practice (练习): 10-15 分钟, completion_mode: "interaction_complete"
   - 按题型播放音频 + 答题
   - blocks: 2-3 个 listening block (每个含 2-3 题, play_mode:"twice")
   - 题目类型混合: multiple_choice + fill_blank + true_false
3. review (复习): 3-5 分钟, completion_mode: "all_viewed"
   - 对答案 + 原文对照 + 听力技巧总结
   - blocks: 1个 text(原文对照) + 1个 text/tip(听力技巧)

注意：listening block 的 audio_url 用 "placeholder"。所有英文教学内容保留英文。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

SPEAKING_TEMPLATE = """请为以下 KET 英语口语模拟课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
必须按以下顺序生成 3 个 Step:
1. introduce (导入): 2-3 分钟, completion_mode: "all_viewed"
   - 介绍口语考试流程和评分标准
   - blocks: 1个 text/callout(考试流程) + 1个 text/note(评分标准)
2. practice (练习): 10-15 分钟, completion_mode: "interaction_complete"
   - 模拟口语各部分
   - blocks: 2-3 个 speaking block
   - speaking_type 混合: personal_questions + discussion 或 picture_description
   - 每个 speaking block 包含 2-3 个 follow_up_prompts
3. review (复习): 3-5 分钟, completion_mode: "all_viewed"
   - AI 评分反馈 + 口语技巧总结
   - blocks: 1个 text/tip(口语技巧) + 1个 text(评分维度说明)

注意：所有英文教学内容保留英文，说明用中英双语。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

MOCK_EXAM_TEMPLATE = """请为以下 KET 英语模拟考试生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
必须按以下顺序生成 2 个 Step:
1. test (考试): 30-40 分钟, completion_mode: "score_threshold"
   - 涵盖 KET 各题型的模拟试题
   - blocks: 1-2 个 reading_passage + 2-3 个 gap_fill + 1 个 matching + 3-5 个 ProblemBlock + 1 个 writing
   - 题目类型混合: 阅读、语法、写作
2. summary (总结): 3-5 分钟, completion_mode: "all_viewed"
   - 考试结果分析 + 各部分表现
   - blocks: 1个 text/note(总体评价) + 1个 text/tip(弱项提升建议)

注意：所有英文教学内容保留英文。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

COMPOSITION_TEMPLATE = """请为以下语文作文课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程 (写作过程模型)
必须按以下顺序生成 5 个 Step:
1. observe (观察): 3-5 分钟, completion_mode: "all_viewed"
   - 展示场景/图片/文字，引导学生用五官感受，积累素材
   - blocks: 1个 text/callout(写作题目) + 1个 illustration 或 image(场景图) + 1个 voice_input(口头描述)
2. conceive (构思): 3-5 分钟, completion_mode: "interaction_complete"
   - 确定主题，选择素材，列写作提纲
   - blocks: 1个 text(构思引导问题) + 1个 draft(draft_purpose:"composition_planning", instructions:"列出你的写作提纲")
3. express (表达): 8-15 分钟, completion_mode: "interaction_complete"
   - 学生独立写作初稿（目标300-500字）
   - blocks: 1个 chn_writing(writing_type:"narrative"|"descriptive"|"imaginative", target_chars:400, min_chars:200, max_chars:600)
4. polish (润色): 5-8 分钟, completion_mode: "interaction_complete"
   - AI反馈后修改语言和结构
   - blocks: 1个 draft(draft_purpose:"composition_revision", instructions:"根据AI反馈修改你的作文")
5. assess_write (评估): 3-5 分钟, completion_mode: "all_viewed"
   - AI多维评分+优秀段落展示+总结
   - blocks: 1个 text/callout(评分结果) + 1个 text/tip(写作建议)

重要：语文作文 AI 教学**必须主动示范**，展示范文、好句、技巧。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

POETRY_READING_TEMPLATE = """请为以下语文古诗词赏析课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程 (分层深化模型)
必须按以下顺序生成 5 个 Step:
1. read_poem (读): 3-4 分钟, completion_mode: "all_viewed"
   - 节奏标注+朗读指导+AI朗读示范
   - blocks: 1个 text(诗歌原文+节奏标注) + 1个 poetry_recitation(recitation_mode:"read_aloud")
2. decipher (解): 3-5 分钟, completion_mode: "all_viewed"
   - 关键字词释义+背景故事+疏通大意
   - blocks: 1个 text/callout(背景介绍) + 1个 text(字词释义) + 1个 text(白话翻译)
3. appreciate (赏): 5-8 分钟, completion_mode: "interaction_complete"
   - 意象解读+手法分析+名句品鉴
   - blocks: 1个 text(意象分析) + 1个 poetry_appreciation(含 2-3 道赏析题)
4. comprehend (悟): 3-5 分钟, completion_mode: "interaction_complete"
   - 情感把握+主旨归纳+联系生活
   - blocks: 1个 text(情感主旨) + 1个 voice_input(你的感受)
5. verify (测): 3-5 分钟, completion_mode: "score_threshold"
   - 默写检测+理解性填空+赏析题
   - blocks: 1个 poetry_dictation(dictation_mode:"fill_blank") + 2个 ProblemBlock

重要：古诗词采用分层深化学习，展示赏析框架给学生思考的脚手架。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

POETRY_DICTATION_TEMPLATE = """请为以下语文诗词默写训练课生成完整的课程内容 JSON。

## 课程信息
- 课程代码: {code}
- 课程标题: {title}
- 知识点: {knowledge_points}
- 预计时长: {estimated_minutes} 分钟
- 学习目标: {objectives}

## Step 流程
只需生成 1 个 Step:
1. verify (默写检测): 10-15 分钟, completion_mode: "score_threshold"
   - 诗词默写填空训练
   - blocks: 2-3 个 poetry_dictation (dictation_mode:"fill_blank", 含 template 和 gaps)
   - 可选 1-2 个 poetry_recitation (recitation_mode:"recite_from_memory")

每个 poetry_dictation 的 full_text 必须是完整正确的原文。
template 用 {{gap:N}} 标记需要填写的空缺位置。
gaps 中的 answer 必须是严格匹配的正确答案。
""" + BLOCK_TYPES_REF + OUTPUT_FORMAT

# ============================================================
# TEMPLATE REGISTRY
# ============================================================

PROMPT_TEMPLATES = {
    "concept": CONCEPT_TEMPLATE,
    "practice": PRACTICE_TEMPLATE,
    "assessment": ASSESSMENT_TEMPLATE,
    "diagnostic": DIAGNOSTIC_TEMPLATE,
    "vocab_drill": VOCAB_TEMPLATE,
    "grammar_drill": GRAMMAR_TEMPLATE,
    "mock_listening": LISTENING_TEMPLATE,
    "mock_speaking": SPEAKING_TEMPLATE,
    "mock_exam": MOCK_EXAM_TEMPLATE,
    "composition": COMPOSITION_TEMPLATE,
    "poetry_reading": POETRY_READING_TEMPLATE,
    "poetry_dictation": POETRY_DICTATION_TEMPLATE,
}


# ============================================================
# SUBJECT → LESSON_TYPE MAPPING
# ============================================================

SUBJECT_LESSON_TYPE_MAP = {
    "amc_math": {"concept", "practice", "assessment", "diagnostic"},
    "ket_english": {"vocab_drill", "grammar_drill", "mock_listening", "mock_speaking", "mock_exam", "concept"},
    "chn_composition": {"composition"},
    "chn_poetry": {"poetry_reading", "poetry_dictation"},
}


def _get_lesson_metadata(lesson: Lesson) -> dict:
    """Extract metadata from a lesson for prompt formatting."""
    content = lesson.content or {}
    knowledge_points = content.get("knowledge_point_codes", [])
    objectives = content.get("objectives", [])

    # Try to infer subject from content or related fields
    subject = content.get("subject", "")
    if not subject:
        # Infer from lesson_type
        lt = lesson.lesson_type or ""
        for subj, types in SUBJECT_LESSON_TYPE_MAP.items():
            if lt in types:
                subject = subj
                break

    return {
        "code": lesson.code or "",
        "title": lesson.title,
        "subject": subject,
        "lesson_type": lesson.lesson_type or "concept",
        "knowledge_points": ", ".join(knowledge_points) if knowledge_points else lesson.title,
        "estimated_minutes": lesson.estimated_minutes or 25,
        "objectives": "; ".join(objectives) if objectives else "根据课程标题生成合适的学习目标",
        "kp_codes": ", ".join(knowledge_points) if knowledge_points else "",
    }


def _format_template(template: str, metadata: dict) -> str:
    """Fill template placeholders with lesson metadata.

    Uses explicit replacement to avoid conflicts with JSON examples
    in the template that contain literal braces like {type:"text"}.
    """
    result = template
    for key, value in metadata.items():
        result = result.replace("{" + key + "}", str(value))
    return result


# ============================================================
# JSON EXTRACTION & CLEANUP
# ============================================================

def _extract_json(text: str) -> str:
    """Extract JSON from LLM response, stripping markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    return text


def _try_parse_json(text: str) -> dict | None:
    """Try to parse JSON with multiple fallback strategies."""
    import re

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Fix trailing commas (common LLM mistake)
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Extract outermost JSON object
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    # Strategy 4: Try fixing truncated JSON by closing unclosed brackets
    if start != -1 and end != -1:
        try:
            snippet = text[start:]
            open_braces = snippet.count('{') - snippet.count('}')
            open_brackets = snippet.count('[') - snippet.count(']')
            fixed = snippet + ']' * max(0, open_brackets) + '}' * max(0, open_braces)
            return json.loads(fixed)
        except (json.JSONDecodeError, Exception):
            pass

    # Strategy 5: Try fixing unescaped quotes in strings
    try:
        cleaned = re.sub(r'(?<!\\)"(?=[^":,}\]]*"[:}\],])', r'\\"', text[start:end + 1])
        return json.loads(cleaned)
    except (json.JSONDecodeError, Exception):
        pass

    return None


def _clean_json_content(content: dict) -> dict:
    """Clean up common LLM JSON issues."""
    # Ensure schema_version is set
    if "schema_version" not in content:
        content["schema_version"] = "1.0"

    # Ensure steps is a list
    if "steps" not in content or not isinstance(content["steps"], list):
        content["steps"] = []

    # Ensure summary exists
    if "summary" not in content:
        content["summary"] = {"key_points": [], "common_mistakes": []}

    # Fix any block-level issues
    for step in content["steps"]:
        if "blocks" not in step or not isinstance(step["blocks"], list):
            step["blocks"] = []
        if "id" not in step:
            step["id"] = step.get("phase", "unknown")
        if "estimated_seconds" not in step:
            step["estimated_seconds"] = 120
        if "completion_mode" not in step:
            step["completion_mode"] = "all_viewed"

        # Fix common LLM block type mistakes
        for block in step["blocks"]:
            if not isinstance(block, dict):
                continue
            # LLM sometimes outputs {"type": "callout"} instead of {"type": "text", "variant": "callout"}
            if block.get("type") == "callout":
                block["type"] = "text"
                block.setdefault("variant", "callout")
            # Same for "tip", "note", "warning" used as standalone types
            if block.get("type") in ("tip", "note", "warning"):
                variant = block["type"]
                block["type"] = "text"
                block.setdefault("variant", variant)

    return content


# ============================================================
# VALIDATION
# ============================================================

async def validate_content(content: dict) -> list[str]:
    """Validate generated content against schema. Return list of errors."""
    errors: list[str] = []

    # Top-level required fields
    for field in ("schema_version", "steps"):
        if field not in content:
            errors.append(f"Missing required field: {field}")

    if "steps" in content and isinstance(content["steps"], list):
        steps = content["steps"]
        if len(steps) == 0:
            errors.append("steps is empty — no content generated")

        for i, step in enumerate(steps):
            step_prefix = f"step[{i}]"

            # Step required fields
            for field in ("id", "phase", "title", "blocks", "completion_mode"):
                if field not in step:
                    errors.append(f"{step_prefix}: missing field '{field}'")

            if "phase" in step and "estimated_seconds" not in step:
                errors.append(f"{step_prefix}: missing 'estimated_seconds'")

            # Check blocks
            blocks = step.get("blocks", [])
            if not isinstance(blocks, list):
                errors.append(f"{step_prefix}: blocks is not a list")
                continue

            if len(blocks) == 0:
                errors.append(f"{step_prefix}: blocks list is empty")

            for j, block in enumerate(blocks):
                block_prefix = f"{step_prefix}.block[{j}]"

                if not isinstance(block, dict):
                    errors.append(f"{block_prefix}: not a dict")
                    continue

                # Check type field
                block_type = block.get("type")
                if not block_type:
                    errors.append(f"{block_prefix}: missing 'type'")
                elif block_type not in ALL_BLOCK_TYPES:
                    errors.append(f"{block_prefix}: unknown type '{block_type}'")

                # ProblemBlock specific checks
                if block_type == "problem":
                    for req in ("question", "correct_answer", "hints", "knowledge_point_codes"):
                        if req not in block:
                            errors.append(f"{block_prefix}: ProblemBlock missing '{req}'")

                    hints = block.get("hints", [])
                    if isinstance(hints, list):
                        if len(hints) < 2:
                            errors.append(
                                f"{block_prefix}: ProblemBlock should have at least 2 hints, got {len(hints)}"
                            )
                        # Check hint levels
                        levels = {h.get("level") for h in hints if isinstance(h, dict)}
                        if levels and max(levels) > 4:
                            errors.append(
                                f"{block_prefix}: hint level > 4 found"
                            )

    if "summary" not in content:
        errors.append("Missing 'summary' field")

    return errors


# ============================================================
# CONTENT GENERATION
# ============================================================

def _is_placeholder_content(content: dict | None) -> bool:
    """Check if content is placeholder (empty steps or no content)."""
    if not content:
        return True
    steps = content.get("steps", [])
    if not isinstance(steps, list) or len(steps) == 0:
        return True
    return False


async def generate_for_lesson(lesson: Lesson, dry_run: bool = False) -> dict | None:
    """Generate content for a single lesson using LLM."""
    lesson_type = lesson.lesson_type or "concept"

    # Select template
    template = PROMPT_TEMPLATES.get(lesson_type)
    if not template:
        logger.warning(
            "No template for lesson_type '%s' (lesson %s), falling back to concept",
            lesson_type, lesson.code,
        )
        template = CONCEPT_TEMPLATE

    # Build metadata
    metadata = _get_lesson_metadata(lesson)
    metadata["subject"] = metadata["subject"] or "amc_math"
    metadata["lesson_type"] = lesson_type

    # Format prompt
    try:
        user_prompt = _format_template(template, metadata)
    except KeyError as e:
        logger.error("Template formatting error for lesson %s: %s", lesson.code, e)
        return None

    from langchain_core.messages import HumanMessage, SystemMessage
    from app.config import LLM_PROVIDER_PROFILES

    profile = LLM_PROVIDER_PROFILES.get(settings.LLM_PROVIDER, {})
    client_type = profile.get("client", "openai")

    llm_kwargs = {
        "model": settings.STRONG_MODEL,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": 0.7,
        "max_tokens": 16384,
        "timeout": 240.0,
        "max_retries": 2,
    }
    if settings.LLM_BASE_URL:
        llm_kwargs["base_url"] = settings.LLM_BASE_URL

    if client_type == "anthropic":
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(**llm_kwargs)
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(**llm_kwargs)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    logger.info("Generating content for lesson %s (%s): %s",
                lesson.code, lesson_type, lesson.title)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            raw_text = response.content
        except Exception as e:
            logger.error("LLM call failed for lesson %s (attempt %d): %s", lesson.code, attempt + 1, e)
            if attempt < max_retries - 1:
                continue
            return None

        json_text = _extract_json(raw_text)
        content = _try_parse_json(json_text)
        if content is not None:
            break

        logger.warning("JSON parse error for lesson %s (attempt %d/%d)",
                       lesson.code, attempt + 1, max_retries)
        if attempt == 0:
            logger.info("Raw LLM output (first 2000 chars):\n%s", raw_text[:2000])
        if attempt < max_retries - 1:
            continue

        logger.error("JSON parse failed after %d attempts for lesson %s", max_retries, lesson.code)
        return None

    # Clean up
    content = _clean_json_content(content)

    # Validate
    errors = await validate_content(content)
    if errors:
        logger.warning("Validation errors for lesson %s:", lesson.code)
        for err in errors:
            logger.warning("  - %s", err)

        # If critical errors (no steps), return None
        if not content.get("steps"):
            logger.error("Lesson %s has no steps after generation, skipping", lesson.code)
            return None

    return content


# ============================================================
# MAIN
# ============================================================

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate lesson content using LLM"
    )
    parser.add_argument(
        "--subject",
        help="Only generate for this subject (amc_math, ket_english, chn_composition, chn_poetry)",
    )
    parser.add_argument(
        "--lesson-code",
        help="Only generate for this lesson code (e.g. AMC-GEO-B3)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write to DB, just print what would be generated",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Max lessons to generate",
    )
    parser.add_argument(
        "--retry",
        action="store_true",
        help="Retry lessons that have placeholder content (default: skip)",
    )
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Check LLM availability
    if not is_llm_available():
        logger.error(
            "LLM not available. Set OPENAI_API_KEY (and optionally LLM_BASE_URL) in .env"
        )
        sys.exit(1)

    # Query lessons
    async with async_session_factory() as session:
        query = select(Lesson).order_by(Lesson.sort_order)

        if args.subject:
            query = query.join(Lesson.unit).join(Unit.course).where(
                Course.subject == args.subject
            )

        if args.lesson_code:
            query = query.where(Lesson.code == args.lesson_code)

        result = await session.execute(query)
        lessons = result.scalars().all()

    if not lessons:
        logger.info("No lessons found matching criteria")
        return

    logger.info("Found %d lessons total", len(lessons))

    # Filter: skip lessons with non-placeholder content
    to_generate = []
    skipped = []
    for lesson in lessons:
        if not _is_placeholder_content(lesson.content):
            skipped.append(lesson)
            continue
        to_generate.append(lesson)

    if skipped:
        logger.info(
            "Skipped %d lessons with existing content: %s",
            len(skipped),
            ", ".join(lesson.code or lesson.title for lesson in skipped),
        )

    if not to_generate:
        logger.info("No lessons need content generation")
        return

    if args.limit:
        to_generate = to_generate[: args.limit]

    logger.info("Will generate content for %d lessons", len(to_generate))

    # Generate content
    success_count = 0
    fail_count = 0

    for i, lesson in enumerate(to_generate, 1):
        logger.info("[%d/%d] Processing: %s (%s)",
                    i, len(to_generate), lesson.code or lesson.title,
                    lesson.lesson_type or "unknown")

        content = await generate_for_lesson(lesson, dry_run=args.dry_run)

        if content is None:
            fail_count += 1
            logger.error("Failed to generate content for lesson %s", lesson.code)
            continue

        if args.dry_run:
            logger.info("[DRY RUN] Would update lesson %s with %d steps",
                        lesson.code, len(content.get("steps", [])))
            if i == 1:
                # Print first generated content as sample
                print("\n=== SAMPLE OUTPUT ===")
                print(json.dumps(content, ensure_ascii=False, indent=2)[:5000])
                print("=== END SAMPLE ===\n")
        else:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(Lesson).where(Lesson.id == lesson.id)
                )
                db_lesson = result.scalar_one_or_none()
                if db_lesson:
                    db_lesson.content = content
                    await session.commit()
                    logger.info(
                        "Updated lesson %s with %d steps",
                        lesson.code,
                        len(content.get("steps", [])),
                    )
                else:
                    logger.error("Lesson %s not found in DB during update", lesson.code)
                    fail_count += 1
                    continue

        success_count += 1

    # Summary
    logger.info("=" * 50)
    logger.info("Generation complete: %d success, %d failed, %d skipped",
                success_count, fail_count, len(skipped))

    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
