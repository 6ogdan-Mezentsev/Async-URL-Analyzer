from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase

from core.settings import settings


ENGINE = create_async_engine(
    settings.database_url,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    ENGINE,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: отдаёт новый AsyncSession для каждого запроса и гарантирует его закрытие."""
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
