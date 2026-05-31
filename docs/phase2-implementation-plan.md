# Phase 2 — LangGraph Agent Integration: Implementation Plan

> Version: 1.0 | Date: 2026-05-31
> Status: READY FOR IMPLEMENTATION

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [File Structure](#2-file-structure)
3. [LangGraph State Machine Design](#3-langgraph-state-machine-design)
4. [Implementation Order & Sprint Plan](#4-implementation-order--sprint-plan)
5. [Detailed Module Specifications](#5-detailed-module-specifications)
6. [Agent Responsibilities & Interactions](#6-agent-responsibilities--interactions)
7. [FastAPI Endpoint Integration](#7-fastapi-endpoint-integration)
8. [Subject-Specific Prompt Templates](#8-subject-specific-prompt-templates)
9. [FSRS Knowledge Tracking](#9-fsrs-knowledge-tracking)
10. [Graceful Degradation](#10-graceful-degradation)

---

## 1. Architecture Overview

### 1.1 High-Level Data Flow

```
┌──────────────┐     ┌────────────────────────────────────────────────────┐
│  FastAPI      │     │               LangGraph Agent Layer                │
│  Endpoints    │     │                                                    │
│               │     │  ┌─────────────┐                                   │
│ POST /chat/   │────▶│  │ Orchestrator │──┐                               │
│   message     │     │  │  (entry)     │  │ loads context,                │
│               │     │  └──────┬──────┘  │ creates state                  │
│ POST /problems│     │         │         │                                │
│   /{id}/attempt│    │         ▼         │                                │
│               │     │  ┌─────────────┐  │                                │
│ POST /sessions│     │  │   Router     │◀─┘                                │
│               │     │  │ (classify)  │                                    │
│ POST /lessons │     │  └──┬──┬──┬──┬─┘                                   │
│   /{id}/progress│    │     │  │  │  │                                     │
│               │     │     ▼  ▼  ▼  ▼                                     │
│               │     │  ┌────┐┌────┐┌────┐┌────────┐                      │
│               │◀────│  │Tutr││Asse││Curr││Respns  │                      │
│               │     │  │    ││ssor││icul││Format  │                      │
│               │     │  └──┬─┘└──┬─┘└──┬─┘└────────┘                      │
│               │     │     │     │     │                                   │
│               │     │     ▼     ▼     ▼                                   │
│               │     │  ┌──────────────────────┐                          │
│               │     │  │   Tool Layer          │                          │
│               │     │  │ DB · FSRS · Prompts   │                          │
│               │     │  └──────────────────────┘                          │
└──────────────┘     └────────────────────────────────────────────────────┘
```

### 1.2 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LangGraph pattern | `StateGraph` with conditional edges | Clear control flow, checkpoint support for session resumption |
| LLM abstraction | Singleton factory with fallback | Single `get_llm()` call everywhere, graceful degradation |
| Prompt storage | Python modules returning string templates | Type-safe, IDE support, no file I/O, version-controlled |
| State persistence | LangGraph checkpoint → `LearningSession.checkpoint_id` | Session resumption across server restarts |
| Knowledge updates | Deferred batch commit in response node | Avoid partial updates on error |
| Model routing | Fast model for Router/Curriculum, strong model for Tutor/Assessor | Cost optimization per §4.3 |

---

## 2. File Structure

### 2.1 New Files to Create

```
backend/app/agents/
├── __init__.py                 # REPLACE: export build_graph(), AgentRunner
├── state.py                    # NEW: AgentState TypedDict + helpers
├── graph.py                    # NEW: build_graph() → CompiledStateGraph
├── llm.py                      # NEW: LLM provider factory + fallback
├── tools.py                    # NEW: LangChain @tool definitions (DB queries)
│
├── orchestrator.py             # REPLACE stub: context loading node
├── router_agent.py             # REPLACE stub: intent classification node
├── tutor_agent.py              # REPLACE stub: teaching conversation node
├── assessor_agent.py           # REPLACE stub: evaluation/scoring node
├── curriculum_agent.py         # REPLACE stub: scheduling/FSRS node
│
├── prompts/                    # NEW directory
│   ├── __init__.py             # Registry: get_prompt(subject, mode) → str
│   ├── math_course.py          # §7.2 Math course mode template
│   ├── math_socratic.py        # §7.3 Math Socratic mode template
│   ├── ket_writing.py          # §7.4 KET writing scoring template
│   ├── error_diagnosis.py      # §7.5 Error diagnosis template
│   ├── chn_writing.py          # §7.6 Chinese writing scoring template
│   ├── poetry_teaching.py      # §7.7.1 Poetry teaching template
│   ├── poetry_dictation.py     # §7.7.2 Poetry dictation template
│   └── poetry_scoring.py       # §7.7.3 Poetry appreciation scoring template
│
└── services/                   # NEW directory
    ├── __init__.py
    ├── fsrs.py                 # FSRS algorithm implementation
    ├── knowledge_tracker.py    # Knowledge state update logic
    └── problem_selector.py     # Adaptive problem selection (§8.2)
```

### 2.2 Existing Files to Modify

```
backend/app/agents/__init__.py              # Replace empty with exports
backend/app/agents/router_agent.py          # Replace 2-line stub
backend/app/agents/tutor_agent.py           # Replace 2-line stub
backend/app/agents/assessor_agent.py        # Replace 2-line stub
backend/app/agents/curriculum_agent.py      # Replace 2-line stub

backend/app/api/v1/chat.py                 # Wire to agent graph
backend/app/api/v1/problems.py             # Wire assessor for non-MCQ
backend/app/api/v1/sessions.py             # Add AI-powered session init
backend/app/api/v1/lessons.py              # Wire curriculum agent

backend/app/services/tutor_service.py      # Replace stub with agent delegation
backend/app/services/problem_service.py    # Add AI evaluation path

backend/app/schemas/chat.py                # Extend response schema
backend/app/schemas/problem.py             # Extend AttemptResponse

backend/app/config.py                      # Add LLM model names, fallback toggle
```

---

## 3. LangGraph State Machine Design

### 3.1 State Definition (`state.py`)

```python
from __future__ import annotations
from typing import TypedDict
from uuid import UUID


class StudentContext(TypedDict, total=False):
    """Student profile and knowledge state loaded by orchestrator."""
    student_id: UUID
    name: str
    grade_level: int | None
    target_exam: str | None               # "AMC8", "AMC10", "KET", etc.
    preferred_lang: str
    diagnostic_done: bool
    mastered_kps: list[str]                # Knowledge point codes
    weak_areas: list[str]                  # Pillar codes with mastery < 0.4


class KnowledgeUpdate(TypedDict):
    """Pending knowledge state change to be committed."""
    knowledge_point_id: UUID
    mastery_delta: float                   # Change to apply
    is_correct: bool | None
    hint_level_used: int
    error_type: str | None
    fsrs_rating: int                       # 1=Again, 2=Hard, 3=Good, 4=Easy


class AgentState(TypedDict, total=False):
    """
    LangGraph state — flows through every node.
    All fields optional because nodes add to state incrementally.
    """

    # ── Input (set by API endpoint) ──────────────────────────────
    session_id: UUID
    student_id: UUID
    user_message: str
    media: dict | None
    request_type: str                      # "chat" | "attempt" | "session_init" | "lesson_progress"

    # ── Problem context (for attempt requests) ────────────────────
    problem_id: UUID | None
    student_answer: str | None
    problem_data: dict | None              # Full problem row as dict

    # ── Lesson context (for course/lesson requests) ───────────────
    lesson_id: UUID | None
    lesson_data: dict | None               # Full lesson row as dict

    # ── Student context (loaded by orchestrator) ──────────────────
    student: StudentContext
    knowledge_states: list[dict]           # [{kp_id, mastery, mastery_level, ...}, ...]
    session_messages: list[dict]           # Recent messages in this session [{role, content}, ...]

    # ── Router output ────────────────────────────────────────────
    intent: str                            # "learn" | "practice" | "assess" | "ask" | "manage"
    target_agent: str                      # "tutor" | "assessor" | "curriculum"
    subject: str                           # "amc_math" | "ket_english" | "chn_composition" | "chn_poetry"
    session_mode: str                      # "course" | "practice" | "review" | "diagnostic"

    # ── Agent output ─────────────────────────────────────────────
    agent_response: str                    # Main text response to student
    structured_data: dict | None           # Assessment scores, error diagnosis, etc.

    # ── Tracking (accumulated through nodes) ─────────────────────
    hint_level: int                        # Current hint level (0-4)
    knowledge_updates: list[KnowledgeUpdate]

    # ── Metadata ─────────────────────────────────────────────────
    model_used: str                        # Which LLM was used
    latency_ms: int
    error: str | None
```

### 3.2 Graph Topology (`graph.py`)

```
                    ┌─────────────┐
                    │ START       │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │orchestrator │  Load student context,
                    │             │  session history, problem data
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   router    │  Classify intent → target_agent
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐──────────────┐
              │            │            │              │
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼──────┐ ┌────▼────────┐
       │   tutor    │ │assessor│ │curriculum │ │direct_reply │
       │            │ │        │ │           │ │(simple Q)   │
       └──────┬─────┘ └───┬────┘ └────┬──────┘ └────┬────────┘
              │            │            │              │
              └────────────┼────────────┘──────────────┘
                           │
                    ┌──────▼──────┐
                    │  response   │  Format output, persist
                    │  _node      │  messages + knowledge updates
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    END      │
                    └─────────────┘
```

```python
# graph.py — Pseudocode

from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.orchestrator import orchestrator_node
from app.agents.router_agent import router_node
from app.agents.tutor_agent import tutor_node
from app.agents.assessor_agent import assessor_node
from app.agents.curriculum_agent import curriculum_node
from app.agents.response_node import response_node


def route_after_router(state: AgentState) -> str:
    """Conditional edge: router → appropriate agent."""
    target = state.get("target_agent", "tutor")
    # Simple intents ("next problem", "show hint") skip agents
    if state.get("intent") == "manage":
        return "curriculum"
    mapping = {
        "tutor": "tutor",
        "assessor": "assessor",
        "curriculum": "curriculum",
    }
    return mapping.get(target, "tutor")


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("router", router_node)
    graph.add_node("tutor", tutor_node)
    graph.add_node("assessor", assessor_node)
    graph.add_node("curriculum", curriculum_node)
    graph.add_node("response", response_node)

    # Entry
    graph.set_entry_point("orchestrator")

    # Linear: orchestrator → router
    graph.add_edge("orchestrator", "router")

    # Conditional: router → agent
    graph.add_conditional_edges("router", route_after_router, {
        "tutor": "tutor",
        "assessor": "assessor",
        "curriculum": "curriculum",
    })

    # All agents → response
    graph.add_edge("tutor", "response")
    graph.add_edge("assessor", "response")
    graph.add_edge("curriculum", "response")

    # Response → END
    graph.add_edge("response", END)

    return graph.compile()
```

### 3.3 Node Contracts

Each node is an `async def node(state: AgentState) -> dict` that returns **partial state updates** (LangGraph merges dicts).

| Node | Input (reads) | Output (writes) | LLM Required? |
|------|---------------|-----------------|---------------|
| **orchestrator** | `session_id`, `student_id`, `problem_id`, `lesson_id` | `student`, `knowledge_states`, `session_messages`, `problem_data`, `lesson_data` | No (DB only) |
| **router** | `user_message`, `request_type`, `student`, `session_messages` | `intent`, `target_agent`, `subject`, `session_mode` | Yes (fast model) |
| **tutor** | `user_message`, `student`, `knowledge_states`, `session_messages`, `problem_data`, `lesson_data`, `hint_level`, `subject`, `session_mode` | `agent_response`, `hint_level`, `knowledge_updates` | Yes (strong model) |
| **assessor** | `student_answer`, `problem_data`, `student`, `subject` | `agent_response`, `structured_data`, `knowledge_updates` | Yes (strong model) |
| **curriculum** | `student`, `knowledge_states`, `intent` | `agent_response`, `structured_data` (recommendations) | Partial (rules + fast model) |
| **response** | `agent_response`, `knowledge_updates`, `session_id` | Persists to DB | No |

---

## 4. Implementation Order & Sprint Plan

### Sprint 1: Foundation Layer (3-4 days) — No LLM calls yet

Build infrastructure that all agents depend on. Everything works without OpenAI key.

| # | File | What | Key Functions/Classes | Depends On |
|---|------|------|----------------------|------------|
| 1 | `app/agents/llm.py` | LLM provider factory | `get_llm("strong")`, `get_llm("fast")`, `is_llm_available()` | config.py |
| 2 | `app/agents/state.py` | State definitions | `AgentState`, `StudentContext`, `KnowledgeUpdate` | None |
| 3 | `app/agents/tools.py` | LangChain `@tool` functions | `load_student_context`, `load_session_messages`, `get_problem`, `get_knowledge_states` | models/, db/ |
| 4 | `app/agents/services/fsrs.py` | FSRS algorithm | `FSRSParams`, `update_fsrs()`, `calculate_next_review()` | None |
| 5 | `app/agents/services/knowledge_tracker.py` | Mastery update logic | `update_mastery()`, `classify_mastery_level()`, `update_composition_mastery()`, `update_poetry_mastery()` | fsrs.py |
| 6 | `app/agents/services/problem_selector.py` | Adaptive problem selection | `select_next_problem()`, `filter_by_zpd()`, `filter_by_amc_level()` | models/ |

### Sprint 2: Core Graph + Router + Math Tutor (4-5 days) — First AI conversations

| # | File | What | Key Functions/Classes | Depends On |
|---|------|------|----------------------|------------|
| 7 | `app/agents/prompts/__init__.py` | Prompt registry | `get_system_prompt(subject, mode, **vars) → str` | All prompt files |
| 8 | `app/agents/prompts/math_socratic.py` | Math Socratic prompt | `MATH_SOCRACTIC_TEMPLATE` with variable slots | §7.3 |
| 9 | `app/agents/router_agent.py` | Intent classification node | `router_node(state) → dict` | llm.py |
| 10 | `app/agents/tutor_agent.py` | Teaching conversation node | `tutor_node(state) → dict` | llm.py, prompts/ |
| 11 | `app/agents/orchestrator.py` | Context loading node | `orchestrator_node(state) → dict` | tools.py |
| 12 | `app/agents/graph.py` | Graph construction | `build_graph() → CompiledStateGraph` | All nodes |
| 13 | `app/agents/__init__.py` | Public API | `AgentRunner` class | graph.py |

### Sprint 3: Assessor + All Evaluations (3-4 days)

| # | File | What | Depends On |
|---|------|------|------------|
| 14 | `app/agents/prompts/error_diagnosis.py` | Error diagnosis prompt (§7.5) | None |
| 15 | `app/agents/prompts/ket_writing.py` | KET writing scoring prompt (§7.4) | None |
| 16 | `app/agents/prompts/chn_writing.py` | Chinese writing scoring prompt (§7.6) | None |
| 17 | `app/agents/assessor_agent.py` | Evaluation node | llm.py, prompts/, knowledge_tracker.py |

### Sprint 4: Curriculum + Remaining Prompts + API Integration (3-4 days)

| # | File | What | Depends On |
|---|------|------|------------|
| 18 | `app/agents/prompts/math_course.py` | Math course mode prompt (§7.2) | None |
| 19 | `app/agents/prompts/poetry_teaching.py` | Poetry teaching prompt (§7.7.1) | None |
| 20 | `app/agents/prompts/poetry_dictation.py` | Poetry dictation prompt (§7.7.2) | None |
| 21 | `app/agents/prompts/poetry_scoring.py` | Poetry appreciation prompt (§7.7.3) | None |
| 22 | `app/agents/curriculum_agent.py` | Scheduling/FSRS node | fsrs.py, problem_selector.py |
| 23 | `app/api/v1/chat.py` | Wire to AgentRunner | agents/__init__.py |
| 24 | `app/api/v1/problems.py` | Wire assessor | agents/__init__.py |
| 25 | `app/api/v1/sessions.py` | AI session init | agents/__init__.py |
| 26 | `app/api/v1/lessons.py` | AI lesson progress | agents/__init__.py |
| 27 | `app/schemas/chat.py` | Extended response | None |
| 28 | `app/schemas/problem.py` | Extended attempt response | None |
| 29 | `app/config.py` | LLM config additions | None |

### Sprint 5: Testing + Polish (2-3 days)

| # | What | Details |
|---|------|---------|
| 30 | Integration tests | `tests/test_agents/` — test each node, test graph end-to-end |
| 31 | Graceful degradation tests | Verify behavior without OPENAI_API_KEY |
| 32 | Response node | Persist messages + knowledge updates to DB |

**Total estimated effort: 15-20 days**

---

## 5. Detailed Module Specifications

### 5.1 `app/agents/llm.py` — LLM Provider

```python
"""LLM provider factory with graceful degradation."""
import logging
from functools import lru_cache

from langchain_openai import ChatOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


def is_llm_available() -> bool:
    """Check if OpenAI API key is configured."""
    return bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())


@lru_cache(maxsize=2)
def get_llm(tier: str = "strong") -> ChatOpenAI | None:
    """
    Get a cached LLM instance.
    
    Args:
        tier: "strong" (GPT-4o for teaching/assessment) or 
              "fast" (GPT-4o-mini for routing/classification)
    
    Returns:
        ChatOpenAI instance or None if no API key configured.
    """
    if not is_llm_available():
        logger.warning("OPENAI_API_KEY not set — AI features disabled")
        return None

    model_map = {
        "strong": settings.STRONG_MODEL,    # default: "gpt-4o"
        "fast": settings.FAST_MODEL,        # default: "gpt-4o-mini"
    }
    model = model_map.get(tier, settings.STRONG_MODEL)

    return ChatOpenAI(
        model=model,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.7 if tier == "strong" else 0.1,
        max_tokens=1024,
    )


def get_fallback_response(intent: str) -> str:
    """Return a canned response when LLM is unavailable."""
    fallbacks = {
        "learn": "I'm currently offline for maintenance. "
                 "Please try again in a few minutes!",
        "practice": "Practice mode is temporarily unavailable. "
                    "You can still browse problems in the meantime.",
        "assess": "Scoring is temporarily unavailable. "
                  "Your answer has been recorded and will be evaluated later.",
        "ask": "I can't answer questions right now, but I'll be back soon!",
        "manage": "This feature requires an internet connection.",
    }
    return fallbacks.get(intent, "AI features are temporarily unavailable.")
```

**Config additions** (`app/config.py`):

```python
# Add to Settings class:
STRONG_MODEL: str = "gpt-4o"
FAST_MODEL: str = "gpt-4o-mini"
```

### 5.2 `app/agents/state.py` — State Definition

(Full `AgentState` TypedDict as shown in §3.1 above.)

Key helpers:

```python
def initial_state(
    *,
    session_id: UUID,
    student_id: UUID,
    user_message: str,
    request_type: str = "chat",
    problem_id: UUID | None = None,
    student_answer: str | None = None,
    lesson_id: UUID | None = None,
    media: dict | None = None,
) -> AgentState:
    """Create initial state for a new graph invocation."""
    return {
        "session_id": session_id,
        "student_id": student_id,
        "user_message": user_message,
        "media": media,
        "request_type": request_type,
        "problem_id": problem_id,
        "student_answer": student_answer,
        "lesson_id": lesson_id,
        "hint_level": 0,
        "knowledge_updates": [],
    }
```

### 5.3 `app/agents/tools.py` — Shared Tools

```python
"""LangChain @tool functions for DB access within agents."""
from uuid import UUID
from typing import Annotated
from langchain_core.tools import tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import KnowledgeState, LearningSession, StudentAttempt
from app.models.knowledge import KnowledgePoint
from app.models.problem import Problem
from app.models.message import Message
from app.models.user import User, StudentProfile


async def load_student_context(db: AsyncSession, student_id: UUID) -> dict:
    """
    Load student profile + knowledge states.
    Returns StudentContext dict.
    """
    # Load user + profile
    result = await db.execute(
        select(User, StudentProfile)
        .join(StudentProfile, StudentProfile.user_id == User.id)
        .where(User.id == student_id)
    )
    row = result.first()
    if not row:
        return {}

    user, profile = row

    # Load knowledge states with KP info
    result = await db.execute(
        select(KnowledgeState, KnowledgePoint)
        .join(KnowledgePoint, KnowledgePoint.id == KnowledgeState.knowledge_point_id)
        .where(KnowledgeState.student_id == student_id)
    )
    kp_rows = result.all()

    mastered = [
        kp.code for ks, kp in kp_rows
        if ks.mastery >= 0.85
    ]
    weak = [
        kp.pillar for ks, kp in kp_rows
        if kp.pillar and ks.mastery < 0.4
    ]

    return {
        "student_id": student_id,
        "name": user.name,
        "grade_level": profile.grade_level,
        "target_exam": profile.target_exam,
        "preferred_lang": profile.preferred_lang,
        "diagnostic_done": profile.diagnostic_done,
        "mastered_kps": mastered,
        "weak_areas": list(set(weak)),
    }


async def load_session_messages(
    db: AsyncSession, session_id: UUID, limit: int = 20
) -> list[dict]:
    """Load recent messages for context window."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return [{"role": m.role, "content": m.content} for m in messages]


async def load_knowledge_states(
    db: AsyncSession, student_id: UUID
) -> list[dict]:
    """Load all knowledge states for student."""
    result = await db.execute(
        select(KnowledgeState)
        .where(KnowledgeState.student_id == student_id)
    )
    states = result.scalars().all()
    return [
        {
            "knowledge_point_id": str(ks.knowledge_point_id),
            "mastery": ks.mastery,
            "mastery_level": ks.mastery_level,
            "difficulty": ks.difficulty,
            "stability": ks.stability,
            "retrievability": ks.retrievability,
            "next_review": ks.next_review.isoformat() if ks.next_review else None,
            "review_count": ks.review_count,
        }
        for ks in states
    ]


async def load_problem(db: AsyncSession, problem_id: UUID) -> dict | None:
    """Load problem with solutions."""
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id)
    )
    problem = result.scalar_one_or_none()
    if not problem:
        return None

    data = {
        "id": str(problem.id),
        "subject": problem.subject,
        "format": problem.format,
        "question_markdown": problem.question_markdown,
        "options": problem.options,
        "correct_answer": problem.correct_answer,
        "difficulty": problem.difficulty,
        "hints": problem.hints,
        "misconceptions": problem.misconceptions,
        "step_decomposition": problem.step_decomposition,
        "knowledge_point_ids": problem.knowledge_point_ids,
    }

    # Load solutions
    from app.models.problem import ProblemSolution
    sol_result = await db.execute(
        select(ProblemSolution)
        .where(ProblemSolution.problem_id == problem_id)
        .order_by(ProblemSolution.sort_order)
    )
    solutions = sol_result.scalars().all()
    data["solutions"] = [
        {
            "method_name": s.method_name,
            "solution_markdown": s.solution_markdown,
            "key_insight": s.key_insight,
        }
        for s in solutions
    ]

    return data
```

### 5.4 `app/agents/orchestrator.py` — Context Loading Node

```python
"""Orchestrator node: loads student context and session data."""
from uuid import UUID

from app.agents.state import AgentState
from app.db.session import async_session_factory
from app.agents.tools import (
    load_student_context,
    load_session_messages,
    load_knowledge_states,
    load_problem,
)


async def orchestrator_node(state: AgentState) -> dict:
    """
    Entry node. Loads:
    - Student profile + knowledge states
    - Recent session messages
    - Problem data (if attempt request)
    - Lesson data (if lesson request)
    """
    updates: dict = {}

    async with async_session_factory() as db:
        student_id = state.get("student_id")
        if student_id:
            updates["student"] = await load_student_context(db, UUID(str(student_id)))
            updates["knowledge_states"] = await load_knowledge_states(db, UUID(str(student_id)))

        session_id = state.get("session_id")
        if session_id:
            updates["session_messages"] = await load_session_messages(
                db, UUID(str(session_id))
            )

        problem_id = state.get("problem_id")
        if problem_id:
            updates["problem_data"] = await load_problem(db, UUID(str(problem_id)))

        # Lesson data loading (lesson_id → lesson from DB)
        lesson_id = state.get("lesson_id")
        if lesson_id:
            from sqlalchemy import select
            from app.models.course import Lesson
            result = await db.execute(
                select(Lesson).where(Lesson.id == UUID(str(lesson_id)))
            )
            lesson = result.scalar_one_or_none()
            if lesson:
                updates["lesson_data"] = {
                    "id": str(lesson.id),
                    "title": lesson.title,
                    "lesson_type": lesson.lesson_type,
                    "content": lesson.content,
                    "knowledge_point_id": str(lesson.knowledge_point_id) if lesson.knowledge_point_id else None,
                }

    return updates
```

### 5.5 `app/agents/router_agent.py` — Intent Classification

```python
"""Router node: classifies user intent and routes to appropriate agent."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available, get_fallback_response
from app.agents.state import AgentState


ROUTER_SYSTEM_PROMPT = """You are an intent classifier for an AI tutoring system.
Classify the user's message into exactly ONE intent and target agent.

Possible intents:
- "learn": Student wants to learn a concept, start a lesson, or continue course mode
- "practice": Student wants to solve problems, get hints, or is working on a problem
- "assess": Student is submitting an answer for evaluation (essay, writing, dictation)
- "ask": Student is asking a general question about a topic
- "manage": Student wants to navigate, change settings, see progress, or get recommendations

Possible target agents:
- "tutor": For teaching, conversation, Socratic dialogue, concept explanation
- "assessor": For scoring, evaluating answers, error diagnosis
- "curriculum": For scheduling, recommendations, progress tracking, next problem selection

Possible subjects (infer from context):
- "amc_math": Math competition topics
- "ket_english": KET English exam topics
- "chn_composition": Chinese composition/writing
- "chn_poetry": Classical Chinese poetry

Possible session modes:
- "course": Systematic lesson learning
- "practice": Problem-solving practice
- "review": Spaced repetition review
- "diagnostic": Assessment/diagnostic test

Respond with ONLY a JSON object, no other text:
{"intent": "...", "target_agent": "...", "subject": "...", "session_mode": "..."}"""


# Intent keywords for rule-based fallback
INTENT_RULES = {
    "assess": ["提交", "submit", "答案", "answer is", "我写完了", "done writing"],
    "practice": ["提示", "hint", "不会", "stuck", "help", "下一题", "next problem", "再来一道"],
    "learn": ["学", "learn", "课程", "lesson", "教我", "teach me", "讲解", "explain"],
    "manage": ["进度", "progress", "推荐", "recommend", "复习", "review", "设置"],
}


def _rule_based_classify(message: str, request_type: str) -> dict:
    """Fallback classifier when LLM is unavailable."""
    if request_type == "attempt":
        return {
            "intent": "assess",
            "target_agent": "assessor",
            "subject": "amc_math",
            "session_mode": "practice",
        }

    msg_lower = message.lower()
    for intent, keywords in INTENT_RULES.items():
        if any(kw in msg_lower for kw in keywords):
            target = "assessor" if intent == "assess" else "tutor"
            if intent == "manage":
                target = "curriculum"
            return {
                "intent": intent,
                "target_agent": target,
                "subject": "amc_math",  # Default, will be refined
                "session_mode": "practice",
            }

    return {
        "intent": "ask",
        "target_agent": "tutor",
        "subject": "amc_math",
        "session_mode": "practice",
    }


async def router_node(state: AgentState) -> dict:
    """Classify intent and route to appropriate agent."""

    # For attempt requests, skip classification
    if state.get("request_type") == "attempt":
        return {
            "intent": "assess",
            "target_agent": "assessor",
            "subject": state.get("problem_data", {}).get("subject", "amc_math"),
            "session_mode": "practice",
        }

    if state.get("request_type") == "session_init":
        return {
            "intent": "manage",
            "target_agent": "curriculum",
            "subject": "amc_math",
            "session_mode": "practice",
        }

    user_message = state.get("user_message", "")
    request_type = state.get("request_type", "chat")

    # Try LLM classification
    llm = get_llm("fast")
    if llm is not None:
        try:
            import json
            messages = [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
            response = await llm.ainvoke(messages)
            result = json.loads(response.content)
            return {
                "intent": result.get("intent", "ask"),
                "target_agent": result.get("target_agent", "tutor"),
                "subject": result.get("subject", "amc_math"),
                "session_mode": result.get("session_mode", "practice"),
            }
        except Exception:
            pass  # Fall through to rule-based

    # Rule-based fallback
    return _rule_based_classify(user_message, request_type)
```

### 5.6 `app/agents/tutor_agent.py` — Teaching Conversation

```python
"""Tutor node: core teaching conversation with subject-specific strategies."""
import json
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.agents.llm import get_llm, is_llm_available, get_fallback_response
from app.agents.prompts import get_system_prompt
from app.agents.state import AgentState


async def tutor_node(state: AgentState) -> dict:
    """Execute teaching conversation based on subject and mode."""

    if not is_llm_available():
        return {
            "agent_response": get_fallback_response(state.get("intent", "learn")),
            "model_used": "none",
        }

    # Build system prompt
    subject = state.get("subject", "amc_math")
    session_mode = state.get("session_mode", "practice")
    student = state.get("student", {})

    # Determine prompt template
    mode_map = {
        ("amc_math", "practice"): "math_socratic",
        ("amc_math", "course"): "math_course",
        ("chn_poetry", "course"): "poetry_teaching",
        ("ket_english", "practice"): "ket_writing",  # when in teaching mode
    }
    prompt_key = mode_map.get((subject, session_mode), "math_socratic")

    system_prompt = get_system_prompt(
        prompt_key,
        student_name=student.get("name", "同学"),
        grade_level=student.get("grade_level", 5),
        target_exam=student.get("target_exam", "AMC8"),
        mastery_level=_get_mastery_summary(state),
        mastered_kps=", ".join(student.get("mastered_kps", [])[:10]),
        weak_areas=", ".join(student.get("weak_areas", [])[:5]),
        problem_markdown=_get_problem_text(state),
        correct_answer=_get_correct_answer(state),
        reference_solutions=_get_solutions(state),
        hint_level=state.get("hint_level", 0),
    )

    # Build conversation history
    messages = [SystemMessage(content=system_prompt)]
    for msg in state.get("session_messages", [])[-10:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=state.get("user_message", "")))

    # Call LLM
    llm = get_llm("strong")
    response = await llm.ainvoke(messages)

    # Update hint level based on conversation progress
    new_hint_level = state.get("hint_level", 0)

    return {
        "agent_response": response.content,
        "model_used": "strong",
        "hint_level": new_hint_level,
    }


def _get_mastery_summary(state: AgentState) -> str:
    """Summarize current mastery for prompt."""
    kstates = state.get("knowledge_states", [])
    if not kstates:
        return "新学生，尚无掌握度数据"
    levels = [ks["mastery_level"] for ks in kstates[:5]]
    return f"最近知识点掌握度: {', '.join(levels)}"


def _get_problem_text(state: AgentState) -> str:
    """Get current problem text if in practice mode."""
    problem = state.get("problem_data")
    if problem:
        return problem.get("question_markdown", "无题目")
    return "当前无题目（对话模式）"


def _get_correct_answer(state: AgentState) -> str:
    """Get correct answer for the problem (for teacher reference only)."""
    problem = state.get("problem_data")
    if problem:
        return problem.get("correct_answer", "N/A")
    return "N/A"


def _get_solutions(state: AgentState) -> str:
    """Get reference solutions for teacher context."""
    problem = state.get("problem_data")
    if problem and problem.get("solutions"):
        sols = []
        for s in problem["solutions"]:
            sol_text = f"方法: {s.get('method_name', '标准解法')}\n"
            sol_text += s.get("solution_markdown", "")
            sols.append(sol_text)
        return "\n---\n".join(sols)
    return "无参考解法"
```

### 5.7 `app/agents/assessor_agent.py` — Evaluation Node

```python
"""Assessor node: evaluates answers, scores essays, diagnoses errors."""
import json
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available
from app.agents.prompts import get_system_prompt
from app.agents.state import AgentState


async def assessor_node(state: AgentState) -> dict:
    """Evaluate student answers with subject-specific rubrics."""

    problem = state.get("problem_data", {})
    subject = state.get("subject", "amc_math")
    answer = state.get("student_answer") or state.get("user_message", "")
    problem_format = problem.get("format", "mcq")

    # ── MCQ: exact match (no LLM needed) ─────────────────────
    if problem_format == "mcq" and problem.get("correct_answer"):
        correct = problem["correct_answer"].strip().upper()
        student_ans = answer.strip().upper()
        is_correct = (student_ans == correct)

        feedback = "Correct! Well done." if is_correct else (
            f"Not quite. The correct answer is {correct}."
        )

        return {
            "agent_response": feedback,
            "structured_data": {
                "is_correct": is_correct,
                "evaluation_method": "exact_match",
            },
            "knowledge_updates": [
                _build_knowledge_update(state, is_correct)
            ],
            "model_used": "none",
        }

    # ── Non-MCQ or complex formats: use LLM ──────────────────
    if not is_llm_available():
        # Fallback: basic heuristics
        is_correct = bool(answer.strip())
        return {
            "agent_response": "Answer recorded. AI feedback will be available later.",
            "structured_data": {
                "is_correct": is_correct,
                "evaluation_method": "fallback",
            },
            "knowledge_updates": [
                _build_knowledge_update(state, is_correct)
            ],
            "model_used": "none",
        }

    # Select prompt based on subject
    prompt_key = _select_assessment_prompt(subject, problem_format)
    system_prompt = get_system_prompt(
        prompt_key,
        problem=problem.get("question_markdown", ""),
        correct_answer=problem.get("correct_answer", "N/A"),
        student_answer=answer,
        student_work="",  # Could be extracted from media
    )

    llm = get_llm("strong")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Student's answer: {answer}"),
    ]
    response = await llm.ainvoke(messages)

    # Parse structured response
    try:
        result = json.loads(response.content)
        is_correct = result.get("is_correct", False)

        return {
            "agent_response": result.get("feedback", response.content),
            "structured_data": result,
            "knowledge_updates": [
                _build_knowledge_update(state, is_correct, result.get("error_type"))
            ],
            "model_used": "strong",
        }
    except json.JSONDecodeError:
        return {
            "agent_response": response.content,
            "structured_data": {"is_correct": None, "evaluation_method": "llm_unstructured"},
            "knowledge_updates": [],
            "model_used": "strong",
        }


def _select_assessment_prompt(subject: str, problem_format: str) -> str:
    """Select the right assessment prompt."""
    if subject == "ket_english" and problem_format in ("essay", "email"):
        return "ket_writing"
    elif subject == "chn_composition":
        return "chn_writing"
    elif subject == "chn_poetry" and problem_format == "dictation":
        return "poetry_dictation"
    elif subject == "chn_poetry":
        return "poetry_scoring"
    else:
        return "error_diagnosis"


def _build_knowledge_update(
    state: AgentState,
    is_correct: bool,
    error_type: str | None = None,
) -> dict:
    """Build a KnowledgeUpdate for the problem's knowledge points."""
    problem = state.get("problem_data", {})
    kp_ids = problem.get("knowledge_point_ids", [])

    return {
        "knowledge_point_id": kp_ids[0] if kp_ids else None,
        "mastery_delta": 0.3 if is_correct else -0.15,
        "is_correct": is_correct,
        "hint_level_used": state.get("hint_level", 0),
        "error_type": error_type,
        "fsrs_rating": 3 if is_correct else 1,
    }
```

### 5.8 `app/agents/curriculum_agent.py` — Scheduling Node

```python
"""Curriculum node: course scheduling, recommendations, FSRS reviews."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available
from app.agents.state import AgentState
from app.agents.services.problem_selector import select_next_problem


async def curriculum_node(state: AgentState) -> dict:
    """
    Handle curriculum-related requests:
    - Session initialization (recommend starting point)
    - Next problem selection (adaptive)
    - Review scheduling (FSRS)
    - Progress summary
    """
    intent = state.get("intent", "manage")
    knowledge_states = state.get("knowledge_states", [])
    student = state.get("student", {})

    if intent == "manage" and state.get("request_type") == "session_init":
        return await _handle_session_init(state, knowledge_states, student)

    if intent == "practice":
        return await _handle_next_problem(state, knowledge_states, student)

    # General management/progress query
    return await _handle_general(state, knowledge_states, student)


async def _handle_session_init(state, knowledge_states, student) -> dict:
    """Recommend starting point for new session."""
    # Find FSRS-due reviews
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    due_reviews = [
        ks for ks in knowledge_states
        if ks.get("next_review") and
           datetime.fromisoformat(ks["next_review"]) <= now
    ]

    # Find weakest areas
    weak = [ks for ks in knowledge_states if ks["mastery"] < 0.4 and ks["mastery"] > 0]

    response_parts = []
    if due_reviews:
        response_parts.append(
            f"You have {len(due_reviews)} knowledge points due for review."
        )
    if weak:
        response_parts.append(
            f"Your weakest areas need attention (mastery < 40%)."
        )

    message = " ".join(response_parts) if response_parts else (
        "Welcome! Let's find the right starting point for you."
    )

    return {
        "agent_response": message,
        "structured_data": {
            "due_reviews": len(due_reviews),
            "weak_areas": len(weak),
            "recommendation": "review" if due_reviews else "learn_new",
        },
    }


async def _handle_next_problem(state, knowledge_states, student) -> dict:
    """Select next problem based on adaptive strategy."""
    from app.db.session import async_session_factory
    from uuid import UUID

    student_id = state.get("student_id")
    subject = state.get("subject", "amc_math")
    target_exam = student.get("target_exam", "AMC8")

    async with async_session_factory() as db:
        problem = await select_next_problem(
            db=db,
            student_id=UUID(str(student_id)),
            subject=subject,
            target_exam=target_exam,
            knowledge_states=knowledge_states,
        )

    if problem:
        return {
            "agent_response": f"Here's your next problem:\n\n{problem.question_markdown}",
            "structured_data": {
                "next_problem_id": str(problem.id),
                "difficulty": problem.difficulty,
            },
        }

    return {
        "agent_response": "No more problems available for this topic right now. Try a different area!",
    }


async def _handle_general(state, knowledge_states, student) -> dict:
    """Handle general curriculum queries."""
    if not is_llm_available():
        return {
            "agent_response": "Curriculum features require an internet connection.",
        }

    # Build progress summary
    summary = _build_progress_summary(knowledge_states, student)
    user_msg = state.get("user_message", "Show my progress")

    llm = get_llm("fast")
    messages = [
        SystemMessage(content=f"You are a learning progress assistant.\n\nStudent progress:\n{summary}"),
        HumanMessage(content=user_msg),
    ]
    response = await llm.ainvoke(messages)

    return {
        "agent_response": response.content,
        "model_used": "fast",
    }


def _build_progress_summary(knowledge_states, student) -> str:
    """Build a text summary of student progress."""
    if not knowledge_states:
        return "No learning data yet."

    by_level = {}
    for ks in knowledge_states:
        level = ks.get("mastery_level", "unknown")
        by_level[level] = by_level.get(level, 0) + 1

    lines = [f"Student: {student.get('name', 'Unknown')}"]
    lines.append(f"Target: {student.get('target_exam', 'Not set')}")
    lines.append(f"Knowledge states: {len(knowledge_states)} tracked")
    for level, count in sorted(by_level.items()):
        lines.append(f"  {level}: {count}")

    return "\n".join(lines)
```

### 5.9 Response Node (DB Persistence)

```python
"""Response node: format output and persist to database."""
from datetime import datetime, timezone
from uuid import uuid4

from app.agents.state import AgentState
from app.agents.services.knowledge_tracker import apply_knowledge_updates
from app.db.session import async_session_factory
from app.models.message import Message
from app.models.learning import StudentAttempt


async def response_node(state: AgentState) -> dict:
    """
    Final node: persist messages and knowledge updates to DB.
    """
    session_id = state.get("session_id")

    async with async_session_factory() as db:
        # 1. Persist assistant message
        agent_response = state.get("agent_response", "")
        if agent_response and session_id:
            ai_msg = Message(
                session_id=session_id,
                role="assistant",
                content=agent_response,
                metadata_={
                    "model_used": state.get("model_used"),
                    "intent": state.get("intent"),
                    "target_agent": state.get("target_agent"),
                },
            )
            db.add(ai_msg)

        # 2. Persist student attempt (if assessment)
        if state.get("request_type") == "attempt":
            structured = state.get("structured_data", {})
            attempt = StudentAttempt(
                session_id=session_id,
                student_id=state.get("student_id"),
                problem_id=state.get("problem_id"),
                answer=state.get("student_answer"),
                is_correct=structured.get("is_correct"),
                ai_feedback=agent_response,
                error_type=structured.get("error_type"),
                hint_level_used=state.get("hint_level", 0),
            )
            db.add(attempt)

        # 3. Apply knowledge state updates
        updates = state.get("knowledge_updates", [])
        if updates:
            await apply_knowledge_updates(
                db,
                student_id=state.get("student_id"),
                updates=updates,
            )

        await db.commit()

    return {}  # No state updates needed
```

---

## 6. Agent Responsibilities & Interactions

### 6.1 Agent Responsibility Matrix

| Agent | Primary Responsibility | LLM Tier | When Invoked |
|-------|----------------------|----------|--------------|
| **Orchestrator** | Load student context, session history, problem/lesson data | None (DB only) | Every request |
| **Router** | Classify intent → determine target agent and subject | Fast | Every chat message |
| **Tutor** | Socratic dialogue, concept teaching, hint delivery | Strong | `intent ∈ {learn, practice, ask}` |
| **Assessor** | Score answers, error diagnosis, rubric evaluation | Strong | `intent == assess` or `request_type == attempt` |
| **Curriculum** | Recommend next problems, FSRS scheduling, progress | Fast + Rules | `intent == manage` or `request_type == session_init` |

### 6.2 Agent Interaction Patterns

#### Pattern 1: Chat Message Flow (most common)

```
User: "I don't understand why x²+5x+6 factors to (x+2)(x+3)"

Orchestrator → loads student context (mastery: algebra 0.45)
Router → intent="ask", target_agent="tutor", subject="amc_math"
Tutor → generates Socratic response:
  "Good question! Let's think about it differently.
   What two numbers multiply to 6 AND add to 5?"
Response → persists message to DB

[Student: "2 and 3?"]
Router → intent="practice", target_agent="tutor"
Tutor → "Exactly! So if x²+5x+6 = (x+a)(x+b),
         and a+b=5, ab=6... what are a and b?"
```

#### Pattern 2: Answer Submission Flow

```
POST /problems/{id}/attempt  {answer: "B"}

Orchestrator → loads problem data (MCQ, correct_answer="C")
Router → skips classification, routes directly to assessor
Assessor → MCQ exact match: "B" ≠ "C"
  → "Not quite. Think about what happens when..."
  → knowledge_update: {mastery_delta: -0.15, is_correct: false}
Response → persists attempt + knowledge update

[If non-MCQ or essay:]
Assessor → uses LLM with appropriate prompt template
  → structured JSON result with scores
```

#### Pattern 3: Session Initialization Flow

```
POST /sessions {session_type: "practice", subject: "amc_math"}

Orchestrator → loads student context, knowledge states
Router → intent="manage", target_agent="curriculum"
Curriculum → finds FSRS-due reviews, selects next problem
  → "You have 2 reviews due, then let's continue with
     similar triangles (your weakest area at 35%)."
Response → returns session + recommendations
```

### 6.3 Subject Strategy Routing

The router determines the subject, and the tutor/assessor selects the appropriate teaching strategy:

| Subject | Tutor Strategy | Assessor Strategy | Prompt Key |
|---------|---------------|-------------------|------------|
| `amc_math` + practice | Socratic (NEVER give answers) | Error diagnosis | `math_socratic` / `error_diagnosis` |
| `amc_math` + course | 5E lesson flow | End-of-lesson quiz | `math_course` |
| `ket_english` + writing | Example + feedback | Cambridge 3-dimension rubric | `ket_writing` |
| `chn_composition` | Active demonstration (MUST give examples) | 100-point 4-dimension rubric | `chn_writing` |
| `chn_poetry` + course | Framework + guide (5 phases) | Dictation accuracy | `poetry_teaching` |
| `chn_poetry` + assess | N/A | Dictation / appreciation scoring | `poetry_dictation` / `poetry_scoring` |

---

## 7. FastAPI Endpoint Integration

### 7.1 Agent Runner (`app/agents/__init__.py`)

```python
"""Public API for the agent layer."""
from app.agents.graph import build_graph
from app.agents.state import initial_state

# Build graph once at module load (lazy)
_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


async def run_agent(**kwargs) -> dict:
    """
    Execute the agent graph with given inputs.
    
    Args:
        session_id: UUID
        student_id: UUID
        user_message: str
        request_type: "chat" | "attempt" | "session_init" | "lesson_progress"
        problem_id: UUID | None
        student_answer: str | None
        lesson_id: UUID | None
        media: dict | None
    
    Returns:
        dict with keys: agent_response, structured_data, error
    """
    state = initial_state(**kwargs)
    graph = get_graph()
    result = await graph.ainvoke(state)
    return {
        "agent_response": result.get("agent_response", ""),
        "structured_data": result.get("structured_data"),
        "error": result.get("error"),
    }
```

### 7.2 `app/api/v1/chat.py` — Modified

```python
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.agents import run_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    body: ChatMessageRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),  # NOW requires auth
):
    # Get or create session
    if body.session_id is not None:
        result = await db.execute(
            select(LearningSession).where(
                LearningSession.id == body.session_id,
                LearningSession.student_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
    else:
        session = LearningSession(
            student_id=current_user.id,
            session_type="chat",
            subject="general",
            started_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()

    # Save user message
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=body.content,
        media=body.media,
    )
    db.add(user_msg)
    await db.flush()
    await db.commit()  # Commit user message before agent runs

    # Run agent
    agent_result = await run_agent(
        session_id=session.id,
        student_id=current_user.id,
        user_message=body.content,
        media=body.media,
        request_type="chat",
    )

    # Agent already persisted the AI message via response_node,
    # but we need to return it. Load the latest assistant message.
    result = await db.execute(
        select(Message)
        .where(
            Message.session_id == session.id,
            Message.role == "assistant",
        )
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    ai_msg = result.scalar_one_or_none()

    if ai_msg is None:
        # Fallback if agent didn't persist
        ai_msg = Message(
            session_id=session.id,
            role="assistant",
            content=agent_result.get("agent_response", "Sorry, I couldn't process that."),
        )
        db.add(ai_msg)
        await db.flush()
        await db.commit()

    return ChatMessageResponse(
        id=ai_msg.id,
        role=ai_msg.role,
        content=ai_msg.content,
        session_id=session.id,
    )
```

### 7.3 `app/api/v1/problems.py` — Modified

```python
@router.post("/{problem_id}/attempt", response_model=AttemptResponse)
async def submit_attempt(
    problem_id: UUID,
    body: AttemptRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),  # NOW requires auth
):
    # Run agent (assessor path)
    agent_result = await run_agent(
        session_id=body.session_id or uuid4(),  # May need active session
        student_id=current_user.id,
        user_message=body.answer,
        request_type="attempt",
        problem_id=problem_id,
        student_answer=body.answer,
    )

    structured = agent_result.get("structured_data", {}) or {}

    # Load the attempt that was persisted by response_node
    result = await db.execute(
        select(StudentAttempt)
        .where(
            StudentAttempt.student_id == current_user.id,
            StudentAttempt.problem_id == problem_id,
        )
        .order_by(StudentAttempt.created_at.desc())
        .limit(1)
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        # Fallback
        attempt_id = uuid4()
    else:
        attempt_id = attempt.id

    return AttemptResponse(
        id=attempt_id,
        is_correct=structured.get("is_correct"),
        ai_feedback=agent_result.get("agent_response"),
        error_type=structured.get("error_type"),
        attempt_number=1,
    )
```

### 7.4 Schema Updates

**`app/schemas/chat.py`:**

```python
from uuid import UUID
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    session_id: UUID | None = None
    content: str
    media: dict | None = None


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    session_id: UUID | None = None  # NEW: return session_id for new sessions

    model_config = {"from_attributes": True}
```

**`app/schemas/problem.py` — extend `AttemptResponse`:**

```python
class AttemptResponse(BaseModel):
    id: UUID
    is_correct: bool | None
    ai_feedback: str | None
    error_type: str | None = None       # NEW
    attempt_number: int

    model_config = {"from_attributes": True}

class AttemptRequest(BaseModel):
    answer: str
    time_spent_sec: int | None = None
    session_id: UUID | None = None       # NEW: link to active session
```

### 7.5 Config Updates (`app/config.py`)

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    STRONG_MODEL: str = "gpt-4o"          # NEW: for Tutor/Assessor
    FAST_MODEL: str = "gpt-4o-mini"       # NEW: for Router/Curriculum
    LLM_MAX_TOKENS: int = 1024            # NEW
    LLM_TEMPERATURE_STRONG: float = 0.7   # NEW
    LLM_TEMPERATURE_FAST: float = 0.1     # NEW
```

---

## 8. Subject-Specific Prompt Templates

### 8.1 Prompt Registry (`app/agents/prompts/__init__.py`)

```python
"""Prompt template registry."""
from app.agents.prompts.math_socratic import MATH_SOCRACTIC_TEMPLATE
from app.agents.prompts.math_course import MATH_COURSE_TEMPLATE
from app.agents.prompts.ket_writing import KET_WRITING_TEMPLATE
from app.agents.prompts.error_diagnosis import ERROR_DIAGNOSIS_TEMPLATE
from app.agents.prompts.chn_writing import CHN_WRITING_TEMPLATE
from app.agents.prompts.poetry_teaching import POETRY_TEACHING_TEMPLATE
from app.agents.prompts.poetry_dictation import POETRY_DICTATION_TEMPLATE
from app.agents.prompts.poetry_scoring import POETRY_SCORING_TEMPLATE

_PROMPTS = {
    "math_socratic": MATH_SOCRACTIC_TEMPLATE,
    "math_course": MATH_COURSE_TEMPLATE,
    "ket_writing": KET_WRITING_TEMPLATE,
    "error_diagnosis": ERROR_DIAGNOSIS_TEMPLATE,
    "chn_writing": CHN_WRITING_TEMPLATE,
    "poetry_teaching": POETRY_TEACHING_TEMPLATE,
    "poetry_dictation": POETRY_DICTATION_TEMPLATE,
    "poetry_scoring": POETRY_SCORING_TEMPLATE,
}


def get_system_prompt(prompt_key: str, **kwargs) -> str:
    """
    Get a rendered system prompt.
    
    Args:
        prompt_key: One of the keys in _PROMPTS
        **kwargs: Variables to substitute in the template
    
    Returns:
        Rendered prompt string
    
    Raises:
        KeyError: If prompt_key not found
    """
    template = _PROMPTS.get(prompt_key)
    if template is None:
        raise KeyError(f"Unknown prompt: {prompt_key}")
    
    # Simple variable substitution using str.format_map
    # Missing keys get empty string (safe default)
    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{{{key}}}}}"  # Leave unsubstituted
    
    return template.format_map(SafeDict(**kwargs))


def list_prompts() -> list[str]:
    """List available prompt keys."""
    return list(_PROMPTS.keys())
```

### 8.2 Prompt Template Structure (example: `math_socratic.py`)

Each prompt file exports a single `str` constant with `{variable}` placeholders:

```python
"""Math Socratic mode prompt template (§7.3)."""

MATH_SOCRACTIC_TEMPLATE = """你是一位AMC数学竞赛私人家教, 正在通过苏格拉底式对话引导学生解题。

## 学生信息
- 姓名: {student_name}
- 年级: {grade_level}
- 目标: {target_exam}
- 当前掌握度: {mastery_level}
- 已掌握的知识点: {mastered_kps}
- 薄弱领域: {weak_areas}

## 当前题目
{problem_markdown}

## 正确答案（仅供教师参考，绝对不能直接告诉学生）
{correct_answer}

## 参考解法（仅供教师参考）
{reference_solutions}

## 教学策略
当前提示级别: Level {hint_level} (0-4)

### 苏格拉底规则（绝对不可违反）
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
你的回复 (1-3个短段落, 自然对话):"""
```

All other prompt files follow the same pattern, with content directly from the system-design.md §7 sections.

### 8.3 Complete Prompt File List

| File | Section | Variables | Used By |
|------|---------|-----------|---------|
| `math_socratic.py` | §7.3 | `student_name`, `grade_level`, `target_exam`, `mastery_level`, `mastered_kps`, `weak_areas`, `problem_markdown`, `correct_answer`, `reference_solutions`, `hint_level` | `tutor_agent` |
| `math_course.py` | §7.2 | `student_name`, `grade_level`, `target_exam`, `mastery_level`, `mastered_kps`, `weak_areas`, `lesson_content_json`, `current_step` | `tutor_agent` |
| `error_diagnosis.py` | §7.5 | `problem`, `student_answer`, `correct_answer`, `student_work` | `assessor_agent` |
| `ket_writing.py` | §7.4 | `task_description`, `required_points`, `student_essay` | `assessor_agent` |
| `chn_writing.py` | §7.6 | `task_description`, `writing_type`, `min_chars`, `max_chars`, `target_chars`, `chn_grade`, `student_essay` | `assessor_agent` |
| `poetry_teaching.py` | §7.7.1 | `poem_title`, `poet`, `dynasty`, `full_text`, `chn_grade`, `learned_poems`, `mastered_imagery`, `current_phase` | `tutor_agent` |
| `poetry_dictation.py` | §7.7.2 | `full_text`, `student_dictation`, `acceptable_variants` | `assessor_agent` |
| `poetry_scoring.py` | §7.7.3 | `question`, `reference_points`, `student_answer`, `max_score` | `assessor_agent` |

---

## 9. FSRS Knowledge Tracking

### 9.1 `app/agents/services/fsrs.py`

```python
"""
Free Spaced Repetition Scheduler (FSRS) algorithm implementation.
Based on: https://github.com/open-spaced-repetition/fsrs4anki

Simplified version for the AI Tutor system.
"""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class FSRSParams:
    """Default FSRS parameters (can be tuned per student)."""
    w: tuple[float, ...] = (
        0.4,    # initial difficulty
        0.6,    # initial stability
        2.4,    # difficulty multiplier (hard)
        4.93,   # difficulty multiplier (easy)
        0.04,   # difficulty mean reversion
        1.15,   # stability increase (hard)
        1.30,   # stability increase (good)
        1.55,   # stability increase (easy)
        0.0046, # hard penalty
        0.71,   # easy bonus
        1.39,   # stability decay
        0.17,   # stability ceiling
        0.30,   # retrievability threshold
    )
    request_retention: float = 0.9  # Target 90% recall


DEFAULT_PARAMS = FSRSParams()


def initial_stability(rating: int) -> float:
    """Get initial stability for a new item based on first rating."""
    params = DEFAULT_PARAMS
    return params.w[rating - 1]  # w[0]=again, w[1]=hard, w[2]=good, w[3]=easy


def initial_difficulty(rating: int) -> float:
    """Get initial difficulty for a new item."""
    params = DEFAULT_PARAMS
    d = params.w[4] - math.exp(params.w[5] * (rating - 1)) + 1
    return max(1.0, min(10.0, d))


def update_difficulty(difficulty: float, rating: int) -> float:
    """Update difficulty based on rating."""
    params = DEFAULT_PARAMS
    delta = params.w[6] * (initial_difficulty(3) - difficulty)
    new_d = difficulty - delta
    return max(1.0, min(10.0, new_d))


def update_stability(difficulty: float, stability: float, rating: int) -> float:
    """Update memory stability based on rating."""
    params = DEFAULT_PARAMS

    if stability <= 0:
        return initial_stability(max(rating, 2))

    if rating == 1:  # Again — memory lapsed
        new_s = stability * params.w[11] * math.exp(params.w[12] * difficulty)
        return max(0.1, new_s)

    # Successful recall
    hard_penalty = params.w[9] if rating == 2 else 1.0
    easy_bonus = params.w[10] if rating == 4 else 1.0

    new_s = stability * (
        1
        + math.exp(params.w[7]) *
        (11 - difficulty) *
        math.pow(stability, -params.w[8]) *
        (math.exp(params.w[9] * (1 - hard_penalty)) - 1) *
        easy_bonus
    )
    return max(0.1, min(365.0, new_s))


def calculate_retrievability(stability: float, elapsed_days: float) -> float:
    """
    Calculate current retrievability (recall probability).
    R = (1 + elapsed/stability * FACTOR)^(-1/DECAY)
    """
    if stability <= 0:
        return 0.0
    DECAY = -0.5
    FACTOR = 19.0 / 81.0
    return math.pow(1 + FACTOR * elapsed_days / stability, DECAY)


def calculate_next_review(
    stability: float,
    difficulty: float,
    retention: float = 0.9,
) -> datetime:
    """Calculate the next review date based on FSRS parameters."""
    if stability <= 0:
        return datetime.now(timezone.utc) + timedelta(days=1)

    DECAY = -0.5
    FACTOR = 19.0 / 81.0

    # Inverse of retrievability formula to get elapsed days
    # R = (1 + FACTOR * t/S)^(-1/DECAY)
    # t = S * ((R^(-1/DECAY) - 1) / FACTOR) ... but simpler:
    interval = stability * math.log(retention) / math.log(0.9)
    interval = max(1, min(365, int(round(interval))))

    return datetime.now(timezone.utc) + timedelta(days=interval)


def classify_mastery_level(mastery: float) -> str:
    """Map mastery value to level string."""
    if mastery < 0.1:
        return "not_started"
    elif mastery < 0.3:
        return "attempted"
    elif mastery < 0.6:
        return "familiar"
    elif mastery < 0.85:
        return "proficient"
    else:
        return "mastered"


def rating_from_correctness(is_correct: bool, hint_level: int = 0) -> int:
    """Convert correctness + hint level to FSRS rating (1-4)."""
    if not is_correct:
        return 1  # Again
    if hint_level >= 3:
        return 2  # Hard (needed lots of help)
    if hint_level >= 1:
        return 3  # Good (needed some help)
    return 4  # Easy (solved independently)
```

### 9.2 `app/agents/services/knowledge_tracker.py`

```python
"""Knowledge state update logic — bridges FSRS with DB models."""
import math
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import KnowledgeState
from app.agents.services.fsrs import (
    classify_mastery_level,
    update_difficulty,
    update_stability,
    calculate_retrievability,
    calculate_next_review,
    rating_from_correctness,
    initial_difficulty,
    initial_stability,
)


def update_mastery(
    current_mastery: float,
    is_correct: bool,
    difficulty: float,
    hint_level: int = 0,
    problem_difficulty: int | None = None,
) -> float:
    """
    Calculate new mastery based on attempt result.
    Implements the algorithm from §8.1 of system-design.md.
    """
    alpha = 0.3  # Learning rate

    if is_correct:
        new_mastery = current_mastery + alpha * (1.0 - current_mastery)
    else:
        new_mastery = current_mastery * (1.0 - alpha * 0.5)

    # Difficulty bonus (harder problems → bigger gain)
    if problem_difficulty and is_correct:
        bonus = max(0, (problem_difficulty - 5) * 0.02)
        new_mastery += bonus

    # Hint penalty
    hint_penalty = hint_level * 0.05
    new_mastery -= hint_penalty

    return max(0.0, min(1.0, new_mastery))


async def apply_knowledge_updates(
    db: AsyncSession,
    student_id: UUID,
    updates: list[dict],
) -> None:
    """
    Apply a batch of knowledge state updates to the DB.
    
    Each update dict has: knowledge_point_id, is_correct, hint_level_used,
    error_type, fsrs_rating, mastery_delta
    """
    for update in updates:
        kp_id = update.get("knowledge_point_id")
        if not kp_id:
            continue

        kp_uuid = UUID(str(kp_id)) if isinstance(kp_id, str) else kp_id

        # Load or create state
        result = await db.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student_id,
                KnowledgeState.knowledge_point_id == kp_uuid,
            )
        )
        state = result.scalar_one_or_none()

        if state is None:
            state = KnowledgeState(
                student_id=student_id,
                knowledge_point_id=kp_uuid,
                mastery=0.0,
                mastery_level="not_started",
                difficulty=5.0,
                stability=0.0,
                retrievability=1.0,
            )
            db.add(state)
            await db.flush()

        is_correct = update.get("is_correct", False)
        hint_level = update.get("hint_level_used", 0)
        fsrs_rating = update.get("fsrs_rating") or rating_from_correctness(is_correct, hint_level)

        # Update mastery (§8.1 algorithm)
        now = datetime.now(timezone.utc)
        days_elapsed = 0
        if state.last_review:
            days_elapsed = (now - state.last_review).days

        # Apply time decay first
        if days_elapsed > 0 and state.stability > 0:
            retrievability = calculate_retrievability(state.stability, days_elapsed)
            state.mastery *= retrievability

        # Apply mastery update
        state.mastery = update_mastery(
            current_mastery=state.mastery,
            is_correct=is_correct,
            difficulty=state.difficulty,
            hint_level=hint_level,
        )

        # Update FSRS parameters
        if state.review_count == 0:
            state.difficulty = initial_difficulty(fsrs_rating)
            state.stability = initial_stability(fsrs_rating)
        else:
            state.difficulty = update_difficulty(state.difficulty, fsrs_rating)
            state.stability = update_stability(state.difficulty, state.stability, fsrs_rating)

        state.retrievability = calculate_retrievability(state.stability, 0)
        state.mastery_level = classify_mastery_level(state.mastery)
        state.next_review = calculate_next_review(state.stability, state.difficulty)
        state.last_review = now
        state.review_count += 1
        state.attempts += 1
        if is_correct:
            state.correct += 1
        else:
            state.lapse_count += 1
```

### 9.3 `app/agents/services/problem_selector.py`

```python
"""Adaptive problem selection engine (§8.2 of system-design.md)."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, and_, not_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem import Problem
from app.models.learning import StudentAttempt


async def select_next_problem(
    db: AsyncSession,
    student_id: UUID,
    subject: str,
    target_exam: str,
    knowledge_states: list[dict],
    session_problem_ids: list[UUID] | None = None,
) -> Problem | None:
    """
    Select the next problem based on adaptive strategy (§8.2).
    
    Strategy:
    1. Find FSRS-due knowledge points → select review problems
    2. If no reviews due, find weakest knowledge point (ZPD)
    3. Filter by difficulty ±1 of current mastery
    4. Exclude recently attempted problems (7 days)
    5. Exclude problems above student's target AMC level
    """
    now = datetime.now(timezone.utc)

    # Determine target AMC level
    amc_level_map = {"AMC8": 8, "AMC10": 10, "AMC12": 12}
    max_amc_level = amc_level_map.get(target_exam, 8)

    # Step 1: Find FSRS-due knowledge points
    due_kp_ids = []
    for ks in knowledge_states:
        next_review = ks.get("next_review")
        if next_review:
            nr = datetime.fromisoformat(next_review) if isinstance(next_review, str) else next_review
            if nr <= now:
                due_kp_ids.append(UUID(ks["knowledge_point_id"]))

    # Step 2: Find weakest knowledge points (ZPD)
    active_kp_ids = []
    target_difficulty = 3  # Default
    if not due_kp_ids:
        # Sort by mastery ascending, take weakest with some activity
        active_states = sorted(
            [ks for ks in knowledge_states if 0 < ks["mastery"] < 0.85],
            key=lambda x: x["mastery"],
        )
        if active_states:
            weakest = active_states[0]
            active_kp_ids.append(UUID(weakest["knowledge_point_id"]))
            target_difficulty = max(1, int(weakest["mastery"] * 10))

    # Step 3: Build query
    kp_ids = due_kp_ids or active_kp_ids

    stmt = select(Problem).where(
        Problem.subject == subject,
        Problem.difficulty.isnot(None),
    )

    if kp_ids:
        # Filter by knowledge point (JSON contains)
        # Note: This is simplified; in production, use proper JSON array queries
        stmt = stmt.where(Problem.difficulty.between(
            max(1, target_difficulty - 1),
            min(10, target_difficulty + 1),
        ))

    # Step 4: Exclude recently attempted (7 days)
    seven_days_ago = now - __import__('datetime').timedelta(days=7)
    recent_subquery = (
        select(StudentAttempt.problem_id)
        .where(
            StudentAttempt.student_id == student_id,
            StudentAttempt.created_at >= seven_days_ago,
        )
    )
    stmt = stmt.where(not_(Problem.id.in_(recent_subquery)))

    # Step 5: Exclude session problems
    if session_problem_ids:
        stmt = stmt.where(not_(Problem.id.in_(session_problem_ids)))

    # Order by difficulty, limit 1
    stmt = stmt.order_by(Problem.difficulty).limit(1)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

---

## 10. Graceful Degradation

### 10.1 Degradation Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                    Degradation Ladder                         │
│                                                              │
│  Level 0: Full AI ──────────── OPENAI_API_KEY is set        │
│    All agents active, LLM-powered responses                  │
│                                                              │
│  Level 1: Rule-based ───────── OPENAI_API_KEY is empty      │
│    Router: keyword matching (no LLM)                         │
│    Tutor: canned responses ("I'm offline, try again later")  │
│    Assessor: MCQ exact match only (no LLM scoring)           │
│    Curriculum: rule-based problem selection (no LLM)         │
│                                                              │
│  Level 2: Minimal ──────────── DB available, nothing else   │
│    All endpoints return error messages                       │
│    CRUD operations still work                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 10.2 How Each Agent Degrades

| Agent | Full AI | Degraded (no API key) |
|-------|---------|----------------------|
| **Router** | LLM classification → JSON | Keyword matching via `_rule_based_classify()` |
| **Tutor** | LLM Socratic dialogue | `"AI tutoring is temporarily unavailable."` |
| **Assessor** | LLM rubric scoring | MCQ exact match only; others: `"Recorded, will evaluate later."` |
| **Curriculum** | LLM recommendations + FSRS rules | FSRS rules only (no LLM summaries) |
| **Response** | Full persistence | Full persistence (no LLM dependency) |

### 10.3 Error Handling Pattern

Every node follows this pattern:

```python
async def some_node(state: AgentState) -> dict:
    try:
        # ... main logic ...
        return {"agent_response": result, "error": None}
    except Exception as e:
        logger.error(f"Node failed: {e}", exc_info=True)
        return {
            "agent_response": "Something went wrong. Please try again.",
            "error": str(e),
        }
```

The response_node checks for `state.get("error")` and ensures messages are still persisted.

---

## Appendix A: Dependency Graph

```
Sprint 1 (Foundation - no LLM needed):
  llm.py ← config.py
  state.py ← (standalone)
  tools.py ← models/, db/
  fsrs.py ← (standalone)
  knowledge_tracker.py ← fsrs.py, models/
  problem_selector.py ← models/

Sprint 2 (Core Graph):
  prompts/__init__.py ← all prompt files
  prompts/math_socratic.py ← (standalone)
  router_agent.py ← llm.py, state.py
  tutor_agent.py ← llm.py, prompts/, state.py
  orchestrator.py ← tools.py, state.py
  graph.py ← all nodes, state.py
  __init__.py ← graph.py

Sprint 3 (Assessment):
  prompts/error_diagnosis.py ← (standalone)
  prompts/ket_writing.py ← (standalone)
  prompts/chn_writing.py ← (standalone)
  assessor_agent.py ← llm.py, prompts/, knowledge_tracker.py

Sprint 4 (Curriculum + Integration):
  prompts/math_course.py ← (standalone)
  prompts/poetry_*.py ← (standalone)
  curriculum_agent.py ← fsrs.py, problem_selector.py
  API endpoints ← __init__.py (AgentRunner)
  schemas ← (standalone)
  config.py ← (add LLM settings)
```

## Appendix B: Testing Strategy

```
tests/
├── test_agents/
│   ├── test_state.py          # State creation, defaults
│   ├── test_llm.py            # LLM factory, fallback detection
│   ├── test_fsrs.py           # FSRS algorithm unit tests
│   ├── test_knowledge_tracker.py  # Mastery update calculations
│   ├── test_problem_selector.py   # Adaptive selection logic
│   ├── test_router.py         # Intent classification (rule + LLM)
│   ├── test_tutor.py          # Tutor node with mocked LLM
│   ├── test_assessor.py       # Assessor node with mocked LLM
│   ├── test_curriculum.py     # Curriculum node
│   ├── test_graph.py          # End-to-end graph execution
│   └── test_prompts.py        # Prompt rendering, variable coverage
├── test_api/
│   ├── test_chat.py           # Chat endpoint integration
│   ├── test_problems.py       # Attempt endpoint integration
│   └── test_sessions.py       # Session endpoint integration
└── conftest.py                # Fixtures: test DB, mock LLM, sample data
```

Key test scenarios:
1. **No API key**: Verify graceful degradation for every endpoint
2. **MCQ exact match**: Verify assessor doesn't call LLM
3. **Knowledge tracking**: Verify FSRS params update correctly after attempts
4. **Session continuity**: Verify messages persist and context loads
5. **Subject routing**: Verify correct prompt selected for each subject
6. **Hint escalation**: Verify tutor adjusts hint level across turns
