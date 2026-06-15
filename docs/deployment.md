# AI Tutor 生产环境部署指南

## 概述

本文档介绍 AI Tutor 系统生产环境的完整部署流程。涵盖 Docker 和裸机两种部署方式，包含架构选型、环境配置、数据库初始化、安全检查等关键步骤。

项目技术栈：
- Frontend: Next.js 15 (Node.js 20+)
- Backend: FastAPI + LangGraph (Python 3.12)
- Database: PostgreSQL 16 + pgvector
- Cache: Redis 7
- AI: OpenAI / Claude / DeepSeek 等 LLM 提供商

---

## 架构选型

### 部署模式对比

| 模式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| Docker Compose 单机 | 小规模部署 / 验证环境 | 部署简单，依赖内聚 | 扩展性有限，资源争抢 |
| Kubernetes 集群 | 生产高可用 | 自动恢复，水平扩展，滚动更新 | 运维复杂度高 |
| 裸机直接部署 | 单一服务器，成本敏感 | 性能无虚拟化开销，资源独占 | 无自动扩缩容，更新不便 |
| Vercel 托管前端 | 前端静态 / SSR 部署 | CDN 加速，无需服务器管理 | 后端 API 必须公网可达 |

### 推荐生产架构

```
                    ┌─────────────┐
                    │   Vercel    │  (或自托管 Nginx)
                    │  Next.js    │
                    └──────┬──────┘
                           │ HTTPS
                           ▼
┌──────────┐      ┌─────────────┐      ┌─────────────┐
│  用户    │─────▶│  Backend    │─────▶│ PostgreSQL  │
│  浏览器  │      │  FastAPI    │      │  + pgvector │
└──────────┘      └──────┬──────┘      └─────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   Redis     │
                  │  Session    │
                  └─────────────┘
```

---

## 前置条件

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 20 GB | 50 GB+ SSD |
| 网络 | 公网 IP | 公网 IP + 域名 |

### 软件依赖

- Docker 24+ 和 Docker Compose v2
- Node.js 20+ (如不使用 Docker)
- Python 3.12+ (如不使用 Docker)
- PostgreSQL 16 + pgvector 扩展
- Redis 7
- Nginx (如自托管前端)
- Git

### 域名与 SSL

1. 配置 DNS A 记录指向服务器 IP
2. 使用 Let's Encrypt 申请免费证书：
   ```bash
   certbot --nginx -d your-domain.com
   ```
3. 或使用云服务商提供的免费证书

---

## 环境变量

完整环境变量说明。复制 `.env.example` 到 `.env` 并填写实际值。

### 核心配置

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `POSTGRES_USER` | 是 | aitutor | PostgreSQL 用户名 |
| `POSTGRES_PASSWORD` | 是 | aitutor | PostgreSQL 密码 |
| `POSTGRES_DB` | 是 | aitutor | 数据库名 |
| `DATABASE_URL` | 是 | - | PostgreSQL 连接 URL，格式：`postgresql+asyncpg://user:pass@host:5432/dbname` |
| `REDIS_URL` | 是 | redis://localhost:6379/0 | Redis 连接 URL |
| `DISABLE_REDIS` | 否 | false | 设为 true 可禁用 Redis（不推荐生产环境） |

### 安全配置

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `SECRET_KEY` | 是 | change-me-in-production | **生产环境必须修改**。必须 ≥32 字符，建议使用 `openssl rand -hex 32` 生成 |
| `ENVIRONMENT` | 是 | development | 设为 `production` 启用生产模式校验 |
| `CORS_ORIGINS` | 是 | ["http://localhost:3000"] | 允许的跨域来源，JSON 数组格式 |

### AI / LLM 配置

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `LLM_PROVIDER` | 是 | openai | LLM 提供商，可选：`openai`、`deepseek`、`minimax`、`custom` |
| `OPENAI_API_KEY` | 条件 | - | OpenAI API Key（使用 OpenAI 时必填） |
| `MINIMAX_API_KEY` | 条件 | - | MiniMax API Key（使用 MiniMax 时必填） |
| `LLM_BASE_URL` | 否 | - | 自定义 API 端点（custom provider 时使用） |
| `STRONG_MODEL` | 否 | - | 强推理模型名称 |
| `FAST_MODEL` | 否 | - | 快速响应模型名称 |
| `EMBEDDING_MODEL` | 否 | - | 向量嵌入模型名称 |
| `LLM_TIMEOUT` | 否 | 30.0 | LLM 请求超时（秒） |
| `LLM_MAX_RETRIES` | 否 | 2 | 最大重试次数 |

