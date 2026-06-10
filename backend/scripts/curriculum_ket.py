"""KET English curriculum data — parsed from course-catalog.md

This module contains the complete KET (Cambridge A2 Key) exam preparation
curriculum: 1 course, 8 units, 29 lessons (incl. diagnostic), knowledge
points, dependencies, and sample problems.

Usage (by seed script):
    from scripts.curriculum_ket import (
        KET_COURSE, KET_KNOWLEDGE_POINTS, KET_KNOWLEDGE_DEPENDENCIES, KET_PROBLEMS,
    )
"""

# ---------------------------------------------------------------------------
# Course + Units + Lessons
# ---------------------------------------------------------------------------

KET_COURSE = {
    "code": "KET",
    "subject": "ket_english",
    "name": "KET 英语备考课程",
    "description": "剑桥 KET (A2 Key) 考试备考课程，涵盖听说读写四项技能",
    "target_exam": "KET",
    "estimated_hours": 18,
    "is_published": True,
    "units": [
        # ------------------------------------------------------------------
        # Unit 0: Diagnostic
        # ------------------------------------------------------------------
        {
            "code": "KET-U0",
            "name": "入学诊断",
            "description": "英语水平测试，确定起始模块",
            "sort_order": 0,
            "required_mastery": 0.0,
            "lessons": [
                {
                    "code": "DIAG-KET",
                    "title": "KET入学诊断",
                    "lesson_type": "diagnostic",
                    "estimated_minutes": 45,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-DIAG",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "diagnostic",
                        "objectives": ["评估英语水平", "确定起始学习模块"],
                        "knowledge_point_codes": ["KET-DIAG"],
                        "prerequisite_codes": [],
                        "estimated_minutes": 45,
                        "xp_base": 0,
                        "steps": [],
                        "summary": {
                            "key_points": ["英语水平测试", "生成知识画像", "判断可跳过的已掌握模块"],
                            "common_mistakes": [],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 1: Module A — 基础词汇
        # ------------------------------------------------------------------
        {
            "code": "KET-U1",
            "name": "Module A 基础词汇",
            "description": "KET核心词汇、场景分类、基础搭配",
            "sort_order": 1,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-A1",
                    "title": "高频日常词汇 (500词)",
                    "lesson_type": "vocab_drill",
                    "estimated_minutes": 35,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-VOC-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "vocab_drill",
                        "objectives": ["掌握KET核心500词", "场景分类记忆", "基础搭配运用"],
                        "knowledge_point_codes": ["KET-VOC-01"],
                        "prerequisite_codes": [],
                        "estimated_minutes": 35,
                        "xp_base": 60,
                        "steps": [],
                        "summary": {
                            "key_points": ["KET核心词汇", "场景分类", "基础搭配"],
                            "common_mistakes": ["混淆形近词", "忽略词性搭配"],
                        },
                    },
                },
                {
                    "code": "KET-A2",
                    "title": "数字/时间/日期",
                    "lesson_type": "vocab_drill",
                    "estimated_minutes": 30,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-VOC-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "vocab_drill",
                        "objectives": ["数字表达", "时间读写", "日期格式"],
                        "knowledge_point_codes": ["KET-VOC-02"],
                        "prerequisite_codes": ["KET-A1"],
                        "estimated_minutes": 30,
                        "xp_base": 60,
                        "steps": [],
                        "summary": {
                            "key_points": ["数字表达", "时间读写", "日期格式"],
                            "common_mistakes": ["混淆序数词和基数词", "日期格式英美差异"],
                        },
                    },
                },
                {
                    "code": "KET-A3",
                    "title": "家庭/学校/食物",
                    "lesson_type": "vocab_drill",
                    "estimated_minutes": 30,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-VOC-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "vocab_drill",
                        "objectives": ["家庭成员词汇", "学科名称", "食物饮品词汇"],
                        "knowledge_point_codes": ["KET-VOC-03"],
                        "prerequisite_codes": ["KET-A1"],
                        "estimated_minutes": 30,
                        "xp_base": 60,
                        "steps": [],
                        "summary": {
                            "key_points": ["家庭成员", "学科名称", "食物饮品"],
                            "common_mistakes": ["名词单复数错误", "不可数名词误加s"],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 2: Module B — 基础语法
        # ------------------------------------------------------------------
        {
            "code": "KET-U2",
            "name": "Module B 基础语法",
            "description": "be动词、一般现在时、过去时、进行时、疑问句、介词、情态动词",
            "sort_order": 2,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-B1",
                    "title": "be动词/一般现在时",
                    "lesson_type": "grammar_drill",
                    "estimated_minutes": 40,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-GRAM-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "grammar_drill",
                        "objectives": ["be动词变形", "一般现在时用法", "主谓一致"],
                        "knowledge_point_codes": ["KET-GRAM-01"],
                        "prerequisite_codes": [],
                        "estimated_minutes": 40,
                        "xp_base": 70,
                        "steps": [],
                        "summary": {
                            "key_points": ["be动词: am/is/are", "一般现在时", "主谓一致规则"],
                            "common_mistakes": ["第三人称单数忘加s", "be动词选择错误"],
                        },
                    },
                },
                {
                    "code": "KET-B2",
                    "title": "一般过去时/进行时",
                    "lesson_type": "grammar_drill",
                    "estimated_minutes": 40,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-GRAM-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "grammar_drill",
                        "objectives": ["规则动词过去式", "不规则动词过去式", "现在进行时"],
                        "knowledge_point_codes": ["KET-GRAM-02"],
                        "prerequisite_codes": ["KET-B1"],
                        "estimated_minutes": 40,
                        "xp_base": 70,
                        "steps": [],
                        "summary": {
                            "key_points": ["规则/不规则动词过去式", "现在进行时: be + doing"],
                            "common_mistakes": ["不规则动词记忆不全", "进行时忘加be"],
                        },
                    },
                },
                {
                    "code": "KET-B3",
                    "title": "疑问句/否定句",
                    "lesson_type": "grammar_drill",
                    "estimated_minutes": 35,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-GRAM-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "grammar_drill",
                        "objectives": ["一般疑问句", "特殊疑问句", "否定结构"],
                        "knowledge_point_codes": ["KET-GRAM-03"],
                        "prerequisite_codes": ["KET-B1"],
                        "estimated_minutes": 35,
                        "xp_base": 70,
                        "steps": [],
                        "summary": {
                            "key_points": ["Do/Does/Did引导一般疑问句", "Wh-疑问词", "否定句: don't/doesn't/didn't"],
                            "common_mistakes": ["疑问句语序混乱", "否定句双重否定"],
                        },
                    },
                },
                {
                    "code": "KET-B4",
                    "title": "介词/冠词",
                    "lesson_type": "grammar_drill",
                    "estimated_minutes": 35,
                    "sort_order": 4,
                    "is_published": True,
                    "knowledge_point_code": "KET-GRAM-04",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "grammar_drill",
                        "objectives": ["常用介词搭配", "a/an/the用法"],
                        "knowledge_point_codes": ["KET-GRAM-04"],
                        "prerequisite_codes": ["KET-B1"],
                        "estimated_minutes": 35,
                        "xp_base": 70,
                        "steps": [],
                        "summary": {
                            "key_points": ["in/on/at搭配", "a/an/the规则"],
                            "common_mistakes": ["介词固定搭配记错", "冠词省略或多余"],
                        },
                    },
                },
                {
                    "code": "KET-B5",
                    "title": "情态动词 (can/must)",
                    "lesson_type": "grammar_drill",
                    "estimated_minutes": 35,
                    "sort_order": 5,
                    "is_published": True,
                    "knowledge_point_code": "KET-GRAM-05",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "grammar_drill",
                        "objectives": ["can/can't表能力", "must/mustn't表义务"],
                        "knowledge_point_codes": ["KET-GRAM-05"],
                        "prerequisite_codes": ["KET-B1"],
                        "estimated_minutes": 35,
                        "xp_base": 70,
                        "steps": [],
                        "summary": {
                            "key_points": ["can表能力和许可", "must表义务和禁止"],
                            "common_mistakes": ["can后加to", "mustn't和needn't混淆"],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 3: Module C — 阅读专项
        # ------------------------------------------------------------------
        {
            "code": "KET-U3",
            "name": "Module C 阅读专项",
            "description": "通知标志理解、多文本匹配、长文精读、完形填空",
            "sort_order": 3,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-C1",
                    "title": "通知/标志理解 (Part 1)",
                    "lesson_type": "concept",
                    "estimated_minutes": 40,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-READ-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "reading",
                        "objectives": ["快速信息提取", "图片+文字多选"],
                        "knowledge_point_codes": ["KET-READ-01"],
                        "prerequisite_codes": [],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["通知类文本快速阅读", "标志含义识别", "关键信息定位"],
                            "common_mistakes": ["过度解读简单文本", "忽略否定词"],
                        },
                    },
                },
                {
                    "code": "KET-C2",
                    "title": "多文本匹配 (Part 2)",
                    "lesson_type": "concept",
                    "estimated_minutes": 40,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-READ-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "reading",
                        "objectives": ["扫读匹配", "3段短文对应问题"],
                        "knowledge_point_codes": ["KET-READ-02"],
                        "prerequisite_codes": ["KET-C1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["扫读技巧", "信息匹配", "排除法"],
                            "common_mistakes": ["逐字阅读耗时过长", "匹配时混淆相似信息"],
                        },
                    },
                },
                {
                    "code": "KET-C3",
                    "title": "长文精读 (Part 3)",
                    "lesson_type": "concept",
                    "estimated_minutes": 45,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-READ-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "reading",
                        "objectives": ["分段阅读理解", "主旨与细节提取"],
                        "knowledge_point_codes": ["KET-READ-03"],
                        "prerequisite_codes": ["KET-C1"],
                        "estimated_minutes": 45,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["段落主旨", "细节定位", "推断题技巧"],
                            "common_mistakes": ["以偏概全", "忽略转折词"],
                        },
                    },
                },
                {
                    "code": "KET-C4",
                    "title": "完形填空技巧 (Part 4-5)",
                    "lesson_type": "concept",
                    "estimated_minutes": 40,
                    "sort_order": 4,
                    "is_published": True,
                    "knowledge_point_code": "KET-READ-04",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "reading",
                        "objectives": ["语境词汇选择(Part 4)", "语法填空(Part 5)"],
                        "knowledge_point_codes": ["KET-READ-04"],
                        "prerequisite_codes": ["KET-C1", "KET-B1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["语境推断词义", "语法结构分析", "固定搭配"],
                            "common_mistakes": ["不读上下文直接选", "忽略语法线索"],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 4: Module D — 写作专项
        # ------------------------------------------------------------------
        {
            "code": "KET-U4",
            "name": "Module D 写作专项",
            "description": "邮件写作、看图写故事、模拟写作+AI评分",
            "sort_order": 4,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-D1",
                    "title": "邮件写作 (Part 6: 25+词)",
                    "lesson_type": "concept",
                    "estimated_minutes": 40,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-WRIT-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "writing",
                        "objectives": ["邮件格式", "3个要点覆盖", "25词以上"],
                        "knowledge_point_codes": ["KET-WRIT-01"],
                        "prerequisite_codes": ["KET-B1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["邮件三要素", "要点覆盖", "字数控制"],
                            "common_mistakes": ["遗漏要点", "字数不足"],
                        },
                    },
                },
                {
                    "code": "KET-D2",
                    "title": "看图写故事 (Part 7: 35+词)",
                    "lesson_type": "concept",
                    "estimated_minutes": 40,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-WRIT-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "writing",
                        "objectives": ["图片描述", "叙事连贯性", "35词以上"],
                        "knowledge_point_codes": ["KET-WRIT-02"],
                        "prerequisite_codes": ["KET-D1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["图片顺序描述", "故事连贯性", "时态一致性"],
                            "common_mistakes": ["跳跃式描述", "时态混乱"],
                        },
                    },
                },
                {
                    "code": "KET-D3",
                    "title": "模拟写作 + AI评分",
                    "lesson_type": "assessment",
                    "estimated_minutes": 35,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-WRIT-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "assessment",
                        "ket_skill": "writing",
                        "objectives": ["Content/Organisation/Language三维度评分", "写作实战"],
                        "knowledge_point_codes": ["KET-WRIT-03"],
                        "prerequisite_codes": ["KET-D1", "KET-D2"],
                        "estimated_minutes": 35,
                        "xp_base": 100,
                        "steps": [],
                        "summary": {
                            "key_points": ["写作评分三维度", "邮件+看图写作", "AI即时反馈"],
                            "common_mistakes": ["要点遗漏", "语法错误集中"],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 5: Module E — 听力专项
        # ------------------------------------------------------------------
        {
            "code": "KET-U5",
            "name": "Module E 听力专项",
            "description": "短对话理解、笔记填空、长对话、匹配练习",
            "sort_order": 5,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-E1",
                    "title": "短对话理解 (Part 1)",
                    "lesson_type": "mock_listening",
                    "estimated_minutes": 40,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-LIST-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_listening",
                        "ket_skill": "listening",
                        "objectives": ["短对话+图片选择", "关键信息抓取"],
                        "knowledge_point_codes": ["KET-LIST-01"],
                        "prerequisite_codes": [],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["抓取关键信息", "图片与对话匹配", "注意数字、时间、地点"],
                            "common_mistakes": ["只听关键词忽略上下文", "混淆相似发音"],
                        },
                    },
                },
                {
                    "code": "KET-E2",
                    "title": "笔记填空 (Part 2)",
                    "lesson_type": "mock_listening",
                    "estimated_minutes": 40,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-LIST-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_listening",
                        "ket_skill": "listening",
                        "objectives": ["独白信息提取", "填入缺失信息"],
                        "knowledge_point_codes": ["KET-LIST-02"],
                        "prerequisite_codes": ["KET-E1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["独白信息提取", "笔记预读", "拼写准确"],
                            "common_mistakes": ["来不及预读笔记", "拼写错误"],
                        },
                    },
                },
                {
                    "code": "KET-E3",
                    "title": "长对话 (Part 3-4)",
                    "lesson_type": "mock_listening",
                    "estimated_minutes": 40,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-LIST-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_listening",
                        "ket_skill": "listening",
                        "objectives": ["多段对话多选", "信息匹配"],
                        "knowledge_point_codes": ["KET-LIST-03"],
                        "prerequisite_codes": ["KET-E1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["多段对话理解", "选项对比", "排除干扰"],
                            "common_mistakes": ["混淆不同对话内容", "被干扰项误导"],
                        },
                    },
                },
                {
                    "code": "KET-E4",
                    "title": "匹配练习 (Part 5)",
                    "lesson_type": "mock_listening",
                    "estimated_minutes": 35,
                    "sort_order": 4,
                    "is_published": True,
                    "knowledge_point_code": "KET-LIST-04",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_listening",
                        "ket_skill": "listening",
                        "objectives": ["对话匹配", "选项对应"],
                        "knowledge_point_codes": ["KET-LIST-04"],
                        "prerequisite_codes": ["KET-E1"],
                        "estimated_minutes": 35,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["对话与选项匹配", "主旨判断", "细节对应"],
                            "common_mistakes": ["匹配过度依赖单个词", "忽略整体语义"],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 6: Module F — 口语专项
        # ------------------------------------------------------------------
        {
            "code": "KET-U6",
            "name": "Module F 口语专项",
            "description": "个人问答、讨论练习、发音训练、模拟口语考试",
            "sort_order": 6,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-F1",
                    "title": "个人问答练习 (Part 1)",
                    "lesson_type": "mock_speaking",
                    "estimated_minutes": 40,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-SPK-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_speaking",
                        "ket_skill": "speaking",
                        "objectives": ["自我介绍", "个人信息问答(3-4分钟)"],
                        "knowledge_point_codes": ["KET-SPK-01"],
                        "prerequisite_codes": ["KET-B1"],
                        "estimated_minutes": 40,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["自我介绍模板", "个人信息问答", "基础问答句型"],
                            "common_mistakes": ["回答过短", "语法错误频繁"],
                        },
                    },
                },
                {
                    "code": "KET-F2",
                    "title": "讨论练习 (Part 2)",
                    "lesson_type": "mock_speaking",
                    "estimated_minutes": 45,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-SPK-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_speaking",
                        "ket_skill": "speaking",
                        "objectives": ["图片讨论", "表达观点与理由(5-6分钟)"],
                        "knowledge_point_codes": ["KET-SPK-02"],
                        "prerequisite_codes": ["KET-F1"],
                        "estimated_minutes": 45,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["图片描述", "表达观点", "给出理由"],
                            "common_mistakes": ["只描述不表达观点", "缺乏连接词"],
                        },
                    },
                },
                {
                    "code": "KET-F3",
                    "title": "发音训练",
                    "lesson_type": "concept",
                    "estimated_minutes": 35,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-SPK-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "ket_skill": "speaking",
                        "objectives": ["音素纠正", "重音与语调", "ASR反馈"],
                        "knowledge_point_codes": ["KET-SPK-03"],
                        "prerequisite_codes": ["KET-F1"],
                        "estimated_minutes": 35,
                        "xp_base": 70,
                        "steps": [],
                        "summary": {
                            "key_points": ["元音辅音纠正", "单词重音", "句子语调"],
                            "common_mistakes": ["中式英语发音", "重音位置错误"],
                        },
                    },
                },
                {
                    "code": "KET-F4",
                    "title": "模拟口语考试",
                    "lesson_type": "mock_speaking",
                    "estimated_minutes": 35,
                    "sort_order": 4,
                    "is_published": True,
                    "knowledge_point_code": "KET-SPK-04",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_speaking",
                        "ket_skill": "speaking",
                        "objectives": ["完整模拟Part 1+Part 2", "4维度评分"],
                        "knowledge_point_codes": ["KET-SPK-04"],
                        "prerequisite_codes": ["KET-F1", "KET-F2"],
                        "estimated_minutes": 35,
                        "xp_base": 100,
                        "steps": [],
                        "summary": {
                            "key_points": ["Grammar & Vocabulary", "Pronunciation", "Interactive Communication", "Global Achievement"],
                            "common_mistakes": ["紧张导致表达断续", "忽视互动交流"],
                        },
                    },
                },
            ],
        },
        # ------------------------------------------------------------------
        # Unit 7: Module G — 综合模拟
        # ------------------------------------------------------------------
        {
            "code": "KET-U7",
            "name": "Module G 综合模拟",
            "description": "完整模拟考试、模拟口语、弱项突破、考试策略",
            "sort_order": 7,
            "required_mastery": 0.8,
            "lessons": [
                {
                    "code": "KET-G1",
                    "title": "完整模拟考试 (阅读/写作/听力)",
                    "lesson_type": "mock_exam",
                    "estimated_minutes": 60,
                    "sort_order": 1,
                    "is_published": True,
                    "knowledge_point_code": "KET-MOCK-01",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_exam",
                        "objectives": ["3卷合一模拟", "模拟真实考试节奏(60+30分钟)"],
                        "knowledge_point_codes": ["KET-MOCK-01"],
                        "prerequisite_codes": ["KET-C1", "KET-D1", "KET-E1"],
                        "estimated_minutes": 60,
                        "xp_base": 100,
                        "steps": [],
                        "summary": {
                            "key_points": ["Reading & Writing 60min", "Listening 30min", "时间分配策略"],
                            "common_mistakes": ["时间不够", "涂卡遗漏"],
                        },
                    },
                },
                {
                    "code": "KET-G2",
                    "title": "模拟口语考试",
                    "lesson_type": "mock_speaking",
                    "estimated_minutes": 30,
                    "sort_order": 2,
                    "is_published": True,
                    "knowledge_point_code": "KET-MOCK-02",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "mock_speaking",
                        "ket_skill": "speaking",
                        "objectives": ["独立口语模拟", "Band评分"],
                        "knowledge_point_codes": ["KET-MOCK-02"],
                        "prerequisite_codes": ["KET-F4"],
                        "estimated_minutes": 30,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["Part 1+Part 2完整模拟", "Band评分反馈"],
                            "common_mistakes": ["回答过于简短", "未能展开讨论"],
                        },
                    },
                },
                {
                    "code": "KET-G3",
                    "title": "弱项突破",
                    "lesson_type": "practice",
                    "estimated_minutes": 45,
                    "sort_order": 3,
                    "is_published": True,
                    "knowledge_point_code": "KET-MOCK-03",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "practice",
                        "objectives": ["根据模拟成绩针对性补强"],
                        "knowledge_point_codes": ["KET-MOCK-03"],
                        "prerequisite_codes": ["KET-G1"],
                        "estimated_minutes": 45,
                        "xp_base": 80,
                        "steps": [],
                        "summary": {
                            "key_points": ["分析模拟弱项", "针对性练习", "查漏补缺"],
                            "common_mistakes": ["忽略弱项", "重复练习已掌握内容"],
                        },
                    },
                },
                {
                    "code": "KET-G4",
                    "title": "考试策略",
                    "lesson_type": "concept",
                    "estimated_minutes": 35,
                    "sort_order": 4,
                    "is_published": True,
                    "knowledge_point_code": "KET-MOCK-04",
                    "content": {
                        "schema_version": "1.0",
                        "subject": "ket_english",
                        "lesson_type": "concept",
                        "objectives": ["时间管理", "猜题技巧", "常见陷阱"],
                        "knowledge_point_codes": ["KET-MOCK-04"],
                        "prerequisite_codes": ["KET-G1"],
                        "estimated_minutes": 35,
                        "xp_base": 60,
                        "steps": [],
                        "summary": {
                            "key_points": ["时间分配", "排除法", "常见陷阱识别"],
                            "common_mistakes": ["在某题耗时过多", "空题不猜"],
                        },
                    },
                },
            ],
        },
    ],
}

