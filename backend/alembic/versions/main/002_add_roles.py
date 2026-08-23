"""Add RBAC roles table and user.role_id."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_roles"
down_revision: Union[str, None] = "001_main_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles_table = op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_roles_code", "roles", ["code"])

    op.bulk_insert(
        roles_table,
        [
            {"id": 1, "code": "employee", "name": "Сотрудник"},
            {"id": 2, "code": "hr", "name": "HR-специалист"},
            {"id": 3, "code": "admin", "name": "Администратор"},
        ],
    )

    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE users SET role_id = 1 WHERE role_id IS NULL"))
    op.alter_column("users", "role_id", nullable=False)
    op.create_foreign_key("fk_users_role_id", "users", "roles", ["role_id"], ["id"])
    op.create_index("ix_users_role_id", "users", ["role_id"])


def downgrade() -> None:
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_constraint("fk_users_role_id", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
    op.drop_index("ix_roles_code", table_name="roles")
    op.drop_table("roles")
