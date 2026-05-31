# AI私人家教系统 — 完整设计文档

> 覆盖 AMC 数学竞赛 + KET 英语考试 + 语文（作文/古诗词）
> 适配 Boox 10寸墨水屏平板
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
- **语文**（中小学基础）：面向小学4-6年级
  - 作文：记叙文/描写文/想象作文/应用文，300-500字
  - 古诗词赏析：课标必背古诗词75首中的核心篇目

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

> **墨水屏适配**: 所有 UI 设计需同时满足 LCD 和墨水屏（e-ink）两种显示环境。
> 墨水屏模式下：关闭所有动画、使用分页翻页、GeoGebra 降级为静态分步图解。
> 详见 §6.9。

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

参考 Brilliant.org "先动手后理论" + 5E教学循环。**每节课包含丰富的图文动画和语音讲解**。

#### 课程内容元素类型

| 元素 | 用途 | 示例 |
|------|------|------|
| 🎤 **语音讲解** | AI老师口述讲解, 像真人老师说话 | "勾股定理是一个有3000年历史的发现..." |
| 📐 **GeoGebra交互** | 可拖拽的几何图形、函数图像 | 拖动三角形顶点, 实时显示边长变化 |
| 📊 **动画演示** | 概念推导过程的动画 | 面积推导动画: 正方形 → 拆分 → 重组 |
| 🖼️ **插图/图解** | 静态示意图 | 勾股定理的经典正方形面积图 |
| 📝 **公式卡片** | 高亮显示的关键公式 | `a² + b² = c²` 带颜色标注 |
| 🗣️ **语音输入** | 学生可以口述回答 | "我觉得斜边等于5" |
| ✏️ **手写/绘图** | 草稿板, 学生写推导过程 | 在屏幕上写 `3²+4² = 9+16 = 25` |
| 💡 **折叠解释** | 默认隐藏的详细推导 | "点击展开: 勾股定理的面积证明" |

#### 勾股定理课程示例

