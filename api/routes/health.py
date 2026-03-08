from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.database import get_session
from core.redis import get_redis_client
from db.queries.health import check_db

router = APIRouter()


@router.get("/health", tags=["health"])
async def health(
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis_client)
):
    """Роут для проверки готовности приложения. Проверяет доступность базы данных и Redis."""
    try:
        await check_db(session)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="db unavailable")

    try:
        pong = await redis.ping()
        if not pong:
            raise HTTPException(status_code=503, detail="redis unavailable")
    except RedisError:
        raise HTTPException(status_code=503, detail="redis unavailable")

    return {"status": "ok", "db": "ok", "redis": "ok"}
