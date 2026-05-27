# AI 私人家教

AI-powered private tutor for academic competitions: AMC (math) & KET (English).

## Documentation

- [完整系统设计文档](docs/system-design.md) — 架构、课程体系、UI/UX、AI Prompt、知识追踪、数据模型

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | Python FastAPI + LangGraph |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 |
| AI | OpenAI / Claude (LLM) + Whisper (ASR) + Edge TTS |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### 1. Start infrastructure services
```bash
docker compose up postgres redis -d
```

### 2. Backend setup
```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Or use Docker Compose for everything
```bash
docker compose up -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
aitutor/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── agents/   # LangGraph AI agents
│   ├── alembic/      # DB migrations
│   └── tests/        # Backend tests
├── frontend/         # Next.js frontend
│   ├── src/
│   │   ├── app/      # Pages (App Router)
│   │   ├── components/  # React components
│   │   ├── hooks/    # Custom hooks
│   │   ├── lib/      # API client, utils
│   │   └── types/    # TypeScript types
│   └── public/       # Static assets
├── docs/             # Design documents
└── docker-compose.yml
```
