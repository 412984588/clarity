"""add solve session fields

Revision ID: c2b0c4e2a7b5
Revises: 3b3f0b3a2c1d
Create Date: 2025-12-22 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2b0c4e2a7b5"
down_revision: Union[str, Sequence[str], None] = "3b3f0b3a2c1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "solve_sessions", sa.Column("locale", sa.String(length=10), server_default="en")
    )
    op.add_column(
        "solve_sessions", sa.Column("first_step_action", sa.Text(), nullable=True)
    )
    op.add_column(
        "solve_sessions", sa.Column("reminder_time", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("solve_sessions", "reminder_time")
    op.drop_column("solve_sessions", "first_step_action")
    op.drop_column("solve_sessions", "locale")
