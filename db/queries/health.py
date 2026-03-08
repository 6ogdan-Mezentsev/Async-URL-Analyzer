from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_db(session: AsyncSession) -> None:
    """Проверяет доступность базы данных, выполняя простой запрос."""
    await session.execute(text("SELECT 1"))
