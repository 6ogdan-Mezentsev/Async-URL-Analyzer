from redis.asyncio import Redis
from typing import AsyncGenerator

from core.settings import settings


_redis = None

def get_redis() -> Redis:
    """Возвращает singleton Redis."""
    global _redis
    if _redis is None:
        if not settings.redis_url:
            raise RuntimeError("REDIS_URL is not set")
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency: отдаёт общий клиент."""
    yield get_redis()


async def close_redis() -> None:
    """Закрывает соединение Redis при завершении приложения."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
