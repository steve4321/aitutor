# 贡献指南

> 本文档是快速参考。完整规范请阅读 [开发指南](docs/development-guide.md)。

## 快速开始

### 环境要求
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### 1. 启动基础设施
```bash
docker compose up postgres redis -d
```

### 2. 后端设置
```bash
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. 前端设置
```bash
cd frontend
npm install
npm run dev
```

## 开发流程

```
1. 确认需求 → 阅读相关设计文档
2. 编写测试用例（先写失败测试）
3. 实现功能代码
4. 运行测试 → 确保全部通过
5. 运行 lsp_diagnostics → 确保零错误
6. 提交代码
```

## Commit 规范

```
<type>(<scope>): <description>

type: feat | fix | refactor | test | docs | chore
scope: agents | api | models | services | prompts | tests
```

示例：
- `feat(agents): implement assessor node with MCQ and LLM scoring`
- `fix(knowledge-tracker): bound mastery to [0, 1] range`

## 测试要求

| 变更类型 | 最低测试要求 |
|---------|-------------|
| 新 API 端点 | 至少 2 个集成测试（正常 + 异常） |
| 新 Agent 节点 | 至少 3 个单元测试（正常 + 边界 + 降级） |
| 算法/计算逻辑 | 至少 5 个单元测试（覆盖边界值） |
| Bug 修复 | 至少 1 个回归测试 |
| 重构 | 现有测试全部通过 + 新增测试 |

### 运行测试
```bash
cd backend

# 全部测试
pytest tests/ -v

# 仅单元测试（最快）
pytest tests/unit/ -v

# 带覆盖率
pytest tests/ --cov=app/agents --cov=app/api --cov-report=term-missing
```

### 测试规范
- LLM 全部 Mock，不依赖 OpenAI API
- DB 用内存 SQLite：`sqlite+aiosqlite:///:memory:`
- 所有测试在 `OPENAI_API_KEY=""` 下通过
- 测试命名：`test_<功能>_<场景>_<预期>`

## 代码质量检查

提交前确认：
- [ ] `pytest tests/ -v` 全部通过
- [ ] `lsp_diagnostics` 零错误
- [ ] 无 `as any`、`type: ignore`、空 catch 块
- [ ] 新函数有类型注解
- [ ] 使用 Python 3.12+ 类型语法（`str | None` 而非 `Optional[str]`）

## PR 流程

1. Fork 仓库并创建分支：`git checkout -b feat/your-feature`
2. 遵循上述规范编写代码和测试
3. 提交前运行完整检查
4. 提交 PR，描述清楚变更内容和测试覆盖
5. PR 必须通过 CI 才能合并

## 相关文档

- [完整开发指南](docs/development-guide.md)
- [系统设计文档](docs/system-design.md)
- [Phase 2 测试方案](docs/phase2-test-plan.md)