# ---------------------------------------------------------------------------
# Knowledge Points — one per lesson
# ---------------------------------------------------------------------------

KET_KNOWLEDGE_POINTS = [
    # Diagnostic
    {"code": "KET-DIAG", "subject": "ket_english", "name": "KET入学诊断", "name_en": "KET Placement Test",
     "description": "英语水平测试，确定起始模块", "pillar": "diagnostic", "difficulty_level": 1, "amc_level": 0, "sort_order": 0, "estimated_minutes": 45},

    # Module A: Vocabulary
    {"code": "KET-VOC-01", "subject": "ket_english", "name": "高频日常词汇", "name_en": "High-Frequency Daily Vocabulary",
     "description": "KET核心词汇、场景分类、基础搭配", "pillar": "vocabulary", "difficulty_level": 1, "amc_level": 0, "sort_order": 1, "estimated_minutes": 35},
    {"code": "KET-VOC-02", "subject": "ket_english", "name": "数字/时间/日期", "name_en": "Numbers, Time and Dates",
     "description": "数字表达、时间读写、日期格式", "pillar": "vocabulary", "difficulty_level": 1, "amc_level": 0, "sort_order": 2, "estimated_minutes": 30},
    {"code": "KET-VOC-03", "subject": "ket_english", "name": "家庭/学校/食物", "name_en": "Family, School and Food",
     "description": "家庭成员、学科名称、食物饮品", "pillar": "vocabulary", "difficulty_level": 1, "amc_level": 0, "sort_order": 3, "estimated_minutes": 30},

    # Module B: Grammar
    {"code": "KET-GRAM-01", "subject": "ket_english", "name": "be动词/一般现在时", "name_en": "Be Verb & Present Simple",
     "description": "be动词变形、一般现在时、主谓一致", "pillar": "grammar", "difficulty_level": 2, "amc_level": 0, "sort_order": 4, "estimated_minutes": 40},
    {"code": "KET-GRAM-02", "subject": "ket_english", "name": "一般过去时/进行时", "name_en": "Past Simple & Present Continuous",
     "description": "规则/不规则动词过去式、现在进行时", "pillar": "grammar", "difficulty_level": 2, "amc_level": 0, "sort_order": 5, "estimated_minutes": 40},
    {"code": "KET-GRAM-03", "subject": "ket_english", "name": "疑问句/否定句", "name_en": "Questions & Negatives",
     "description": "一般疑问句、特殊疑问句、否定结构", "pillar": "grammar", "difficulty_level": 2, "amc_level": 0, "sort_order": 6, "estimated_minutes": 35},
    {"code": "KET-GRAM-04", "subject": "ket_english", "name": "介词/冠词", "name_en": "Prepositions & Articles",
     "description": "常用介词搭配、a/an/the用法", "pillar": "grammar", "difficulty_level": 2, "amc_level": 0, "sort_order": 7, "estimated_minutes": 35},
    {"code": "KET-GRAM-05", "subject": "ket_english", "name": "情态动词 (can/must)", "name_en": "Modal Verbs (can/must)",
     "description": "can/can't表能力、must/mustn't表义务", "pillar": "grammar", "difficulty_level": 2, "amc_level": 0, "sort_order": 8, "estimated_minutes": 35},

    # Module C: Reading
    {"code": "KET-READ-01", "subject": "ket_english", "name": "通知/标志理解", "name_en": "Understanding Notices & Signs",
     "description": "快速信息提取、图片+文字多选", "pillar": "reading", "difficulty_level": 2, "amc_level": 0, "sort_order": 9, "estimated_minutes": 40},
    {"code": "KET-READ-02", "subject": "ket_english", "name": "多文本匹配", "name_en": "Multiple Text Matching",
     "description": "扫读匹配、3段短文对应问题", "pillar": "reading", "difficulty_level": 2, "amc_level": 0, "sort_order": 10, "estimated_minutes": 40},
    {"code": "KET-READ-03", "subject": "ket_english", "name": "长文精读", "name_en": "Long Text Comprehension",
     "description": "分段阅读理解、主旨与细节", "pillar": "reading", "difficulty_level": 3, "amc_level": 0, "sort_order": 11, "estimated_minutes": 45},
    {"code": "KET-READ-04", "subject": "ket_english", "name": "完形填空技巧", "name_en": "Cloze Test Skills",
     "description": "语境词汇选择(Part 4)、语法填空(Part 5)", "pillar": "reading", "difficulty_level": 3, "amc_level": 0, "sort_order": 12, "estimated_minutes": 40},

    # Module D: Writing
    {"code": "KET-WRIT-01", "subject": "ket_english", "name": "邮件写作", "name_en": "Email Writing (Part 6)",
     "description": "邮件格式、3个要点覆盖、25词以上", "pillar": "writing", "difficulty_level": 2, "amc_level": 0, "sort_order": 13, "estimated_minutes": 40},
    {"code": "KET-WRIT-02", "subject": "ket_english", "name": "看图写故事", "name_en": "Picture Story Writing (Part 7)",
     "description": "图片描述、叙事连贯性、35词以上", "pillar": "writing", "difficulty_level": 3, "amc_level": 0, "sort_order": 14, "estimated_minutes": 40},
    {"code": "KET-WRIT-03", "subject": "ket_english", "name": "模拟写作 + AI评分", "name_en": "Mock Writing + AI Scoring",
     "description": "Content/Organisation/Language三维度评分", "pillar": "writing", "difficulty_level": 3, "amc_level": 0, "sort_order": 15, "estimated_minutes": 35},

    # Module E: Listening
    {"code": "KET-LIST-01", "subject": "ket_english", "name": "短对话理解", "name_en": "Short Dialogue Comprehension (Part 1)",
     "description": "短对话+图片选择、关键信息抓取", "pillar": "listening", "difficulty_level": 2, "amc_level": 0, "sort_order": 16, "estimated_minutes": 40},
    {"code": "KET-LIST-02", "subject": "ket_english", "name": "笔记填空", "name_en": "Note-Taking (Part 2)",
     "description": "独白信息提取、填入缺失信息", "pillar": "listening", "difficulty_level": 2, "amc_level": 0, "sort_order": 17, "estimated_minutes": 40},
    {"code": "KET-LIST-03", "subject": "ket_english", "name": "长对话", "name_en": "Long Dialogue (Part 3-4)",
     "description": "多段对话多选、信息匹配", "pillar": "listening", "difficulty_level": 3, "amc_level": 0, "sort_order": 18, "estimated_minutes": 40},
    {"code": "KET-LIST-04", "subject": "ket_english", "name": "匹配练习", "name_en": "Matching Practice (Part 5)",
     "description": "对话匹配、选项对应", "pillar": "listening", "difficulty_level": 3, "amc_level": 0, "sort_order": 19, "estimated_minutes": 35},

    # Module F: Speaking
    {"code": "KET-SPK-01", "subject": "ket_english", "name": "个人问答练习", "name_en": "Personal Q&A (Part 1)",
     "description": "自我介绍、个人信息问答(3-4分钟)", "pillar": "speaking", "difficulty_level": 2, "amc_level": 0, "sort_order": 20, "estimated_minutes": 40},
    {"code": "KET-SPK-02", "subject": "ket_english", "name": "讨论练习", "name_en": "Discussion Practice (Part 2)",
     "description": "图片讨论、表达观点与理由(5-6分钟)", "pillar": "speaking", "difficulty_level": 3, "amc_level": 0, "sort_order": 21, "estimated_minutes": 45},
    {"code": "KET-SPK-03", "subject": "ket_english", "name": "发音训练", "name_en": "Pronunciation Training",
     "description": "音素纠正、重音与语调、ASR反馈", "pillar": "speaking", "difficulty_level": 2, "amc_level": 0, "sort_order": 22, "estimated_minutes": 35},
    {"code": "KET-SPK-04", "subject": "ket_english", "name": "模拟口语考试", "name_en": "Mock Speaking Exam",
     "description": "完整模拟Part 1+Part 2，4维度评分", "pillar": "speaking", "difficulty_level": 3, "amc_level": 0, "sort_order": 23, "estimated_minutes": 35},

    # Module G: Mock Exam
    {"code": "KET-MOCK-01", "subject": "ket_english", "name": "完整模拟考试", "name_en": "Full Mock Exam (R/W/L)",
     "description": "3卷合一，模拟真实考试节奏", "pillar": "mock_exam", "difficulty_level": 3, "amc_level": 0, "sort_order": 24, "estimated_minutes": 60},
    {"code": "KET-MOCK-02", "subject": "ket_english", "name": "模拟口语考试", "name_en": "Mock Speaking Test",
     "description": "独立口语模拟，Band评分", "pillar": "mock_exam", "difficulty_level": 3, "amc_level": 0, "sort_order": 25, "estimated_minutes": 30},
    {"code": "KET-MOCK-03", "subject": "ket_english", "name": "弱项突破", "name_en": "Weakness Targeting",
     "description": "根据模拟成绩针对性补强", "pillar": "mock_exam", "difficulty_level": 3, "amc_level": 0, "sort_order": 26, "estimated_minutes": 45},
    {"code": "KET-MOCK-04", "subject": "ket_english", "name": "考试策略", "name_en": "Exam Strategies",
     "description": "时间管理、猜题技巧、常见陷阱", "pillar": "mock_exam", "difficulty_level": 2, "amc_level": 0, "sort_order": 27, "estimated_minutes": 35},
]

