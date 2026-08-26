"""Add templates table and seed initial templates."""

from typing import Sequence, Union

from alembic import op

revision: str = "004_templates_seed"
down_revision: Union[str, None] = "003_align_canonical_ddl"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path = app, public")
    op.execute(
        """
        CREATE TABLE templates (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            file_path TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX idx_templates_code ON templates(code)")
    op.execute(
        """
        INSERT INTO templates (name, code, file_path, is_active) VALUES
        ('Заявление на отпуск', 'vacation_application', 'zayavlenie_na_otpusk.docx', TRUE),
        ('Заявление на больничный', 'sick_leave_application', 'zayavlenie_na_bolnichiy.docx', TRUE)
        ON CONFLICT (code) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("SET search_path = app, public")
    op.execute("DROP TABLE IF EXISTS templates")