"""
Асинхронные подключения к PostgreSQL.

Контур разделён на две независимые БД:
- MainBD  — бизнес-сущности (заявки, пользователи, справочники)
- LogBD   — аудит, auth-логи, доступ к ПД, системные события
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


class MainBase(DeclarativeBase):
    """Базовый класс ORM-моделей MainBD."""


class LogBase(DeclarativeBase):
    """Базовый класс ORM-моделей LogBD."""


def _create_engine(url: str, *, echo: bool) -> AsyncEngine:
    return create_async_engine(
        url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# --- Движки ---
main_engine: AsyncEngine = _create_engine(
    settings.main_database_url,
    echo=settings.debug,
)
log_engine: AsyncEngine = _create_engine(
    settings.log_database_url,
    echo=settings.debug,
)

# --- Фабрики сессий ---
MainSessionLocal = async_sessionmaker(
    bind=main_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
LogSessionLocal = async_sessionmaker(
    bind=log_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_main_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: сессия MainBD с автоматическим rollback при ошибке."""
    async with MainSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_log_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: сессия LogBD с автоматическим rollback при ошибке."""
    async with LogSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
