"""Конфигурация приложения на базе Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Централизованные настройки сервиса КЭДО."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Общие ---
    app_name: str = "KEDO"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # --- MainBD ---
    main_db_host: str = "localhost"
    main_db_port: int = 5432
    main_db_user: str = "kedo"
    main_db_password: str = "changeme"
    main_db_name: str = "kedo_main"

    # --- LogBD ---
    log_db_host: str = "localhost"
    log_db_port: int = 5432
    log_db_user: str = "kedo_log"
    log_db_password: str = "changeme"
    log_db_name: str = "kedo_log"

    # --- JWT ---
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- Файлы ---
    upload_dir: str = "./uploads"

    # --- Генерация документов ---
    document_templates_dir: str = "./app/templates" # путь к шаблонам
    generated_documents_dir: str = "./generated_docs" # путь к сгенеренным файлам
    organization_name: str = 'ООО "Компания"'  
    director_name: str = "Иванов И.И." 
    director_position: str = "Генеральный директор"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        """Разбирает список разрешённых CORS-источников."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def main_database_url(self) -> str:
        """Async URL для основной БД (MainBD)."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.main_db_user,
                password=self.main_db_password,
                host=self.main_db_host,
                port=self.main_db_port,
                path=self.main_db_name,
            )
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def log_database_url(self) -> str:
        """Async URL для БД аудита (LogBD)."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.log_db_user,
                password=self.log_db_password,
                host=self.log_db_host,
                port=self.log_db_port,
                path=self.log_db_name,
            )
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def main_database_url_sync(self) -> str:
        """Sync URL для Alembic (MainBD)."""
        return self.main_database_url.replace("+asyncpg", "")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def log_database_url_sync(self) -> str:
        """Sync URL для Alembic (LogBD)."""
        return self.log_database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Singleton настроек (кэшируется на время жизни процесса)."""
    return Settings()
