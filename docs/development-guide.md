# 开发指南

> 本文档定义了项目的开发规范和流程。所有贡献者必须遵循。

## 1. 测试规范（强制）

### 1.1 测试要求

**所有新功能、Bug 修复、重构都必须包含测试。** 无测试的 PR 不予合并。

| 变更类型 | 最低测试要求 |
|---------|-------------|
| 新 API 端点 | 至少 2 个集成测试（正常 + 异常） |
| 新 Agent 节点 | 至少 3 个单元测试（正常 + 边界 + 降级） |
| 算法/计算逻辑 | 至少 5 个单元测试（覆盖边界值） |
| Bug 修复 | 至少 1 个回归测试（验证 bug 已修复） |
| 重构 | 现有测试全部通过 + 新增覆盖重构路径的测试 |
| Schema 变更 | 更新相关测试的 fixture |

### 1.2 测试文件组织

```
backend/tests/
├── conftest.py              # 全局 fixtures（DB、用户、认证、Mock LLM）
├── unit/                    # 纯函数/算法测试，无外部依赖
│   ├── test_fsrs.py
│   ├── test_knowledge_tracker.py
│   ├── test_problem_selector.py
│   ├── test_prompts.py
│   └── test_llm_factory.py
├── agents/                  # Agent 节点测试，Mock LLM
│   ├── test_router.py
│   ├── test_assessor.py
│   ├── test_tutor.py
│   ├── test_curriculum.py
│   ├── test_orchestrator.py
│   └── test_graph.py        # Graph 全流程集成
├── api/                     # API 端点测试
│   ├── test_chat.py
│   └── test_problems.py
└── e2e/                     # 端到端场景测试
    └── test_learning_flow.py
```

### 1.3 运行测试

```bash
# 全部测试
cd backend && pytest tests/ -v

# 仅单元测试（最快，开发时频繁运行）
pytest tests/unit/ -v

# 仅 Agent 测试
pytest tests/agents/ -v

# 带覆盖率报告
pytest tests/ --cov=app/agents --cov=app/api --cov-report=term-missing

# 运行单个测试文件
pytest tests/unit/test_fsrs.py -v
```

### 1.4 测试编写规则

1. **LLM 全部 Mock** — 测试逻辑正确性，不依赖 OpenAI API
2. **DB 用内存 SQLite** — `sqlite+aiosqlite:///:memory:`，每个测试隔离
3. **无 API Key 环境运行** — 所有测试在 `OPENAI_API_KEY=""` 下通过
4. **使用共享 Fixture** — 优先使用 `conftest.py` 中的 fixture，避免重复创建
5. **测试命名** — `test_<功能>_<场景>_<预期>`，如 `test_assessor_mcq_correct_returns_true`
6. **每个测试独立** — 不依赖执行顺序，不依赖其他测试的数据
7. **Mock 最小化** — 只 Mock 外部依赖（LLM、外部 API），不 Mock 内部逻辑

### 1.5 测试覆盖目标

| 模块 | 最低覆盖率 |
|------|-----------|
| `agents/services/fsrs.py` | 95% |
| `agents/services/knowledge_tracker.py` | 90% |
| `agents/assessor_agent.py` | 85% |
| `agents/router_agent.py` | 85% |
| `agents/tutor_agent.py` | 80% |
| `agents/curriculum_agent.py` | 80% |
| `api/v1/chat.py` | 80% |
| `api/v1/problems.py` | 80% |

## 2. 开发流程

### 2.1 功能开发流程

```
1. 确认需求 → 阅读相关设计文档
2. 编写测试用例（先写失败测试）
3. 实现功能代码
4. 运行测试 → 确保全部通过
5. 运行 `lsp_diagnostics` → 确保零错误
6. 提交代码（commit message 清晰描述变更）
```

### 2.2 Git Commit 规范

```
<type>(<scope>): <description>

type: feat | fix | refactor | test | docs | chore
scope: agents | api | models | services | prompts | tests
```

示例：
- `feat(agents): implement assessor node with MCQ and LLM scoring`
- `fix(knowledge-tracker): bound mastery to [0, 1] range`
- `test(agents): add router node unit tests`

### 2.3 代码质量检查

每次提交前检查：
- [ ] `pytest tests/ -v` 全部通过
- [ ] `lsp_diagnostics` 零错误
- [ ] 无 `as any`、`@ts-ignore`、空 catch 块
- [ ] 新函数有类型注解
- [ ] 新模块有 module docstring

## 3. 技术约束

### 3.1 类型安全
- 所有函数必须有参数和返回值类型注解
- 禁止 `as any`、`# type: ignore`
- 使用 Python 3.12+ 类型语法（`str | None` 而非 `Optional[str]`）

### 3.2 异步
- 所有 DB 操作使用 `async/await`
- 所有 Agent 节点是 `async def`
- 测试使用 `pytest-asyncio`，自动检测 `async def test_`

### 3.3 数据库
- 开发环境: SQLite (`data/aitutor.db`)
- 测试环境: 内存 SQLite (`sqlite+aiosqlite:///:memory:`)
- 生产环境: PostgreSQL 16
- 所有 DB 操作通过 `get_db` 依赖注入
- Agent 内部 DB 访问通过 `async_session_factory`

## 4. 相关文档

- [系统设计文档](system-design.md) — 架构、课程体系、AI Prompt、知识追踪
- [Phase 2 实施计划](phase2-implementation-plan.md) — LangGraph Agent 详细设计
- [Phase 2 测试方案](phase2-test-plan.md) — 测试用例清单和示例代码
- [课程目录](course-catalog.md) — 完整课程列表
- [课程内容 Schema](lesson-content-schema.md) — 内容格式规范