"""Drop tables/columns not present in canonical MainBD DDL."""

from typing import Sequence, Union

from alembic import op

revision: str = "003_align_canonical_ddl"
down_revision: Union[str, None] = "002_users_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET search_path = app, public")
    op.execute("DROP TABLE IF EXISTS request_history")
    op.execute("DROP TABLE IF EXISTS refresh_tokens")
    op.execute("ALTER TABLE requests DROP COLUMN IF EXISTS date_from")
    op.execute("ALTER TABLE requests DROP COLUMN IF EXISTS date_to")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS manager_id")
    op.execute("DROP INDEX IF EXISTS idx_users_manager")
    op.execute("DELETE FROM statuses WHERE name IN ('Черновик', 'На доработке')")
    op.execute(
        """
        DELETE FROM request_types WHERE name IN (
            'Отпуск', 'Больничный', 'Командировка', 'Кадровый перевод'
        )
        """
    )


def downgrade() -> None:
    pass
