# Phase 2 测试方案

> Version: 1.0 | Date: 2026-05-31
> 范围: LangGraph Agent 集成 — 单元测试 + 集成测试 + 端到端测试

---

## 目录

1. [测试策略概览](#1-测试策略概览)
2. [测试环境搭建](#2-测试环境搭建)
3. [单元测试 — FSRS 算法](#3-单元测试--fsrs-算法)
4. [单元测试 — 知识追踪](#4-单元测试--知识追踪)
5. [单元测试 — 题目选择器](#5-单元测试--题目选择器)
6. [单元测试 — Prompt 模板](#6-单元测试--prompt-模板)
7. [单元测试 — Agent 节点 (Mock LLM)](#7-单元测试--agent-节点-mock-llm)
8. [集成测试 — Agent Graph 全流程](#8-集成测试--agent-graph-全流程)
9. [集成测试 — API 端点](#9-集成测试--api-端点)
10. [端到端测试 — 完整学习场景](#10-端到端测试--完整学习场景)
11. [降级测试 — 无 API Key 场景](#11-降级测试--无-api-key-场景)
12. [测试脚本 & 运行方式](#12-测试脚本--运行方式)

---

## 1. 测试策略概览

### 1.1 测试金字塔

```
        ╱  E2E  ╲            5 个场景测试 — 完整学习路径
       ╱─────────╲           需要真实 DB + Mock LLM
      ╱ Integration ╲        12 个测试 — Graph + API
     ╱───────────────╲       需要 DB + Mock LLM
    ╱   Unit Tests    ╲      40+ 个测试 — 纯函数 + Mock
   ╱───────────────────╲     无外部依赖，毫秒级
```

### 1.2 测试分层

| 层 | 测试目标 | 数量 | 外部依赖 | 运行时间 |
|----|---------|------|---------|---------|
| **Unit** | FSRS、知识追踪、题目选择、Prompt、Agent 节点 | ~40 | Mock LLM | < 5s |
| **Integration** | Graph 全流程、API 端点 | ~12 | SQLite + Mock LLM | < 15s |
| **E2E** | 完整学习路径（聊天 → 答题 → FSRS → 推荐） | ~5 | SQLite + Mock LLM | < 30s |

### 1.3 核心测试原则

1. **LLM 全部 Mock** — 测试逻辑正确性，不测 LLM 输出质量
2. **DB 用 SQLite 内存** — `sqlite+aiosqlite:///:memory:`，每个测试隔离
3. **无 OPENAI_API_KEY** — 所有测试在无 API Key 环境运行，验证降级路径
4. **种子数据复用** — 用 fixture 创建标准学生、题目、知识点

---

## 2. 测试环境搭建

### 2.1 目录结构

```
backend/tests/
├── conftest.py                    # 全局 fixtures（DB、用户、认证）
├── test_main.py                   # (已有) 健康检查
│
├── unit/
│   ├── __init__.py
│   ├── test_fsrs.py               # FSRS 算法单元测试
│   ├── test_knowledge_tracker.py  # 知识追踪单元测试
│   ├── test_problem_selector.py   # 题目选择器单元测试
│   ├── test_prompts.py            # Prompt 模板测试
│   └── test_llm_factory.py        # LLM 工厂 + 降级测试
│
├── agents/
│   ├── __init__.py
│   ├── test_orchestrator.py       # Orchestrator 节点
│   ├── test_router.py             # Router 节点
│   ├── test_tutor.py              # Tutor 节点
│   ├── test_assessor.py           # Assessor 节点
│   ├── test_curriculum.py         # Curriculum 节点
│   └── test_graph.py              # 完整 Graph 集成
│
├── api/
│   ├── __init__.py
│   ├── test_chat.py               # Chat API 端点
│   └── test_problems.py           # Problems API 端点
│
└── e2e/
    ├── __init__.py
    └── test_learning_flow.py      # 完整学习场景
```

### 2.2 核心 Fixture (`conftest.py`)

```python
"""共享测试 fixtures。"""
import pytest
import pytest_asyncio
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models.base import Base
from app.models.user import User, StudentProfile
from app.models.problem import Problem
from app.models.knowledge import KnowledgePoint
from app.models.learning import KnowledgeState, LearningSession
from app.api.deps import get_db


# ── 内存 SQLite 引擎 ──────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """隔离的数据库会话，每个测试自动回滚。"""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(engine):
    """HTTP 测试客户端，注入内存 DB。"""
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── 种子数据 Fixtures ──────────────────────────────────

@pytest_asyncio.fixture
async def student(db_session):
    """标准测试学生。"""
    user = User(id=uuid4(), name="测试小明", email="test@example.com",
                hashed_password="fake_hash")
    db_session.add(user)
    await db_session.flush()

    profile = StudentProfile(
        user_id=user.id, grade_level=5, target_exam="AMC8",
        preferred_lang="zh-CN", diagnostic_done=False,
    )
    db_session.add(profile)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def knowledge_points(db_session):
    """3 个数学知识点。"""
    kps = [
        KnowledgePoint(id=uuid4(), code="algebra.01", name="一元一次方程",
                       pillar="代数", subject="amc_math"),
        KnowledgePoint(id=uuid4(), code="geometry.01", name="相似三角形",
                       pillar="几何", subject="amc_math"),
        KnowledgePoint(id=uuid4(), code="number.01", name="整除性",
                       pillar="数论", subject="amc_math"),
    ]
    for kp in kps:
        db_session.add(kp)
    await db_session.flush()
    return {kp.code: kp for kp in kps}


@pytest_asyncio.fixture
async def mcq_problem(db_session, knowledge_points):
    """标准 MCQ 题目。"""
    kp = knowledge_points["algebra.01"]
    problem = Problem(
        id=uuid4(), subject="amc_math", format="mcq",
        question_markdown="解方程 2x + 3 = 7，x = ?",
        options={"A": "1", "B": "2", "C": "3", "D": "4"},
        correct_answer="B",
        difficulty=3,
        knowledge_point_ids=[str(kp.id)],
    )
    db_session.add(problem)
    await db_session.flush()
    return problem


@pytest_asyncio.fixture
async def auth_token(student):
    """生成测试用 JWT token。"""
    from app.services.auth_service import create_access_token
    return create_access_token(student.id)
```

### 2.3 依赖安装

在 `requirements.txt` 中已有 `httpx`、`pytest`（通过 fastapi 间接）。需要额外添加:

```
# Testing
pytest>=8.0.0
pytest-asyncio>=0.24.0
```

---

## 3. 单元测试 — FSRS 算法

> 文件: `tests/unit/test_fsrs.py`
> 目标: 验证 FSRS 数学公式正确性
> 无外部依赖，纯函数测试

### 3.1 测试用例清单

| # | 测试函数 | 输入 | 预期输出 | 验证点 |
|---|---------|------|---------|--------|
| 1 | `test_initial_stability_ratings` | rating=1,2,3,4 | w[0]=0.4, w[1]=0.6, w[2]=2.4, w[3]=5.0 | 初始稳定性映射 |
| 2 | `test_initial_difficulty_bounds` | rating=1,2,3,4 | 全在 [1.0, 10.0] | 难度值范围 |
| 3 | `test_initial_difficulty_decreases_with_rating` | rating 1→4 | difficulty 递减 | 高评分 = 低难度 |
| 4 | `test_update_difficulty_converges` | 初始 d=8, rating=4 多次 | d 趋向均值 | 均值回归特性 |
| 5 | `test_update_stability_again_lapses` | s=5.0, rating=1 | s=2.5 | Again 衰减 50% |
| 6 | `test_update_stability_easy_increases` | s=5.0, d=3, rating=4 | s > 5.0 | Easy 增长 |
| 7 | `test_update_stability_zero_stability` | s=0, rating=3 | s = initial_stability(3) | 零稳定性回退 |
| 8 | `test_retrievability_at_zero_days` | s=5.0, elapsed=0 | 1.0 | 刚复习时记忆率 100% |
| 9 | `test_retrievability_decreases_over_time` | s=5.0, elapsed=1,5,10 | R 递减 | 遗忘曲线递减 |
| 10 | `test_retrievability_zero_stability` | s=0 | 0.0 | 零稳定性 = 零记忆率 |
| 11 | `test_next_review_future_date` | s=5.0 | 日期 > now | 下次复习在未来 |
| 12 | `test_next_review_zero_stability` | s=0 | 1 天后 | 零稳定性 = 明天复习 |
| 13 | `test_classify_mastery_levels` | 0.05, 0.2, 0.45, 0.7, 0.9 | not_started, attempted, familiar, proficient, mastered | 5 级分类边界 |
| 14 | `test_classify_mastery_boundary_values` | 0.1, 0.3, 0.6, 0.85 | attempted, familiar, proficient, mastered | 边界值归属 |
| 15 | `test_rating_from_correctness_mapping` | 4 种组合 | 1(Again), 2(Hard), 3(Good), 4(Easy) | 正确性→FSRS 映射 |

### 3.2 示例测试代码

```python
"""FSRS 算法单元测试。"""
import math
from datetime import datetime, timezone

import pytest

from app.agents.services.fsrs import (
    DEFAULT_PARAMS,
    calculate_next_review,
    calculate_retrievability,
    classify_mastery_level,
    initial_difficulty,
    initial_stability,
    rating_from_correctness,
    update_difficulty,
    update_stability,
)


class TestInitialValues:
    def test_initial_stability_ratings(self):
        assert initial_stability(1) == DEFAULT_PARAMS.w[0]
        assert initial_stability(2) == DEFAULT_PARAMS.w[1]
        assert initial_stability(3) == DEFAULT_PARAMS.w[2]
        assert initial_stability(4) == DEFAULT_PARAMS.w[3]

    def test_initial_difficulty_bounds(self):
        for rating in range(1, 5):
            d = initial_difficulty(rating)
            assert 1.0 <= d <= 10.0

    def test_initial_difficulty_decreases_with_rating(self):
        d1 = initial_difficulty(1)
        d4 = initial_difficulty(4)
        assert d1 > d4  # 评分越高，初始难度越低


class TestUpdateFunctions:
    def test_update_stability_again_lapses(self):
        new_s = update_stability(difficulty=5.0, stability=5.0, rating=1)
        assert new_s == pytest.approx(2.5, abs=0.01)

    def test_update_stability_easy_increases(self):
        new_s = update_stability(difficulty=3.0, stability=5.0, rating=4)
        assert new_s > 5.0

    def test_update_stability_zero_stability_fallback(self):
        new_s = update_stability(difficulty=5.0, stability=0, rating=3)
        assert new_s == initial_stability(3)

    def test_update_difficulty_converges(self):
        d = 8.0
        for _ in range(10):
            d = update_difficulty(d, rating=4)
        assert d < 8.0  # 向均值回归


class TestRetrievability:
    def test_at_zero_days(self):
        r = calculate_retrievability(stability=5.0, elapsed_days=0)
        assert r == pytest.approx(1.0, abs=0.01)

    def test_decreases_over_time(self):
        r1 = calculate_retrievability(5.0, elapsed_days=1)
        r5 = calculate_retrievability(5.0, elapsed_days=5)
        r10 = calculate_retrievability(5.0, elapsed_days=10)
        assert r1 > r5 > r10

    def test_zero_stability(self):
        assert calculate_retrievability(0, elapsed_days=5) == 0.0


class TestMasteryClassification:
    @pytest.mark.parametrize("value,expected", [
        (0.05, "not_started"),
        (0.1, "attempted"),
        (0.25, "attempted"),
        (0.3, "familiar"),
        (0.5, "familiar"),
        (0.6, "proficient"),
        (0.8, "proficient"),
        (0.85, "mastered"),
        (0.95, "mastered"),
    ])
    def test_classify(self, value, expected):
        assert classify_mastery_level(value) == expected


class TestRatingMapping:
    def test_wrong_answer_is_again(self):
        assert rating_from_correctness(is_correct=False, hint_level=0) == 1

    def test_correct_no_hint_is_easy(self):
        assert rating_from_correctness(is_correct=True, hint_level=0) == 4

    def test_correct_with_hint_is_good(self):
        assert rating_from_correctness(is_correct=True, hint_level=1) == 3

    def test_correct_with_many_hints_is_hard(self):
        assert rating_from_correctness(is_correct=True, hint_level=3) == 2
```

---

## 4. 单元测试 — 知识追踪

> 文件: `tests/unit/test_knowledge_tracker.py`
> 目标: 验证掌握度更新逻辑正确性
> 需要 DB session（用内存 SQLite）

### 4.1 测试用例清单

| # | 测试函数 | 输入 | 预期输出 | 验证点 |
|---|---------|------|---------|--------|
| 1 | `test_update_mastery_correct_increases` | mastery=0.5, correct | new > 0.5 | 正确 → 掌握度上升 |
| 2 | `test_update_mastery_wrong_decreases` | mastery=0.5, incorrect | new < 0.5 | 错误 → 掌握度下降 |
| 3 | `test_update_mastery_bounded_0_1` | mastery=0.99, correct | ≤ 1.0 | 不超过 1.0 |
| 4 | `test_update_mastery_bounded_0` | mastery=0.01, incorrect | ≥ 0.0 | 不低于 0.0 |
| 5 | `test_update_mastery_hint_penalty` | mastery=0.5, correct, hint=2 | 比 hint=0 低 | 提示越多，掌握度越低 |
| 6 | `test_update_mastery_high_difficulty_bonus` | correct, difficulty=8 | 比难度 5 高 | 高难度正确有奖励 |
| 7 | `test_apply_updates_creates_new_state` | 全新知识点 | 创建 KnowledgeState | 首次答题自动创建记录 |
| 8 | `test_apply_updates_updates_existing` | 已有记录 | 更新 mastery/difficulty/stability | 增量更新 |
| 9 | `test_apply_updates_fsrs_rating_4` | correct, no hint | stability 增长显著 | Easy rating → 稳定性大幅增长 |
| 10 | `test_apply_updates_fsrs_rating_1` | incorrect | lapse_count++ | Again rating → 记录遗忘 |

### 4.2 示例测试代码

```python
"""知识追踪单元测试。"""
from uuid import uuid4

import pytest

from app.agents.services.knowledge_tracker import update_mastery, apply_knowledge_updates


class TestUpdateMastery:
    def test_correct_increases(self):
        new = update_mastery(0.5, is_correct=True, difficulty=5.0)
        assert new > 0.5

    def test_wrong_decreases(self):
        new = update_mastery(0.5, is_correct=False, difficulty=5.0)
        assert new < 0.5

    def test_bounded_upper(self):
        new = update_mastery(0.99, is_correct=True, difficulty=10)
        assert new <= 1.0

    def test_bounded_lower(self):
        new = update_mastery(0.01, is_correct=False, difficulty=1)
        assert new >= 0.0

    def test_hint_penalty(self):
        no_hint = update_mastery(0.5, is_correct=True, difficulty=5.0, hint_level=0)
        with_hint = update_mastery(0.5, is_correct=True, difficulty=5.0, hint_level=2)
        assert no_hint > with_hint

    def test_difficulty_bonus(self):
        easy = update_mastery(0.5, is_correct=True, difficulty=3, problem_difficulty=3)
        hard = update_mastery(0.5, is_correct=True, difficulty=5, problem_difficulty=8)
        assert hard >= easy
```

---

## 5. 单元测试 — 题目选择器

> 文件: `tests/unit/test_problem_selector.py`
> 目标: 验证自适应选题策略
> 需要 DB + 种子题目

### 5.1 测试用例清单

| # | 测试函数 | 场景 | 预期行为 |
|---|---------|------|---------|
| 1 | `test_select_due_review_first` | 有 FSRS-due 知识点 + 题目 | 优先选复习题 |
| 2 | `test_select_weakest_when_no_due` | 无 due 复习 | 选最薄弱知识点对应题 |
| 3 | `test_exclude_recently_attempted` | 7 天内做过的题 | 不选该题 |
| 4 | `test_exclude_session_problems` | 本次会话做过的题 | 不选该题 |
| 5 | `test_no_matching_problem` | 无匹配题目 | 返回 None |
| 6 | `test_difficulty_range_filter` | 目标难度 3 | 选 difficulty ∈ [2, 4] |

---

## 6. 单元测试 — Prompt 模板

> 文件: `tests/unit/test_prompts.py`
> 目标: 验证所有模板可渲染且变量完整
> 无外部依赖

### 6.1 测试用例清单

| # | 测试函数 | 验证点 |
|---|---------|------|
| 1 | `test_all_prompts_registered` | 8 个 key 全部在 registry 中 |
| 2 | `test_list_prompts_returns_all` | `list_prompts()` 返回 8 个 |
| 3 | `test_math_socratic_renders` | 传入全部变量，无 `{var}` 残留 |
| 4 | `test_math_course_renders` | 同上 |
| 5 | `test_ket_writing_renders` | 同上，JSON 示例中 `{{` 保留 |
| 6 | `test_error_diagnosis_renders` | 同上 |
| 7 | `test_chn_writing_renders` | 同上 |
| 8 | `test_poetry_teaching_renders` | 同上 |
| 9 | `test_poetry_dictation_renders` | 同上 |
| 10 | `test_poetry_scoring_renders` | 同上 |
| 11 | `test_missing_variable_left_as_is` | 缺少变量时保留 `{var}` 不报错 |
| 12 | `test_json_braces_preserved` | 模板中 `{{` 和 `}}` 渲染为 `{` 和 `}` |

### 6.2 示例测试代码

```python
"""Prompt 模板单元测试。"""
from app.agents.prompts import get_system_prompt, list_prompts


EXPECTED_PROMPTS = [
    "math_socratic", "math_course", "ket_writing", "error_diagnosis",
    "chn_writing", "poetry_teaching", "poetry_dictation", "poetry_scoring",
]


def test_all_prompts_registered():
    for key in EXPECTED_PROMPTS:
        prompt = get_system_prompt(key)
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # 每个模板至少 100 字符


def test_list_prompts_returns_all():
    result = list_prompts()
    assert set(result) == set(EXPECTED_PROMPTS)


def test_math_socratic_renders():
    prompt = get_system_prompt(
        "math_socratic",
        student_name="小明",
        grade_level="5",
        target_exam="AMC8",
        mastery_level="familiar",
        mastered_kps="algebra.01",
        weak_areas="geometry",
        problem_markdown="2x+3=7",
        correct_answer="B",
        reference_solutions="标准解法...",
        hint_level=0,
    )
    # 渲染后不应有未替换的模板变量（JSON 中的 {{ }} 除外）
    assert "{student_name}" not in prompt
    assert "{grade_level}" not in prompt


def test_missing_variable_left_as_is():
    prompt = get_system_prompt("math_socratic", student_name="小明")
    # 缺少变量保留原样，不报错
    assert isinstance(prompt, str)


def test_json_braces_preserved():
    prompt = get_system_prompt("error_diagnosis",
        problem="test", student_answer="A",
        correct_answer="B", student_work="",
    )
    # JSON 示例中的花括号应保留
    assert "feedback" in prompt or "{" in prompt
```

---

## 7. 单元测试 — Agent 节点 (Mock LLM)

> 文件: `tests/agents/test_*.py`
> 目标: 验证每个节点的路由/逻辑正确性
> LLM 全部 Mock，不发起真实 API 调用

### 7.1 Mock LLM 策略

```python
# tests/agents/conftest.py
"""Agent 测试共享 fixtures — Mock LLM。"""
from unittest.mock import AsyncMock, patch

import pytest

from langchain_core.messages import AIMessage


@pytest.fixture
def mock_llm():
    """返回一个 Mock LLM，可自定义 ainvoke 返回值。"""
    llm = AsyncMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(content='{"intent": "learn", "target_agent": "tutor", "subject": "amc_math", "session_mode": "practice"}'))
    return llm


@pytest.fixture
def mock_llm_unavailable():
    """Mock is_llm_available() 返回 False。"""
    with patch("app.agents.llm.is_llm_available", return_value=False):
        yield
```

### 7.2 Router 测试 (`test_router.py`)

| # | 测试函数 | 输入 | 预期路由 | 验证点 |
|---|---------|------|---------|--------|
| 1 | `test_attempt_routes_to_assessor` | request_type="attempt" | target="assessor" | 答题请求直通 assessor |
| 2 | `test_session_init_routes_to_curriculum` | request_type="session_init" | target="curriculum" | 会话初始化走 curriculum |
| 3 | `test_learn_keyword_routes_to_tutor` | "教我一元二次方程" + Mock LLM | target="tutor", intent="learn" | LLM 分类正确 |
| 4 | `test_practice_keyword_routes_to_tutor` | "给我提示" + Mock LLM | target="tutor", intent="practice" | 练习关键词识别 |
| 5 | `test_assess_keyword_routes_to_assessor` | "我写完了" + Mock LLM | target="assessor" | 评估关键词识别 |
| 6 | `test_manage_keyword_routes_to_curriculum` | "看看我的进度" + Mock LLM | target="curriculum" | 管理关键词识别 |
| 7 | `test_fallback_when_llm_fails` | Mock LLM 抛异常 | 规则匹配降级 | LLM 失败时回退到规则 |
| 8 | `test_fallback_when_no_api_key` | is_llm_available=False | 规则匹配 | 无 Key 时纯规则路由 |

### 7.3 Assessor 测试 (`test_assessor.py`)

| # | 测试函数 | 场景 | 预期行为 |
|---|---------|------|---------|
| 1 | `test_mcq_correct_answer` | answer="B", correct="B" | is_correct=True, "Correct!" |
| 2 | `test_mcq_wrong_answer` | answer="A", correct="B" | is_correct=False, "correct answer is B" |
| 3 | `test_mcq_case_insensitive` | answer="b", correct="B" | is_correct=True |
| 4 | `test_mcq_generates_knowledge_update` | correct MCQ answer | knowledge_updates 有 1 条 |
| 5 | `test_non_mcq_no_llm_fallback` | format="essay", no API key | "Answer recorded..." fallback |
| 6 | `test_error_diagnosis_prompt_selected` | subject="amc_math" | prompt_key="error_diagnosis" |
| 7 | `test_ket_writing_prompt_selected` | subject="ket_english", format="essay" | prompt_key="ket_writing" |
| 8 | `test_chn_writing_prompt_selected` | subject="chn_composition" | prompt_key="chn_writing" |
| 9 | `test_poetry_dictation_prompt_selected` | subject="chn_poetry", format="dictation" | prompt_key="poetry_dictation" |
| 10 | `test_llm_json_response_parsed` | Mock LLM 返回 JSON | structured_data 有 is_correct |
| 11 | `test_llm_unparsed_response` | Mock LLM 返回纯文本 | evaluation_method="llm_unstructured" |

### 7.4 Tutor 测试 (`test_tutor.py`)

| # | 测试函数 | 场景 | 预期行为 |
|---|---------|------|---------|
| 1 | `test_fallback_when_no_llm` | 无 API Key | 返回 fallback 消息 |
| 2 | `test_math_practice_uses_socratic_prompt` | subject="amc_math", mode="practice" | prompt_key="math_socratic" |
| 3 | `test_math_course_uses_course_prompt` | subject="amc_math", mode="course" | prompt_key="math_course" |
| 4 | `test_poetry_uses_teaching_prompt` | subject="chn_poetry", mode="course" | prompt_key="poetry_teaching" |
| 5 | `test_default_prompt_is_socratic` | 未知 subject/mode | 默认 math_socratic |
| 6 | `test_conversation_history_included` | session_messages 有 5 条 | messages 列表包含历史 |
| 7 | `test_history_limited_to_10` | session_messages 有 15 条 | 只取最近 10 条 |

### 7.5 Curriculum 测试 (`test_curriculum.py`)

| # | 测试函数 | 场景 | 预期行为 |
|---|---------|------|---------|
| 1 | `test_session_init_with_due_reviews` | 2 个 FSRS-due 知识点 | 提到 "2 knowledge points due" |
| 2 | `test_session_init_no_due_reviews` | 无 due 复习 | "Welcome!" 消息 |
| 3 | `test_session_init_recommendation_review` | 有 due | recommendation="review" |
| 4 | `test_session_init_recommendation_learn` | 无 due | recommendation="learn_new" |
| 5 | `test_next_problem_returns_problem` | DB 中有匹配题目 | 返回题目 markdown |
| 6 | `test_next_problem_no_match` | 无匹配题目 | "No more problems available" |
| 7 | `test_general_query_no_llm` | 无 API Key | "requires internet connection" |
| 8 | `test_progress_summary_format` | 3 个 knowledge_states | 包含学生名 + 统计 |

### 7.6 Orchestrator 测试 (`test_orchestrator.py`)

| # | 测试函数 | 场景 | 预期行为 |
|---|---------|------|---------|
| 1 | `test_loads_student_context` | 有效 student_id | student dict 有 name/grade |
| 2 | `test_loads_session_messages` | 有效 session_id | session_messages 列表 |
| 3 | `test_loads_problem_data` | 有效 problem_id | problem_data dict |
| 4 | `test_handles_missing_student` | 无效 student_id | student dict 只有 student_id |
| 5 | `test_handles_missing_problem` | 无效 problem_id | 无 problem_data key |

---

## 8. 集成测试 — Agent Graph 全流程

> 文件: `tests/agents/test_graph.py`
> 目标: 验证 `run_agent()` 端到端正确性
> 需要 DB + Mock LLM

### 8.1 测试用例清单

| # | 测试函数 | 场景 | 验证点 |
|---|---------|------|--------|
| 1 | `test_chat_message_flow` | 发送聊天 → orchestrator → router → tutor → response | AI 消息持久化到 DB |
| 2 | `test_attempt_flow_mcq_correct` | 提交正确答案 → assessor → response | StudentAttempt + KnowledgeState 正确更新 |
| 3 | `test_attempt_flow_mcq_wrong` | 提交错误答案 | is_correct=False, knowledge_update 产生 |
| 4 | `test_session_init_flow` | session_init 请求 → curriculum | 返回 recommendation |
| 5 | `test_graph_degraded_no_llm` | 无 API Key | 聊天返回 fallback, MCQ 仍然评分 |
| 6 | `test_knowledge_update_persisted` | attempt 后检查 DB | mastery/difficulty/stability 已更新 |

### 8.2 示例测试代码

```python
"""Graph 集成测试。"""
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest

from langchain_core.messages import AIMessage

from app.agents import run_agent


@pytest.fixture
def mock_strong_llm():
    """Mock strong LLM 返回教学回复。"""
    llm = AsyncMock()
    llm.ainvoke = AsyncMock(return_value=AIMessage(
        content="让我们想想，什么数字乘以 2 等于 4？"
    ))
    with patch("app.agents.llm.get_llm", return_value=llm):
        yield llm


async def test_chat_message_flow(db_session, student, mock_strong_llm):
    """聊天消息走完整 graph 流程。"""
    session_id = uuid4()
    result = await run_agent(
        session_id=session_id,
        student_id=student.id,
        user_message="我不理解为什么 2×2=4",
        request_type="chat",
    )

    assert result["agent_response"]  # 有响应
    assert result["error"] is None


async def test_attempt_mcq_correct(db_session, student, mcq_problem):
    """MCQ 正确答案走 assessor 路径，无 LLM 也能工作。"""
    with patch("app.agents.llm.is_llm_available", return_value=False):
        result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="B",
            request_type="attempt",
            problem_id=mcq_problem.id,
            student_answer="B",
        )

    assert result["structured_data"]["is_correct"] is True
    assert "Correct" in result["agent_response"]
```

---

## 9. 集成测试 — API 端点

> 文件: `tests/api/test_chat.py` + `tests/api/test_problems.py`
> 目标: 验证 HTTP 层正确性
> 需要 client fixture + Mock LLM

### 9.1 Chat API 测试

| # | 测试函数 | 请求 | 预期 | 验证点 |
|---|---------|------|------|--------|
| 1 | `test_send_message_creates_session` | POST /chat/message, 无 session_id | 201 + session_id | 自动创建会话 |
| 2 | `test_send_message_existing_session` | POST /chat/message, 有 session_id | 200 + 消息 | 使用已有会话 |
| 3 | `test_send_message_requires_auth` | 无 Authorization header | 403 | 认证守卫 |
| 4 | `test_send_message_invalid_session` | 不存在的 session_id | 404 | 会话不存在 |
| 5 | `test_send_message_persists_conversation` | 发送消息 | DB 中有 user + assistant 消息 | 双向持久化 |

### 9.2 Problems API 测试

| # | 测试函数 | 请求 | 预期 | 验证点 |
|---|---------|------|------|--------|
| 1 | `test_submit_attempt_correct` | POST /problems/{id}/attempt, answer="B" | is_correct=True | MCQ 正确评分 |
| 2 | `test_submit_attempt_wrong` | answer="A" | is_correct=False | MCQ 错误评分 |
| 3 | `test_submit_attempt_requires_auth` | 无 header | 403 | 认证守卫 |
| 4 | `test_submit_attempt_returns_error_type` | 错误答案 | error_type 字段存在 | 新增字段 |
| 5 | `test_list_problems_still_works` | GET /problems | 200 + 列表 | 现有端点不受影响 |

---

## 10. 端到端测试 — 完整学习场景

> 文件: `tests/e2e/test_learning_flow.py`
> 目标: 验证典型学习路径的完整流程

### 10.1 场景清单

| # | 场景 | 步骤 | 验证点 |
|---|------|------|--------|
| 1 | **新学生首次学习** | session_init → chat(学概念) → practice(做题) → attempt(答题) | 初始化推荐 → 对话正常 → 答题评分 → knowledge state 创建 |
| 2 | **FSRS 复习循环** | 创建 1 天前的 knowledge_state(next_review=now) → session_init | 识别到期复习 → recommendation="review" |
| 3 | **多轮对话记忆** | 连续发送 3 条消息 | 每条都能获取到之前的对话历史 |
| 4 | **错误后知识追踪** | 答错 MCQ → 检查 mastery 下降 → 再答对 → 检查 mastery 上升 | 掌握度先降后升 |
| 5 | **降级模式** | 设置 OPENAI_API_KEY="" → 聊天 → MCQ 答题 | 聊天返回 fallback，MCQ 正常评分 |

### 10.2 示例场景测试

```python
"""E2E: 新学生首次学习流程。"""


async def test_new_student_first_session(
    client, student, knowledge_points, mcq_problem, auth_token
):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Step 1: 初始化会话
    resp = await client.post("/sessions", json={
        "session_type": "practice",
        "subject": "amc_math",
    }, headers=headers)
    assert resp.status_code == 200
    session_id = resp.json()["id"]

    # Step 2: 聊天求助
    resp = await client.post("/chat/message", json={
        "session_id": session_id,
        "content": "教我一元一次方程",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "assistant"

    # Step 3: 答题
    with patch("app.agents.llm.is_llm_available", return_value=False):
        resp = await client.post(
            f"/problems/{mcq_problem.id}/attempt",
            json={"answer": "B", "session_id": session_id},
            headers=headers,
        )
    assert resp.status_code == 200
    assert resp.json()["is_correct"] is True
```

---

## 11. 降级测试 — 无 API Key 场景

> 贯穿各层测试，确保系统在无 OPENAI_API_KEY 时仍然可用

### 11.1 降级矩阵

| 组件 | 有 API Key | 无 API Key |
|------|-----------|-----------|
| **Router** | LLM 分类意图 | 关键词规则匹配 |
| **Tutor** | LLM 苏格拉底式教学 | 返回固定 fallback 消息 |
| **Assessor (MCQ)** | 精确匹配（不用 LLM） | **相同** — 精确匹配 |
| **Assessor (非 MCQ)** | LLM 评分 | "Answer recorded..." 记录但不评分 |
| **Curriculum** | LLM 进度查询 | "requires internet connection" |
| **FSRS/知识追踪** | **相同** — 纯算法 | **相同** — 纯算法 |
| **题目选择** | **相同** — 纯 SQL | **相同** — 纯 SQL |

### 11.2 降级测试用例

| # | 测试 | 验证点 |
|---|------|--------|
| 1 | `test_no_key_router_uses_rules` | Router 降级到关键词匹配 |
| 2 | `test_no_key_tutor_returns_fallback` | Tutor 返回 fallback 消息 |
| 3 | `test_no_key_assessor_mcq_still_works` | MCQ 评分正常工作 |
| 4 | `test_no_key_assessor_non_mcq_records` | 非 MCQ 记录但不评分 |
| 5 | `test_no_key_curriculum_returns_message` | Curriculum 返回提示信息 |
| 6 | `test_no_key_fsrs_unaffected` | FSRS 算法不受影响 |
| 7 | `test_no_key_problem_selector_unaffected` | 选题算法不受影响 |

---

## 12. 测试脚本 & 运行方式

### 12.1 运行命令

```bash
# 全部测试
cd backend
pytest tests/ -v --tb=short

# 仅单元测试（最快）
pytest tests/unit/ -v

# 仅 Agent 测试
pytest tests/agents/ -v

# 仅 API 测试
pytest tests/api/ -v

# E2E 测试
pytest tests/e2e/ -v

# 指定文件
pytest tests/unit/test_fsrs.py -v

# 带覆盖率
pytest tests/ --cov=app/agents --cov=app/api --cov-report=term-missing
```

### 12.2 CI 配置 (`.github/workflows/test.yml`)

```yaml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt pytest pytest-asyncio
      - run: cd backend && pytest tests/ -v --tb=short
        env:
          OPENAI_API_KEY: ""  # 确保降级路径被测试
```

### 12.3 测试文件创建优先级

建议按以下顺序实施测试文件：

1. `tests/unit/test_fsrs.py` — 纯函数，零依赖，秒级完成
2. `tests/unit/test_prompts.py` — 纯模板测试，零依赖
3. `tests/unit/test_knowledge_tracker.py` — `update_mastery` 纯函数部分
4. `tests/conftest.py` — 完善 fixture（DB、种子数据、auth）
5. `tests/agents/test_assessor.py` — MCQ 评分是核心路径
6. `tests/agents/test_router.py` — 路由逻辑验证
7. `tests/agents/test_tutor.py` — Tutor prompt 选择
8. `tests/agents/test_curriculum.py` — FSRS due 检测
9. `tests/agents/test_graph.py` — 全流程集成
10. `tests/api/test_chat.py` + `tests/api/test_problems.py` — HTTP 层
11. `tests/e2e/test_learning_flow.py` — 完整场景

---

## 附录 A: Mock LLM 辅助工具

```python
# tests/helpers.py
"""测试辅助工具。"""
from unittest.mock import AsyncMock
from langchain_core.messages import AIMessage
import json


def make_mock_llm(response_content: str | dict):
    """创建 Mock LLM。

    Args:
        response_content: 字符串（纯文本回复）或 dict（自动序列化为 JSON）
    """
    llm = AsyncMock()
    if isinstance(response_content, dict):
        content = json.dumps(response_content, ensure_ascii=False)
    else:
        content = response_content
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=content))
    return llm


# 预定义 Mock 响应
ROUTER_RESPONSE_LEARN = {"intent": "learn", "target_agent": "tutor", "subject": "amc_math", "session_mode": "course"}
ROUTER_RESPONSE_PRACTICE = {"intent": "practice", "target_agent": "tutor", "subject": "amc_math", "session_mode": "practice"}
ROUTER_RESPONSE_ASSESS = {"intent": "assess", "target_agent": "assessor", "subject": "amc_math", "session_mode": "practice"}
ROUTER_RESPONSE_MANAGE = {"intent": "manage", "target_agent": "curriculum", "subject": "amc_math", "session_mode": "practice"}

ASSESSOR_CORRECT = {"is_correct": True, "feedback": "Correct! Well done.", "error_type": None}
ASSESSOR_WRONG = {"is_correct": False, "feedback": "Not quite right.", "error_type": "concept_misunderstanding"}

TUTOR_RESPONSE = "让我们想想，2x + 3 = 7 中，如果先减去 3，得到什么？"
```

## 附录 B: 测试数量统计

| 分类 | 文件数 | 测试数 | 预计耗时 |
|------|-------|-------|---------|
| Unit — FSRS | 1 | 15 | < 1s |
| Unit — Knowledge Tracker | 1 | 10 | < 1s |
| Unit — Problem Selector | 1 | 6 | < 2s |
| Unit — Prompts | 1 | 12 | < 1s |
| Unit — LLM Factory | 1 | 3 | < 1s |
| Agent — Router | 1 | 8 | < 2s |
| Agent — Assessor | 1 | 11 | < 2s |
| Agent — Tutor | 1 | 7 | < 2s |
| Agent — Curriculum | 1 | 8 | < 2s |
| Agent — Orchestrator | 1 | 5 | < 2s |
| Integration — Graph | 1 | 6 | < 5s |
| Integration — API | 2 | 10 | < 5s |
| E2E | 1 | 5 | < 10s |
| **合计** | **14** | **~107** | **< 35s** |