### 应用配置

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `NEXT_PUBLIC_API_URL` | 是 | http://localhost:8000/api/v1 | 前端使用的后端 API 地址 |
| `SENTRY_DSN` | 否 | - | Sentry DSN，用于错误追踪 |
| `DB_POOL_SIZE` | 否 | 20 | 数据库连接池大小 |
| `DB_MAX_OVERFLOW` | 否 | 10 | 连接池溢出上限 |
| `DB_POOL_RECYCLE` | 否 | 1800 | 连接回收时间（秒） |

### 生产环境 SECRET_KEY 校验

代码中强制校验：生产环境下 `SECRET_KEY` 必须 ≥32 字符且不能为默认值。部署前务必修改：

```bash
# 生成随机密钥
openssl rand -hex 32
```

---

## 数据库配置

### PostgreSQL + pgvector 安装

#### Docker 方式（推荐）

```bash
docker run -d \
  --name aitutor-postgres \
  -e POSTGRES_USER=aitutor \
  -e POSTGRES_PASSWORD=your-strong-password \
  -e POSTGRES_DB=aitutor \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

#### 裸机安装

```bash
# Ubuntu/Debian
apt install -y postgresql-16 postgresql-16-pgvector

# 启动服务
systemctl start postgresql
systemctl enable postgresql

# 创建用户和数据库
su - postgres
psql << EOF
CREATE USER aitutor WITH PASSWORD 'your-strong-password';
CREATE DATABASE aitutor OWNER aitutor;
\c aitutor
CREATE EXTENSION IF NOT EXISTS vector;
EOF
```

### 数据库迁移 (Alembic)

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DATABASE_URL=postgresql+asyncpg://aitutor:your-password@localhost:5432/aitutor

# 执行迁移
alembic upgrade head
```

### 数据初始化

```bash
# 运行种子数据脚本（如有）
python -m app.scripts.seed
```

---

## 后端部署

### Docker 部署（推荐）

#### 1. 构建镜像

```bash
cd /mnt/c/work/aitutor

# 构建后端镜像
docker build -t aitutor-backend:latest ./backend
```

#### 2. 配置环境变量

```bash
cp .env.example backend/.env
# 编辑 backend/.env 填写实际值
```

#### 3. 启动容器

```bash
docker run -d \
  --name aitutor-backend \
  -p 8000:8000 \
  --env-file ./backend/.env \
  --restart unless-stopped \
  aitutor-backend:latest
```

#### 4. 验证部署

```bash
# 检查容器状态
docker ps | grep aitutor-backend

# 健康检查
curl http://localhost:8000/health

# 查看日志
docker logs aitutor-backend
```

### 裸机部署

#### 1. 安装依赖

```bash
apt update && apt install -y \
  python3.12 python3.12-venv \
  build-essential pkg-config \
  libcairo2-dev libpango1.0-dev \
  texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
  ffmpeg
```

#### 2. 创建用户和目录

```bash
useradd -m -s /bin/bash appuser
mkdir -p /opt/aitutor/backend
chown appuser:appuser /opt/aitutor/backend
```

#### 3. 部署应用

```bash
# 解压或拉取代码
cd /opt/aitutor/backend
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL=postgresql+asyncpg://aitutor:your-password@localhost:5432/aitutor
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=your-32-char-minimum-secret-key
export ENVIRONMENT=production
export CORS_ORIGINS='["https://your-domain.com"]'
```

#### 4. 运行迁移和启动

```bash
alembic upgrade head

# 使用 systemd 管理进程
cat > /etc/systemd/system/aitutor-backend.service << EOF
[Unit]
Description=AI Tutor Backend
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/aitutor/backend
EnvironmentFile=/opt/aitutor/backend/.env
ExecStart=/opt/aitutor/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=unless-stopped

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable aitutor-backend
systemctl start aitutor-backend
```

---

## 前端部署

### Vercel 部署（推荐）

#### 1. 安装 Vercel CLI

```bash
npm install -g vercel
```

#### 2. 配置环境变量

在 Vercel Dashboard 中设置：
- `NEXT_PUBLIC_API_URL`: `https://your-backend-domain.com/api/v1`
- `NEXT_TELEMETRY_DISABLED`: `1`

#### 3. 部署

```bash
cd frontend
vercel --prod
```

#### 4. 自定义域名

在 Vercel Dashboard 中绑定域名，配置 DNS CNAME 记录。

### Docker 部署（自托管）

#### 1. 构建生产镜像

```bash
cd frontend

# 设置环境变量
export NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1

# 构建
docker build -t aitutor-frontend:latest .
```

#### 2. 启动容器

```bash
docker run -d \
  --name aitutor-frontend \
  -p 3000:3000 \
  --env NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1 \
  --restart unless-stopped \
  aitutor-frontend:latest
```

### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```

启用 SSL：
```bash
certbot --nginx -d your-domain.com
```

---

## Docker Compose 完整部署

### 生产配置

创建 `docker-compose.prod.yml`：

```yaml
version: "3.8"

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1g

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
      CORS_ORIGINS: ${CORS_ORIGINS}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1g

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512m

volumes:
  postgres_data:
```

### 启动命令

```bash
# 设置环境变量
cp .env.example .env
# 编辑 .env 填写实际值

# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 查看状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

---

## 安全检查清单

### 部署前检查

- [ ] `SECRET_KEY` 已修改为随机值，长度 ≥32 字符
- [ ] `ENVIRONMENT` 设置为 `production`
- [ ] `CORS_ORIGINS` 只包含生产域名
- [ ] PostgreSQL 密码已修改为强密码（非默认值）
- [ ] 数据库不允许远程连接（或已配置 IP 白名单）
- [ ] Redis 已设置密码（`redis://:password@host:6379/0`）
- [ ] SSL 证书已配置并生效
- [ ] 所有 API Key 已从代码库移除，改为环境变量注入

### 运行时检查

- [ ] 容器/进程正常启动，无崩溃
- [ ] 健康检查端点返回 200
- [ ] 前端能正常调用后端 API
- [ ] Sentry 收到测试事件的确认
- [ ] 日志中无密码或密钥泄露
- [ ] 防火墙只开放必要端口（80, 443, 22）

### 监控告警

- [ ] 已配置 Sentry 错误告警
- [ ] 已配置服务器资源监控（CPU/内存/磁盘）
- [ ] 已配置数据库连接数监控
- [ ] 定期备份已配置

---

## 健康监控

### 健康检查端点

| 服务 | 端点 | 预期响应 |
|------|------|---------|
| Backend | `GET /health` | `{"status":"ok"}` |
| Backend | `GET /ready` | 数据库和 Redis 连接状态 |
| PostgreSQL | `pg_isready` 命令 | `accepting connections` |
| Redis | `redis-cli ping` | `PONG` |

### 日志查看

```bash
# Docker 部署
docker logs aitutor-backend --tail=100 -f
docker logs aitutor-frontend --tail=100 -f

# systemd 部署
journalctl -u aitutor-backend -n 100 -f
journalctl -u aitutor-frontend -n 100 -f
```

### 常见监控指标

- API 响应时间 p95/p99
- 数据库查询延迟
- Redis 内存使用量
- 后端进程内存占用
- LLM API 调用失败率

---

## 故障排查

### 数据库连接失败

```
Error: connection refused
```

检查清单：
1. PostgreSQL 服务是否运行：`systemctl status postgresql` 或 `docker ps`
2. 端口是否可达：`telnet localhost 5432`
3. 防火墙是否开放：`ufw allow 5432`
4. `DATABASE_URL` 格式是否正确

### Redis 连接失败

```
Error: Redis connection error
```

检查清单：
1. Redis 服务是否运行：`systemctl status redis` 或 `docker ps`
2. `REDIS_URL` 是否正确
3. 如配置密码，确认 URL 格式为 `redis://:password@host:6379/0`

### 后端启动失败

```
SECRET_KEY must be changed from the default and be at least 32 characters
```

生产环境下 `SECRET_KEY` 必须满足：
1. 不能是默认值 `change-me-in-production`
2. 长度必须 ≥32 字符

修复：
```bash
openssl rand -hex 32
# 将输出填入 SECRET_KEY 环境变量
```

### 前端无法调用后端 API

1. 确认 `NEXT_PUBLIC_API_URL` 指向正确地址
2. 确认后端 CORS 配置包含前端域名
3. 检查浏览器控制台具体错误信息

### LLM API 调用失败

1. 确认 API Key 正确且未过期
2. 检查账户余额或配额
3. 查看后端日志中的具体错误信息
4. 确认网络能访问 LLM 提供商端点

### Docker 容器内存不足

```
Killed
```

增加内存限制或优化应用内存使用：

```bash
# 查看内存使用
docker stats

# 调整 docker-compose.yml 中的内存限制
```

### 数据库迁移失败

```bash
# 查看当前迁移版本
alembic current

# 查看迁移历史
alembic history

# 手动执行迁移
alembic upgrade head

# 如需回滚
alembic downgrade -1
```

---

## 相关文档

- [本地开发指南](development-guide.md) - 本地环境搭建
- [系统设计文档](system-design.md) - 架构设计和数据模型
- [课程目录](course-catalog.md) - 课程内容结构

---

## 更新日志

- v1.0.0 (2026-06-15) - 初始版本