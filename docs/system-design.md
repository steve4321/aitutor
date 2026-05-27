# AI私人家教系统 — 完整设计文档

> 覆盖 AMC 数学竞赛 + KET 英语考试
> 版本：v1.0 | 日期：2026-05-27

---

## 目录

1. [系统总览](#1-系统总览)
2. [AMC数学模块设计](#2-amc数学模块设计)
3. [KET英语模块设计](#3-ket英语模块设计)
4. [系统架构与技术选型](#4-系统架构与技术选型)
5. [数据模型设计](#5-数据模型设计)
6. [学生端UI/UX设计](#6-学生端uiux设计)
7. [AI Prompt与教学策略](#7-ai-prompt与教学策略)
8. [评估与知识追踪系统](#8-评估与知识追踪系统)
9. [多Agent协作架构](#9-多agent协作架构)
10. [家长端与报告系统](#10-家长端与报告系统)

---

## 1. 系统总览

### 1.1 产品定位

面向中小学生的AI私人家教，专注于：
- **AMC**（美国数学竞赛）：AMC 8 / AMC 10 / AMC 12 / AIME
  - 课程按级别标记（🟢 AMC 8 / 🟡 AMC 10 / 🔴 AMC 12）
  - AMC 8 学生可跳过 🟡🔴 进阶内容，学有余力时可主动探索
  - 支持随时切换目标级别，自动调整课程路径
- **KET**（剑桥英语通用基础考试）：CEFR A2级别

### 1.2 核心设计理念

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI 私人家教                               │
│                                                                 │
│   双模式架构                                                     │
│   ┌────────────────────┐    ┌──────────────────────────┐        │
│   │  📚 课程模式         │    │  🎯 刷题模式              │      │
│   │  系统学知识          │    │  实战练题目              │       │
│   │  互动发现→概念→练习  │    │  苏格拉底式引导          │       │
│   └────────┬───────────┘    └──────────┬───────────────┘        │
│            │                           │                         │
│            ▼                           ▼                         │
│   ┌───────────────────────────────────────────────────────┐     │
│   │              🧠 共享知识引擎                            │     │
│   │  知识图谱 · 掌握度追踪 · 间隔重复 · 学生画像            │     │
│   └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 双模式切换逻辑

| 触发条件 | 切换方向 | 示例 |
|---------|---------|------|
| 完成课程一节 | 课程→刷题 | "刚学完相似三角形，来做几道AMC真题？" |
| 刷题遇到未学知识 | 刷题→课程 | "这题需要互补计数技巧，要先学一下吗？" |
| 错题分析发现知识漏洞 | 刷题→课程 | "你在圆的定理上错了3题，建议复习L2.6" |
| 课程掌握度>85% | 自动解锁对应难度真题 | "因式分解已精通，来做AMC 10级题目" |
| 间隔重复到期 | 任何模式→复习 | 自动插入复习卡片到当日任务 |

---

## 2. AMC数学模块设计

### 2.1 课程路径（四大支柱）

基于AMC 8十年数据（2016-2025，225题分析）和AMC 10/12分布：

> **图例**: `🟢` = AMC 8 必学 | `🟡` = AMC 10 新增（AMC 8阶段可跳过） | `🔴` = AMC 12 新增

```
📍 阶段0: 入学诊断 (1次课)
│   10道跨领域诊断题 → 生成知识画像 → 跳过已掌握模块
│   根据目标考试(AMC 8/10/12)自动显示/隐藏对应级别课程
│
├─── 📐 支柱A: 代数 (AMC 10占比28-36%)
│    ├── 🟢 A1 一次方程与不等式
│    ├── 🟢 A2 方程组
│    ├── 🟢 A3 函数入门（定义、图像、一次函数）
│    ├── 🟢 A4 比例、百分比、比率
│    ├── 🟢 A5 指数与根式
│    ├── 🔑 阶段测试A-1
│    ├── 🟡 A6 二次方程—因式分解法            ← AMC 10新增
│    ├── 🟡 A7 二次方程—配方法与求根公式       ← AMC 10新增
│    ├── 🟡 A8 特殊因式分解（差平方、立方和差） ← AMC 10新增
│    ├── 🟡 A9 函数进阶（复合、反函数、二次函数图像） ← AMC 10新增
│    ├── 🟡 A10 数列（等差、等比、求和、望远镜求和）  ← AMC 10新增
│    └── 🔑 阶段测试A-2 (AMC 10)
│
├─── 📏 支柱B: 几何 (AMC 8占比22%, AMC 10占比24-32%, 难题占36%)
│    ├── 🟢 B1 角度与平行线
│    ├── 🟢 B2 三角形（面积、全等）
│    ├── 🟢 B3 勾股定理 (50%几何题涉及)
│    ├── 🟡 B4 相似三角形                    ← AMC 10新增
│    ├── 🟢 B5 四边形与多边形
│    ├── 🟡 B6 圆（圆心角、圆周角、切割线、Power of a Point） ← AMC 10新增
│    ├── 🟢 B7 组合图形面积计算
│    ├── 🟡 B8 坐标几何                      ← AMC 10新增
│    ├── 🟡 B9 立体几何                      ← AMC 10新增
│    └── 🔑 阶段测试B
│
├─── 🎲 支柱C: 计数与概率 (难题占29%, 学校最不教)
│    ├── 🟢 C1 加法原理与乘法原理
│    ├── 🟢 C2 排列
│    ├── 🟡 C3 组合                          ← AMC 10新增
│    ├── 🟡 C4 杨辉三角与二项式定理           ← AMC 10新增
│    ├── 🟢 C5 基础概率
│    ├── 🟡 C6 互补计数与分类讨论             ← AMC 10新增
│    ├── 🔑 阶段测试C-1
│    ├── 🟡 C7 容斥原理                      ← AMC 10新增
│    ├── 🟡 C8 递推                          ← AMC 10新增
│    └── 🟡 C9 期望值                        ← AMC 10新增
│
└─── 🔢 支柱D: 数论 (上升趋势, 2023年2题→2025年5题)
     ├── 🟢 D1 整除与整除规则 (2,3,4,5,9,11)
     ├── 🟢 D2 质数与质因数分解
     ├── 🟢 D3 GCD与LCM（辗转相除法）
     ├── 🟡 D4 余数与同余基础                 ← AMC 10新增
     ├── 🟡 D5 进位制                         ← AMC 10新增
     ├── 🔑 阶段测试D-1
     ├── 🟡 D6 不定方程                       ← AMC 10新增
     └── 🔟 D7 欧拉定理入门                   ← AMC 10新增
```

#### AMC 8 vs AMC 10 课程范围对照

| 支柱 | AMC 8 课程 | AMC 10 新增课程 | 说明 |
|------|-----------|----------------|------|
| **代数** | A1-A5 (一次方程、方程组、函数入门、比例、指数) | A6-A10 (二次方程、因式分解、函数进阶、数列) | AMC 8不考二次方程 |
| **几何** | B1-B3, B5, B7 (角度、三角形、勾股定理、四边形、面积) | B4, B6, B8, B9 (相似三角形、圆、坐标几何、立体几何) | AMC 8几何以面积和勾股为主 |
| **计数** | C1-C2, C5 (乘法原理、排列、基础概率) | C3-C4, C6-C9 (组合、二项式、互补计数、容斥、递推、期望) | AMC 8计数以基础排列和概率为主 |
| **数论** | D1-D3 (整除、质因数、GCD/LCM) | D4-D7 (同余、进位制、不定方程、欧拉定理) | AMC 8数论以基础整除和质数为主 |

> **跳过逻辑**: 当学生目标设为 AMC 8 时，🟡和🔴课程默认折叠/隐藏，显示"AMC 10进阶内容"入口供学有余力的学生探索。学生可随时切换目标级别来展开全部课程。

### 2.2 知识点前置依赖图

> 🟢 AMC 8 必学 | 🟡 AMC 10 新增 | 🔴 AMC 12 新增

```
🟢一次方程 ──→ 🟢方程组 ──→ 🟢函数入门
   │                         │
   ↓                         ↓
🟢指数根式 → 🟡二次方程(因式分解) → 🟡二次方程(公式法)
                   │
                   ↓
             🟡特殊因式分解 → 🔴多项式进阶(Vieta)

🟢角度平行线 → 🟢三角形 → 🟢勾股定理 → 🟡相似三角形 → 🟡圆
                         │                   │
                         ↓                   ↓
                     🟡坐标几何 ←──── 🟢面积计算

🟢乘法原理 → 🟢排列 → 🟡组合 → 🟡二项式定理 → 🟢概率
               │                          │
               └→ 🟡互补计数 → 🟡分类讨论 ─┘

🟢整除 → 🟢质因数分解 → 🟢GCD/LCM → 🟡同余 → 🟡不定方程
```

#### 跨级别前置依赖

AMC 10 的 🟡 课程依赖 AMC 8 的 🟢 课程作为前置。例如：
- 🟡二次方程 需要 🟢一次方程 + 🟢指数根式 作为前置
- 🟡相似三角形 需要 🟢勾股定理 作为前置
- 🟡组合 需要 🟢排列 作为前置

当 AMC 8 学生尝试访问 🟡 课程时，系统会提示：
> "这是 AMC 10 进阶内容，需要先完成 [前置🟢课程]。确认要学习吗？"

### 2.3 单节课结构（20-30分钟）

参考 Brilliant.org "先动手后理论" + 5E教学循环：

```
┌─────────────────────────────────────────────────────┐
│  Lesson: B3 勾股定理                                 │
│  时长: 25min | 前置: ✅三角形基础 ✅面积计算          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📖 ENGAGE 引入 (3 min)                             │
│  展示一个3-4-5直角三角形的GeoGebra交互图              │
│  "你能量出斜边多长吗？"                              │
│                                                     │
│  🔢 EXPLORE 探索发现 (5 min)                        │
│  学生测量不同直角三角形的边长                         │
│  "3²+4²=5²? 那5²+12²=?" → 发现规律                 │
│                                                     │
│  💡 EXPLAIN 概念讲解 (5 min)                        │
│  归纳 a² + b² = c²                                  │
│  展示公式 + 图形标注 + 几何证明动画                   │
│  强调: "AMC约50%几何题用到此定理"                     │
│                                                     │
│  ✏️ ELABORATE 引导练习 (8 min)                      │
│  Q1: 直角边6,8 → 斜边? (基础)                       │
│  Q2: 斜边13,一边5 → 另一边? (逆向)                  │
│  Q3: 正方形对角线10√2 → 边长? (变形)                │
│  苏格拉底式引导, 不直接给答案                         │
│                                                     │
│  ✅ EVALUATE 小测验 (4 min)                          │
│  3道检测题 → 80%正确率通过 → 解锁B4相似三角形        │
│                                                     │
│  📊 结果: 掌握度更新 → 间隔重复安排 → 下课推荐       │
└─────────────────────────────────────────────────────┘
```

### 2.4 刷题模式交互设计

#### 完整交互流程（6阶段）

```
Stage 1: 出题与诊断
  AI根据学生画像推荐 / 学生自由选择 / 拍照上传
     ↓
Stage 2: 理解题目
  "用你自己的话, 告诉我这道题在问什么？"
     ↓
Stage 3: 策略探索
  "这属于什么类型？你见过类似的题吗？"
  苏格拉底式引导, 不给答案
     ↓
Stage 4: 逐步求解
  学生主导推导, AI在卡住时给提示
  提示从L0(元认知)到L4(示例演示)逐级升级
     ↓
Stage 5: 验证反思
  "用小数值验证一下？还有别的解法吗？"
  总结关键技能和策略
     ↓
Stage 6: 适应性跟进
  更新掌握度 → 推荐下一题 → 安排间隔复习
```

#### 5级提示升级系统

| 级别 | 名称 | 示例 | 触发条件 |
|------|------|------|---------|
| L0 | 元认知 | "你觉得第一步应该做什么？" | 初始引导 |
| L1 | 策略 | "这是指数题, 你学过哪些指数法则？" | 1轮无进展 |
| L2 | 概念 | "想想 2^a × 2^b 等于什么？" | 2轮无进展 |
| L3 | 操作 | "试试把 2^2023 + 2^2023 看成 a + a" | 3轮无进展 |
| L4 | 示例 | 展示简化版同类题的完整解法 | 4轮或学生请求 |

规则: 每次只升一级, 学生有进展则降一级。

#### 错误处理3种模式

**计算错误**: 不说"你错了", 引导自行验证
```
S: "2^10 = 2014"
T: "验证一下: 2^5 × 2^5 = 32 × 32 = ?"
```

**方法错误**: 用反问引导发现不适用
```
S: "我要用对数来算"
T: "题目要精确值还是近似值？对数能给你精确值吗？"
```

**概念误解**: 用反例制造认知冲突
```
S: "2^2023 + 2^2023 = 2^4046"
T: "测试: 3^2 + 3^2 = 9+9 = 18, 但 3^4 = 81。18=81吗？问题在哪？"
```

---

## 3. KET英语模块设计

### 3.1 KET考试结构

| 试卷 | 内容 | 时长 | 题数 | 占比 |
|------|------|------|------|------|
| Reading & Writing | 理解文本、基础写作 | 60min | 32题+2写作 | 50% |
| Listening | 跟听慢速材料 | ~30min | 25题 | 25% |
| Speaking | 面对面对话 | 8-10min | 2部分 | 25% |

### 3.2 四大技能模块

```
┌──────────────────────────────────────────────────────────┐
│                   KET 英语课程体系                         │
│                                                          │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌─────────┐ │
│  │ 📖 阅读     │ │ ✍️ 写作     │ │ 🎧 听力   │ │ 🗣 口语  │ │
│  │            │ │            │ │          │ │         │ │
│  │ 7种题型    │ │ 2种写作    │ │ 5种题型  │ │ 2部分   │ │
│  │ 选择/匹配  │ │ 邮件/故事  │ │ 对话/独白│ │ 问答/讨论│ │
│  │ 填空/完形  │ │ 25-35词    │ │ 信息提取 │ │ AI角色扮演│ │
│  └────────────┘ └────────────┘ └──────────┘ └─────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  📚 词汇 & 语法 (贯穿所有模块, 间隔重复)          │    │
│  │  1,500核心词汇 · 基础语法结构 · 语用场景           │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 3.3 各技能模块交互设计

#### 阅读 (Reading)

**交互流程**:
```
展示文章段落 → 学生阅读 → AI提问(自由文本回答) → 评分+反馈
                                          ↓
                               答错 → 显示原文出处+参考答案
                               答对 → 追问更深理解
```

**KET 7种题型的AI练习设计**:

| 题型 | AI练习方式 | 交互特点 |
|------|----------|---------|
| Part 1: 多选(通知/标志) | 展示图片+文字→选择含义 | 训练快速信息提取 |
| Part 2: 匹配(3短文) | 拖拽匹配问题到对应文本 | 训练扫读能力 |
| Part 3: 多选(长文) | 分段阅读+每段后提问 | 训练精读理解 |
| Part 4: 完形填空(词汇) | 下拉选择/拖拽填入 | 训练语境词汇 |
| Part 5: 开放完形(语法) | 手动输入1词 | 训练语法+拼写 |
| Part 6: 引导写作(邮件) | 独立写作模块 | 见写作设计 |
| Part 7: 看图写作(故事) | 独立写作模块 | 见写作设计 |

**Socratic阅读引导**:
```
AI: "这段话里, 作者说'It was pouring outside'。'pouring'在这里是什么意思？"
学生: "下雨很大？"
AI: "对！这是一个比喻表达——雨像倒水一样。你能想出其他形容大雨的词吗？"
```

#### 写作 (Writing)

**评估管线**:
```
学生提交作文 → Content检查(3个要点是否覆盖)
                    → Organisation评估(结构是否清晰)
                    → Language评估(语法/词汇/拼写)
                    → 综合Band评分(0-5)
                    → 具体反馈+高亮标注
                    → 学生修改 → 重新提交
```

**KET写作评分标准 (Cambridge官方)**:

| Band | Content | Organisation | Language |
|------|---------|-------------|----------|
| 5 | 3个要点全部传达, 清晰 | 结构良好, 连贯 | 只有轻微拼写/语法错误 |
| 3 | 3个要点都尝试, 部分需读者推断 | 基本结构 | 一些不影响理解的错误 |
| 1 | 只传达1个要点 | 结构不清 | 错误影响理解 |

**交互设计**:
```
Step 1: 展示题目(3个必须包含的要点) + 字数提示(25-35词)
Step 2: 学生在编辑区写作, 实时显示字数
Step 3: 提交后AI检查:
        ✓ 要点1覆盖了吗？ ✓ 要点2覆盖了吗？ ✓ 要点3覆盖了吗？
        ✓ 字数达标吗？ ✓ 有语法/拼写错误吗？
Step 4: 显示反馈:
        "你的邮件传达了所有3个要点！但第2点的表达可以更自然。
         'I want go cinema' → 'I want to go to the cinema'
         要修改后重新提交吗？"
Step 5: 学生修改 → 重新评分 → 进步可视化
```

#### 听力 (Listening)

**系统架构**:
```
TTS音频生成 → 播放音频(练习模式可重播, 考试模式只播一次)
              → 展示题目 → 学生作答 → 评分+回顾
```

**KET听力5种题型**:

| 部分 | 内容 | AI练习方式 |
|------|------|----------|
| Part 1 | 短对话+图片选择 | 播放对话→选择匹配图片 |
| Part 2 | 独白→填空笔记 | 播放独白→填入缺失信息 |
| Part 3 | 对话→多选 | 播放对话→选择正确答案 |
| Part 4 | 5段短材料→多选 | 播放每段→选择答案 |
| Part 5 | 对话→匹配 | 播放对话→拖拽匹配选项 |

**交互特色**:
- 练习模式: 无限重播, 可点击任意句子重复听
- 考试模式: 仅播放两次, 模拟真实考试
- 听力原文: 答题后可查看原文, 高亮答案出处
- 语速调节: 0.8x / 1.0x / 1.2x 可选

#### 口语 (Speaking)

**AI评估管线**:
```
学生录音 → ASR(Whisper)转录 → 评估引擎分析:
  ├── 语法与词汇 (Grammar & Vocabulary)
  ├── 发音 (Pronunciation: ASR置信度+音素分析)
  ├── 交互沟通 (Interactive Communication)
  └── 整体表现 (Global Achievement)
→ Band评分(0-5) + 具体反馈
→ TTS语音回复, 模拟考官
```

**Part 1 — 个人问答 (3-4分钟)**:
```
AI考官(语音): "Hello, what's your name? Can you spell it?"
学生(语音): "My name is Li Ming. L-I, M-I-N-G."
AI: "Where do you live?"
学生: "I live in Shanghai."
AI: [内部评估: 语法✓, 词汇基础✓, 发音L-I需要更清晰]
AI: "Great! Tell me about what you like to do on weekends."
```

**Part 2 — 讨论 (5-6分钟)**:
```
AI扮演讨论伙伴:
展示一张活动图片 → AI: "Look at these activities. Which one do you like?"
学生回答 → AI追问: "Why?" → 学生解释 → AI提出不同观点
模拟与另一位考生的讨论互动
```

#### 词汇与语法 (贯穿所有模块)

**词汇教学 — 间隔重复**:

采用 FSRS 算法调度:
```
新词学习 → 1天后复习 → 3天 → 7天 → 14天 → 30天
遗忘(答错) → 重置间隔, 插入当日复习队列
```

**词汇学习交互**:
```
Step 1: 展示单词 + 图片/场景 (不用中文翻译, 用英文解释)
Step 2: "Guess: What does 'pouring' mean?" (猜词→反馈)
Step 3: 在句子中练习填空
Step 4: 造句练习
Step 5: 间隔重复自动安排
```

**语法教学 — 苏格拉底式对话**:

4级提示升级(与数学类似):
```
L1: 展示错误句子 → "Something is wrong here. Can you find it?"
L2: "Look at the verb. Does it match the subject?"
L3: "The rule is: third person singular needs -s. 'He want' → ?"
L4: "The correct form is 'He wants'. Let's practice more examples."
```

### 3.4 KET课程路径

```
📍 入学诊断: 英语水平测试
│
├─── 🅰️ 基础词汇 (2-3周)
│    ├── 高频日常词汇(500词)
│    ├── 数字/时间/日期
│    ├── 家庭/学校/食物
│    └── 间隔重复开始
│
├─── 🅱️ 基础语法 (3-4周)
│    ├── be动词/一般现在时
│    ├── 一般过去时/进行时
│    ├── 疑问句/否定句
│    ├── 介词/冠词
│    └── 情态动词(can/must)
│
├─── 🅲 阅读专项 (3-4周)
│    ├── 通知/标志理解(Part 1)
│    ├── 多文本匹配(Part 2)
│    ├── 长文精读(Part 3)
│    └── 完形填空技巧(Part 4-5)
│
├─── 🅳 写作专项 (2-3周)
│    ├── 邮件写作(Part 6: 25+词)
│    ├── 看图写故事(Part 7: 35+词)
│    └── 模拟写作+AI评分
│
├─── 🅴 听力专项 (2-3周)
│    ├── 短对话理解(Part 1)
│    ├── 笔记填空(Part 2)
│    ├── 长对话(Part 3-4)
│    └── 匹配练习(Part 5)
│
├─── 🅵 口语专项 (2-3周)
│    ├── 个人问答练习(Part 1)
│    ├── 讨论练习(Part 2)
│    ├── 发音训练
│    └── 模拟口语考试
│
└─── 🅶 综合模拟 (2-4周)
     ├── 完整模拟考试(阅读/写作/听力)
     ├── 模拟口语考试
     ├── 弱项突破
     └── 考试策略
```

---

## 4. 系统架构与技术选型

### 4.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                        客户端层                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  iOS App     │  │  Android App │  │  Web App     │       │
│  │  (React      │  │  (React      │  │  (Next.js)   │       │
│  │   Native)    │  │   Native)    │  │              │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         └──────────────────┼──────────────────┘              │
│                            │ REST API + WebSocket             │
├────────────────────────────┼─────────────────────────────────┤
│                       API 网关层                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  API Gateway (认证/限流/路由)                          │    │
│  └──────────────────────────┬───────────────────────────┘    │
├────────────────────────────┼─────────────────────────────────┤
│                       服务层                                  │
│                                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐     │
│  │ Tutor Agent │ │ Curriculum   │ │ Assessment       │     │
│  │ (教学对话)   │ │ Engine       │ │ Engine           │     │
│  │             │ │ (课程调度)    │ │ (评估/知识追踪)   │     │
│  └──────┬──────┘ └──────┬───────┘ └────────┬─────────┘     │
│         │               │                   │               │
│  ┌──────┴──────┐ ┌──────┴───────┐ ┌───────┴──────────┐    │
│  │ Problem     │ │ Knowledge    │ │ Speech           │    │
│  │ Service     │ │ Graph        │ │ Service          │    │
│  │ (题库管理)   │ │ (知识图谱)    │ │ (ASR/TTS/评分)   │    │
│  └─────────────┘ └──────────────┘ └──────────────────┘    │
│                                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ User        │ │ Analytics    │ │ Notification     │    │
│  │ Service     │ │ Service      │ │ Service          │    │
│  │ (用户/家长)  │ │ (数据分析)    │ │ (推送/报告)       │    │
│  └─────────────┘ └──────────────┘ └──────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                       数据层                                  │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐   │
│  │PostgreSQL│ │  Redis   │ │ ChromaDB │ │   S3/OSS   │   │
│  │(关系数据) │ │(缓存/会话)│ │(向量检索) │ │ (文件/音频) │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LLM Provider Layer                                  │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │ OpenAI     │ │ 本地模型    │ │ ASR/TTS    │       │   │
│  │  │ / Claude   │ │ (Ollama)   │ │ (Whisper/  │       │   │
│  │  │ (强模型)    │ │ (快模型)    │ │  Azure)    │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 技术选型

| 层级 | 组件 | 选型 | 理由 |
|------|------|------|------|
| **前端** | 跨平台框架 | React Native (Expo) | 一套代码 iOS/Android/Web |
| **前端** | 数学渲染 | KaTeX + MathJax | LaTeX公式实时渲染 |
| **前端** | 图形交互 | GeoGebra API | 动态几何, 函数图像 |
| **后端** | API框架 | Python FastAPI | 高性能异步, AI生态好 |
| **后端** | Agent编排 | LangGraph | 状态机+人工介入+检查点 |
| **后端** | 任务队列 | Celery + Redis | 异步任务(评分, TTS生成) |
| **数据库** | 主库 | PostgreSQL + pgvector | 关系数据 + 向量检索 |
| **数据库** | 缓存 | Redis Stack | 会话状态 + 向量索引 + 发布订阅 |
| **数据库** | 向量库 | ChromaDB (原型) → Qdrant (生产) | RAG混合检索 |
| **AI** | 强模型 | GPT-4o / Claude | 解题, 课程生成, 深度对话 |
| **AI** | 快模型 | GPT-4o-mini / 本地Llama | 意图分类, 简单批改, 分类 |
| **AI** | ASR | Faster-Whisper | 语音识别, 发音评分 |
| **AI** | TTS | Azure TTS / Edge TTS | 听力材料, 口语考试音频 |
| **存储** | 文件 | S3兼容 (阿里OSS/Cloudflare R2) | 音频文件, 图片, PDF |
| **部署** | 容器 | Docker + Docker Compose | 开发环境一致 |
| **部署** | 生产 | 可选: Vercel(前端) + 云服务器(后端) | 按需选择 |

### 4.3 双模型路由策略

```
用户消息 → Router Agent (快模型, ~50ms)
              │
              ├── 简单意图 → 快模型处理
              │   "下一题" / "再听一遍" / "给我提示"
              │
              ├── 教学意图 → 强模型处理
              │   "为什么这步要因式分解？" / "帮我理解同余"
              │
              └── 复杂意图 → 多Agent协作
                  "这题我不懂" → 诊断+教学+出题
```

---

## 5. 数据模型设计

### 5.1 核心实体关系

```
User 1──N StudentProfile
User 1──N ParentLink
StudentProfile 1──N LearningSession
StudentProfile 1──N KnowledgeState (per knowledge_point)
StudentProfile 1──N SpacedRepetitionCard
StudentProfile 1──N WeaknessRecord

KnowledgePoint 1──N KnowledgePoint (prerequisites, self-referencing)
KnowledgePoint 1──N Problem
KnowledgePoint 1──N Lesson
KnowledgePoint 1──N KnowledgeState

Lesson 1──N LessonStep
Lesson 1──N KnowledgePoint
Course 1──N Unit 1──N Lesson

Problem 1──N ProblemSolution
Problem 1──N KnowledgePoint (tags)
Problem 1──N StudentAttempt

LearningSession 1──N Message
LearningSession 1──N StudentAttempt
```

### 5.2 关键数据表Schema

#### 用户与学生画像

```sql
-- 用户表
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE,
    phone       VARCHAR(20) UNIQUE,
    name        VARCHAR(100) NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('student', 'parent', 'admin')),
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 学生画像
CREATE TABLE student_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES users(id),
    grade_level         SMALLINT,            -- 年级
    target_exam         VARCHAR(20),          -- 'AMC8', 'AMC10', 'AMC12', 'KET'
    target_date         DATE,                 -- 目标考试日期
    daily_goal_minutes  SMALLINT DEFAULT 20,  -- 每日学习目标(分钟)
    timezone            VARCHAR(50) DEFAULT 'Asia/Shanghai',
    preferred_lang      VARCHAR(10) DEFAULT 'zh-CN',

    -- 诊断结果
    diagnostic_done     BOOLEAN DEFAULT FALSE,
    diagnostic_result   JSONB,                -- 各领域初始分数

    -- 游戏化
    xp_total            INTEGER DEFAULT 0,
    streak_days         INTEGER DEFAULT 0,
    longest_streak      INTEGER DEFAULT 0,
    last_active_date    DATE,

    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 家长关联
CREATE TABLE parent_links (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id   UUID REFERENCES users(id),
    student_id  UUID REFERENCES users(id),
    relation    VARCHAR(20),  -- 'father', 'mother', 'guardian'
    notify_settings JSONB,    -- 通知偏好
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(parent_id, student_id)
);
```

#### 知识图谱

```sql
-- 知识点
CREATE TABLE knowledge_points (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(50) UNIQUE NOT NULL,  -- 'AMC-ALG-01', 'KET-VOC-DAILY'
    subject         VARCHAR(20) NOT NULL,           -- 'amc_math', 'ket_english'
    name            VARCHAR(200) NOT NULL,
    name_en         VARCHAR(200),
    description     TEXT,
    
    -- 分类
    pillar          VARCHAR(50),      -- 'algebra', 'geometry', 'counting', 'number_theory'
                                            -- 'reading', 'writing', 'listening', 'speaking', 'vocabulary', 'grammar'
    difficulty_level SMALLINT,         -- 1-10 (MathLake对齐)
    amc_level       SMALLINT NOT NULL DEFAULT 8,  -- 8=AMC 8, 10=AMC 10, 12=AMC 12
                                           -- 标识该知识点首次出现在哪个级别
                                           -- AMC 8 学生可跳过 amc_level > 8 的课程
    
    -- 课程关联
    lesson_id       UUID,             -- 对应的课程
    sort_order      SMALLINT,         -- 在课程中的顺序
    
    -- 元数据
    estimated_minutes SMALLINT,        -- 预计学习时间
    amc_levels      VARCHAR(50),      -- 'AMC8,AMC10' 适用级别
    
    -- 向量嵌入 (用于语义检索)
    embedding       vector(1536),
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 知识点依赖关系
CREATE TABLE knowledge_dependencies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prerequisite_id     UUID REFERENCES knowledge_points(id),  -- 前置知识
    target_id           UUID REFERENCES knowledge_points(id),  -- 目标知识
    dependency_type     VARCHAR(20) DEFAULT 'requires',  -- 'requires', 'related', 'extends'
    strength            SMALLINT DEFAULT 1,  -- 1-5 依赖强度
    UNIQUE(prerequisite_id, target_id)
);
```

#### 题库

```sql
-- 题目
CREATE TABLE problems (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          VARCHAR(100),          -- 'AMC 10 2023', 'MATH Dataset', 'Custom'
    source_year     SMALLINT,
    source_code     VARCHAR(50),           -- 'AMC10A-2023-P15'
    
    subject         VARCHAR(20) NOT NULL,  -- 'amc_math', 'ket_english'
    format          VARCHAR(30) NOT NULL,  -- 'multiple_choice', 'fill_blank', 'free_response',
                                           -- 'essay', 'gap_fill', 'matching', 'speaking'
    
    -- 内容
    question_markdown TEXT NOT NULL,        -- LaTeX / Markdown
    question_data     JSONB,                -- 图片URL, 音频URL, 选项等
    options           JSONB,                -- [{label: 'A', text: '...'}, ...]
    correct_answer    TEXT,
    
    -- 分类
    knowledge_point_ids UUID[] NOT NULL,    -- 关联知识点
    difficulty         SMALLINT,            -- 1-10
    estimated_time_sec SMALLINT,            -- 预计用时(秒)
    
    -- 辅助教学数据
    hints              JSONB,               -- [{level: 1, text: '...'}, ...] 5级提示
    misconceptions     JSONB,               -- [{desc: '...', correction: '...'}, ...]
    step_decomposition JSONB,               -- [{step: 1, desc: '...'}, ...]
    
    -- 统计
    times_attempted    INTEGER DEFAULT 0,
    times_correct      INTEGER DEFAULT 0,
    avg_time_sec       SMALLINT,
    
    -- 向量嵌入
    embedding          vector(1536),
    
    created_at         TIMESTAMPTZ DEFAULT NOW()
);

-- 题目解答 (多种解法)
CREATE TABLE problem_solutions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id  UUID REFERENCES problems(id),
    method_name VARCHAR(100),              -- '因式分解法', '配方法'
    solution_markdown TEXT NOT NULL,        -- LaTeX解答
    key_insight TEXT,                       -- 核心思路
    sort_order  SMALLINT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

#### 学习状态

```sql
-- 知识掌握状态 (每个学生每个知识点一条)
CREATE TABLE knowledge_states (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID REFERENCES users(id),
    knowledge_point_id UUID REFERENCES knowledge_points(id),
    
    mastery         FLOAT DEFAULT 0,       -- 0.0 - 1.0 掌握度
    mastery_level   VARCHAR(20) DEFAULT 'not_started',
                     -- 'not_started', 'attempted', 'familiar', 'proficient', 'mastered'
    
    attempts        INTEGER DEFAULT 0,
    correct         INTEGER DEFAULT 0,
    
    -- FSRS参数
    difficulty      FLOAT DEFAULT 0,        -- FSRS难度 (1-10)
    stability       FLOAT DEFAULT 0,        -- FSRS稳定性 (天)
    retrievability  FLOAT DEFAULT 1.0,      -- 当前可检索性
    next_review     TIMESTAMPTZ,            -- 下次复习时间
    last_review     TIMESTAMPTZ,            -- 上次复习时间
    review_count    INTEGER DEFAULT 0,
    lapse_count     INTEGER DEFAULT 0,      -- 遗忘次数
    
    UNIQUE(student_id, knowledge_point_id)
);

-- 学习会话
CREATE TABLE learning_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      UUID REFERENCES users(id),
    session_type    VARCHAR(30) NOT NULL,
                     -- 'course', 'practice', 'mock_exam', 'review', 'diagnostic'
    subject         VARCHAR(20) NOT NULL,    -- 'amc_math', 'ket_english'
    knowledge_point_id UUID REFERENCES knowledge_points(id),
    
    started_at      TIMESTAMPTZ NOT NULL,
    ended_at        TIMESTAMPTZ,
    duration_sec    INTEGER,
    
    -- 结果
    problems_total  SMALLINT,
    problems_correct SMALLINT,
    score_pct       FLOAT,
    xp_earned       INTEGER DEFAULT 0,
    
    -- LangGraph checkpoint (用于恢复会话)
    checkpoint_id   VARCHAR(100),
    
    -- 摘要
    summary         TEXT,                   -- AI生成的会话摘要
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 学生答题记录
CREATE TABLE student_attempts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES learning_sessions(id),
    student_id      UUID REFERENCES users(id),
    problem_id      UUID REFERENCES problems(id),
    
    answer          TEXT,                   -- 学生答案
    is_correct      BOOLEAN,
    time_spent_sec  INTEGER,
    
    -- AI评估详情
    hint_level_used SMALLINT DEFAULT 0,     -- 使用了几级提示
    error_type      VARCHAR(50),            -- 'arithmetic', 'conceptual', 'procedural', 'misconception'
    ai_feedback     TEXT,                   -- AI反馈
    
    attempt_number  SMALLINT DEFAULT 1,     -- 第几次尝试
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 对话消息
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES learning_sessions(id),
    role            VARCHAR(20) NOT NULL,   -- 'system', 'assistant', 'user', 'tool'
    content         TEXT NOT NULL,
    metadata        JSONB,                  -- 工具调用, 图片, 音频等
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

#### 课程结构

```sql
-- 课程
CREATE TABLE courses (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(50) UNIQUE,          -- 'AMC8-PREP', 'KET-FULL'
    subject     VARCHAR(20) NOT NULL,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    target_exam VARCHAR(50),
    estimated_hours SMALLINT,
    is_published BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 单元
CREATE TABLE units (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id   UUID REFERENCES courses(id),
    code        VARCHAR(50),
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    sort_order  SMALLINT NOT NULL,
    required_mastery FLOAT DEFAULT 0.8,      -- 解锁下一单元需要的掌握度
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 课程
CREATE TABLE lessons (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id     UUID REFERENCES units(id),
    knowledge_point_id UUID REFERENCES knowledge_points(id),
    code        VARCHAR(50),
    title       VARCHAR(200) NOT NULL,
    lesson_type VARCHAR(30),                  -- 'concept', 'practice', 'assessment', 'review'
    
    -- 课程内容 (JSON结构, 由AI生成或人工编辑)
    content     JSONB NOT NULL,
    /*
    content结构示例:
    {
      "introduction": { "text": "...", "visual": "geogebra://..." },
      "exploration": [{ "prompt": "...", "expected_discovery": "..." }],
      "explanation": { "text": "...", "formula": "a²+b²=c²", "key_insight": "..." },
      "guided_practice": [{ "problem_id": "...", "hint_levels": [...] }],
      "assessment": [{ "problem_id": "..." }],
      "summary": { "key_points": [...], "next_lesson": "..." }
    }
    */
    
    estimated_minutes SMALLINT,
    sort_order  SMALLINT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.3 向量检索配置

```sql
-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建向量索引 (用于RAG检索)
CREATE INDEX ON problems USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON knowledge_points USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 6. 学生端UI/UX设计

### 6.1 信息架构

```
底部导航栏 (4个主Tab):
┌──────┬──────┬──────┬──────┐
│  🏠  │  📚  │  🎯  │  👤  │
│ 首页 │ 课程 │ 练习 │ 我的 │
└──────┴──────┴──────┴──────┘
```

### 6.2 首页 (Home)

参考 Duolingo 的旅程地图 + 可汗学院的每日任务:

```
┌─────────────────────────────────────┐
│ ☀️ 早上好, 小明!        🔥47天     │ ← 状态栏: 连续天数
│ 目标: AMC 8 (2026年11月)          │ ← 显示当前目标级别
│ [切换目标: AMC 10 →]              │ ← 可切换考试级别
├─────────────────────────────────────┤
│                                     │
│ 📋 今日任务                         │
│ ┌─────────────────────────────────┐│
│ │ ✅ 复习: 因式分解 (间隔重复)    ││ ← FSRS到期复习
│ │ ✅ 课程: 相似三角形 (新知识)    ││ ← 课程模式任务
│ │ ○  练习: AMC 10 几何 x5题      ││ ← 刷题模式任务
│ │ ○  词汇: KET 日常用语 (15词)   ││ ← 英语词汇复习
│ └─────────────────────────────────┘│
│                                     │
│ 📊 本周进度                         │
│ ┌─────────────────────────────────┐│
│ │ 代数   ████████░░ 80%  熟练     ││
│ │ 几何   ██████░░░░ 60%  入门     ││ ← 各支柱掌握度
│ │ 计数   ████░░░░░░ 40%  入门     ││
│ │ 数论   ██░░░░░░░░ 20%  未开始   ││
│ └─────────────────────────────────┘│
│                                     │
│ 🏆 成就                             │
│ ┌──────┐ ┌──────┐ ┌──────┐        │
│ │🌟    │ │📐    │ │🔥    │        │
│ │首次  │ │几何  │ │连续  │        │ ← Duolingo式成就
│ │满分  │ │达人  │ │47天  │        │
│ └──────┘ └──────┘ └──────┘        │
│                                     │
│ 📅 学习日历                         │
│ 日 一 二 三 四 五 六               │
│ ✓  ✓  ✓  ✓  ✓  ·  ·              │ ← 本周打卡记录
└─────────────────────────────────────┘
```

### 6.3 课程页面 (Course)

线性路径 + 检查点门控 (Duolingo风格):

```
┌─────────────────────────────────────┐
│ [← 返回]  AMC 8 几何  🔑 80%      │ ← 标题显示当前目标级别
│ [切换到 AMC 10 ▼]                  │ ← 可切换目标级别
├─────────────────────────────────────┤
│                                     │
│    ✅ B1 角度与平行线      🟢      │
│    │                                │
│    ✅ B2 三角形基础         🟢      │
│    │                                │
│    ✅ B3 勾股定理 ⭐⭐⭐  🟢       │
│    │                                │
│    🔵 B4 组合图形面积      🟢      │ ← 当前课程 (AMC 8范围)
│    │                                │
│    🔒 B5 四边形与多边形    🟢      │
│    │                                │
│    🔑 B 阶段测试 (AMC 8)           │ ← AMC 8 阶段测试门控
│    │                                │
│    ── ── ── AMC 10 进阶 ── ── ──  │ ← 分隔线: AMC 10内容
│    │  (已折叠, 点击展开)    ▼      │
│    │                                │
│    ┌─ 🟡 AMC 10 进阶内容 ──────┐  │ ← 折叠区域 (AMC 8时默认收起)
│    │  🔒 B4 相似三角形         │  │
│    │  🔒 B6 圆                │  │
│    │  🔒 B8 坐标几何           │  │
│    │  🔒 B9 立体几何           │  │
│    │  🔑 B 阶段测试 (AMC 10)  │  │
│    └────────────────────────────┘  │
│                                     │
│  [课程路径可视化 - 类似Duolingo     │
│   的竖向滚动路径]                   │
└─────────────────────────────────────┘
```

#### AMC 10 进阶内容展开后的界面

```
┌─────────────────────────────────────┐
│ [← 返回]  AMC 8 几何 → AMC 10进阶  │
│ 当前目标: AMC 8  [切换目标级别]     │
├─────────────────────────────────────┤
│                                     │
│  ── ── AMC 8 基础 (已完成) ── ──  │
│    ✅ B1-B5, B7  🔑 测试通过       │
│                                     │
│  ── ── AMC 10 进阶 ── ── ── ──   │
│    │                                │
│    ⚠️ B4 相似三角形      🟡       │ ← "需要先完成勾股定理(✅已满足)"
│    │                                │
│    🔒 B6 圆               🟡       │ ← "需要先完成相似三角形"
│    │                                │
│    🔒 B8 坐标几何          🟡       │
│    │                                │
│    🔒 B9 立体几何          🟡       │
│    │                                │
│    🔑 B 阶段测试 (AMC 10)          │
│                                     │
│  💡 提示: 这些是AMC 10额外要求。   │
│  如果你的目标是AMC 8, 可以暂时跳过。│
│  学有余力的话, 提前学习会更有优势!  │
│                                     │
│  [收起 AMC 10 内容]                │
└─────────────────────────────────────┘
```

#### 目标级别切换交互

```
┌─────────────────────────────────────┐
│        选择目标考试级别              │
├─────────────────────────────────────┤
│                                     │
│  ◉ AMC 8  (当前)                   │
│    显示: 14节基础课                  │
│    预计: 3-4个月                     │
│                                     │
│  ○ AMC 10                           │
│    显示: 基础课 + 16节进阶课         │
│    预计: 8-12个月                    │
│    新增: 二次方程, 相似三角形,       │
│          组合, 同余, 坐标几何...     │
│                                     │
│  ○ AMC 12                           │
│    显示: 全部课程                    │
│    预计: 12-18个月                   │
│    新增: 三角函数, 对数, 复数...     │
│                                     │
│  [确认]                             │
└─────────────────────────────────────┘
```

### 6.4 课程进行中的界面

参考 Brilliant.org 的交互式学习:

```
┌─────────────────────────────────────┐
│ [←]  B4 相似三角形    ████░░ 65%  │ ← 课程进度条
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │   [GeoGebra交互区域]          │  │ ← 几何可视化
│  │   可拖拽的三角形              │  │
│  │   实时显示边长比例            │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  🧑‍🏫 AI老师:                       │
│  "看这两个三角形——如果把小的     │
│   放大2倍, 它和大的重合吗？       │
│   试试拖动滑块。"                  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ 👦 你的回答:                   │  │
│  │ [输入框 / 选项 / 拖拽区域]     │  │
│  │                               │  │
│  │ [💡提示]  [📝笔记]  [📸拍照]  │  │ ← 工具栏
│  └───────────────────────────────┘  │
│                                     │
│  [继续 →]                          │
└─────────────────────────────────────┘
```

### 6.5 刷题界面

```
┌─────────────────────────────────────┐
│ [←] AMC 10 练习    ⏱ 12:34    3/5 │ ← 计时器 + 进度
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │  题目 #3                      │  │
│  │                               │  │
│  │  In triangle ABC, AB = 5,     │  │ ← LaTeX渲染的题目
│  │  BC = 12, and AC = 13.       │  │
│  │  What is the area of the      │  │
│  │  circumscribed circle?        │  │
│  │                               │  │
│  │  A) 169π/4                    │  │
│  │  B) 65π/4                     │  │
│  │  C) 13π                       │  │
│  │  D) 169π/10                   │  │
│  │  E) 65π/2                     │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ 🧑‍🏫 AI引导对话                  │  │ ← 对话区
│  │ "先别急着算——这个三角形       │  │
│  │  的三边有什么特殊之处？"       │  │
│  │                               │  │
│  │ 👦 "5²+12²=169=13²,是直角三角形"│  │
│  │                               │  │
│  │ 🧑‍🏫 "很好！那直角三角形的       │  │
│  │  外接圆半径和斜边有什么关系？" │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ [📝草稿板]  [💡提示 L0]       │  │ ← 工具栏
│  │ 我觉得答案是: [B]  [提交]     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 6.6 KET写作界面

```
┌─────────────────────────────────────┐
│ [←] KET 写作 Part 6    📝 25+词    │
├─────────────────────────────────────┤
│                                     │
│  题目:                              │
│  你收到了英国笔友Sam的邮件。       │
│  请写一封回复邮件, 包含以下3点:     │
│                                     │
│  ✅ 1. 告诉Sam你的年龄             │ ← 3个必须包含的要点
│  ✅ 2. 描述你最喜欢的科目          │
│  ✅ 3. 你周末通常做什么            │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Hi Sam,                       │  │
│  │                               │  │ ← 写作区
│  │ I'm 13 years old. My favorite │  │
│  │ subject is math because it    │  │
│  │ is interesting. On weekend    │  │
│  │ I usually play basketball     │  │
│  │ with my friends.              │  │
│  │                               │  │
│  │ Best wishes,                  │  │
│  │ Li Ming                       │  │
│  └───────────────────────────────┘  │
│                                     │
│  字数: 32词  ✅ 达标 (需25+词)     │ ← 实时字数
│  要点: ✅ 1 ✅ 2 ✅ 3              │ ← 要点检查
│                                     │
│  [提交评分]                         │
└─────────────────────────────────────┘
```

### 6.7 学习仪表盘 (我的页面)

```
┌─────────────────────────────────────┐
│ 👤 小明  |  AMC 10  |  🔥47天     │
├─────────────────────────────────────┤
│                                     │
│  📊 知识雷达图                      │
│  ┌───────────────────────────────┐  │
│  │          代数 80%              │  │
│  │       /        \              │  │ ← AMC四支柱雷达图
│  │   数论 20%   几何 60%          │  │
│  │       \        /              │  │
│  │          计数 40%              │  │
│  └───────────────────────────────┘  │
│                                     │
│  📈 近30天学习趋势                  │
│  ┌───────────────────────────────┐  │
│  │     ▁▂▃▄▅▆▇█▇▆▇████████     │  │ ← 学习时长+正确率
│  │     平均: 35分钟/天            │  │
│  └───────────────────────────────┘  │
│                                     │
│  🏅 成就墙                          │
│  ┌─────┐┌─────┐┌─────┐┌─────┐    │
│  │ 🔥  ││ 📐  ││ 💯  ││ 🎯  │    │
│  │47天 ││几何5││满分3││百题 │    │
│  │连续 ││节课 ││次   ││完成 │    │
│  └─────┘└─────┘└─────┘└─────┘    │
│                                     │
│  ⚙️ 设置                            │
│  每日目标: [20分钟 ▼]               │
│  提醒时间: [19:00]                  │
│  主题: [浅色 ▼]                     │
│  [家长端入口 →]                     │
└─────────────────────────────────────┘
```

### 6.8 无障碍设计

| 要求 | 实现 |
|------|------|
| 字体 | 默认无衬线字体 + 可选OpenDyslexic |
| 字号 | 最小16px, 支持200%缩放 |
| 对比度 | 最低4.5:1, 关键元素7:1 |
| 触摸区域 | 最小44×44px |
| 屏幕阅读器 | 所有元素有accessibility label |
| 色盲友好 | 不依赖颜色传达信息, 使用图标+文字 |

---

## 7. AI Prompt与教学策略

### 7.1 Prompt架构

```
┌─────────────────────────────────────────────┐
│              System Prompt                   │
│  ┌─────────────────────────────────────┐    │
│  │  角色定义 + 核心规则                 │    │
│  │  "你是一位AMC数学竞赛私人家教..."    │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  学生画像注入                        │    │
│  │  [当前掌握度, 弱项, 学习风格, ZPD]  │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  当前上下文                          │    │
│  │  [题目/课程内容/对话历史/提示级别]   │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  检索增强 (RAG)                      │    │
│  │  [相关知识点, 类似题目, 教学素材]   │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  输出格式约束                        │    │
│  │  [JSON schema / Markdown格式要求]   │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 7.2 数学课程模式 Prompt 模板

```
你是一位AMC数学竞赛私人家教, 正在教授"{{knowledge_point_name}}"这节课。

## 你的学生
- 姓名: {{student_name}}
- 年级: {{grade_level}}
- 目标: {{target_exam}}
- 当前掌握度: {{mastery_level}}
- 已掌握的知识点: {{mastered_kps}}
- 薄弱领域: {{weak_areas}}
- 学习风格偏好: {{learning_style}}

## 课程内容
{{lesson_content_json}}

## 教学规则
1. 先让学生动手探索, 再归纳概念 (Brilliant.org方法)
2. 使用GeoGebra/图形辅助理解
3. 每讲完一个概念, 立即给一道练习题验证
4. 学生答错时不直接纠正, 用反问引导
5. 适当联系AMC考试: "这个知识点在AMC 10中约出现X次"
6. 用中文教学, 数学术语保留英文

## 当前阶段
正在执行: {{current_step}} (introduction / exploration / explanation / practice / assessment)

## 输出格式
根据当前阶段, 输出相应的内容:
- introduction: 一个吸引人的引入问题或情境
- exploration: 一个交互式探索任务 (描述GeoGebra操作)
- explanation: 概念讲解 + 公式 + 关键洞察
- practice: 一道练习题 (含5级提示)
- assessment: 一道测验题 (含正确答案, 不直接展示)

保持对话自然, 每次回复不超过3-4个短段落。
```

### 7.3 数学刷题模式苏格拉底 Prompt

```
你是一位AMC数学竞赛私人家教, 正在通过苏格拉底式对话引导学生解题。

## 学生信息
{{student_profile_summary}}

## 当前题目
{{problem_markdown}}

## 正确答案
{{correct_answer}}

## 参考解法
{{reference_solutions}}

## 教学策略
当前提示级别: Level {{hint_level}} (0-4)

### 苏格拉底规则 (绝对不可违反)
1. **永远不直接给出答案**
2. **永远不直接给出完整的解题步骤**
3. 只通过提问引导学生思考
4. 每次只问一个问题
5. 学生说对了要肯定, 但追问"为什么"

### 提示级别指南
- L0 (元认知): "你觉得第一步应该做什么？"
- L1 (策略): 引导识别题目类型/选择策略
- L2 (概念): 提及关键知识点/定理
- L3 (操作): 给出具体操作方向 (不说完整步骤)
- L4 (示例): 展示一道更简单的同类题解法

### 错误处理
- 计算错误: 引导自行验证 ("我们验证一下...")
- 方法错误: 用反问指出方法不适用
- 概念误解: 用反例制造认知冲突

### 特殊情况
- 如果学生完全卡住超过4轮 → 可以给L3提示
- 如果学生请求帮助 → 提升一级提示
- 如果学生答对 → 要求解释为什么, 然后总结

## 输出格式
你的回复 (1-3个短段落, 自然对话):
```

### 7.4 KET写作评分 Prompt

```
你是一位KET (Cambridge English: Key) 考试评分专家。

## 评分标准 (Cambridge官方)
使用Content / Organisation / Language三个维度, 每个维度0-5分:

### Content (内容)
- Band 5: 3个要点全部清晰传达
- Band 3: 3个要点都尝试, 部分需推断
- Band 1: 只传达1个要点

### Organisation (组织)
- Band 5: 结构良好, 连贯, 使用连接词
- Band 3: 基本结构, 部分不连贯
- Band 1: 缺乏结构

### Language (语言)
- Band 5: 只有轻微错误, 不影响理解
- Band 3: 有一些错误但基本可理解
- Band 1: 错误严重影响理解

## 题目要求
{{task_description}}
必须包含的3个要点: {{required_points}}

## 学生作文
{{student_essay}}

## 输出格式 (JSON)
{
  "content_score": 0-5,
  "organisation_score": 0-5,
  "language_score": 0-5,
  "total_band": 0-5,
  "word_count": N,
  "points_covered": [true/false, true/false, true/false],
  "feedback": {
    "strengths": ["...", "..."],
    "improvements": ["...", "..."],
    "specific_errors": [
      {
        "original": "I want go cinema",
        "correction": "I want to go to the cinema",
        "explanation": "want后面需要to, go后面需要to+地点"
      }
    ]
  },
  "sample_improved_version": "..."
}

## 重要
- KET是A2级别, 不要用过高标准
- 关注"能否有效沟通"而非语法完美
- 错误反馈要具体, 指出位置和原因
```

### 7.5 错误诊断 Prompt

```
你是一位数学学习诊断专家。根据学生的答题记录, 诊断错误类型和根因。

## 学生答题记录
题目: {{problem}}
学生答案: {{student_answer}}
正确答案: {{correct_answer}}
解题过程(如有): {{student_work}}

## 诊断维度
请判断:
1. **错误类型**: arithmetic(计算) / conceptual(概念) / procedural(方法) / misconception(误解) / careless(粗心)
2. **错误根因**: 具体是哪个知识点理解有误
3. **建议干预**: 回到课程复习 / 同类型题练习 / 苏格拉底式引导
4. **相关前置知识**: 是否有更基础的知识点未掌握

## 输出格式 (JSON)
{
  "error_type": "...",
  "root_cause": "...",
  "affected_knowledge_points": ["kp_id_1", "kp_id_2"],
  "intervention": "course_review | targeted_practice | socratic_dialogue",
  "severity": "low | medium | high",
  "explanation_for_student": "用友善的语气向学生解释哪里出了问题",
  "follow_up_problem_ids": ["建议练习的题目ID"]
}
```

---

## 8. 评估与知识追踪系统

### 8.1 掌握度计算模型

采用改良版FSRS (Free Spaced Repetition Scheduler) + Bayesian Knowledge Tracing混合方案:

```
每个知识点维护以下状态:
├── mastery: 0.0-1.0 (综合掌握度)
├── difficulty: 1.0-10.0 (FSRS难度)
├── stability: N天 (记忆稳定性)
├── retrievability: 0.0-1.0 (当前可检索性)
└── mastery_level: 枚举(5级)
```

**掌握度等级定义**:

| 等级 | mastery范围 | 含义 | 解锁权限 |
|------|------------|------|---------|
| not_started | 0.0-0.1 | 未开始 | 无 |
| attempted | 0.1-0.3 | 尝试过 | 基础练习题 |
| familiar | 0.3-0.6 | 基本理解 | AMC简单题 |
| proficient | 0.6-0.85 | 熟练掌握 | AMC中等题 |
| mastered | 0.85-1.0 | 精通 | AMC难题 + 间隔复习 |

**掌握度更新算法**:

```python
def update_mastery(state: KnowledgeState, attempt: StudentAttempt):
    """
    基于答题结果更新知识点掌握度
    """
    # 1. 基础更新 (移动平均)
    alpha = 0.3  # 学习速率
    if attempt.is_correct:
        state.mastery = state.mastery + alpha * (1.0 - state.mastery)
    else:
        state.mastery = state.mastery * (1.0 - alpha * 0.5)
    
    # 2. 难度修正 (难题得分加成)
    difficulty_bonus = max(0, (attempt.problem.difficulty - 5) * 0.02)
    if attempt.is_correct:
        state.mastery += difficulty_bonus
    
    # 3. 提示使用惩罚 (用了提示说明不完全掌握)
    hint_penalty = attempt.hint_level_used * 0.05
    state.mastery -= hint_penalty
    
    # 4. 时间衰减 (遗忘曲线)
    days_since_last = (now() - state.last_review).days
    if days_since_last > 0:
        # FSRS遗忘公式: R = e^(-days/stability)
        retrievability = math.exp(-days_since_last / state.stability)
        state.mastery *= retrievability
    
    # 5. 更新FSRS参数
    if attempt.is_correct:
        state.stability *= (1.0 + 0.5 * (10.0 - state.difficulty) / 10.0)
    else:
        state.stability *= 0.5
        state.lapse_count += 1
    
    state.difficulty = update_fsrs_difficulty(state.difficulty, attempt)
    state.last_review = now()
    state.review_count += 1
    
    # 6. 更新等级
    state.mastery_level = classify_mastery(state.mastery)
    state.next_review = calculate_next_review(state)
```

### 8.2 自适应出题策略

```
┌──────────────────────────────────────────────────────────────┐
│                     出题决策引擎                              │
│                                                              │
│  输入: 学生画像 + 当前模式 + 会话历史                        │
│                                                              │
│  Step 1: 确定目标知识点                                      │
│  ├── 课程模式: 按课程顺序                                    │
│  ├── 刷题模式: 选掌握度最低的知识点 (ZPD策略)                │
│  ├── 复习模式: FSRS到期的知识点                              │
│  └── 模拟考试: 按AMC分布比例选题                             │
│                                                              │
│  Step 2: 确定难度                                            │
│  ├── 新学知识点: difficulty = current_mastery * 10           │
│  ├── 熟悉知识点: difficulty = current_mastery * 10 + 1      │
│  └── 模拟考试: 按AMC分布 (简单30% / 中等40% / 难30%)       │
│                                                              │
│  Step 3: 从题库检索                                          │
│  ├── 条件: knowledge_point = target AND difficulty ± 1      │
│  ├── 过滤: 排除最近做过的题 (7天内)                         │
│  ├── 过滤: 排除 amc_level > student.target_exam 的题目      │ ← 按目标级别过滤
│  ├── 排序: 按学生错误率相似度排序                            │
│  └── 去重: 同一会话不重复相似题                              │
│                                                              │
│  Step 4: 备选方案                                            │
│  如果目标知识点题不足 → 降级到前置知识点                     │
│  如果所有题都做过 → 生成新题 (AI出题)                        │
│                                                              │
│  输出: problem_id + 预期完成时间 + 关联提示                  │
└──────────────────────────────────────────────────────────────┘
```

### 8.3 学习报告生成

**每日报告** (给学生):
```
📊 今日学习报告 — 2026年5月27日

⏱ 学习时长: 42分钟
📝 完成题目: 12题 (正确9题, 正确率75%)
📚 课程进度: B4 相似三角形 (65%)
🔥 连续学习: 47天

💪 今日亮点:
- 相似三角形判定: 3/3全对!
- 勾股定理复习: 正确率从60%提升到90%

📝 需要加强:
- 圆的面积计算: 1/3正确, 建议复习B6

📅 明日计划:
- 完成 B4 相似三角形
- 复习 因式分解 (间隔重复到期)
- AMC 10 模拟练习 x5题
```

**每周报告** (给家长):
```
📊 小明本周学习报告 — 5/20 ~ 5/26

⏱ 本周学习: 3小时15分钟 (日均28分钟)
🎯 目标完成率: 85%

📈 进步概览:
| 科目 | 上周 | 本周 | 变化 |
|------|------|------|------|
| 代数 | 75%  | 82%  | ↑7%  |
| 几何 | 45%  | 58%  | ↑13% | ← 进步最大
| 计数 | 35%  | 38%  | ↑3%  |
| 数论 | 15%  | 18%  | ↑3%  |

🏆 本周成就:
- 几何单元从"入门"升级到"熟悉"
- 连续学习47天

⚠️ 关注点:
- 计数与概率进度较慢, 建议增加练习
- 周三未完成每日目标

💡 AI建议:
"小明在几何方面进步显著, 建议下周重点突破计数模块。"
```

---

## 9. 多Agent协作架构

### 9.1 Agent分工

```
┌──────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                     │
│                    (总协调, 路由分发)                      │
└──────┬──────────┬──────────┬──────────┬────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌────────────┐┌────────────┐┌────────────┐┌────────────┐
│ Router     ││ Tutor      ││ Assessor   ││ Curriculum │
│ Agent      ││ Agent      ││ Agent      ││ Agent      │
│            ││            ││            ││            │
│ 意图分类    ││ 教学对话    ││ 评估评分    ││ 课程调度    │
│ 模式切换    ││ 苏格拉底式  ││ 错误诊断    ││ 知识追踪    │
│ 快模型      ││ 强模型      ││ 强模型      ││ 快模型+规则 │
└────────────┘└────────────┘└────────────┘└────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────────────────────────────────────────────────────┐
│                   Tool Layer                             │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │RAG     │ │Code    │ │GeoGebra│ │TTS/ASR │           │
│  │检索    │ │Exec    │ │绘图    │ │语音    │            │
│  └────────┘ └────────┘ └────────┘ └────────┘           │
│  ┌────────┐ ┌────────┐ ┌────────┐                      │
│  │DB查询  │ │计算器  │ │搜索    │                      │
│  └────────┘ └────────┘ └────────┘                      │
└──────────────────────────────────────────────────────────┘
```

### 9.2 各Agent职责

| Agent | 模型 | 职责 | 工具 |
|-------|------|------|------|
| **Orchestrator** | 快模型 | 接收消息, 路由到合适Agent, 管理会话状态 | DB查询, 会话管理 |
| **Router** | 快模型 | 分类意图: 课程/刷题/提问/闲聊/管理 | 意图分类器 |
| **Tutor** | 强模型 | 核心教学对话, 苏格拉底式引导, 概念讲解 | RAG, GeoGebra, 代码执行, 计算器 |
| **Assessor** | 强模型 | 评分(数学/写作/口语), 错误诊断, 知识状态更新 | 代码执行, 评分rubric |
| **Curriculum** | 规则+快模型 | 课程调度, 出题推荐, 间隔重复安排, 进度追踪 | DB查询, FSRS算法 |

### 9.3 典型请求流程

**场景: 学生说"这道题不会"**

```
学生消息 → Orchestrator
    │
    ├── Router分类: "刷题求助" → 路由到Tutor Agent
    │
    ├── Curriculum查询:
    │   - 当前题目: AMC10A-2023-P15
    │   - 学生掌握度: 几何0.45, 圆0.2
    │   - 提示级别: L0 (首次请求)
    │
    ├── Tutor执行:
    │   - 加载题目+参考解法 (RAG)
    │   - 生成L0级苏格拉底提问
    │   - "这个三角形的三边有什么特殊关系？"
    │
    └── 返回给学生
```

**场景: 学生提交写作作业**

```
学生提交作文 → Orchestrator
    │
    ├── Router分类: "KET写作提交" → 路由到Assessor Agent
    │
    ├── Assessor执行:
    │   - Content检查 (3个要点覆盖)
    │   - Organisation评估
    │   - Language评估 (语法/拼写检查)
    │   - 生成Band评分 + 具体反馈
    │
    ├── Curriculum更新:
    │   - 更新写作掌握度
    │   - 如果分数<3 → 安排写作复习课
    │   - 如果分数≥3 → 解锁下一个写作类型
    │
    └── 返回评分+反馈给学生
```

---

## 10. 家长端与报告系统

### 10.1 家长功能

```
┌─────────────────────────────────────┐
│ 👨‍👩‍👦 家长中心                        │
├─────────────────────────────────────┤
│                                     │
│ 📊 学习概览                         │
│ ┌─────────────────────────────────┐│
│ │ 小明 | AMC 10 | 🔥47天          ││
│ │ 本周: 3h15m | 日均28min         ││
│ │ 目标完成率: 85%                  ││
│ └─────────────────────────────────┘│
│                                     │
│ 📈 知识掌握趋势 (最近4周)           │
│ ┌─────────────────────────────────┐│
│ │ 代数   ▁▂▃▅▆▇▇▇ (→82%)        ││
│ │ 几何   ▁▁▂▃▅▆▇▇ (→58%)        ││
│ │ 计数   ▁▂▂▃▃▃▄▄ (→38%)        ││
│ │ 数论   ▁▁▁▂▂▂▃▃ (→18%)        ││
│ └─────────────────────────────────┘│
│                                     │
│ 🔔 通知                             │
│ • [5/27] 几何从"入门"升到"熟悉"    │
│ • [5/25] 连续学习45天成就解锁       │
│ • [5/23] ⚠️ 计数模块进度偏慢       │ ← AI生成的关注提醒
│ • [5/22] 模拟考试得分: 82/150     │
│                                     │
│ 📅 周报告 (每周一推送)              │
│ [查看最新周报 →]                    │
│                                     │
│ ⚙️ 设置                             │
│ 通知偏好: [学习提醒/成就/异常]      │
│ [调整学习计划] [联系AI家教]         │
└─────────────────────────────────────┘
```

### 10.2 通知策略

| 事件类型 | 推送方式 | 时机 |
|---------|---------|------|
| 知识点升级 | APP推送 | 实时 |
| 成就解锁 | APP推送 | 实时 |
| 每日目标完成 | 无 | (避免打扰) |
| 连续学习中止 | APP推送 | 当日23:00未学习 |
| 知识点退步 | APP推送+微信 | mastery下降超过20% |
| 周报 | 微信/邮件 | 每周一 9:00 |
| 月度分析报告 | 邮件 | 每月1日 |

### 10.3 隐私保护

- 家长看到的是**聚合数据**和**AI分析**, 不是原始对话内容
- 学生的具体答题内容/对话不对家长可见
- 家长可以设定每日学习时长上限
- 学生可以选择"私密模式"(不向家长推送)

---

## 附录A: AMC知识点频率参考

### AMC 8 十年分析 (2016-2025)

| 排名 | 主题 | 题数 | 占比 | 难题(Q21-25) |
|------|------|------|------|-------------|
| 1 | 几何 | 50 | 22% | 36% |
| 2 | 应用题 | 41 | 18% | 低 |
| 3 | 计数 | 35 | 16% | 29% |
| 4 | 数论 | 29 | 13% | 18% (上升) |
| 5 | 代数 | 30 | 13% | 16% |

### AMC 10/12 分布

| 模块 | AMC 10 | AMC 12 |
|------|--------|--------|
| 代数 | 28-36% | 32-40% |
| 几何 | 24-32% | 20-28% |
| 计数 | 16-24% | 16-24% |
| 数论 | 12-20% | 12-16% |
| 三角 | 0% | 8-16% |
| 对数/复数 | 0% | 8-16% |

## 附录B: KET评分标准速查

### 写作Band评分 (Content/Organisation/Language 各0-5)

| Band | 总结 |
|------|------|
| 5 | 完美传达, 轻微错误 |
| 4 | 全部传达, 有些不阻碍理解的错误 |
| 3 | 全部尝试, 部分需推断 |
| 2 | 只传达2个要点 |
| 1 | 只传达1个要点 |
| 0 | 未作答或完全不可理解 |

### 口语评分标准 (4维度各0-5)

| 维度 | 评估重点 |
|------|---------|
| Grammar & Vocabulary | 简单句型的控制力, 日常词汇 |
| Pronunciation | 整体可理解度 |
| Interactive Communication | 维持简单交流的能力 |
| Global Achievement | 整体完成度 |

## 附录C: 推荐参考项目

| 项目 | 用途 | 地址 |
|------|------|------|
| DeepTutor | 多Agent架构参考 | github.com/HKUDS/DeepTutor |
| OpenTutor | 课程模式+间隔重复 | github.com/zijinz456/OpenTutor |
| ChatTutor | 可视化白板+AI | github.com/HugeCatLab/ChatTutor |
| MATH Dataset | AMC训练数据 | huggingface.co/datasets/hendrycks/competition_math |
| MathDial | 师生对话数据集 | github.com/eth-nlped/mathdial |
| SocraticMATH | 苏格拉底对话数据集 | github.com/ECNU-ICALK/SocraticMath |
