import asyncio
from dataclasses import dataclass
from uuid import UUID

import httpx
from bs4 import BeautifulSoup

from core.database import AsyncSessionLocal
from core.redis import get_redis, close_redis
from core.redis_queue import dequeue_task, publish_task_update
from db.models import TaskStatus
from db.queries.tasks import (
    get_task_by_id,
    set_task_failed,
    set_task_status,
    upsert_task_result,
)


@dataclass(slots=True)
class AnalyzeResult:
    """Модель для результата анализа страницы."""
    http_status: int
    title: str | None
    links_count: int
    h1_count: int
    text_length: int


async def analyze_url(url: str) -> AnalyzeResult:
    """Анализирует страницу по заданному URL и возвращает результат анализа."""
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.get(url)

    html = resp.text or ""
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    links_count = len(soup.find_all("a"))
    h1_count = len(soup.find_all("h1"))
    text_length = len(soup.get_text(" ", strip=True))

    return AnalyzeResult(
        http_status=resp.status_code,
        title=title,
        links_count=links_count,
        h1_count=h1_count,
        text_length=text_length,
    )


async def process_task(task_id: UUID) -> None:
    """
    Обрабатывает задачу:
    выполняет анализ URL и обновляет статус задачи в базе данных и Redis.
    """
    redis = get_redis()

    async with AsyncSessionLocal() as session:
        task = await get_task_by_id(session, task_id)
        if task is None:
            return

        await set_task_status(session, task_id, TaskStatus.IN_PROGRESS)
        await publish_task_update(redis, task_id, TaskStatus.IN_PROGRESS.value)

        try:
            result = await analyze_url(task.url)

            await upsert_task_result(
                session,
                task_id=task_id,
                http_status=result.http_status,
                title=result.title,
                links_count=result.links_count,
                h1_count=result.h1_count,
                text_length=result.text_length,
            )

            await set_task_status(session, task_id, TaskStatus.SUCCESS)
            await publish_task_update(redis, task_id, TaskStatus.SUCCESS.value)
        except Exception as exc:
            await set_task_failed(session, task_id, str(exc))
            await publish_task_update(redis, task_id, TaskStatus.FAILED.value)


async def worker_loop() -> None:
    """
    Основной цикл воркера,
    который постоянно слушает очередь Redis
    и обрабатывает задачи по мере их поступления.
    """
    redis = get_redis()

    try:
        while True:
            task_id = await dequeue_task(redis, timeout=5)
            if task_id is None:
                continue

            await process_task(task_id)
    finally:
        await close_redis()


def main() -> None:
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()