# ---------------------------------------------------------------------------
# Knowledge Dependencies  (prerequisite_code, target_code, dependency_type, strength)
# ---------------------------------------------------------------------------

KET_KNOWLEDGE_DEPENDENCIES = [
    # Module A: Vocabulary chain
    ("KET-VOC-01", "KET-VOC-02", "requires", 1),
    ("KET-VOC-01", "KET-VOC-03", "requires", 1),

    # Module B: Grammar — all depend on B1
    ("KET-GRAM-01", "KET-GRAM-02", "requires", 1),
    ("KET-GRAM-01", "KET-GRAM-03", "requires", 1),
    ("KET-GRAM-01", "KET-GRAM-04", "requires", 1),
    ("KET-GRAM-01", "KET-GRAM-05", "requires", 1),

    # Module C: Reading chain
    ("KET-READ-01", "KET-READ-02", "requires", 1),
    ("KET-READ-01", "KET-READ-03", "requires", 1),
    ("KET-READ-01", "KET-READ-04", "requires", 1),
    ("KET-GRAM-01", "KET-READ-04", "recommends", 1),

    # Module D: Writing chain
    ("KET-GRAM-01", "KET-WRIT-01", "requires", 1),
    ("KET-WRIT-01", "KET-WRIT-02", "requires", 1),
    ("KET-WRIT-01", "KET-WRIT-03", "requires", 1),
    ("KET-WRIT-02", "KET-WRIT-03", "requires", 1),

    # Module E: Listening chain
    ("KET-LIST-01", "KET-LIST-02", "requires", 1),
    ("KET-LIST-01", "KET-LIST-03", "requires", 1),
    ("KET-LIST-01", "KET-LIST-04", "requires", 1),

    # Module F: Speaking chain
    ("KET-GRAM-01", "KET-SPK-01", "requires", 1),
    ("KET-SPK-01", "KET-SPK-02", "requires", 1),
    ("KET-SPK-01", "KET-SPK-03", "requires", 1),
    ("KET-SPK-01", "KET-SPK-04", "requires", 1),
    ("KET-SPK-02", "KET-SPK-04", "requires", 1),

    # Module G: Mock exam dependencies
    ("KET-READ-01", "KET-MOCK-01", "requires", 1),
    ("KET-WRIT-01", "KET-MOCK-01", "requires", 1),
    ("KET-LIST-01", "KET-MOCK-01", "requires", 1),
    ("KET-SPK-04", "KET-MOCK-02", "requires", 1),
    ("KET-MOCK-01", "KET-MOCK-03", "requires", 1),
    ("KET-MOCK-01", "KET-MOCK-04", "recommends", 1),
]