```
┌──────────────────────────────────────────────────────────┐
│  Lesson: B3 勾股定理                                      │
│  时长: 25min | 前置: ✅三角形基础 ✅面积计算               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ 📖 ENGAGE 引入 (3 min) ──────────────────────────┐  │
│  │                                                    │  │
│  │  🎤 [▶ 播放] AI老师:                               │  │ ← 语音讲解
│  │  "今天我们来学一个有3000年历史的定理。              │  │
│  │   先看这个直角三角形..."                            │  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │                                            │   │  │ ← GeoGebra交互
│  │  │         /|                                  │   │  │    可拖拽顶点
│  │  │       /  |  4                               │   │  │    实时显示边长
│  │  │     /    |                                   │   │  │
│  │  │   /______|                                   │   │  │
│  │  │     3      ?                                 │   │  │
│  │  │                                            │   │  │
│  │  │  [拖动顶点改变三角形形状]                    │   │  │
│  │  └────────────────────────────────────────────┘   │  │
│  │                                                    │  │
│  │  💬 "你能量出斜边多长吗？试试拖动测量工具。"       │  │ ← 文字+语音同步
│  │                                                    │  │
│  │  🗣️ [按住说话] 或 ✏️ [输入答案]                   │  │ ← 支持语音输入
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ 🔢 EXPLORE 探索发现 (5 min) ────────────────────┐  │
│  │                                                    │  │
│  │  🎤 AI老师:                                       │  │
│  │  "好，再试试这个：直角边是5和12的直角三角形？"     │  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │         📊 填写表格:                        │   │  │ ← 互动表格
│  │  │  ┌──────┬──────┬──────┬──────────────────┐ │   │  │
│  │  │  │  a   │  b   │  c   │  a² + b² = ?    │ │   │  │
│  │  │  ├──────┼──────┼──────┼──────────────────┤ │   │  │
│  │  │  │  3   │  4   │  5   │ 9+16 = 25 ✅    │ │   │  │
│  │  │  │  5   │ 12   │ [  ] │ 25+144 = ?      │ │   │  │ ← 学生填写
│  │  │  │  8   │ 15   │ [  ] │ 64+225 = ?      │ │   │  │
│  │  │  └──────┴──────┴──────┴──────────────────┘ │   │  │
│  │  └────────────────────────────────────────────┘   │  │
│  │                                                    │  │
│  │  🗣️ 学生: "5²+12² = 25+144 = 169, 所以c = 13"    │  │ ← 语音回答
│  │  🎤 AI老师: "你发现规律了吗？看看 a²+b² 和 c²"    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ 💡 EXPLAIN 概念讲解 (5 min) ────────────────────┐  │
│  │                                                    │  │
│  │  🎤 AI老师: "你刚重新发现了勾股定理！"             │  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │     📝 公式卡片                              │   │  │ ← 高亮公式卡
│  │  │  ┌──────────────────────────────────────┐  │   │  │
│  │  │  │                                      │  │   │  │
│  │  │  │     a² + b² = c²                     │  │   │  │
│  │  │  │                                      │  │   │  │    彩色高亮
│  │  │  │  a, b = 直角边 (legs) 🔵             │  │   │  │    a,b 蓝色
│  │  │  │  c = 斜边 (hypotenuse) 🔴            │  │   │  │    c 红色
│  │  │  │                                      │  │   │  │
│  │  │  │  ⚠️ 只适用于直角三角形!               │  │   │  │
│  │  │  └──────────────────────────────────────┘  │   │  │
│  │  └────────────────────────────────────────────┘   │  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │  🖼️ 经典面积图解                             │   │  │ ← 静态插图
│  │  │                                            │   │  │
│  │  │     ┌─────┐       ┌──┬──┐                  │   │  │
│  │  │     │     │ a²    │  │  │                   │   │  │
│  │  │     │  a  │   →   ├──┼──┤ = a²+b²          │   │  │
│  │  │     │     │       │  │  │                   │   │  │
│  │  │     └─────┘       └──┴──┘                  │   │  │
│  │  │       b²                                     │   │  │
│  │  │                                            │   │  │
│  │  │  面积守恒: a² + b² = c²                    │   │  │
│  │  └────────────────────────────────────────────┘   │  │
│  │                                                    │  │
│  │  🎤 AI老师: "这个定理在AMC约50%几何题都会用到！"   │  │
│  │                                                    │  │
│  │  [▶ 查看面积证明动画]  [▶ 查看代数证明]            │  │ ← 折叠深度内容
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ ✏️ ELABORATE 引导练习 (8 min) ─────────────────┐  │
│  │                                                    │  │
│  │  🎤 AI老师: "来做几道练习巩固一下"                 │  │
│  │                                                    │  │
│  │  Q1: 直角边6,8 → 斜边? (基础)                     │  │
│  │  ┌──────────────────────────────────────────┐    │  │
│  │  │ ✏️ 草稿板 (可手写/打字)                    │    │  │ ← 手写区域
│  │  │                                          │    │  │
│  │  │  6²+8² = 36+64 = 100 → √100 = 10       │    │  │
│  │  │                                          │    │  │
│  │  └──────────────────────────────────────────┘    │  │
│  │  🗣️ [口述回答] 或 输入: [10] [✓ 提交]            │  │ ← 语音或键盘
│  │                                                    │  │
│  │  Q2: 斜边13,一边5 → 另一边? (逆向)               │  │
│  │  Q3: 正方形对角线10√2 → 边长? (变形)              │  │
│  │  苏格拉底式引导, 不直接给答案                       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ ✅ EVALUATE 小测验 (4 min) ─────────────────────┐  │
│  │  3道检测题 → 80%正确率通过 → 解锁B4相似三角形     │  │
│  │  📊 结果: 掌握度更新 → 间隔重复安排 → 下课推荐     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

#### 语音交互设计

**语音输出 (AI老师讲话)**:
- 每段教学内容都有对应的语音讲解, 非纯TTS合成
- 学生可以选择开启/关闭语音自动播放
- 语音播放时, 对应文字高亮滚动 (类似有声书)
- 关键公式读法: `a²+b²=c²` 读作 "a squared plus b squared equals c squared"

**语音输入 (学生回答)**:
- 对话区常驻 🎤 按钮, 按住说话或点击切换
- ASR实时转文字, 学生可以确认后发送
- 数学表达识别: "x平方加5x加6" → `x²+5x+6`
- 英语模式: 支持英文语音输入 + 发音评分

**语音场景矩阵**:

| 场景 | 语音输入 | 语音输出 | 示例 |
|------|---------|---------|------|
| 课程讲解 | ❌ | ✅ 自动播放 | AI老师讲勾股定理 |
| 课程互动 | ✅ 口述回答 | ✅ 语音反馈 | "你觉得斜边多长？" |
| 刷题对话 | ✅ 口述思路 | ✅ 语音引导 | 苏格拉底式引导解题 |
| KET口语 | ✅ 录音评分 | ✅ AI考官 | 模拟口语考试 |
| KET听力 | ❌ | ✅ TTS播放 | 听力理解练习 |

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
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐     │
│  │ Problem     │ │ Knowledge    │ │ Speech           │    │
│  │ Service     │ │ Graph        │ │ Service          │    │
│  │ (题库管理)   │ │ (知识图谱)    │ │ (ASR/TTS/评分)   │     │
│  └─────────────┘ └──────────────┘ └──────────────────┘    │
│                                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ User        │ │ Analytics    │ │ Media             │    │
│  │ Service     │ │ Service      │ │ Service           │    │
│  │ (用户/家长)  │ │ (数据分析)    │ │ (音频/图片/动画)  │    │
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
| **AI** | TTS | Azure TTS / Edge TTS | 听力材料, 口语考试音频, AI老师讲解 |
| **AI** | 数学ASR | 联合方案: Whisper + LaTeX解析 | 数学语音输入: "x平方加5" → x²+5 |
| **AI** | 图像生成 | DALL-E / Stable Diffusion (按需) | 课程配图, 几何示意图 |
| **前端** | 图形动画 | Manim (Python→MP4) + Lottie | 数学概念动画, 几何推导过程 |
| **前端** | 手写识别 | MyScript Math SDK | 手写数学公式→LaTeX |
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
    target_exam         VARCHAR(20),          -- 'AMC8', 'AMC10', 'AMC12', 'KET', 'CHN_COMP', 'CHN_POETRY'
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
    subject         VARCHAR(20) NOT NULL,           -- 'amc_math', 'ket_english', 'chn_composition', 'chn_poetry'
    name            VARCHAR(200) NOT NULL,
    name_en         VARCHAR(200),
    description     TEXT,
    
    -- 分类
    pillar          VARCHAR(50),      -- 'algebra', 'geometry', 'counting', 'number_theory'
                                            -- 'reading', 'writing', 'listening', 'speaking', 'vocabulary', 'grammar'
                                            -- 'composition_basic', 'narrative', 'descriptive', 'imaginative', 'practical'
                                            -- 'poetry_basics', 'seasonal', 'landscape', 'emotions', 'masters', 'comprehensive'
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
    content         TEXT NOT NULL,           -- 文字内容
    
    -- 多模态支持
    media           JSONB,                  -- 音频/图片/视频/文件
    /*
    media格式:
    {
      "type": "audio" | "image" | "video" | "geogebra",
      "url": "s3://...",
      "duration_sec": 5.2,          -- 音频时长
      "transcript": "x平方加5...",  -- ASR转写文本
      "confidence": 0.95,           -- ASR置信度(用于发音评分)
      "thumbnail_url": "...",       -- 视频/GeoGebra缩略图
      "latex_parsed": "x^2+5"      -- 数学语音→LaTeX解析结果
    }
    */
    
    metadata        JSONB,                  -- 工具调用, 播放状态等
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
    content结构示例 (支持图文并茂+语音):
    {
      "introduction": {
        "text": "今天我们来学勾股定理...",
        "audio_url": "s3://.../intro.mp3",
        "visual": {
          "type": "geogebra",
          "applet_id": "pythagoras_explore",
          "instructions": "拖动三角形顶点, 观察边长变化"
        }
      },
      "exploration": [
        {
          "prompt": "你能量出斜边多长吗？",
          "prompt_audio_url": "s3://.../prompt1.mp3",
          "input_mode": ["voice", "text", "drawing"],
          "expected_discovery": "a² + b² = c²",
          "interactive_table": {
            "columns": ["a", "b", "c", "a²+b²"],
            "rows": [[3,4,5,null],[5,12,null,null]]
          }
        }
      ],
      "explanation": {
        "text": "勾股定理: 直角三角形中 a² + b² = c²",
        "audio_url": "s3://.../explain.mp3",
        "formula_card": {
          "latex": "a^2 + b^2 = c^2",
          "color_coding": {"a_b": "#4A90D9", "c": "#E74C3C"},
          "note": "只适用于直角三角形!"
        },
        "illustrations": [
          {
            "type": "image",
            "url": "s3://.../pythagorean_squares.png",
            "caption": "经典面积图解: a²+b²=c²"
          }
        ],
        "animations": [
          {
            "type": "manim",
            "video_url": "s3://.../area_proof.mp4",
            "thumbnail_url": "s3://.../area_proof_thumb.png",
            "duration_sec": 45,
            "title": "面积证明动画"
          }
        ],
        "expandable_proofs": [
          {
            "title": "面积证明",
            "type": "manim",
            "video_url": "s3://.../area_proof.mp4"
          },
          {
            "title": "代数证明",
            "type": "text",
            "markdown": "设..."
          }
        ]
      },
      "guided_practice": [
        {
          "problem_id": "...",
          "scratchpad": true,
          "hint_levels": [
            {"level": 0, "text": "你觉得第一步做什么？", "audio_url": "..."},
            {"level": 1, "text": "这是直角三角形, 用勾股定理", "audio_url": "..."}
          ]
        }
      ],
      "assessment": [
        {"problem_id": "..."}
      ],
      "summary": {
        "key_points": ["a²+b²=c²", "只适用于直角三角形", "可用于求边长"],
        "amc_tip": "AMC约50%几何题会用到此定理",
        "next_lesson": "B4"
      }
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

参考 Brilliant.org 的交互式学习, 支持语音讲解和丰富图文:

```
┌──────────────────────────────────────────────────────────┐
│ [←]  B4 相似三角形                    ████░░ 65%        │ ← 课程进度条
│ 🔊 语音: [自动播放 ●] [速度 1.0x ▼]  [🔇静音]         │ ← 语音控制栏
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ 📐 可视化内容区 ──────────────────────────────────┐  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │                                            │   │  │ ← GeoGebra交互
│  │  │          A                                 │   │  │    可拖拽顶点
│  │  │         /│          A'                     │   │  │    实时标注比例
│  │  │        / │         /│                      │   │  │
│  │  │     3 /  │ 4    6 / │ 8                    │   │  │
│  │  │      /   │  ══▶   /  │                     │   │  │ ← 动画: 放大2倍
│  │  │     /____│       /____│                     │   │  │
│  │  │    B    C        B'  C'                     │   │  │
│  │  │                                            │   │  │
│  │  │  比例: AB:A'B' = 1:2  ✅ 对应边成比例      │   │  │ ← 实时标注
│  │  └────────────────────────────────────────────┘   │  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │  🖼️ 图解: 相似三角形的判定                   │   │  │ ← 图解卡片
│  │  │                                            │   │  │
│  │  │  AA相似: 两个角相等 → 相似 ✅               │   │  │
│  │  │  SSS相似: 三边成比例 → 相似 ✅              │   │  │
│  │  │  SAS相似: 两边成比例+夹角相等 → 相似 ✅     │   │  │
│  │  │                                            │   │  │
│  │  │  [▶ 展开每个判定的动画证明]                  │   │  │ ← 可展开深度
│  │  └────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ 🧑‍🏫 AI老师讲解区 ────────────────────────────────┐  │
│  │                                                    │  │
│  │  🔊 [▶ 正在播放...]                               │  │ ← 语音播放状态
│  │  "看这两个三角形——如果把小的                       │  │ ← 语音+文字同步
│  │   放大2倍, 它和大的重合吗？                        │  │    当前播到的句子高亮
│  │   试试拖动滑块。"                                  │  │
│  │                                                    │  │
│  │  ⏸️ [暂停] ⏭️ [跳过] 📖 [只看文字]                │  │ ← 播放控制
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ 👦 学生回答区 ────────────────────────────────────┐  │
│  │                                                    │  │
│  │  🗣️ [按住说话]  或  ✏️ [输入文字]                 │  │ ← 语音/文字切换
│  │                                                    │  │
│  │  ┌──────────────────────────────────────────┐    │  │
│  │  │  ✏️ 草稿板 (可手写推导)                    │    │  │ ← 手写/绘图板
│  │  │                                          │    │  │
│  │  │  △ABC ~ △A'B'C'                         │    │  │
│  │  │  AB/A'B' = BC/B'C' = 1/2                │    │  │
│  │  └──────────────────────────────────────────┘    │  │
│  │                                                    │  │
│  │  [💡提示]  [📸拍照上传]  [📝笔记]                  │  │ ← 工具栏
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  [继续 →]                                               │
└──────────────────────────────────────────────────────────┘
```

### 6.5 刷题界面

```
┌──────────────────────────────────────────────────────────┐
│ [←] AMC 10 练戏    ⏱ 12:34    3/5                      │ ← 计时器 + 进度
│ 🔊 [语音引导 ●]  [🔇]                                   │ ← 语音开关
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ 📝 题目区 ────────────────────────────────────────┐  │
│  │                                                    │  │
│  │  题目 #3                                           │  │
│  │                                                    │  │
│  │  ┌────────────────────────────────────────────┐   │  │
│  │  │          C                                  │   │  │ ← 配套图形
│  │  │         / \        circumscribed            │   │  │
│  │  │    13  /   \  5    circle?                  │   │  │
│  │  │     /     \                                 │   │  │
│  │  │    A───────B                                │   │  │
│  │  │       12                                    │   │  │
│  │  └────────────────────────────────────────────┘   │  │
│  │                                                    │  │
│  │  In △ABC, AB = 5, BC = 12, AC = 13.              │  │ ← LaTeX渲染
│  │  What is the area of the circumscribed circle?    │  │
│  │                                                    │  │
│  │  A) 169π/4   B) 65π/4   C) 13π                   │  │
│  │  D) 169π/10  E) 65π/2                             │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ 💬 AI引导对话 ────────────────────────────────────┐  │
│  │                                                    │  │
│  │  🧑‍🏫 🔊 [▶ 播放中]                               │  │ ← 语音可播放
│  │  "先别急着算——这个三角形                           │  │
│  │   的三边有什么特殊之处？"                           │  │
│  │                                                    │  │
│  │  👦 🗣️ (语音输入)                                  │  │ ← 学生语音回答
│  │  "5²+12²=169=13², 是直角三角形"                   │  │    ASR转文字
│  │                                                    │  │
│  │  🧑‍🏫 🔊 "很好！那直角三角形的                       │  │
│  │   外接圆半径和斜边有什么关系？"                     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ 输入工具栏 ──────────────────────────────────────┐  │
│  │                                                    │  │
│  │  🗣️ [按住说话]  ✏️ [打字输入]  📸 [拍照上传]      │  │ ← 三种输入方式
│  │                                                    │  │
│  │  📝 [草稿板]   💡 [提示 L0]                        │  │ ← 辅助工具
│  │                                                    │  │
│  │  我觉得答案是: [B]  [提交]                          │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
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
| 墨水屏适配 | 检测 `@media (monochrome)` 自动启用 e-ink 模式 |
| 字号 (墨水屏) | 墨水屏模式最小 16px, 正文 18px |
| 对比度 (墨水屏) | 仅使用 #000/#fff/#333/#eee 四色 |
| 触控区域 (墨水屏) | 最小 44×44px |

