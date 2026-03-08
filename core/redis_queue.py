import json
from uuid import UUID

from redis.asyncio import Redis

QUEUE_KEY = "queue:tasks"
PUBSUB_PREFIX = "tasks:updates:"


async def enqueue_task(redis: Redis, task_id: UUID) -> None:
    """Добавляет задачу в очередь Redis. """
    await redis.rpush(QUEUE_KEY, json.dumps({"task_id": str(task_id)}))


async def dequeue_task(redis: Redis, timeout: int = 5) -> UUID | None:
    """Извлекает первую задачу из очереди Redis. Если очередь пуста, возвращает None после таймаута."""
    queue_item = await redis.blpop(QUEUE_KEY, timeout=timeout)
    if not queue_item:
        return None
    _key, raw = queue_item
    return UUID(json.loads(raw)["task_id"])


async def publish_task_update(redis: Redis, task_id: UUID, status: str) -> None:
    """Публикует обновление статуса задачи в Redis."""
    channel = f"{PUBSUB_PREFIX}{task_id}"
    await redis.publish(channel, json.dumps({"task_id": str(task_id), "status": status}))
