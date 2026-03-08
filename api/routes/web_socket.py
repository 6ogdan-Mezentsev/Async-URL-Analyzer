from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.redis import get_redis
from core.redis_queue import PUBSUB_PREFIX

router = APIRouter()


@router.websocket("/ws/tasks/{task_id}")
async def task_updates_ws(websocket: WebSocket, task_id: UUID) -> None:
    """
    WebSocket: стримит real-time обновления статуса задачи.
    Подписывается на Redis Pub/Sub канал `tasks:updates:{task_id}` и пересылает сообщения клиенту.
    """
    await websocket.accept()

    redis: Redis = get_redis()
    pubsub = redis.pubsub()

    channel = f"{PUBSUB_PREFIX}{task_id}"

    try:
        await pubsub.subscribe(channel)

        await websocket.send_json({"type": "subscribed", "task_id": str(task_id), "channel": channel})

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                continue

            await websocket.send_text(message["data"])

    except WebSocketDisconnect:
        pass
    except RedisError as exc:
        await websocket.send_json({"type": "error", "detail": "redis unavailable", "error": str(exc)})
    finally:
        try:
            await pubsub.unsubscribe(channel)
        finally:
            await pubsub.close()