---

### 6.9 墨水屏适配设计

> 目标设备: Boox 10寸墨水屏平板 (Note Air 3 / Go 10.3 / Tab Ultra)
> 屏幕参数: 1404×1872, 227 PPI, 16级灰度, 刷新率 15-30Hz
> 系统: Android 11-15, 支持 Chrome/Firefox, 可安装第三方 APK
> 部署方式: Web App (Next.js) + PWA (添加到桌面)

#### 6.9.1 设备能力与限制

| 能力 | 支持 | 说明 |
|------|------|------|
| Web App 浏览器访问 | ✅ | Chrome / Firefox / NeoBrowser |
| PWA 添加到桌面 | ✅ | Chrome 支持 |
| APK 安装 | ✅ | Google Play + 侧载 |
| 触控操作 | ✅ | 但响应比 LCD 慢 |
| 手写笔 | ✅ | Wacom/EMR 触控笔 |
| 音频播放 | ✅ | TTS/听力材料正常 |
| 语音输入 | ⚠️ | 可用但 ASR 可能有延迟 |
| 视频播放 | ❌ | 极度卡顿，不可用 |
| 动画/拖拽 | ❌ | 刷新率不足以支持流畅动画 |
| 彩色显示 | ❌ | 16级灰度，颜色不可区分 |

