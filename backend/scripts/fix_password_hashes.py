"""One-off: fix invalid password hashes in MainBD."""

import asyncio

import asyncpg

from app.core.config import get_settings
from app.core.security import hash_password, verify_password

PASSWORD = "Password123!"


async def main() -> None:
    settings = get_settings()
    password_hash = hash_password(PASSWORD)
    assert verify_password(PASSWORD, password_hash)
    assert len(password_hash) == 60
    print("hash ok:", password_hash)

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

        result = await conn.execute(
            "UPDATE users SET password_hash = $1",
            password_hash,
        )
        print("updated hashes:", result)

        seeds = (
            ("employee@kedo.local", "Иван Работник", "Работник", "IT"),
            ("manager@kedo.local", "Пётр Руководитель", "Руководитель", "IT"),
            ("hr@kedo.local", "Анна HR", "HR", "HR"),
            ("admin@kedo.local", "Системный Админ", "Администратор", "HR"),
        )
        for email, full_name, position, department in seeds:
            await conn.execute(
                """
                INSERT INTO users (email, full_name, password_hash, department_id, position_id, hire_date)
                SELECT $1, $2, $3,
                       (SELECT id FROM departments WHERE name = $4),
                       (SELECT id FROM positions WHERE name = $5),
                       CURRENT_DATE
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = $1)
                """,
                email,
                full_name,
                password_hash,
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

        rows = await conn.fetch(
            """
            SELECT u.email, length(u.password_hash) AS len, p.name AS position
            FROM users u
            LEFT JOIN positions p ON p.id = u.position_id
            WHERE u.email LIKE '%@kedo.local'
            ORDER BY u.email
            """
        )
        for row in rows:
            print(row["email"], row["len"], row["position"])
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
