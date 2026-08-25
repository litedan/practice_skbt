"""Seed dev users."""

from typing import Sequence, Union

from alembic import op

revision: str = "002_users_history"
down_revision: Union[str, None] = "001_main_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# bcrypt hash for Password123! (60 chars)
_DEV_PASSWORD_HASH = "$2b$12$r9RR1tV1jfb2XVZpXXxRf.FxlSOyFhbMzSuY312mUGcrFr1IER9u6"


def upgrade() -> None:
    op.execute("SET search_path = app, public")
    op.execute(
        f"""
        INSERT INTO users (email, full_name, password_hash, phone, city, department_id, position_id, hire_date)
        SELECT
            'employee@example.com',
            'Иван Работник',
            '{_DEV_PASSWORD_HASH}',
            '+79001112233',
            'Москва',
            (SELECT id FROM departments WHERE name = 'IT'),
            (SELECT id FROM positions WHERE name = 'Работник'),
            CURRENT_DATE - INTERVAL '365 days'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'employee@example.com');

        INSERT INTO users (email, full_name, password_hash, phone, city, department_id, position_id, hire_date)
        SELECT
            'manager@example.com',
            'Пётр Руководитель',
            '{_DEV_PASSWORD_HASH}',
            '+79001112244',
            'Москва',
            (SELECT id FROM departments WHERE name = 'IT'),
            (SELECT id FROM positions WHERE name = 'Руководитель'),
            CURRENT_DATE - INTERVAL '1000 days'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'manager@example.com');

        INSERT INTO users (email, full_name, password_hash, phone, city, department_id, position_id, hire_date)
        SELECT
            'hr@example.com',
            'Анна HR',
            '{_DEV_PASSWORD_HASH}',
            '+79001112255',
            'Москва',
            (SELECT id FROM departments WHERE name = 'HR'),
            (SELECT id FROM positions WHERE name = 'HR'),
            CURRENT_DATE - INTERVAL '800 days'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'hr@example.com');

        INSERT INTO users (email, full_name, password_hash, phone, city, department_id, position_id, hire_date)
        SELECT
            'admin@example.com',
            'Системный Админ',
            '{_DEV_PASSWORD_HASH}',
            '+79001112266',
            'Москва',
            (SELECT id FROM departments WHERE name = 'HR'),
            (SELECT id FROM positions WHERE name = 'Администратор'),
            CURRENT_DATE - INTERVAL '2000 days'
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@example.com');
        """
    )


def downgrade() -> None:
    op.execute("SET search_path = app, public")
    op.execute(
        """
        DELETE FROM users WHERE email IN (
            'employee@example.com',
            'manager@example.com',
            'hr@example.com',
            'admin@example.com'
        );
        """
    )
