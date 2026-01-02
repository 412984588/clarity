"""merge prompt_templates and previous migrations

Revision ID: a123ffbf5a05
Revises: c4d5e6f7a8b9, c9cb822b00d0
Create Date: 2026-01-01 06:54:14.209510

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "a123ffbf5a05"
down_revision: Union[str, Sequence[str], None] = ("c4d5e6f7a8b9", "c9cb822b00d0")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