#### 6.9.2 核心适配策略

**原则：检测到墨水屏时，启用 e-ink 模式，降级所有动态交互为静态分步展示。**

```css
/* 墨水屏检测与全局适配 */
@media (monochrome) {
  :root {
    --eink-bg: #ffffff;
    --eink-text: #000000;
    --eink-border: #000000;
    --eink-accent: #333333;
    --eink-alt-bg: #f0f0f0;
  }

  /* 全局：关闭所有动画和过渡 */
  * {
    animation: none !important;
    transition: none !important;
    box-shadow: none !important;
    filter: none !important;
    transform: none !important;
  }

  /* 强制白底黑字 */
  body {
    background: #ffffff !important;
    color: #000000 !important;
    font-size: 18px;
    line-height: 1.6;
  }

  /* 图片转高对比灰度 */
  img {
    filter: grayscale(100%) contrast(1.2);
  }

  /* 按钮：粗边框替代填充 */
  button, .btn {
    border: 2px solid #000;
    background: #fff;
    color: #000;
    min-height: 44px;
    font-weight: 600;
    border-radius: 0;
  }

  button:active {
    background: #000;
    color: #fff;
  }

  /* 输入框：粗边框 */
  input, textarea, select {
    border: 2px solid #000;
    border-radius: 0;
    font-size: 16px;
  }

  /* 隐藏所有动画元素 */
  .animate, .spinner, .loading-dots {
    display: none !important;
  }

  /* 改用文字提示加载状态 */
  .loading-text-eink {
    display: block !important;
  }
}

/* 同时支持 prefers-reduced-motion（墨水屏始终为 reduce） */
@media (prefers-reduced-motion: reduce) {
  .spinner, .loading-animation {
    display: none;
  }
  .loading-text-fallback {
    display: block;
  }
}
```

