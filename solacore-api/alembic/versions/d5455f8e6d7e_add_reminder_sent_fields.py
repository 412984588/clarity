"""add_reminder_sent_fields

Revision ID: d5455f8e6d7e
Revises: e7b9c1d2a3f4
Create Date: 2026-01-08 07:36:50.153189

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5455f8e6d7e"
down_revision: Union[str, Sequence[str], None] = "e7b9c1d2a3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add reminder_sent column with default False
    op.add_column(
        "solve_sessions",
        sa.Column(
            "reminder_sent", sa.Boolean(), server_default="false", nullable=False
        ),
    )

    # Add reminder_sent_at column (nullable)
    op.add_column(
        "solve_sessions", sa.Column("reminder_sent_at", sa.DateTime(), nullable=True)
    )

    # Create partial index for efficient reminder queries
    op.create_index(
        "idx_solve_sessions_reminder",
        "solve_sessions",
        ["reminder_time", "reminder_sent"],
        postgresql_where=sa.text("reminder_time IS NOT NULL AND reminder_sent = FALSE"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index first
    op.drop_index("idx_solve_sessions_reminder", table_name="solve_sessions")

    # Drop columns
    op.drop_column("solve_sessions", "reminder_sent_at")
    op.drop_column("solve_sessions", "reminder_sent")
