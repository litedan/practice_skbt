"""Seed справочников: статусы заявок и типы."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_seed_dictionaries"
down_revision: Union[str, None] = "002_add_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    statuses = sa.table(
        "statuses",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        statuses,
        [
            {"id": 1, "name": "Новая"},
            {"id": 2, "name": "В работе"},
            {"id": 3, "name": "Одобрена"},
            {"id": 4, "name": "Отклонена"},
        ],
    )

    request_types = sa.table(
        "request_types",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("file_path", sa.String),
    )
    op.bulk_insert(
        request_types,
        [
            {"id": 1, "name": "Отпуск", "file_path": None},
            {"id": 2, "name": "Справка с места работы", "file_path": None},
            {"id": 3, "name": "Больничный", "file_path": None},
            {"id": 4, "name": "Командировка", "file_path": None},
        ],
    )

    consent_statuses = sa.table(
        "consent_statuses",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        consent_statuses,
        [
            {"id": 1, "name": "Активно"},
            {"id": 2, "name": "Отозвано"},
            {"id": 3, "name": "Истекло"},
        ],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM request_types WHERE id IN (1, 2, 3, 4)"))
    op.execute(sa.text("DELETE FROM statuses WHERE id IN (1, 2, 3, 4)"))
    op.execute(sa.text("DELETE FROM consent_statuses WHERE id IN (1, 2, 3)"))
