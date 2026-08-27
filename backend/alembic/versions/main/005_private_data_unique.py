"""Unique indexes for personal document fields."""

from typing import Sequence, Union

from alembic import op

revision: str = "005_private_data_unique"
down_revision: Union[str, None] = "004_templates_seed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FIELDS = ("passport", "snils", "inn", "military_id")


def upgrade() -> None:
    op.execute("SET search_path = app, public")

    for field in _FIELDS:
        op.execute(
            f"""
            UPDATE user_private_data
            SET {field} = NULL
            WHERE {field} IS NOT NULL AND btrim({field}) = ''
            """
        )
        # Keep earliest row, clear duplicates so unique index can be created
        op.execute(
            f"""
            UPDATE user_private_data AS upd
            SET {field} = NULL
            WHERE upd.{field} IS NOT NULL
              AND upd.id NOT IN (
                  SELECT keep_id FROM (
                      SELECT MIN(id) AS keep_id
                      FROM user_private_data
                      WHERE {field} IS NOT NULL
                      GROUP BY lower(btrim({field}))
                  ) AS kept
              )
            """
        )
        op.execute(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_user_private_data_{field}
            ON user_private_data ({field})
            WHERE {field} IS NOT NULL
            """
        )


def downgrade() -> None:
    op.execute("SET search_path = app, public")
    for field in _FIELDS:
        op.execute(f"DROP INDEX IF EXISTS uq_user_private_data_{field}")