#### 6.9.3 各模块墨水屏适配方案

| 模块 | 普通屏幕 | 墨水屏适配 | 优先级 |
|------|---------|-----------|--------|
| **GeoGebra 交互** | 可拖拽图形 | 静态图解 + 分步切换按钮（上一步/下一步） | P0 |
| **动画演示 (Manim/Lottie)** | 视频动画播放 | 逐帧截图 + 前后翻页 | P0 |
| **语音播放** | 自动播放 + 文字同步高亮 | 点击播放 + 静态文字展示（不高亮动画） | P1 |
| **进度条** | 彩色填充动画 | 黑白粗边框 + 文字百分比 | P1 |
| **成就徽章** | 彩色图标 | 黑白线条图标 + 文字标签 | P2 |
| **知识雷达图** | 彩色雷达图 | 黑白条形图（各支柱竖条） | P2 |
| **底部导航** | 图标+文字 | 纯文字 Tab（图标在灰度下难辨认） | P1 |
| **课程内容** | 连续滚动 | **分页翻页**模式（减少残影） | P0 |
| **草稿板** | 手写板 | Boox 手写笔原生支持（最佳体验） | P0 |
| **写作编辑器** | 富文本编辑 | 纯文本编辑 + 字数统计 | P1 |
| **口语录音** | 波形动画 | 录音按钮 + 文字状态 | P2 |
| **选择题** | 点击选项高亮 | 选中项反转色（白→黑，黑→白） | P0 |

#### 6.9.4 GeoGebra / 动画降级方案

GeoGebra 和 Manim 动画在墨水屏上无法流畅运行。需要准备静态替代方案：

```
普通屏幕:
  GeoGebra 可拖拽图形 → 学生自由探索

墨水屏降级:
  Step 1/5: [静态截图] 初始状态
  Step 2/5: [静态截图] 拖动到位置 A
  Step 3/5: [静态截图] 拖动到位置 B
  Step 4/5: [静态截图] 关键发现
  Step 5/5: [静态截图] 结论
  
  [< 上一步]  3/5  [下一步 >]
```

**实现方式**:
- 每个 GeoGebra/Animation Block 增加可选的 `eink_fallback` 字段
- `eink_fallback` 包含一组静态截图 + 分步说明
- 前端检测 `@media (monochrome)` 或用户手动切换 e-ink 模式时，渲染 fallback

