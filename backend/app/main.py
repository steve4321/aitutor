import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import text

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import global_exception_handler
from app.core.rate_limit import limiter

logger = logging.getLogger(__name__)

# Initialize Sentry (no-op if SENTRY_DSN is empty)
if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist (dev only)
    if settings.ENVIRONMENT == "development":
        from app.models.base import Base
        from app.db.session import engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    from app.db.session import engine

    await engine.dispose()


app = FastAPI(
    title="AI Tutor API",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(api_router)

static_dir = Path(__file__).resolve().parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health")
async def health_check():
    checks: dict = {"status": "ok", "checks": {}}

    try:
        from app.db.session import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["checks"]["database"] = f"error: {e}"
        checks["status"] = "degraded"

    if not settings.DISABLE_REDIS:
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.REDIS_URL)
            await r.ping()
            await r.aclose()
            checks["checks"]["redis"] = "ok"
        except Exception as e:
            checks["checks"]["redis"] = f"error: {e}"
            checks["status"] = "degraded"
    else:
        checks["checks"]["redis"] = "disabled"

    return checks


@app.get("/")
async def root():
    return {
        "name": "AI Tutor API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
