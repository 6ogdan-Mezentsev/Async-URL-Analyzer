from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from core.redis_queue import enqueue_task
from db.models import Task, TaskStatus
from db.queries.tasks import insert_task, set_task_failed
from services.url_validator import normalize_and_validate_url


async def create_task_use_case(session: AsyncSession, redis: Redis, raw_url: str) -> Task:
    """
    Нормализует и валидирует URL, создает новую задачу,
    сохраняет её в базе данных и добавляет в очередь Redis.
    """
    normalized_url = normalize_and_validate_url(raw_url)

    task = Task(url=normalized_url, status=TaskStatus.PENDING)
    await insert_task(session, task)

    try:
        await enqueue_task(redis, task.id)
    except Exception as exc:
        await set_task_failed(session, task.id, f"enqueue failed: {exc}")
        raise RuntimeError("failed to enqueue task") from exc
    return task
