"""add_session_tags

Revision ID: a903714778fe
Revises: 68cecfd82b54
Create Date: 2026-01-08 08:14:21.784073

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a903714778fe"
down_revision: Union[str, Sequence[str], None] = "68cecfd82b54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "solve_sessions",
        sa.Column(
            "tags", postgresql.ARRAY(sa.String(50)), nullable=True, server_default="{}"
        ),
    )

    op.create_index(
        "idx_solve_sessions_tags", "solve_sessions", ["tags"], postgresql_using="gin"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_solve_sessions_tags", table_name="solve_sessions")
    op.drop_column("solve_sessions", "tags")