```typescript
// GeoGebra Block 扩展
interface GeoGebraBlock {
  // ... existing fields ...
  
  /** 墨水屏降级方案（可选） */
  eink_fallback?: {
    /** 分步静态截图 */
    steps: Array<{
      /** 截图 URL */
      image_url: string;
      /** 该步骤说明 */
      caption: string;
      /** 该步骤关键发现 */
      insight?: string;
    }>;
    /** 降级说明文字 */
    fallback_note?: string;
  };
}

// Animation Block 扩展
interface AnimationBlock {
  // ... existing fields ...
  
  /** 墨水屏降级方案（可选） */
  eink_fallback?: {
    /** 关键帧截图（3-8帧） */
    keyframes: Array<{
      /** 截图 URL */
      image_url: string;
      /** 时间点标注 */
      timestamp?: string;
      /** 帧说明 */
      caption: string;
    }>;
  };
}
```

#### 6.9.5 分页翻页模式

墨水屏上连续滚动会产生严重残影（ghosting）。课程内容采用**分页翻页**：

```css
/* 墨水屏：强制分页 */
@media (monochrome) {
  .lesson-content {
    /* 禁用滚动 */
    overflow: hidden;
    height: 100vh;
  }
  
  .lesson-page {
    display: none;
    height: 100%;
    padding: 1rem;
  }
  
  .lesson-page.active {
    display: block;
  }
  
  /* 翻页按钮 */
  .page-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    background: #fff;
    border-top: 2px solid #000;
  }
}
```

每 5 页触发一次全刷（full refresh）清除残影：

```javascript
class EInkPageManager {
  constructor() {
    this.pageCount = 0;
    this.fullRefreshInterval = 5;
  }

  turnPage() {
    this.pageCount++;
    if (this.pageCount >= this.fullRefreshInterval) {
      this.fullRefresh();
      this.pageCount = 0;
    }
  }

  fullRefresh() {
    // 触发全刷清除残影
    document.body.style.opacity = '0.99';
    requestAnimationFrame(() => {
      document.body.style.opacity = '1';
    });
  }
}
```

#### 6.9.6 触控优化

```css
/* 墨水屏触控优化 */
@media (monochrome) {
  /* 最小触控区域 44px */
  button, a, .clickable {
    min-height: 44px;
    min-width: 44px;
    padding: 0.75rem 1rem;
  }

  /* 选项间距加大（减少误触） */
  .option-list > li {
    margin-bottom: 0.75rem;
    padding: 0.75rem;
    border: 2px solid #000;
  }

  /* 选中项：反转色（最清晰的反馈） */
  .option-list > li.selected {
    background: #000;
    color: #fff;
  }

  /* 禁用 hover（墨水屏无 hover） */
  *:hover {
    /* 不做任何视觉变化 */
  }

  /* 使用 :active 替代 */
  *:active {
    outline: 3px solid #000;
  }
}
```

#### 6.9.7 排版规范

| 参数 | 墨水屏推荐值 | 原因 |
|------|------------|------|
| 正文字号 | 18px（最小 16px） | 墨水屏需要更大字号保证清晰 |
| 标题字号 | H1: 28px / H2: 22px / H3: 18px | 层次区分 |
| 字重 | 最小 400（regular），标题 600 | 细体在墨水屏上消失 |
| 行高 | 1.6-1.8 | 墨水屏需要更多呼吸空间 |
| 字体 | system-ui, sans-serif | 系统字体避免额外渲染开销 |
| 段落间距 | 1.5em | 清晰分隔段落 |
| 颜色 | 仅用 #000 / #fff / #333 / #eee | 4色灰度系统 |
| 边框 | 2px solid #000 | 粗边框替代填充色区分 |

#### 6.9.8 墨水屏模式切换

用户可手动开关墨水屏模式（部分 Boox 彩色版可能不需要）：

```typescript
// 检测与切换逻辑
const useEInkMode = () => {
  // 自动检测
  const mediaQuery = window.matchMedia('(monochrome)');
  const [isEInk, setIsEInk] = useState(mediaQuery.matches);

  useEffect(() => {
    const handler = (e: MediaQueryListEvent) => setIsEInk(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  // 同时允许手动切换（设置页面）
  const toggleEInkMode = () => setIsEInk(prev => !prev);

  return { isEInk, toggleEInkMode };
};
```

设置页面增加：
```
┌─────────────────────────────────────┐
│ ⚙️ 设置                             │
├─────────────────────────────────────┤
│ 显示模式:                            │
│ ◉ 标准模式                          │
│ ○ 墨水屏模式 (高对比/无动画/分页)    │
│                                     │
│ [自动检测设备] ← 点击自动判断         │
└─────────────────────────────────────┘
```

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

### 7.6 语文作文评分 Prompt

