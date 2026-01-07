from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e7b9c1d2a3f4"
down_revision: Union[str, Sequence[str], None] = "a123ffbf5a05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "solve_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column(
            "schema_version", sa.String(length=20), nullable=False, server_default="v1"
        ),
        sa.Column("profile", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"], ["solve_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index(
        "ix_solve_profiles_session_id", "solve_profiles", ["session_id"], unique=False
    )
    op.create_index(
        "ix_solve_profiles_schema_version",
        "solve_profiles",
        ["schema_version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_solve_profiles_schema_version", table_name="solve_profiles")
    op.drop_index("ix_solve_profiles_session_id", table_name="solve_profiles")
    op.drop_table("solve_profiles")
