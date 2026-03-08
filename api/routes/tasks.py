from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.tasks import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskReadResponse,
    TaskResultReadResponse,
)
from core.database import get_session
from core.redis import get_redis_client
from db.queries.tasks import get_task_by_id, get_task_result_by_id
from services.tasks import create_task_use_case

router = APIRouter()

@router.post("/tasks", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
async def create_task(
        task_request: TaskCreateRequest,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis_client),
) -> TaskCreateResponse:
    """
    Роут для создания новой задачи.
    Вызывает бизнес-логику создания задачи.
    """
    try:
        task = await create_task_use_case(session=session, redis=redis, raw_url=task_request.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return TaskCreateResponse(task_id=task.id, status=task.status)


@router.get("/tasks/{task_id}", response_model=TaskReadResponse, status_code=status.HTTP_200_OK, tags=["tasks"])
async def get_task(
        task_id: UUID,
        session: AsyncSession = Depends(get_session)
) -> TaskReadResponse:
    task = await get_task_by_id(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")

    return TaskReadResponse(
        task_id=task.id,
        url=task.url,
        status=task.status,
        created_at=task.created_at,
        finished_at=task.finished_at,
        error=task.error,
    )


@router.get("/tasks/{task_id}/result", response_model=TaskResultReadResponse, status_code=status.HTTP_200_OK, tags=["tasks"])
async def get_task_result(
        task_id: UUID,
        session: AsyncSession = Depends(get_session),
) -> TaskResultReadResponse:
    result = await get_task_result_by_id(session, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="task result not found")

    return TaskResultReadResponse(
        task_id=result.task_id,
        http_status=result.http_status,
        title=result.title,
        links_count=result.links_count,
        h1_count=result.h1_count,
        text_length=result.text_length,
    )
