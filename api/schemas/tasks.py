from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from db.models import TaskStatus

class TaskCreateRequest(BaseModel):
    """Схема для создания новой задачи. Содержит URL, который нужно обработать."""
    url: str = Field(..., min_length=1, max_length=2048)

class TaskCreateResponse(BaseModel):
    """Схема для ответа при создании новой задачи. Содержит ID новой задачи и её статус."""
    task_id: UUID
    status: TaskStatus

class TaskReadResponse(BaseModel):
    """Схема для ответа при запросе информации о задаче. Cодержит ID задачи, URL, статус, время создания и время завершения (если есть)."""
    task_id: UUID
    url: str
    status: TaskStatus
    created_at: datetime
    finished_at: datetime | None
    error: str | None

class TaskResultReadResponse(BaseModel):
    """Схема для ответа при запросе результата задачи. Содержит ID задачи и результаты анализа страницы."""
    task_id: UUID
    http_status: int
    title: str | None
    links_count: int
    h1_count: int
    text_length: int