# ---------------------------------------------------------------------------
# Problems — 1-2 per lesson (vocab, grammar, reading only)
# ---------------------------------------------------------------------------

KET_PROBLEMS = [
    # === Module A: Vocabulary ===
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-A1-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Vocabulary\n\nChoose the correct word:\n\nMy sister is very good ___ playing the piano.",
        "options": {"A": "in", "B": "at", "C": "on", "D": "with"},
        "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-VOC-01"],
        "hints": ["Think about the phrase 'good at doing something'."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-A1-P2",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Vocabulary\n\nChoose the correct word:\n\nCan I have a ___ of water, please?",
        "options": {"A": "glass", "B": "cup", "C": "plate", "D": "bowl"},
        "correct_answer": "A", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-VOC-01"],
        "hints": ["Water is usually served in a glass."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-A2-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Vocabulary\n\nWhat time is 'quarter past three'?",
        "options": {"A": "3:15", "B": "3:30", "C": "3:45", "D": "3:00"},
        "correct_answer": "A", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-VOC-02"],
        "hints": ["A quarter = 15 minutes. Past means after."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-A3-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Vocabulary\n\nWhich word is a subject you study at school?",
        "options": {"A": "brother", "B": "history", "C": "apple", "D": "kitchen"},
        "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-VOC-03"],
        "hints": ["Think about your school timetable."],
    },

    # === Module B: Grammar ===
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B1-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nShe ___ a student at Park School.",
        "options": {"A": "am", "B": "is", "C": "are", "D": "be"},
        "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-GRAM-01"],
        "hints": ["Use 'is' for he/she/it."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B1-P2",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nI usually ___ breakfast at 7 o'clock.",
        "options": {"A": "eat", "B": "eats", "C": "eating", "D": "ate"},
        "correct_answer": "A", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-GRAM-01"],
        "hints": ["'I' takes the base form of the verb."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B2-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nWe ___ to the cinema last Saturday.",
        "options": {"A": "go", "B": "goes", "C": "went", "D": "going"},
        "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-GRAM-02"],
        "hints": ["'Last Saturday' means past tense."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B2-P2",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nLook! The children ___ in the park.",
        "options": {"A": "play", "B": "plays", "C": "are playing", "D": "played"},
        "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-GRAM-02"],
        "hints": ["'Look!' signals something happening right now."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B3-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct question:\n\nYou want to know where the bank is.",
        "options": {
            "A": "Where the bank is?",
            "B": "Where is the bank?",
            "C": "Where does the bank?",
            "D": "Where the bank?",
        },
        "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-GRAM-03"],
        "hints": ["Questions with 'where' invert subject and verb."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B4-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nThe meeting is ___ Monday ___ 9 o'clock.",
        "options": {"A": "in / at", "B": "on / at", "C": "on / in", "D": "at / on"},
        "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-GRAM-04"],
        "hints": ["Use 'on' for days, 'at' for specific times."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-B5-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nYou ___ drive without a license. It's illegal.",
        "options": {"A": "can't", "B": "mustn't", "C": "don't have to", "D": "shouldn't"},
        "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 45,
        "knowledge_point_codes": ["KET-GRAM-05"],
        "hints": ["'Mustn't' means it is prohibited."],
    },

    # === Module C: Reading ===
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-C1-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Reading\n\nRead the notice and answer:\n\n"
            "> **NOTICE: The school library will be closed on Monday for cleaning. "
            "Please return all books by Friday.**\n\n"
            "When should you return your books?"
        ),
        "options": {"A": "Monday", "B": "Friday", "C": "Saturday", "D": "Sunday"},
        "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 60,
        "knowledge_point_codes": ["KET-READ-01"],
        "hints": ["Look for the day mentioned after 'return'."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-C2-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Reading\n\n"
            "> Hi Tom, I can't come to your party on Saturday because I have a football match. "
            "Can we meet on Sunday instead? — Alex\n\n"
            "Why can't Alex go to the party?"
        ),
        "options": {
            "A": "He is sick.",
            "B": "He has a football match.",
            "C": "He doesn't like parties.",
            "D": "He has to study.",
        },
        "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 60,
        "knowledge_point_codes": ["KET-READ-02"],
        "hints": ["Look for the reason after 'because'."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-C3-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Reading\n\n"
            "Read the passage and answer:\n\n"
            "> Emma loves animals. She has a dog called Max and a cat called Lily. "
            "Every morning, she takes Max for a walk in the park. In the afternoon, "
            "she feeds Lily and gives her fresh water. On weekends, Emma volunteers "
            "at the animal shelter near her home.\n\n"
            "What does Emma do on weekends?"
        ),
        "options": {
            "A": "She walks Max.",
            "B": "She feeds Lily.",
            "C": "She volunteers at an animal shelter.",
            "D": "She goes to school.",
        },
        "correct_answer": "C", "difficulty": 2, "estimated_time_sec": 60,
        "knowledge_point_codes": ["KET-READ-03"],
        "hints": ["Look at the last sentence of the passage."],
    },
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-C4-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Reading\n\n"
            "Choose the correct word to complete the sentence:\n\n"
            "I ___ to school every day by bus."
        ),
        "options": {"A": "go", "B": "goes", "C": "going", "D": "went"},
        "correct_answer": "A", "difficulty": 2, "estimated_time_sec": 45,
        "knowledge_point_codes": ["KET-READ-04"],
        "hints": ["'I' uses the base form of the verb in present simple."],
    },

    # === Module E: Listening (text-based, no audio) ===
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-E1-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Listening Comprehension\n\n"
            "You hear: \"Excuse me, where is the nearest post office?\" "
            "\"Go straight ahead and turn left at the traffic lights.\"\n\n"
            "Where is the post office?"
        ),
        "options": {
            "A": "On the right.",
            "B": "Straight ahead on the left.",
            "C": "Behind the traffic lights.",
            "D": "Next to the bank.",
        },
        "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 45,
        "knowledge_point_codes": ["KET-LIST-01"],
        "hints": ["Listen for direction words: 'straight' and 'left'."],
    },

    # === Module F: Speaking (conceptual questions) ===
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-F1-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Speaking\n\n"
            "In KET Speaking Part 1, which topic is NOT usually asked about?"
        ),
        "options": {
            "A": "Your name and age",
            "B": "Your hobbies",
            "C": "Your political opinions",
            "D": "Your school subjects",
        },
        "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-SPK-01"],
        "hints": ["KET asks about everyday personal topics."],
    },

    # === Module G: Mock Exam ===
    {
        "source": "KET", "source_year": 2024, "source_code": "KET-G4-P1",
        "subject": "ket_english", "format": "mcq",
        "question_markdown": (
            "## Exam Strategy\n\n"
            "During the KET Reading & Writing test, you have 60 minutes for 7 parts. "
            "What is the best time management strategy?"
        ),
        "options": {
            "A": "Spend most time on Part 1 and rush the rest",
            "B": "Spend about 8-9 minutes per part",
            "C": "Skip the writing parts entirely",
            "D": "Only do the parts you find easy",
        },
        "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
        "knowledge_point_codes": ["KET-MOCK-04"],
        "hints": ["7 parts × ~8.5 min = 60 min."],
    },
]
