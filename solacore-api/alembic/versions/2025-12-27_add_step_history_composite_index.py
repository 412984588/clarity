"""add composite index for step_history lookups

Revision ID: 8c1e5a2f9d3b
Revises: 7a8b9c0d1e2f
Create Date: 2025-12-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c1e5a2f9d3b"
down_revision: Union[str, Sequence[str], None] = "7a8b9c0d1e2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite index for StepHistory lookups."""
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY "
            "ix_step_history_session_step_completed_started_at "
            "ON step_history (session_id, step, completed_at, started_at)"
        )


def downgrade() -> None:
    """Drop composite index for StepHistory lookups."""
    with op.get_context().autocommit_block():
        op.execute(
            "DROP INDEX CONCURRENTLY "
            "ix_step_history_session_step_completed_started_at"
        )
