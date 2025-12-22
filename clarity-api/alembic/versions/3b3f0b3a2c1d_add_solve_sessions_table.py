"""add solve sessions table

Revision ID: 3b3f0b3a2c1d
Revises: 9a1c8d0fb58e
Create Date: 2025-12-22 02:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3b3f0b3a2c1d"
down_revision: Union[str, Sequence[str], None] = "9a1c8d0fb58e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "solve_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("current_step", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_solve_sessions_user_id", "solve_sessions", ["user_id"], unique=False)
    op.create_index(
        "ix_solve_sessions_user_status",
        "solve_sessions",
        ["user_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_solve_sessions_user_status", table_name="solve_sessions")
    op.drop_index("ix_solve_sessions_user_id", table_name="solve_sessions")
    op.drop_table("solve_sessions")
