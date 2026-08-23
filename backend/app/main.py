"""
Точка входа FastAPI-приложения КЭДО.

Запуск (dev):
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import log_engine, main_engine
from app.core.exceptions import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Lifecycle: startup / shutdown ресурсов."""
    # startup
    yield
    # shutdown — корректно закрываем пулы соединений
    await main_engine.dispose()
    await log_engine.dispose()


def create_app() -> FastAPI:
    """Application Factory — удобно для тестов и production."""
    # Swagger/ReDoc доступны в dev/staging; в production отключены
    enable_docs = settings.app_env != "production"

    app = FastAPI(
        title=settings.app_name,
        description="Кадровый Электронный Документооборот (КЭДО)",
        version="1.0.0",
        docs_url="/docs" if enable_docs else None,
        redoc_url="/redoc" if enable_docs else None,
        openapi_url="/openapi.json" if enable_docs else None,
        lifespan=lifespan,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception handlers ---
    register_exception_handlers(app)

    # --- Routers ---
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
