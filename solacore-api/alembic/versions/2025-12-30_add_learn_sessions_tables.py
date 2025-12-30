"""add learn sessions and messages tables

Revision ID: a1b2c3d4e5f6
Revises: 8c1e5a2f9d3b
Create Date: 2025-12-30 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op  # type: ignore[attr-defined]
from sqlalchemy.dialects.postgresql import JSON, UUID

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "8c1e5a2f9d3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建学习会话和消息表"""
    # 创建 learn_sessions 表
    op.create_table(
        "learn_sessions",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status", sa.String(length=50), nullable=True, server_default="active"
        ),
        sa.Column(
            "current_step", sa.String(length=50), nullable=True, server_default="start"
        ),
        sa.Column("locale", sa.String(length=10), nullable=True, server_default="zh"),
        sa.Column("topic", sa.Text(), nullable=True),
        sa.Column("key_concepts", JSON(), nullable=True),
        sa.Column("review_schedule", JSON(), nullable=True),
        sa.Column("learning_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_learn_sessions_user_id", "learn_sessions", ["user_id"], unique=False
    )
    op.create_index(
        "ix_learn_sessions_user_status",
        "learn_sessions",
        ["user_id", "status"],
        unique=False,
    )

    # 创建 learn_messages 表
    op.create_table(
        "learn_messages",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("step", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"], ["learn_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_learn_messages_session_id", "learn_messages", ["session_id"], unique=False
    )


def downgrade() -> None:
    """删除学习相关表"""
    op.drop_index("ix_learn_messages_session_id", table_name="learn_messages")
    op.drop_table("learn_messages")
    op.drop_index("ix_learn_sessions_user_status", table_name="learn_sessions")
    op.drop_index("ix_learn_sessions_user_id", table_name="learn_sessions")
    op.drop_table("learn_sessions")