```
你是一位小学语文作文评分专家，正在为4-6年级学生的作文打分。

## 评分标准（100分制，4维度）

### 内容（40分）
- 36-40分：主题明确，内容充实，选材新颖，有真情实感
- 30-35分：主题明确，内容较充实，选材恰当
- 24-29分：主题基本明确，内容较简单，不够具体
- 18-23分：主题不够明确，内容空泛
- 0-17分：主题不明确或严重偏离题意

### 结构（20分）
- 18-20分：条理清晰，段落分明，过渡自然，开头结尾呼应
- 15-17分：条理较清晰，段落较分明
- 12-14分：有一定条理，段落划分不够清楚
- 6-11分：条理不清，段落混乱
- 0-5分：无明显结构

### 语言（30分）
- 27-30分：语言生动，善用修辞（比喻/拟人/排比），用词准确，句式多样
- 22-26分：语言通顺，偶有修辞，用词较准确
- 16-21分：语言基本通顺，有少量语病
- 10-15分：语病较多，表达不够清楚
- 0-9分：语言混乱，严重影响理解

### 书写（10分）
- 9-10分：书写工整，标点正确，格式规范
- 7-8分：书写较工整，标点基本正确
- 5-6分：书写一般，有标点错误
- 0-4分：书写潦草，标点错误多

## 年级字数标准
| 年级 | 基本要求 | 目标 | 加分 |
|------|---------|------|------|
| 四年级 | ≥200字 | 300字 | ≥400字 |
| 五年级 | ≥300字 | 400字 | ≥500字 |
| 六年级 | ≥350字 | 450字 | ≥550字 |

## 题目要求
{{task_description}}
文体要求: {{writing_type}}
字数要求: {{min_chars}}-{{max_chars}}字（目标{{target_chars}}字）
学生年级: {{chn_grade}}年级

## 学生作文
{{student_essay}}

## 输出格式 (JSON)
{
  "content_score": 0-40,
  "structure_score": 0-20,
  "language_score": 0-30,
  "handwriting_score": 0-10,
  "total_score": 0-100,
  "char_count": N,
  "meets_word_count": true/false,
  "writing_type_match": true/false,
  "feedback": {
    "strengths": ["...", "..."],
    "improvements": ["...", "..."],
    "highlights": [
      {
        "text": "原文中的好句",
        "comment": "为什么写得好"
      }
    ],
    "specific_suggestions": [
      {
        "original": "原文中需要修改的句子",
        "suggestion": "修改后的版本",
        "reason": "修改原因"
      }
    ]
  },
  "revision_plan": {
    "priority": "content | structure | language",
    "action_items": ["具体可操作的改进建议1", "..."],
    "encouragement": "一句鼓励的话"
  }
}

## 重要规则
- 你是给小学生打分，语气要温和鼓励
- **先肯定优点**（至少找2个亮点），再指出改进方向
- 修改建议要**具体可操作**：不说"写得更生动"，而是说"试试把'花很漂亮'改成'花儿像穿上了彩色的裙子'"
- 字数不足时扣分，但不要因此全盘否定
- 允许有小毛病，关注学生的进步空间
- 不要用过高标准（这不是高考作文）
```

### 7.7 古诗词教学 Prompt

#### 7.7.1 诗词赏析引导 Prompt

```
你是一位古诗词鉴赏老师，正在教小学4-6年级学生赏析古诗词。

## 当前诗歌
标题: {{poem_title}}
诗人: {{poet}}
朝代: {{dynasty}}
原文: {{full_text}}

## 学生信息
年级: {{chn_grade}}年级
已学过的诗歌: {{learned_poems}}
已掌握的意象: {{mastered_imagery}}

## 教学规则
1. **展示赏析框架**：先给学生思考的脚手架
   - 第一步：通读全诗，用自己的话说大意
   - 第二步：找意象，联想象征意义
   - 第三步：析手法（比喻/拟人/对偶/夸张等）
   - 第四步：悟情感
2. **联系学生生活**：找到诗歌情感与现代生活的连接点
3. **朗读指导**：标注节奏，鼓励有感情地朗读
4. **允许个性化理解**：同一首诗可以有不同的感受
5. **知识串联**：联系之前学过的同主题/同诗人作品

## 当前阶段
正在执行: {{current_phase}} (read_poem / decipher / appreciate / comprehend / verify)

## 输出要求
- read_poem: 节奏标注 + 朗读指导 + 背景故事引入
- decipher: 关键字词释义 + 疏通大意 + 趣味知识
- appreciate: 意象分析 + 手法讲解 + 名句品鉴（展示赏析角度，引导学生发现）
- comprehend: 情感归纳 + 主旨理解 + 联系生活
- verify: 默写检测题 + 理解性填空 + 赏析小题

保持语气亲切，像讲故事一样教诗词。每次回复2-3个短段落。
```

#### 7.7.2 诗词默写评估 Prompt

```
你是一位古诗词默写评估系统。判断学生的默写是否正确。

## 原诗
{{full_text}}

## 学生默写
{{student_dictation}}

## 评估规则
1. **精确匹配**：每个字必须完全正确
2. **容错项**：
   - 允许的异体字: {{acceptable_variants}}
   - 标点符号不计入正确性判断
3. **错误分类**：
   - 错别字（形近混淆）：记录具体错误
   - 漏字/添字：标记位置
   - 语序颠倒：标记并纠正

## 输出格式 (JSON)
{
  "is_correct": true/false,
  "accuracy": 0.0-1.0,
  "errors": [
    {
      "position": 字的位置索引,
      "expected": "正确字",
      "actual": "学生写的字",
      "error_type": "wrong_char | missing | extra | swapped"
    }
  ],
  "feedback": "温和的反馈文字，指出错误并鼓励"
}
```

