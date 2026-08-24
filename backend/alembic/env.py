"""Alembic migration environment (MainBD / LogBD)."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings

# Импорт всех моделей для регистрации metadata
import app.models.main  # noqa: F401
import app.models.log  # noqa: F401
from app.core.database import LogBase, MainBase

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Выбор контура БД через: alembic -x db=main|log ...
x_args = context.get_x_argument(as_dictionary=True)
db_target = x_args.get("db", "main")

if db_target == "log":
    target_metadata = LogBase.metadata
    database_url = settings.log_database_url
    version_locations = ["alembic/versions/log"]
    version_table_schema = None
else:
    target_metadata = MainBase.metadata
    database_url = settings.main_database_url
    version_locations = ["alembic/versions/main"]
    version_table_schema = "app"


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        version_locations=version_locations,
        version_table_schema=version_table_schema,
        include_schemas=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_locations=version_locations,
        version_table_schema=version_table_schema,
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = database_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        if db_target != "log":
            await connection.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
            await connection.commit()
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
