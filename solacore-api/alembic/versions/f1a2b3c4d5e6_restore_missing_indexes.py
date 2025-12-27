"""restore missing indexes for performance

Revision ID: f1a2b3c4d5e6
Revises: c8a2f3d4e5b6
Create Date: 2025-12-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "c8a2f3d4e5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Restore missing indexes that were accidentally dropped."""
    # 恢复 password_reset_tokens 索引（重置密码查询）
    op.create_index(
        op.f("ix_password_reset_tokens_token_hash"),
        "password_reset_tokens",
        ["token_hash"],
        unique=False,
    )

    # 恢复 solve_sessions 索引（会话列表查询）
    op.create_index(
        op.f("ix_solve_sessions_user_id"),
        "solve_sessions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_solve_sessions_user_status"),
        "solve_sessions",
        ["user_id", "status"],
        unique=False,
    )

    # 为 step_history 添加 session_id 索引（步骤历史查询）
    op.create_index(
        op.f("ix_step_history_session_id"),
        "step_history",
        ["session_id"],
        unique=False,
    )

    # 为 analytics_events 添加 session_id 索引（分析事件查询）
    op.create_index(
        op.f("ix_analytics_events_session_id"),
        "analytics_events",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the restored indexes."""
    op.drop_index(op.f("ix_analytics_events_session_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_step_history_session_id"), table_name="step_history")
    op.drop_index(op.f("ix_solve_sessions_user_status"), table_name="solve_sessions")
    op.drop_index(op.f("ix_solve_sessions_user_id"), table_name="solve_sessions")
    op.drop_index(
        op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens"
    )