#### 7.7.3 诗词赏析评分 Prompt

```
你是一位古诗词赏析评分专家，评估学生的赏析回答。

## 题目
{{question}}

## 参考答案要点
{{reference_points}}

## 学生回答
{{student_answer}}

## 评分规则
- 不要求与参考答案完全一致
- 关注思考过程和角度是否正确
- 能自圆其说且有理有据即可给分
- 个性化理解（与参考答案不同但合理）同样得分

## 输出格式 (JSON)
{
  "score": 0-{{max_score}},
  "covered_points": ["匹配到的参考要点"],
  "missed_points": ["未覆盖的参考要点"],
  "unique_insights": ["学生独特的见解"],
  "feedback": "具体反馈"
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

### 8.1.1 语文作文掌握度模型

作文不适用二元对错模型。采用**多维度独立追踪**：

```python
def update_composition_mastery(student_id: str, composition_result: dict):
    """
    作文掌握度：4个维度独立追踪
    每个维度有自己的 mastery (0.0-1.0)
    """
    dimensions = {
        "content": composition_result["content_score"] / 40,     # 0-40 → 0.0-1.0
        "structure": composition_result["structure_score"] / 20, # 0-20 → 0.0-1.0
        "language": composition_result["language_score"] / 30,   # 0-30 → 0.0-1.0
    }
    # 不追踪 handwriting（书写与打字无关）
    
    for dim_name, score in dimensions.items():
        state = get_or_create_dimension_state(student_id, dim_name)
        alpha = 0.25  # 较慢的学习速率（作文进步缓慢）
        state.mastery = state.mastery + alpha * (score - state.mastery)
        state.history.append({"score": score, "date": now()})
    
    # 综合掌握度 = 加权平均
    overall = (
        content_mastery * 0.4 +
        structure_mastery * 0.2 +
        language_mastery * 0.3
    )
    return overall
```

### 8.1.2 古诗词掌握度模型

古诗词采用**分层追踪**，三个维度各自独立：

| 维度 | 追踪方式 | 更新算法 |
|------|---------|---------|
| **背诵掌握度** | FSRS 二元模型 | 默写准确率 → is_correct → FSRS standard update |
| **理解掌握度** | 渐进度模型 | 理解性填空/选择题 → 正确率 → EMA 更新 |
| **赏析能力** | 等级制 | 赏析题评分 → 等级映射（入门/进阶/高级） |

```python
def update_poetry_mastery(student_id: str, poem_code: str, assessment: dict):
    # 1. 背诵维度 — FSRS 二元
    dictation_accuracy = assessment.get("dictation_accuracy", 0)
    is_correct = dictation_accuracy >= 0.95  # 95%以上算"记住"
    update_fsrs(student_id, poem_code + "#recite", is_correct)
    
    # 2. 理解维度 — EMA
    understanding_score = assessment.get("understanding_score", 0)
    state = get_understanding_state(student_id, poem_code)
    alpha = 0.3
    state.mastery = state.mastery + alpha * (understanding_score - state.mastery)
    
    # 3. 赏析维度 — 等级制
    appreciation_score = assessment.get("appreciation_score", 0)
    if appreciation_score >= 0.8:
        state.appreciation_level = "advanced"
    elif appreciation_score >= 0.5:
        state.appreciation_level = "intermediate"
    else:
        state.appreciation_level = "beginner"
    
    # 综合（用于课程解锁判断）
    overall = (
        recite_mastery * 0.3 +
        understanding_mastery * 0.4 +
        appreciation_normalized * 0.3
    )
    return overall
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
| **Tutor** | 强模型 | 核心教学对话, 苏格拉底式引导, 概念讲解 | RAG, GeoGebra, 代码执行, 计算器, TTS, Manim |
| **Assessor** | 强模型 | 评分(数学/写作/口语), 错误诊断, 知识状态更新 | 代码执行, 评分rubric, ASR评分 |
| **Curriculum** | 规则+快模型 | 课程调度, 出题推荐, 间隔重复安排, 进度追踪 | DB查询, FSRS算法 |

### 9.2.1 学科教学策略差异

| 学科 | AI 教学策略 | 给答案？ | 核心方法 |
|------|-----------|---------|---------|
| AMC 数学 | 苏格拉底式 | **永不** | 提问引导，让学生自己发现 |
| KET 英语写作 | 范文+反馈 | 展示范文 | 示范→练习→反馈→修改 |
| 语文作文 | **主动示范** | **必须给** | 展示范文/好句/技巧，鼓励模仿 |
| 古诗词赏析 | 框架+引导 | 给赏析角度 | 展示思考框架，引导发现 |

> ⚠️ **关键区别**：数学的"永远不给答案"策略如果用到作文上，效果比没有AI还差。
> 作文学习的核心是**模仿**，AI 必须主动展示好的例子和技巧。

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
