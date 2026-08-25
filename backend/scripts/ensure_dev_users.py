"""Ensure dev @kedo.local users exist (idempotent). Used on Docker startup."""

import asyncio

import asyncpg

from app.core.config import get_settings
from app.core.security import hash_password

PASSWORD = "Password123!"

SEEDS = (
    ("employee@kedo.local", "Иван Работник", "Работник", "IT", "+79001112233"),
    ("manager@kedo.local", "Пётр Руководитель", "Руководитель", "IT", "+79001112244"),
    ("hr@kedo.local", "Анна HR", "HR", "HR", "+79001112255"),
    ("admin@kedo.local", "Системный Админ", "Администратор", "HR", "+79001112266"),
)


async def main() -> None:
    settings = get_settings()
    password_hash = hash_password(PASSWORD)

    conn = await asyncpg.connect(
        user=settings.main_db_user,
        password=settings.main_db_password,
        database=settings.main_db_name,
        host=settings.main_db_host,
        port=settings.main_db_port,
    )
    try:
        await conn.execute("SET search_path = app, public")

        for name in ("Работник", "HR", "Руководитель", "Администратор"):
            await conn.execute(
                "INSERT INTO positions (name) VALUES ($1) ON CONFLICT DO NOTHING",
                name,
            )
        for name in ("HR", "IT", "Finance"):
            await conn.execute(
                "INSERT INTO departments (name) VALUES ($1) ON CONFLICT DO NOTHING",
                name,
            )

        for email, full_name, position, department, phone in SEEDS:
            await conn.execute(
                """
                INSERT INTO users (
                    email, full_name, password_hash, phone, city,
                    department_id, position_id, hire_date
                )
                SELECT
                    $1, $2, $3, $4, 'Москва',
                    (SELECT id FROM departments WHERE name = $5),
                    (SELECT id FROM positions WHERE name = $6),
                    CURRENT_DATE
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = $1)
                """,
                email,
                full_name,
                password_hash,
                phone,
                department,
                position,
            )
            await conn.execute(
                """
                UPDATE users
                SET password_hash = $1,
                    position_id = (SELECT id FROM positions WHERE name = $2),
                    department_id = COALESCE(
                        department_id,
                        (SELECT id FROM departments WHERE name = $3)
                    )
                WHERE email = $4
                """,
                password_hash,
                position,
                department,
                email,
            )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
