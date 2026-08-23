"""Кастомные исключения и обработчики ошибок FastAPI."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


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


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует единообразные JSON-ответы на ошибки."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        # В production здесь также пишем в system_events_log
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Внутренняя ошибка сервера", "code": "internal_error"},
        )
