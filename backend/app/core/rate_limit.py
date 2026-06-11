import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

logger = logging.getLogger(__name__)

RATE_LIMITS = {
    "auth_login": "5/minute",
    "chat_message": "20/minute",
    "api_read": "60/minute",
    "api_write": "30/minute",
}

if not settings.DISABLE_REDIS:
    try:
        import redis

        _r = redis.from_url(settings.REDIS_URL)
        _r.ping()
        _r.close()
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=settings.REDIS_URL,
        )
        logger.info("Rate limiter using Redis backend (%s)", settings.REDIS_URL)
    except Exception:
        limiter = Limiter(key_func=get_remote_address)
        logger.warning("Redis unavailable — rate limiter falling back to in-memory storage")
else:
    limiter = Limiter(key_func=get_remote_address)
