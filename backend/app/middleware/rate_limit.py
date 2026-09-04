import logging
import time

import redis

from app.config import settings
from app.core.exceptions import CodalyraException

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis | None:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()
        except Exception:
            logger.warning("Redis unavailable — rate limiting disabled")
            _redis_client = None
    return _redis_client


class RateLimitExceeded(CodalyraException):
    def __init__(self, detail: str = "Rate limit exceeded. Try again later."):
        super().__init__(status_code=429, detail=detail)


def check_rate_limit(
    user_id: str,
    action: str = "review",
    max_requests: int = 10,
    window_seconds: int = 3600,
) -> None:
    r = _get_redis()
    if r is None:
        return

    key = f"ratelimit:{action}:{user_id}"
    try:
        current = r.get(key)
        if current is not None and int(current) >= max_requests:
            raise RateLimitExceeded(
                f"Rate limit exceeded: max {max_requests} {action}s per hour"
            )
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        pipe.execute()
    except RateLimitExceeded:
        raise
    except Exception:
        logger.warning("Rate limit check failed — allowing request")
