from uuid import UUID, uuid4
from datetime import datetime
from enum import StrEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum

from core.database import Base


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(
        TaskStatus,
        name="task_status",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        create_type=True,
    ), nullable=False, default=TaskStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True)

    result = relationship(
        "TaskResult",
        back_populates="task",
        uselist=False,
    )

class TaskResult(Base):
    __tablename__ = "task_result"

    task_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    http_status: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    links_count: Mapped[int] = mapped_column(Integer, nullable=False)
    h1_count: Mapped[int] = mapped_column(Integer, nullable=False)
    text_length: Mapped[int] = mapped_column(Integer, nullable=False)

    task = relationship(
        "Task",
        back_populates="result",
    )
