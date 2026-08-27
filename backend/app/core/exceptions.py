"""Кастомные исключения и обработчики ошибок FastAPI."""

import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.database import LogSessionLocal
from app.services.audit_service import AuditService


class AppError(Exception):
    """Базовое прикладное исключение."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "app_error",
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Ресурс не найден") -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, code="not_found")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Доступ запрещён") -> None:
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, code="forbidden")


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Требуется авторизация") -> None:
        super().__init__(
            message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="unauthorized",
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Конфликт данных") -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, code="conflict")


def _clean_validation_msg(msg: str) -> str:
    prefixes = ("Value error, ", "value_error, ")
    for prefix in prefixes:
        if msg.startswith(prefix):
            return msg[len(prefix) :]
    return msg


async def _write_system_event(
    *,
    endpoint: str | None,
    error_message: str,
    stack_trace: str | None,
    event_type: str,
) -> None:
    """Best-effort запись в LogBD; ошибки логирования не должны ломать ответ."""
    try:
        async with LogSessionLocal() as session:
            audit = AuditService(session)
            await audit.log_system_event(
                endpoint=endpoint,
                error_message=error_message,
                stack_trace=stack_trace,
                event_type=event_type,
            )
            await session.commit()
    except Exception:
        pass


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует единообразные JSON-ответы на ошибки."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        messages: list[str] = []
        for err in exc.errors():
            msg = _clean_validation_msg(str(err.get("msg", "Ошибка валидации")))
            messages.append(msg)
        detail = "; ".join(messages) if messages else "Ошибка валидации"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail, "code": "validation_error"},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        await _write_system_event(
            endpoint=str(request.url.path),
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            event_type="unhandled_exception",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Внутренняя ошибка сервера", "code": "internal_error"},
        )
