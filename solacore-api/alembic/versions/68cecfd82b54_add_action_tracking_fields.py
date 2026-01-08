"""add_action_tracking_fields

Revision ID: 68cecfd82b54
Revises: d5455f8e6d7e
Create Date: 2026-01-08 08:07:18.559762

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "68cecfd82b54"
down_revision: Union[str, Sequence[str], None] = "d5455f8e6d7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "solve_sessions",
        sa.Column(
            "action_completed", sa.Boolean(), server_default="false", nullable=False
        ),
    )

    op.add_column(
        "solve_sessions", sa.Column("action_completed_at", sa.DateTime(), nullable=True)
    )

    op.create_index(
        "idx_solve_sessions_action_status",
        "solve_sessions",
        ["user_id", "action_completed", sa.text("created_at DESC")],
        postgresql_where=sa.text("first_step_action IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_solve_sessions_action_status", table_name="solve_sessions")
    op.drop_column("solve_sessions", "action_completed_at")
    op.drop_column("solve_sessions", "action_completed")
