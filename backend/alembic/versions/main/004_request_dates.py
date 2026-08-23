"""Add date_from and date_to to requests."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_request_dates"
down_revision: Union[str, None] = "003_seed_dictionaries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("requests", sa.Column("date_from", sa.Date(), nullable=True))
    op.add_column("requests", sa.Column("date_to", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("requests", "date_to")
    op.drop_column("requests", "date_from")
