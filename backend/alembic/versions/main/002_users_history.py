"""Seed dev users."""

from typing import Sequence, Union

from alembic import op

revision: str = "002_users_history"
down_revision: Union[str, None] = "001_main_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# bcrypt hash for Password123! (60 chars)
_DEV_PASSWORD_HASH = "$2b$12$r9RR1tV1jfb2XVZpXXxRf.FxlSOyFhbMzSuY312mUGcrFr1IER9u6"

_SEED_USERS = [
    ("employee@kedo.local", "Иван Работник", "+79001112233", "IT", "Работник", "365 days"),
    ("manager@kedo.local", "Пётр Руководитель", "+79001112244", "IT", "Руководитель", "1000 days"),
    ("hr@kedo.local", "Анна HR", "+79001112255", "HR", "HR", "800 days"),
    ("admin@kedo.local", "Системный Админ", "+79001112266", "HR", "Администратор", "2000 days"),
]


def upgrade() -> None:
    op.execute("SET search_path = app, public")
    for email, full_name, phone, dept, position, hire_interval in _SEED_USERS:
        op.execute(
            f"""
            INSERT INTO users (email, full_name, password_hash, phone, city, department_id, position_id, hire_date)
            SELECT
                '{email}',
                '{full_name}',
                '{_DEV_PASSWORD_HASH}',
                '{phone}',
                'Москва',
                (SELECT id FROM departments WHERE name = '{dept}'),
                (SELECT id FROM positions WHERE name = '{position}'),
                CURRENT_DATE - INTERVAL '{hire_interval}'
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = '{email}')
            """
        )


def downgrade() -> None:
    op.execute("SET search_path = app, public")
    emails = ", ".join(f"'{email}'" for email, *_ in _SEED_USERS)
    op.execute(f"DELETE FROM users WHERE email IN ({emails})")
