from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Task,TaskResult, TaskStatus


async def insert_task(session: AsyncSession, task: Task) -> None:
    """Добавляет новую задачу в базу данных."""
    session.add(task)
    await session.commit()
    await session.refresh(task)


async def get_task_by_id(session: AsyncSession, task_id: UUID) -> Task | None:
    """Получает задачу по её ID."""
    res = await session.execute(select(Task).where(Task.id == task_id))
    return res.scalar_one_or_none()

async def get_task_result_by_id(session: AsyncSession, task_id: UUID) -> TaskResult | None:
    """Получает результат задачи по её ID."""
    res = await session.execute(select(TaskResult).where(TaskResult.task_id == task_id))
    return res.scalar_one_or_none()

async def set_task_status(session: AsyncSession, task_id: UUID, status: TaskStatus) -> None:
    """Обновляет статус задачи и устанавливает время завершения, если задача завершена."""
    await session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(status=status, finished_at=None if status == TaskStatus.IN_PROGRESS else datetime.utcnow())
    )
    await session.commit()


async def set_task_failed(session: AsyncSession, task_id: UUID, error: str) -> None:
    """Устанавливает статус задачи как FAILED и сохраняет сообщение об ошибке."""
    await session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(status=TaskStatus.FAILED, error=error, finished_at=datetime.utcnow())
    )
    await session.commit()

async def upsert_task_result(
    session: AsyncSession,
    task_id: UUID,
    http_status: int,
    title: str | None,
    links_count: int,
    h1_count: int,
    text_length: int,
) -> None:
    """
    Вставляет или обновляет результат задачи в базе данных.
    Если результат для данной задачи уже существует, он будет обновлен, иначе будет создан новый.
    """
    res = await session.execute(select(TaskResult).where(TaskResult.task_id == task_id))
    existing = res.scalar_one_or_none()

    if existing is None:
        session.add(
            TaskResult(
                task_id=task_id,
                http_status=http_status,
                title=title,
                links_count=links_count,
                h1_count=h1_count,
                text_length=text_length,
            )
        )
    else:
        existing.http_status = http_status
        existing.title = title
        existing.links_count = links_count
        existing.h1_count = h1_count
        existing.text_length = text_length

    await session.commit()

